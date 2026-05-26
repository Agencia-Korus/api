from typing import Annotated

from core.enums import PapelUsuario
from core.security import exigir_papel
from core.swagger import exemplo_requisicao_json
from deps import DependenciaPaginacao, DependenciaSessao
from fastapi import APIRouter, Depends, status
from modules.integracoes.schema import (
	IntegracaoAtualizar,
	IntegracaoCriar,
	IntegracaoResposta,
)
from modules.integracoes.service import ServicoIntegracao

router = APIRouter(
	prefix='/integracoes',
	tags=['Integrações'],
	dependencies=[Depends(exigir_papel(PapelUsuario.ADMIN.value))],
)


def _servico(sessao: DependenciaSessao) -> ServicoIntegracao:
	"""Função para criar o serviço de aplicação com a sessão atual."""
	return ServicoIntegracao(sessao)


DependenciaServico = Annotated[ServicoIntegracao, Depends(_servico)]


@router.post(
	'',
	response_model=IntegracaoResposta,
	status_code=status.HTTP_201_CREATED,
	summary='Configura integração Google Calendar (somente admin)',
	description='Somente a integração com Google Calendar é aceita neste projeto.',
)
async def criar(dados: IntegracaoCriar, servico: DependenciaServico):
	"""Função para criar um novo registro."""
	return await servico.criar(dados)


@router.get(
	'',
	response_model=list[IntegracaoResposta],
	summary='Lista configuração do Google Calendar (somente admin)',
	openapi_extra=exemplo_requisicao_json({'offset': 0, 'limit': 20}),
)
async def listar(servico: DependenciaServico, pagina: DependenciaPaginacao):
	"""Função para listar registros."""
	return await servico.listar(offset=pagina.offset, limit=pagina.limit)


@router.get(
	'/{integracao_id}',
	response_model=IntegracaoResposta,
	summary='Obtém configuração do Google Calendar (somente admin)',
	openapi_extra=exemplo_requisicao_json({'integracao_id': 1}),
)
async def obter(integracao_id: int, servico: DependenciaServico):
	"""Função para obter um registro pelo ID."""
	return await servico.obter(integracao_id)


@router.patch(
	'/{integracao_id}',
	response_model=IntegracaoResposta,
	summary='Atualiza configuração do Google Calendar (somente admin)',
)
async def atualizar(
	integracao_id: int, dados: IntegracaoAtualizar, servico: DependenciaServico
):
	"""Função para atualizar um registro pelo ID."""
	return await servico.atualizar(integracao_id, dados)


@router.delete(
	'/{integracao_id}',
	status_code=status.HTTP_204_NO_CONTENT,
	summary='Remove configuração do Google Calendar (somente admin)',
	openapi_extra=exemplo_requisicao_json({'integracao_id': 1}),
)
async def deletar(integracao_id: int, servico: DependenciaServico):
	"""Função para excluir um registro pelo ID."""
	await servico.deletar(integracao_id)
