from typing import Annotated

<<<<<<< HEAD
from fastapi import Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

=======
>>>>>>> main
from core.constants import (
	PAGINATION_DEFAULT_LIMIT,
	PAGINATION_DEFAULT_OFFSET,
	PAGINATION_MAX_LIMIT,
)
from db.session import get_session
<<<<<<< HEAD
=======
from fastapi import Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
>>>>>>> main


class Pagination:
	def __init__(
		self,
		offset: int = Query(
			default=PAGINATION_DEFAULT_OFFSET,
			ge=0,
<<<<<<< HEAD
			description='Quantos registros pular.',
=======
			description='Quantos registros pular',
>>>>>>> main
		),
		limit: int = Query(
			default=PAGINATION_DEFAULT_LIMIT,
			ge=1,
			le=PAGINATION_MAX_LIMIT,
<<<<<<< HEAD
			description='Tamanho máximo da página.',
=======
			description='Tamanho máximo da página',
>>>>>>> main
		),
	):
		self.offset = offset
		self.limit = limit

<<<<<<< HEAD
SessionDep = Annotated[AsyncSession, Depends(get_session)]
PaginationDep = Annotated[Pagination, Depends(Pagination)]
=======

SessionDep = Annotated[AsyncSession, Depends(get_session)]
PaginationDep = Annotated[Pagination, Depends(Pagination)]
>>>>>>> main
