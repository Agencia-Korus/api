from typing import Annotated

from core.enums import PapelUsuario
from core.security import exigir_papel
from deps import DependenciaPaginacao, DependenciaSessao
from fastapi import APIRouter, Depends, Query, status
from modules.portfolio.schema import (
	PortfolioAtualizar,
	PortfolioCriar,
	PortfolioResposta,
)
from modules.portfolio.service import ServicoPortfolio

roteador = APIRouter(
	prefix='/portfolio',
	tags=['Portfólio'],
	dependencies=[Depends(exigir_papel(PapelUsuario.ADMIN.value))],
)


def _servico(sessao: DependenciaSessao) -> ServicoPortfolio:
	"""Função para criar o serviço de aplicação com a sessão atual."""
	return ServicoPortfolio(sessao)


DependenciaServico = Annotated[ServicoPortfolio, Depends(_servico)]


@roteador.post(
	'', response_model=PortfolioResposta, status_code=status.HTTP_201_CREATED
)
async def criar(dados: PortfolioCriar, servico: DependenciaServico):
	"""Função para criar um novo registro."""
	return await servico.criar(dados)


DestaquesQuery = Annotated[bool, Query(description='Listar apenas destaques.')]


@roteador.get('', response_model=list[PortfolioResposta])
async def listar(
	servico: DependenciaServico,
	pagina: DependenciaPaginacao,
	destaques: DestaquesQuery = False,
	categoria: str | None = None,
):
	"""Função para listar registros."""
	return await servico.listar_filtrados(
		offset=pagina.offset,
		limit=pagina.limit,
		destaques=destaques,
		categoria=categoria,
	)


@roteador.get('/{item_id}', response_model=PortfolioResposta)
async def obter(item_id: int, servico: DependenciaServico):
	"""Função para obter um registro pelo ID."""
	return await servico.obter(item_id)


@roteador.patch('/{item_id}', response_model=PortfolioResposta)
async def atualizar(
	item_id: int, dados: PortfolioAtualizar, servico: DependenciaServico
):
	"""Função para atualizar um registro pelo ID."""
	return await servico.atualizar(item_id, dados)


@roteador.delete('/{item_id}', status_code=status.HTTP_204_NO_CONTENT)
async def deletar(item_id: int, servico: DependenciaServico):
	"""Função para excluir um registro pelo ID."""
	await servico.deletar(item_id)
