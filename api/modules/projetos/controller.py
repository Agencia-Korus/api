from typing import Annotated

from core.enums import ProjetoStatus, UserRole
from core.security import CurrentUser, get_current_user, require_role
from deps import PaginationDep, SessionDep
from fastapi import APIRouter, Depends, Query, status
from modules.projetos.schema import (
	ProjetoCriar,
	ProjetoFuncionarioCriar,
	ProjetoFuncionarioResposta,
	ProjetoResposta,
	ProjetoAtualizar,
)
from modules.projetos.service import ServicoProjeto

router = APIRouter(prefix='/projetos', tags=['Projetos'])


def _service(session: SessionDep) -> ServicoProjeto:
	"""Função para criar o serviço de aplicação com a sessão atual."""
	return ServicoProjeto(session)


ServiceDep = Annotated[ServicoProjeto, Depends(_service)]
AdminGuard = Depends(require_role(UserRole.ADMIN.value))
CurrentUserDep = Annotated[CurrentUser, Depends(get_current_user)]


@router.post(
	'',
	response_model=ProjetoResposta,
	status_code=status.HTTP_201_CREATED,
	dependencies=[AdminGuard],
	summary='Cria projeto e define cliente vinculado (somente admin)',
)
async def criar(payload: ProjetoCriar, service: ServiceDep):
	"""Função para criar um novo registro."""
	return await service.criar(payload)


@router.get(
	'',
	response_model=list[ProjetoResposta],
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
	"""Função para listar registros."""
	return await service.listar_visible(
		offset=page.offset,
		limit=page.limit,
		usuario_id=current_user.id,
		role=current_user.role,
		cliente_id=cliente_id,
		status=status_filter,
	)


@router.get(
	'/{projeto_id}',
	response_model=ProjetoResposta,
	summary='Obtém projeto visível ao usuário autenticado',
)
async def obter(projeto_id: int, service: ServiceDep, current_user: CurrentUserDep):
	"""Função para obter um registro pelo ID."""
	return await service.obter_visible(projeto_id, current_user.id, current_user.role)


@router.patch(
	'/{projeto_id}',
	response_model=ProjetoResposta,
	dependencies=[AdminGuard],
	summary='Atualiza projeto (somente admin)',
)
async def atualizar(projeto_id: int, payload: ProjetoAtualizar, service: ServiceDep):
	"""Função para atualizar um registro pelo ID."""
	return await service.atualizar(projeto_id, payload)


@router.delete(
	'/{projeto_id}',
	status_code=status.HTTP_204_NO_CONTENT,
	dependencies=[AdminGuard],
	summary='Remove projeto (somente admin)',
)
async def deletar(projeto_id: int, service: ServiceDep):
	"""Função para excluir um registro pelo ID."""
	await service.deletar(projeto_id)


@router.post(
	'/{projeto_id}/equipe',
	response_model=ProjetoFuncionarioResposta,
	status_code=status.HTTP_201_CREATED,
	dependencies=[AdminGuard],
	summary='Adiciona funcionário ao projeto (somente admin)',
)
async def adicionar_membro(
	projeto_id: int, payload: ProjetoFuncionarioCriar, service: ServiceDep
):
	"""Função para adicionar um funcionário à equipe do projeto."""
	return await service.adicionar_membro(projeto_id, payload)


@router.get(
	'/{projeto_id}/equipe',
	response_model=list[ProjetoFuncionarioResposta],
	summary='Lista equipe do projeto visível ao usuário autenticado',
)
async def listar_equipe(
	projeto_id: int, service: ServiceDep, current_user: CurrentUserDep
):
	"""Função para listar a equipe de um projeto."""
	await service.obter_visible(projeto_id, current_user.id, current_user.role)
	return await service.listar_equipe(projeto_id)


@router.delete(
	'/{projeto_id}/equipe/{funcionario_id}',
	status_code=status.HTTP_204_NO_CONTENT,
	dependencies=[AdminGuard],
	summary='Remove funcionário do projeto (somente admin)',
)
async def remover_membro(projeto_id: int, funcionario_id: int, service: ServiceDep):
	"""Função para remover um funcionário da equipe do projeto."""
	await service.remover_membro(projeto_id, funcionario_id)
