from typing import Annotated

from core.enums import UserRole
from core.security import require_role
from deps import PaginationDep, SessionDep
from fastapi import APIRouter, Depends, status
from modules.integracoes.schema import (
	IntegracaoCriar,
	IntegracaoResposta,
	IntegracaoAtualizar,
)
from modules.integracoes.service import ServicoIntegracao

router = APIRouter(
	prefix='/integracoes',
	tags=['Integrações'],
	dependencies=[Depends(require_role(UserRole.ADMIN.value))],
)


def _service(session: SessionDep) -> ServicoIntegracao:
	"""Função para criar o serviço de aplicação com a sessão atual."""
	return ServicoIntegracao(session)


ServiceDep = Annotated[ServicoIntegracao, Depends(_service)]


@router.post(
	'',
	response_model=IntegracaoResposta,
	status_code=status.HTTP_201_CREATED,
	summary='Configura integração Google Calendar (somente admin)',
	description='Somente a integração com Google Calendar é aceita neste projeto.',
)
async def criar(payload: IntegracaoCriar, service: ServiceDep):
	"""Função para criar um novo registro."""
	return await service.criar(payload)


@router.get(
	'',
	response_model=list[IntegracaoResposta],
	summary='Lista configuração do Google Calendar (somente admin)',
)
async def listar(service: ServiceDep, page: PaginationDep):
	"""Função para listar registros."""
	return await service.listar(offset=page.offset, limit=page.limit)


@router.get(
	'/{integracao_id}',
	response_model=IntegracaoResposta,
	summary='Obtém configuração do Google Calendar (somente admin)',
)
async def obter(integracao_id: int, service: ServiceDep):
	"""Função para obter um registro pelo ID."""
	return await service.obter(integracao_id)


@router.patch(
	'/{integracao_id}',
	response_model=IntegracaoResposta,
	summary='Atualiza configuração do Google Calendar (somente admin)',
)
async def atualizar(integracao_id: int, payload: IntegracaoAtualizar, service: ServiceDep):
	"""Função para atualizar um registro pelo ID."""
	return await service.atualizar(integracao_id, payload)


@router.delete(
	'/{integracao_id}',
	status_code=status.HTTP_204_NO_CONTENT,
	summary='Remove configuração do Google Calendar (somente admin)',
)
async def deletar(integracao_id: int, service: ServiceDep):
	"""Função para excluir um registro pelo ID."""
	await service.deletar(integracao_id)
