from typing import Annotated

from core.enums import ComunicadoAlvo, UserRole
from core.security import get_current_user_id, require_role
from deps import PaginationDep, SessionDep
from fastapi import APIRouter, Depends, Query, status
from modules.comunicados.schema import (
	ComunicadoCriar,
	ComunicadoLeituraResposta,
	ComunicadoResposta,
	ComunicadoAtualizar,
)
from modules.comunicados.service import ServicoComunicado

router = APIRouter(prefix='/comunicados', tags=['Comunicados'])


def _service(session: SessionDep) -> ServicoComunicado:
	"""Função para criar o serviço de aplicação com a sessão atual."""
	return ServicoComunicado(session)


ServiceDep = Annotated[ServicoComunicado, Depends(_service)]
CurrentUserId = Annotated[int, Depends(get_current_user_id)]
AdminGuard = Depends(require_role(UserRole.ADMIN.value))
AuthenticatedGuard = Depends(
	require_role(
		UserRole.CLIENTE.value,
		UserRole.FUNCIONARIO.value,
		UserRole.ADMIN.value,
	)
)


@router.post(
	'',
	response_model=ComunicadoResposta,
	status_code=status.HTTP_201_CREATED,
	dependencies=[AdminGuard],
	summary='Cria comunicado (somente admin)',
)
async def criar(payload: ComunicadoCriar, service: ServiceDep):
	"""Função para criar um novo registro."""
	return await service.criar(payload)


@router.get(
	'',
	response_model=list[ComunicadoResposta],
	dependencies=[AuthenticatedGuard],
	summary='Lista comunicados (clientes, funcionários e admins)',
)
async def listar(
	service: ServiceDep,
	page: PaginationDep,
	alvo: Annotated[ComunicadoAlvo | None, Query()] = None,
):
	"""Função para listar registros."""
	return await service.listar_filtrados(offset=page.offset, limit=page.limit, alvo=alvo)


@router.get(
	'/{comunicado_id}',
	response_model=ComunicadoResposta,
	dependencies=[AuthenticatedGuard],
	summary='Obtém comunicado (clientes, funcionários e admins)',
)
async def obter(comunicado_id: int, service: ServiceDep):
	"""Função para obter um registro pelo ID."""
	return await service.obter(comunicado_id)


@router.patch(
	'/{comunicado_id}',
	response_model=ComunicadoResposta,
	dependencies=[AdminGuard],
	summary='Atualiza comunicado (somente admin)',
)
async def atualizar(comunicado_id: int, payload: ComunicadoAtualizar, service: ServiceDep):
	"""Função para atualizar um registro pelo ID."""
	return await service.atualizar(comunicado_id, payload)


@router.delete(
	'/{comunicado_id}',
	status_code=status.HTTP_204_NO_CONTENT,
	dependencies=[AdminGuard],
	summary='Remove comunicado (somente admin)',
)
async def deletar(comunicado_id: int, service: ServiceDep):
	"""Função para excluir um registro pelo ID."""
	await service.deletar(comunicado_id)


@router.post(
	'/{comunicado_id}/leituras',
	response_model=ComunicadoLeituraResposta,
	status_code=status.HTTP_201_CREATED,
	summary='Marca comunicado como lido (usuário autenticado)',
)
async def marcar_lido(
	comunicado_id: int, service: ServiceDep, current_user_id: CurrentUserId
):
	"""Função para registrar a leitura de um comunicado."""
	return await service.marcar_lido(comunicado_id, current_user_id)


@router.get(
	'/{comunicado_id}/leituras',
	response_model=list[ComunicadoLeituraResposta],
	dependencies=[AdminGuard],
	summary='Lista leituras do comunicado (somente admin)',
)
async def listar_leituras(comunicado_id: int, service: ServiceDep):
	"""Função para listar leituras de um comunicado."""
	return await service.listar_leituras(comunicado_id)
