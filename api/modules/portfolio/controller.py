from typing import Annotated

from core.enums import PapelUsuario
from core.security import exigir_papel
from core.swagger import exemplo_requisicao_json
from deps import DependenciaPaginacao, DependenciaSessao
from fastapi import APIRouter, Depends, Query, status
from modules.portfolio.schema import (
	PortfolioAtualizar,
	PortfolioCriar,
	PortfolioResposta,
)
from modules.portfolio.service import ServicoPortfolio

router = APIRouter(
	prefix='/portfolio',
	tags=['Portfólio'],
	dependencies=[Depends(exigir_papel(PapelUsuario.ADMIN.value))],
)


def _servico(sessao: DependenciaSessao) -> ServicoPortfolio:
	"""Função para criar o serviço de aplicação com a sessão atual."""
	return ServicoPortfolio(sessao)


DependenciaServico = Annotated[ServicoPortfolio, Depends(_servico)]


@router.post(
	'', response_model=PortfolioResposta, status_code=status.HTTP_201_CREATED
)
async def criar(dados: PortfolioCriar, servico: DependenciaServico):
	"""Função para criar um novo registro."""
	return await servico.criar(dados)


DestaquesQuery = Annotated[bool, Query(description='Listar apenas destaques.')]


@router.get(
	'',
	response_model=list[PortfolioResposta],
	openapi_extra=exemplo_requisicao_json({
		'offset': 0,
		'limit': 20,
		'destaques': True,
		'categoria': 'Branding',
	}),
)
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


@router.get(
	'/{item_id}',
	response_model=PortfolioResposta,
	openapi_extra=exemplo_requisicao_json({'item_id': 1}),
)
async def obter(item_id: int, servico: DependenciaServico):
	"""Função para obter um registro pelo ID."""
	return await servico.obter(item_id)


@router.patch('/{item_id}', response_model=PortfolioResposta)
async def atualizar(
	item_id: int, dados: PortfolioAtualizar, servico: DependenciaServico
):
	"""Função para atualizar um registro pelo ID."""
	return await servico.atualizar(item_id, dados)


@router.delete(
	'/{item_id}',
	status_code=status.HTTP_204_NO_CONTENT,
	openapi_extra=exemplo_requisicao_json({'item_id': 1}),
)
async def deletar(item_id: int, servico: DependenciaServico):
	"""Função para excluir um registro pelo ID."""
	await servico.deletar(item_id)
