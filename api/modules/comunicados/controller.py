from typing import Annotated

from fastapi import APIRouter, Depends, Query, status

from api.deps import PaginationDep, SessionDep
from core.enums import ComunicadoAlvo, UserRole
from core.security import get_current_user_id, require_role
from modules.comunicados.schema import (
	ComunicadoCreate,
	ComunicadoLeituraResponse,
	ComunicadoResponse,
	ComunicadoUpdate,
)
from modules.comunicados.service import ComunicadoService

router = APIRouter(prefix='/comunicados', tags=['Comunicados'])


def _service(session: SessionDep) -> ComunicadoService:
	return ComunicadoService(session)


ServiceDep = Annotated[ComunicadoService, Depends(_service)]
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
	response_model=ComunicadoResponse,
	status_code=status.HTTP_201_CREATED,
	dependencies=[AdminGuard],
	summary='Cria comunicado (somente admin)',
)
async def criar(payload: ComunicadoCreate, service: ServiceDep):
	return await service.create(payload)


@router.get(
	'',
	response_model=list[ComunicadoResponse],
	dependencies=[AuthenticatedGuard],
	summary='Lista comunicados (clientes, funcionários e admins)',
)
async def listar(
	service: ServiceDep,
	page: PaginationDep,
	alvo: Annotated[ComunicadoAlvo | None, Query()] = None,
):
	return await service.list_filtered(offset=page.offset, limit=page.limit, alvo=alvo)


@router.get(
	'/{comunicado_id}',
	response_model=ComunicadoResponse,
	dependencies=[AuthenticatedGuard],
	summary='Obtém comunicado (clientes, funcionários e admins)',
)
async def obter(comunicado_id: int, service: ServiceDep):
	return await service.get(comunicado_id)


@router.patch(
	'/{comunicado_id}',
	response_model=ComunicadoResponse,
	dependencies=[AdminGuard],
	summary='Atualiza comunicado (somente admin)',
)
async def atualizar(comunicado_id: int, payload: ComunicadoUpdate, service: ServiceDep):
	return await service.update(comunicado_id, payload)


@router.delete(
	'/{comunicado_id}',
	status_code=status.HTTP_204_NO_CONTENT,
	dependencies=[AdminGuard],
	summary='Remove comunicado (somente admin)',
)
async def deletar(comunicado_id: int, service: ServiceDep):
	await service.delete(comunicado_id)


@router.post(
	'/{comunicado_id}/leituras',
	response_model=ComunicadoLeituraResponse,
	status_code=status.HTTP_201_CREATED,
	summary='Marca comunicado como lido (usuário autenticado)',
)
async def marcar_lido(
	comunicado_id: int, service: ServiceDep, current_user_id: CurrentUserId
):
	return await service.marcar_lido(comunicado_id, current_user_id)


@router.get(
	'/{comunicado_id}/leituras',
	response_model=list[ComunicadoLeituraResponse],
	dependencies=[AdminGuard],
	summary='Lista leituras do comunicado (somente admin)',
)
async def listar_leituras(comunicado_id: int, service: ServiceDep):
	return await service.list_leituras(comunicado_id)