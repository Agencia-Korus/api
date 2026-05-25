from typing import Annotated

from core.enums import UserRole
from core.security import require_role
from deps import PaginationDep, SessionDep
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


def _service(session: SessionDep) -> ServicoPortfolio:
	"""Função para criar o serviço de aplicação com a sessão atual."""
	return ServicoPortfolio(session)


ServiceDep = Annotated[ServicoPortfolio, Depends(_service)]


@router.post('', response_model=PortfolioResposta, status_code=status.HTTP_201_CREATED)
async def criar(payload: PortfolioCriar, service: ServiceDep):
	"""Função para criar um novo registro."""
	return await service.criar(payload)


DestaquesQuery = Annotated[bool, Query(description='Listar apenas destaques.')]


@router.get('', response_model=list[PortfolioResposta])
async def listar(
	service: ServiceDep,
	page: PaginationDep,
	destaques: DestaquesQuery = False,
	categoria: str | None = None,
):
	"""Função para listar registros."""
	return await service.listar_filtrados(
		offset=page.offset,
		limit=page.limit,
		destaques=destaques,
		categoria=categoria,
	)


@router.get('/{item_id}', response_model=PortfolioResposta)
async def obter(item_id: int, service: ServiceDep):
	"""Função para obter um registro pelo ID."""
	return await service.obter(item_id)


@router.patch('/{item_id}', response_model=PortfolioResposta)
async def atualizar(item_id: int, payload: PortfolioAtualizar, service: ServiceDep):
	"""Função para atualizar um registro pelo ID."""
	return await service.atualizar(item_id, payload)


@router.delete('/{item_id}', status_code=status.HTTP_204_NO_CONTENT)
async def deletar(item_id: int, service: ServiceDep):
	"""Função para excluir um registro pelo ID."""
	await service.deletar(item_id)
