from typing import Annotated

from core.enums import UserRole
from core.security import require_role
from deps import DependenciaPaginacao, DependenciaSessao
from fastapi import APIRouter, Depends, Query, status
from modules.portfolio.schema import (
	PortfolioCriar,
	PortfolioResposta,
	PortfolioAtualizar,
)
from modules.portfolio.service import ServicoPortfolio

router = APIRouter(
	prefix='/portfolio',
	tags=['Portfólio'],
	dependencies=[Depends(require_role(UserRole.ADMIN.value))],
)


def _service(session: DependenciaSessao) -> ServicoPortfolio:
	"""Função para criar o serviço de aplicação com a sessão atual."""
	return ServicoPortfolio(session)


DependenciaServico = Annotated[ServicoPortfolio, Depends(_service)]


@router.post('', response_model=PortfolioResposta, status_code=status.HTTP_201_CREATED)
async def criar(dados: PortfolioCriar, servico: DependenciaServico):
	"""Função para criar um novo registro."""
	return await servico.criar(dados)


DestaquesQuery = Annotated[bool, Query(description='Listar apenas destaques.')]


@router.get('', response_model=list[PortfolioResposta])
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


@router.get('/{item_id}', response_model=PortfolioResposta)
async def obter(item_id: int, servico: DependenciaServico):
	"""Função para obter um registro pelo ID."""
	return await servico.obter(item_id)


@router.patch('/{item_id}', response_model=PortfolioResposta)
async def atualizar(item_id: int, dados: PortfolioAtualizar, servico: DependenciaServico):
	"""Função para atualizar um registro pelo ID."""
	return await servico.atualizar(item_id, dados)


@router.delete('/{item_id}', status_code=status.HTTP_204_NO_CONTENT)
async def deletar(item_id: int, servico: DependenciaServico):
	"""Função para excluir um registro pelo ID."""
	await servico.deletar(item_id)
