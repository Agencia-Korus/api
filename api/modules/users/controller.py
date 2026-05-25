from typing import Annotated

from core.enums import UserRole, UserStatus
from core.security import require_role
from deps import PaginationDep, SessionDep
from fastapi import APIRouter, Depends, Query, status
from modules.users.schema import (
	UsuarioCriar,
	UsuarioResposta,
	UsuarioAtualizar,
)
from modules.users.service import ServicoUsuario
from starlette.status import HTTP_201_CREATED

router = APIRouter(prefix='/usuarios', tags=['Usuários'])


def _service(session: SessionDep) -> ServicoUsuario:
	"""Função para criar o serviço de aplicação com a sessão atual."""
	return ServicoUsuario(session)


ServiceDep = Annotated[ServicoUsuario, Depends(_service)]
AdminGuard = Depends(require_role(UserRole.ADMIN.value))


@router.post(
	'',
	response_model=UsuarioResposta,
	status_code=HTTP_201_CREATED,
	dependencies=[AdminGuard],
	summary='Cria usuário (somente admin)',
)
async def criar(payload: UsuarioCriar, service: ServiceDep):
	"""Função para criar um novo registro."""
	return await service.criar(payload)


@router.get('', response_model=list[UsuarioResposta], dependencies=[AdminGuard])
async def listar(
	service: ServiceDep,
	page: PaginationDep,
	role: UserRole | None = None,
	status_filter: Annotated[UserStatus | None, Query(alias='status')] = None,
	search: str | None = None,
):
	"""Função para listar registros."""
	return await service.listar_filtrados(
		offset=page.offset,
		limit=page.limit,
		role=role,
		status=status_filter,
		search=search,
	)


@router.get('/{usuario_id}', response_model=UsuarioResposta, dependencies=[AdminGuard])
async def obter(usuario_id: int, service: ServiceDep):
	"""Função para obter um registro pelo ID."""
	return await service.obter(usuario_id)


@router.patch(
	'/{usuario_id}',
	response_model=UsuarioResposta,
	dependencies=[AdminGuard],
	summary='Edita dados do usuário (somente admin)',
)
async def atualizar(usuario_id: int, payload: UsuarioAtualizar, service: ServiceDep):
	"""Função para atualizar um registro pelo ID."""
	return await service.atualizar(usuario_id, payload)


@router.post(
	'/{usuario_id}/aprovar',
	response_model=UsuarioResposta,
	dependencies=[AdminGuard],
	summary='Aprova cadastro pendente, ativando o usuário (somente admin)',
)
async def aprovar(usuario_id: int, service: ServiceDep):
	"""Função para aprovar o cadastro de um usuário."""
	return await service.aprovar(usuario_id)


@router.delete(
	'/{usuario_id}',
	status_code=status.HTTP_204_NO_CONTENT,
	dependencies=[AdminGuard],
	summary='Remove usuário (somente admin)',
)
async def deletar(usuario_id: int, service: ServiceDep):
	"""Função para excluir um registro pelo ID."""
	await service.deletar(usuario_id)
