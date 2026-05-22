from typing import Annotated

from fastapi import APIRouter, Depends, Query, status

from api.deps import PaginationDep, SessionDep
from core.enums import UserRole
from core.security import require_role
from modules.portfolio.schema import (
	PortfolioCreate,
	PortfolioResponse,
	PortfolioUpdate,
)
from modules.portfolio.service import PortfolioService

router = APIRouter(
	prefix='/portfolio',
	tags=['Portfólio'],
	dependencies=[Depends(require_role(UserRole.ADMIN.value))],
)


def _service(session: SessionDep) -> PortfolioService:
	return PortfolioService(session)


ServiceDep = Annotated[PortfolioService, Depends(_service)]


@router.post('', response_model=PortfolioResponse, status_code=status.HTTP_201_CREATED)
async def criar(payload: PortfolioCreate, service: ServiceDep):
	return await service.create(payload)


DestaquesQuery = Annotated[bool, Query(description='Listar apenas destaques.')]


@router.get('', response_model=list[PortfolioResponse])
async def listar(
	service: ServiceDep,
	page: PaginationDep,
	destaques: DestaquesQuery = False,
	categoria: str | None = None,
):
	return await service.list_filtered(
		offset=page.offset,
		limit=page.limit,
		destaques=destaques,
		categoria=categoria,
	)


@router.get('/{item_id}', response_model=PortfolioResponse)
async def obter(item_id: int, service: ServiceDep):
	return await service.get(item_id)


@router.patch('/{item_id}', response_model=PortfolioResponse)
async def atualizar(item_id: int, payload: PortfolioUpdate, service: ServiceDep):
	return await service.update(item_id, payload)


@router.delete('/{item_id}', status_code=status.HTTP_204_NO_CONTENT)
async def deletar(item_id: int, service: ServiceDep):
	await service.delete(item_id)
