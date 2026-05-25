from typing import Annotated

from core.enums import UserRole
from core.security import require_role
from deps import DependenciaPaginacao, DependenciaSessao
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


def _service(session: DependenciaSessao) -> ServicoIntegracao:
	"""Função para criar o serviço de aplicação com a sessão atual."""
	return ServicoIntegracao(session)


DependenciaServico = Annotated[ServicoIntegracao, Depends(_service)]


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
)
async def listar(servico: DependenciaServico, pagina: DependenciaPaginacao):
	"""Função para listar registros."""
	return await servico.listar(offset=pagina.offset, limit=pagina.limit)


@router.get(
	'/{integracao_id}',
	response_model=IntegracaoResposta,
	summary='Obtém configuração do Google Calendar (somente admin)',
)
async def obter(integracao_id: int, servico: DependenciaServico):
	"""Função para obter um registro pelo ID."""
	return await servico.obter(integracao_id)


@router.patch(
	'/{integracao_id}',
	response_model=IntegracaoResposta,
	summary='Atualiza configuração do Google Calendar (somente admin)',
)
async def atualizar(integracao_id: int, dados: IntegracaoAtualizar, servico: DependenciaServico):
	"""Função para atualizar um registro pelo ID."""
	return await servico.atualizar(integracao_id, dados)


@router.delete(
	'/{integracao_id}',
	status_code=status.HTTP_204_NO_CONTENT,
	summary='Remove configuração do Google Calendar (somente admin)',
)
async def deletar(integracao_id: int, servico: DependenciaServico):
	"""Função para excluir um registro pelo ID."""
	await servico.deletar(integracao_id)
