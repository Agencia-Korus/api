from typing import Annotated

from core.enums import UserRole, UserStatus
from core.security import require_role
from deps import PaginationDep, SessionDep
from fastapi import APIRouter, Depends, Query, status
from modules.users.schema import (
	UsuarioCreate,
	UsuarioResponse,
	UsuarioUpdate,
)
from modules.users.service import UsuarioService
from starlette.status import HTTP_201_CREATED

router = APIRouter(prefix='/usuarios', tags=['Usuários'])


def _service(session: SessionDep) -> UsuarioService:
	return UsuarioService(session)


ServiceDep = Annotated[UsuarioService, Depends(_service)]
AdminGuard = Depends(require_role(UserRole.ADMIN.value))


@router.post(
	'',
	response_model=UsuarioResponse,
	status_code=HTTP_201_CREATED,
	dependencies=[AdminGuard],
	summary='Cria usuário (somente admin)',
)
async def criar(payload: UsuarioCreate, service: ServiceDep):
	return await service.create(payload)


@router.get('', response_model=list[UsuarioResponse])
async def listar(
	service: ServiceDep,
	page: PaginationDep,
	role: UserRole | None = None,
	status_filter: Annotated[UserStatus | None, Query(alias='status')] = None,
	search: str | None = None,
):
	return await service.list_filtered(
		offset=page.offset,
		limit=page.limit,
		role=role,
		status=status_filter,
		search=search,
	)


@router.get('/{usuario_id}', response_model=UsuarioResponse)
async def obter(usuario_id: int, service: ServiceDep):
	return await service.get(usuario_id)


@router.patch(
	'/{usuario_id}',
	response_model=UsuarioResponse,
	dependencies=[AdminGuard],
	summary='Edita dados do usuário (somente admin)',
)
async def atualizar(usuario_id: int, payload: UsuarioUpdate, service: ServiceDep):
	return await service.update(usuario_id, payload)


@router.post(
	'/{usuario_id}/aprovar',
	response_model=UsuarioResponse,
	dependencies=[AdminGuard],
	summary='Aprova cadastro pendente, ativando o usuário (somente admin)',
)
async def aprovar(usuario_id: int, service: ServiceDep):
	return await service.approve(usuario_id)


@router.delete(
	'/{usuario_id}',
	status_code=status.HTTP_204_NO_CONTENT,
	dependencies=[AdminGuard],
	summary='Remove usuário (somente admin)',
)
async def deletar(usuario_id: int, service: ServiceDep):
	await service.delete(usuario_id)
