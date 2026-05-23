from typing import Annotated

from db.session import get_session
from fastapi import Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from core.constants import (
	PAGINATION_DEFAULT_LIMIT,
	PAGINATION_DEFAULT_OFFSET,
	PAGINATION_MAX_LIMIT,
)


class Pagination:
	def __init__(
		self,
		offset: int = Query(
			default=PAGINATION_DEFAULT_OFFSET,
			ge=0,
			description='Quantos registros pular.',
		),
		limit: int = Query(
			default=PAGINATION_DEFAULT_LIMIT,
			ge=1,
			le=PAGINATION_MAX_LIMIT,
			description='Tamanho máximo da página.',
		),
	):
		self.offset = offset
		self.limit = limit


SessionDep = Annotated[AsyncSession, Depends(get_session)]
PaginationDep = Annotated[Pagination, Depends(Pagination)]
