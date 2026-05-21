from typing import Annotated

from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from auth.db import get_session
from auth.repository import UsuarioRepository
from auth.schema import (
	LoginRequest,
	RefreshRequest,
	RegisterRequest,
	TokenResponse,
	UsuarioInfo,
)
from auth.security import (
	CREDENTIALS_EXCEPTION,
	TOKEN_TYPE_ACCESS,
	decode_token,
)
from auth.service import AuthService

router = APIRouter(prefix='/auth', tags=['Auth'])

oauth2_scheme = OAuth2PasswordBearer(tokenUrl='/auth/login', auto_error=False)


def _service(session: Annotated[AsyncSession, Depends(get_session)]) -> AuthService:
	return AuthService(session)


ServiceDep = Annotated[AuthService, Depends(_service)]


async def get_current_user(
	token: Annotated[str | None, Depends(oauth2_scheme)],
	session: Annotated[AsyncSession, Depends(get_session)],
) -> UsuarioInfo:
	if not token:
		raise CREDENTIALS_EXCEPTION
	payload = decode_token(token, TOKEN_TYPE_ACCESS)
	repo = UsuarioRepository(session)
	usuario = await repo.get(int(payload['sub']))
	if not usuario:
		raise CREDENTIALS_EXCEPTION
	return UsuarioInfo.model_validate(usuario)


@router.post(
	'/register', response_model=UsuarioInfo, status_code=status.HTTP_201_CREATED
)
async def register(payload: RegisterRequest, service: ServiceDep):
	return await service.register(payload)


@router.post('/login', response_model=TokenResponse)
async def login(payload: LoginRequest, service: ServiceDep):
	_, tokens = await service.login(payload)
	return tokens


@router.post('/refresh', response_model=TokenResponse)
async def refresh(payload: RefreshRequest, service: ServiceDep):
	return await service.refresh(payload.refresh_token)


@router.get('/me', response_model=UsuarioInfo)
async def me(current_user: Annotated[UsuarioInfo, Depends(get_current_user)]):
	return current_user
