from typing import Annotated

from fastapi import APIRouter, Depends, Query, status

from api.deps import PaginationDep, SessionDep
from core.enums import ProjetoStatus, UserRole
from core.security import CurrentUser, get_current_user, require_role
from modules.projetos.schema import (
	ProjetoCreate,
	ProjetoFuncionarioCreate,
	ProjetoFuncionarioResponse,
	ProjetoResponse,
	ProjetoUpdate,
)
from modules.projetos.service import ProjetoService

router = APIRouter(prefix='/projetos', tags=['Projetos'])


def _service(session: SessionDep) -> ProjetoService:
	return ProjetoService(session)


ServiceDep = Annotated[ProjetoService, Depends(_service)]
AdminGuard = Depends(require_role(UserRole.ADMIN.value))
CurrentUserDep = Annotated[CurrentUser, Depends(get_current_user)]


@router.post(
	'',
	response_model=ProjetoResponse,
	status_code=status.HTTP_201_CREATED,
	dependencies=[AdminGuard],
	summary='Cria projeto e define cliente vinculado (somente admin)',
)
async def criar(payload: ProjetoCreate, service: ServiceDep):
	return await service.create(payload)


@router.get(
	'',
	response_model=list[ProjetoResponse],
	summary='Lista projetos visíveis ao usuário autenticado',
	description=(
		'Admin lista todos. Cliente lista os próprios projetos. Funcionário '
		'lista projetos onde participa da equipe.'
	),
)
async def listar(
	service: ServiceDep,
	page: PaginationDep,
	current_user: CurrentUserDep,
	cliente_id: int | None = None,
	status_filter: Annotated[ProjetoStatus | None, Query(alias='status')] = None,
):
	return await service.list_visible(
		offset=page.offset,
		limit=page.limit,
		usuario_id=current_user.id,
		role=current_user.role,
		cliente_id=cliente_id,
		status=status_filter,
	)


@router.get(
	'/{projeto_id}',
	response_model=ProjetoResponse,
	summary='Obtém projeto visível ao usuário autenticado',
)
async def obter(projeto_id: int, service: ServiceDep, current_user: CurrentUserDep):
	return await service.get_visible(projeto_id, current_user.id, current_user.role)


@router.patch(
	'/{projeto_id}',
	response_model=ProjetoResponse,
	dependencies=[AdminGuard],
	summary='Atualiza projeto (somente admin)',
)
async def atualizar(projeto_id: int, payload: ProjetoUpdate, service: ServiceDep):
	return await service.update(projeto_id, payload)


@router.delete(
	'/{projeto_id}',
	status_code=status.HTTP_204_NO_CONTENT,
	dependencies=[AdminGuard],
	summary='Remove projeto (somente admin)',
)
async def deletar(projeto_id: int, service: ServiceDep):
	await service.delete(projeto_id)


@router.post(
	'/{projeto_id}/equipe',
	response_model=ProjetoFuncionarioResponse,
	status_code=status.HTTP_201_CREATED,
	dependencies=[AdminGuard],
	summary='Adiciona funcionário ao projeto (somente admin)',
)
async def adicionar_membro(
	projeto_id: int, payload: ProjetoFuncionarioCreate, service: ServiceDep
):
	return await service.adicionar_membro(projeto_id, payload)


@router.get(
	'/{projeto_id}/equipe',
	response_model=list[ProjetoFuncionarioResponse],
	summary='Lista equipe do projeto visível ao usuário autenticado',
)
async def listar_equipe(
	projeto_id: int, service: ServiceDep, current_user: CurrentUserDep
):
	await service.get_visible(projeto_id, current_user.id, current_user.role)
	return await service.listar_equipe(projeto_id)


@router.delete(
	'/{projeto_id}/equipe/{funcionario_id}',
	status_code=status.HTTP_204_NO_CONTENT,
	dependencies=[AdminGuard],
	summary='Remove funcionário do projeto (somente admin)',
)
async def remover_membro(projeto_id: int, funcionario_id: int, service: ServiceDep):
	await service.remover_membro(projeto_id, funcionario_id)
