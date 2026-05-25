import json
from http import HTTPStatus
from typing import Annotated
from urllib.parse import parse_qs

import httpx
from core.config import get_settings
from core.enums import UserStatus
from core.password import verify_password
from core.security import create_access_token, create_refresh_token
from db.session import get_session
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import JSONResponse
from modules.users.model import Usuario
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(prefix='/auth', tags=['Auth'])

settings = get_settings()
AUTH_PROXY_TIMEOUT_SECONDS = 10
SessionDep = Annotated[AsyncSession, Depends(get_session)]


@router.post('/login', summary='Login via serviço de autenticação')
async def login(request: Request, session: SessionDep):
	"""Função para autenticar o usuário e retornar tokens JWT."""
	body = await request.body()
	content_type = request.headers.get(
		'content-type', 'application/x-www-form-urlencoded'
	)
	headers = {
		'accept': 'application/json',
		'content-type': content_type,
	}

	try:
		async with httpx.AsyncClient(timeout=AUTH_PROXY_TIMEOUT_SECONDS) as client:
			response = await client.post(
				settings.auth_token_url,
				content=body,
				headers=headers,
			)
	except httpx.RequestError as exc:
		return await _login_local(body, content_type, session, exc)

	if response.status_code == HTTPStatus.NOT_FOUND or (
		response.status_code >= HTTPStatus.INTERNAL_SERVER_ERROR
	):
		return await _login_local(
			body,
			content_type,
			session,
			RuntimeError('Serviço auth indisponível ou mal configurado.'),
		)

	return JSONResponse(
		status_code=response.status_code,
		content=_response_content(response),
	)


def _response_content(response: httpx.Response):
	"""Função para converter a resposta do auth em conteúdo JSON."""
	try:
		return response.json()
	except ValueError:
		return {'detail': response.text}


async def _login_local(
	body: bytes,
	content_type: str,
	session: AsyncSession,
	original_error: Exception,
) -> JSONResponse:
	"""Função para autenticar pela API quando o serviço auth estiver indisponível."""
	email, senha = _extract_credentials(body, content_type)
	if not email or not senha:
		raise HTTPException(
			status_code=HTTPStatus.UNPROCESSABLE_ENTITY,
			detail='Informe email/username e senha/password.',
		) from original_error

	result = await session.execute(select(Usuario).where(Usuario.email == email))
	usuario = result.scalar_one_or_none()
	if not usuario or not verify_password(senha, usuario.senha_hash):
		raise HTTPException(
			status_code=HTTPStatus.UNAUTHORIZED,
			detail='Credenciais inválidas',
			headers={'WWW-Authenticate': 'Bearer'},
		) from original_error

	if usuario.status != UserStatus.ATIVO:
		raise HTTPException(
			status_code=HTTPStatus.FORBIDDEN,
			detail='Usuário pendente ou inativo',
		) from original_error

	role = getattr(usuario.role, 'value', usuario.role)
	return JSONResponse(
		status_code=HTTPStatus.OK,
		content={
			'access_token': create_access_token(usuario.id, {'role': role}),
			'refresh_token': create_refresh_token(usuario.id),
			'token_type': 'bearer',
		},
	)


def _extract_credentials(body: bytes, content_type: str) -> tuple[str, str]:
	"""Função para extrair email e senha do corpo recebido pelo Swagger."""
	if 'application/json' in content_type:
		payload = json.loads(body.decode('utf-8') or '{}')
		return str(payload.get('email') or ''), str(payload.get('senha') or '')

	form = parse_qs(body.decode('utf-8'), keep_blank_values=True)
	email = _first_form_value(form, 'username') or _first_form_value(form, 'email')
	senha = _first_form_value(form, 'password') or _first_form_value(form, 'senha')
	return email, senha


def _first_form_value(form: dict[str, list[str]], key: str) -> str:
	"""Função para obter o primeiro valor de um campo de formulário."""
	values = form.get(key)
	if not values:
		return ''
	return values[0]
