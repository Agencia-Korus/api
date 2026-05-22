from typing import Annotated

from fastapi import APIRouter, Depends, Query, status

from api.deps import PaginationDep, SessionDep
from core.enums import ServicoStatus, UserRole
from core.security import require_role
from modules.servicos.schema import (
	EntregavelCreate,
	EntregavelResponse,
	EntregavelUpdate,
	ServicoCreate,
	ServicoResponse,
	ServicoUpdate,
)
from modules.servicos.service import ServicoService

router = APIRouter(
	prefix='/servicos',
	tags=['Serviços'],
	dependencies=[Depends(require_role(UserRole.ADMIN.value))],
)


def _service(session: SessionDep) -> ServicoService:
	return ServicoService(session)


ServiceDep = Annotated[ServicoService, Depends(_service)]


@router.post('', response_model=ServicoResponse, status_code=status.HTTP_201_CREATED)
async def criar(payload: ServicoCreate, service: ServiceDep):
	return await service.create(payload)


@router.get('', response_model=list[ServicoResponse])
async def listar(
	service: ServiceDep,
	page: PaginationDep,
	status_filter: Annotated[ServicoStatus | None, Query(alias='status')] = None,
):
	return await service.list_filtered(
		offset=page.offset, limit=page.limit, status=status_filter
	)


@router.get('/{servico_id}', response_model=ServicoResponse)
async def obter(servico_id: int, service: ServiceDep):
	return await service.get(servico_id)


@router.patch('/{servico_id}', response_model=ServicoResponse)
async def atualizar(servico_id: int, payload: ServicoUpdate, service: ServiceDep):
	return await service.update(servico_id, payload)


@router.delete('/{servico_id}', status_code=status.HTTP_204_NO_CONTENT)
async def deletar(servico_id: int, service: ServiceDep):
	await service.delete(servico_id)


@router.post(
	'/{servico_id}/entregaveis',
	response_model=EntregavelResponse,
	status_code=status.HTTP_201_CREATED,
)
async def adicionar_entregavel(
	servico_id: int, payload: EntregavelCreate, service: ServiceDep
):
	payload_with_id = payload.model_copy(update={'servico_id': servico_id})
	return await service.create_entregavel(payload_with_id)


@router.get('/{servico_id}/entregaveis', response_model=list[EntregavelResponse])
async def listar_entregaveis(servico_id: int, service: ServiceDep):
	return await service.list_entregaveis(servico_id)


@router.patch('/entregaveis/{entregavel_id}', response_model=EntregavelResponse)
async def atualizar_entregavel(
	entregavel_id: int, payload: EntregavelUpdate, service: ServiceDep
):
	return await service.update_entregavel(entregavel_id, payload)


@router.delete('/entregaveis/{entregavel_id}', status_code=status.HTTP_204_NO_CONTENT)
async def remover_entregavel(entregavel_id: int, service: ServiceDep):
	await service.delete_entregavel(entregavel_id)
