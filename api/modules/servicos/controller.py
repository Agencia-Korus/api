from typing import Annotated

from core.enums import ServicoStatus, UserRole
from core.security import require_role
from deps import DependenciaPaginacao, DependenciaSessao
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


def _service(session: DependenciaSessao) -> ServicoServico:
	"""Função para criar o serviço de aplicação com a sessão atual."""
	return ServicoServico(session)


DependenciaServico = Annotated[ServicoServico, Depends(_service)]


@router.post('', response_model=ServicoResposta, status_code=status.HTTP_201_CREATED)
async def criar(dados: ServicoCriar, servico: DependenciaServico):
	"""Função para criar um novo registro."""
	return await servico.criar(dados)


@router.get('', response_model=list[ServicoResposta])
async def listar(
	servico: DependenciaServico,
	pagina: DependenciaPaginacao,
	filtro_situacao: Annotated[ServicoStatus | None, Query(alias='status')] = None,
):
	"""Função para listar registros."""
	return await servico.listar_filtrados(
		offset=pagina.offset, limit=pagina.limit, status=filtro_situacao
	)


@router.get('/{servico_id}', response_model=ServicoResposta)
async def obter(servico_id: int, servico: DependenciaServico):
	"""Função para obter um registro pelo ID."""
	return await servico.obter(servico_id)


@router.patch('/{servico_id}', response_model=ServicoResposta)
async def atualizar(servico_id: int, dados: ServicoAtualizar, servico: DependenciaServico):
	"""Função para atualizar um registro pelo ID."""
	return await servico.atualizar(servico_id, dados)


@router.delete('/{servico_id}', status_code=status.HTTP_204_NO_CONTENT)
async def deletar(servico_id: int, servico: DependenciaServico):
	"""Função para excluir um registro pelo ID."""
	await servico.deletar(servico_id)


@router.post(
	'/{servico_id}/entregaveis',
	response_model=EntregavelResposta,
	status_code=status.HTTP_201_CREATED,
)
async def adicionar_entregavel(
	servico_id: int, dados: EntregavelCriar, servico: DependenciaServico
):
	"""Função para adicionar um entregável a um serviço."""
	payload_with_id = dados.model_copy(update={'servico_id': servico_id})
	return await servico.criar_entregavel(payload_with_id)


@router.get('/{servico_id}/entregaveis', response_model=list[EntregavelResposta])
async def listar_entregaveis(servico_id: int, servico: DependenciaServico):
	"""Função para listar entregáveis de um serviço."""
	return await servico.listar_entregaveis(servico_id)


@router.patch('/entregaveis/{entregavel_id}', response_model=EntregavelResposta)
async def atualizar_entregavel(
	entregavel_id: int, dados: EntregavelAtualizar, servico: DependenciaServico
):
	"""Função para atualizar um entregável pelo ID."""
	return await servico.atualizar_entregavel(entregavel_id, dados)


@router.delete('/entregaveis/{entregavel_id}', status_code=status.HTTP_204_NO_CONTENT)
async def remover_entregavel(entregavel_id: int, servico: DependenciaServico):
	"""Função para remover um entregável pelo ID."""
	await servico.deletar_entregavel(entregavel_id)
