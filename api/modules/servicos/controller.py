from typing import Annotated

from core.enums import ServicoStatus, UserRole
from core.security import require_role
from deps import PaginationDep, SessionDep
from fastapi import APIRouter, Depends, Query, status
from modules.servicos.schema import (
	EntregavelCriar,
	EntregavelResposta,
	EntregavelAtualizar,
	ServicoCriar,
	ServicoResposta,
	ServicoAtualizar,
)
from modules.servicos.service import ServicoServico

router = APIRouter(
	prefix='/servicos',
	tags=['Serviços'],
	dependencies=[Depends(require_role(UserRole.ADMIN.value))],
)


def _service(session: SessionDep) -> ServicoServico:
	"""Função para criar o serviço de aplicação com a sessão atual."""
	return ServicoServico(session)


ServiceDep = Annotated[ServicoServico, Depends(_service)]


@router.post('', response_model=ServicoResposta, status_code=status.HTTP_201_CREATED)
async def criar(payload: ServicoCriar, service: ServiceDep):
	"""Função para criar um novo registro."""
	return await service.criar(payload)


@router.get('', response_model=list[ServicoResposta])
async def listar(
	service: ServiceDep,
	page: PaginationDep,
	status_filter: Annotated[ServicoStatus | None, Query(alias='status')] = None,
):
	"""Função para listar registros."""
	return await service.listar_filtrados(
		offset=page.offset, limit=page.limit, status=status_filter
	)


@router.get('/{servico_id}', response_model=ServicoResposta)
async def obter(servico_id: int, service: ServiceDep):
	"""Função para obter um registro pelo ID."""
	return await service.obter(servico_id)


@router.patch('/{servico_id}', response_model=ServicoResposta)
async def atualizar(servico_id: int, payload: ServicoAtualizar, service: ServiceDep):
	"""Função para atualizar um registro pelo ID."""
	return await service.atualizar(servico_id, payload)


@router.delete('/{servico_id}', status_code=status.HTTP_204_NO_CONTENT)
async def deletar(servico_id: int, service: ServiceDep):
	"""Função para excluir um registro pelo ID."""
	await service.deletar(servico_id)


@router.post(
	'/{servico_id}/entregaveis',
	response_model=EntregavelResposta,
	status_code=status.HTTP_201_CREATED,
)
async def adicionar_entregavel(
	servico_id: int, payload: EntregavelCriar, service: ServiceDep
):
	"""Função para adicionar um entregável a um serviço."""
	payload_with_id = payload.model_copy(update={'servico_id': servico_id})
	return await service.criar_entregavel(payload_with_id)


@router.get('/{servico_id}/entregaveis', response_model=list[EntregavelResposta])
async def listar_entregaveis(servico_id: int, service: ServiceDep):
	"""Função para listar entregáveis de um serviço."""
	return await service.listar_entregaveis(servico_id)


@router.patch('/entregaveis/{entregavel_id}', response_model=EntregavelResposta)
async def atualizar_entregavel(
	entregavel_id: int, payload: EntregavelAtualizar, service: ServiceDep
):
	"""Função para atualizar um entregável pelo ID."""
	return await service.atualizar_entregavel(entregavel_id, payload)


@router.delete('/entregaveis/{entregavel_id}', status_code=status.HTTP_204_NO_CONTENT)
async def remover_entregavel(entregavel_id: int, service: ServiceDep):
	"""Função para remover um entregável pelo ID."""
	await service.deletar_entregavel(entregavel_id)
