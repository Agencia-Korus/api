from typing import Annotated

from core.enums import UserRole
from core.security import require_role
from fastapi import APIRouter, Depends, status
from modules.integracoes.schema import (
	IntegracaoCreate,
	IntegracaoResponse,
	IntegracaoUpdate,
)
from modules.integracoes.service import IntegracaoService

from api.deps import PaginationDep, SessionDep

router = APIRouter(
	prefix='/integracoes',
	tags=['Integrações'],
	dependencies=[Depends(require_role(UserRole.ADMIN.value))],
)


def _service(session: SessionDep) -> IntegracaoService:
	return IntegracaoService(session)


ServiceDep = Annotated[IntegracaoService, Depends(_service)]


@router.post(
	'',
	response_model=IntegracaoResponse,
	status_code=status.HTTP_201_CREATED,
	summary='Configura integração Google Calendar (somente admin)',
	description='Somente a integração com Google Calendar é aceita neste projeto.',
)
async def criar(payload: IntegracaoCreate, service: ServiceDep):
	return await service.create(payload)


@router.get(
	'',
	response_model=list[IntegracaoResponse],
	summary='Lista configuração do Google Calendar (somente admin)',
)
async def listar(service: ServiceDep, page: PaginationDep):
	return await service.list(offset=page.offset, limit=page.limit)


@router.get(
	'/{integracao_id}',
	response_model=IntegracaoResponse,
	summary='Obtém configuração do Google Calendar (somente admin)',
)
async def obter(integracao_id: int, service: ServiceDep):
	return await service.get(integracao_id)


@router.patch(
	'/{integracao_id}',
	response_model=IntegracaoResponse,
	summary='Atualiza configuração do Google Calendar (somente admin)',
)
async def atualizar(integracao_id: int, payload: IntegracaoUpdate, service: ServiceDep):
	return await service.update(integracao_id, payload)


@router.delete(
	'/{integracao_id}',
	status_code=status.HTTP_204_NO_CONTENT,
	summary='Remove configuração do Google Calendar (somente admin)',
)
async def deletar(integracao_id: int, service: ServiceDep):
	await service.delete(integracao_id)
