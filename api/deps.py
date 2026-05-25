from typing import Annotated

from core.constants import (
	PAGINATION_DEFAULT_LIMIT,
	PAGINATION_DEFAULT_OFFSET,
	PAGINATION_MAX_LIMIT,
)
from db.session import get_session
from fastapi import Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession


class Pagination:
	"""Classe que agrupa os parâmetros de paginação das rotas."""

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
		"""Função para inicializar a instância com suas dependências."""
		self.offset = offset
		self.limit = limit


DependenciaSessao = Annotated[AsyncSession, Depends(get_session)]
DependenciaPaginacao = Annotated[Pagination, Depends(Pagination)]
