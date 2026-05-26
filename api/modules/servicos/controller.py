from typing import Annotated

from core.enums import PapelUsuario, SituacaoServico
from core.security import exigir_papel
from deps import DependenciaPaginacao, DependenciaSessao
from fastapi import APIRouter, Depends, Query, status
from modules.servicos.schema import (
	EntregavelAtualizar,
	EntregavelCriar,
	EntregavelResposta,
	ServicoAtualizar,
	ServicoCriar,
	ServicoResposta,
)
from modules.servicos.service import ServicoServico

roteador = APIRouter(
	prefix='/servicos',
	tags=['Serviços'],
	dependencies=[Depends(exigir_papel(PapelUsuario.ADMIN.value))],
)


def _servico(sessao: DependenciaSessao) -> ServicoServico:
	"""Função para criar o serviço de aplicação com a sessão atual."""
	return ServicoServico(sessao)


DependenciaServico = Annotated[ServicoServico, Depends(_servico)]


@roteador.post('', response_model=ServicoResposta, status_code=status.HTTP_201_CREATED)
async def criar(dados: ServicoCriar, servico: DependenciaServico):
	"""Função para criar um novo registro."""
	return await servico.criar(dados)


@roteador.get('', response_model=list[ServicoResposta])
async def listar(
	servico: DependenciaServico,
	pagina: DependenciaPaginacao,
	filtro_situacao: Annotated[SituacaoServico | None, Query(alias='status')] = None,
):
	"""Função para listar registros."""
	return await servico.listar_filtrados(
		offset=pagina.offset, limit=pagina.limit, status=filtro_situacao
	)


@roteador.get('/{servico_id}', response_model=ServicoResposta)
async def obter(servico_id: int, servico: DependenciaServico):
	"""Função para obter um registro pelo ID."""
	return await servico.obter(servico_id)


@roteador.patch('/{servico_id}', response_model=ServicoResposta)
async def atualizar(
	servico_id: int, dados: ServicoAtualizar, servico: DependenciaServico
):
	"""Função para atualizar um registro pelo ID."""
	return await servico.atualizar(servico_id, dados)


@roteador.delete('/{servico_id}', status_code=status.HTTP_204_NO_CONTENT)
async def deletar(servico_id: int, servico: DependenciaServico):
	"""Função para excluir um registro pelo ID."""
	await servico.deletar(servico_id)


@roteador.post(
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


@roteador.get('/{servico_id}/entregaveis', response_model=list[EntregavelResposta])
async def listar_entregaveis(servico_id: int, servico: DependenciaServico):
	"""Função para listar entregáveis de um serviço."""
	return await servico.listar_entregaveis(servico_id)


@roteador.patch('/entregaveis/{entregavel_id}', response_model=EntregavelResposta)
async def atualizar_entregavel(
	entregavel_id: int, dados: EntregavelAtualizar, servico: DependenciaServico
):
	"""Função para atualizar um entregável pelo ID."""
	return await servico.atualizar_entregavel(entregavel_id, dados)


@roteador.delete('/entregaveis/{entregavel_id}', status_code=status.HTTP_204_NO_CONTENT)
async def remover_entregavel(entregavel_id: int, servico: DependenciaServico):
	"""Função para remover um entregável pelo ID."""
	await servico.deletar_entregavel(entregavel_id)
