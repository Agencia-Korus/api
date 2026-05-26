from typing import Annotated

from core.constants import (
	DESLOCAMENTO_PADRAO_PAGINACAO,
	LIMITE_MAXIMO_PAGINACAO,
	LIMITE_PADRAO_PAGINACAO,
)
from db.session import obter_sessao
from fastapi import Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession


class Paginacao:
	"""Classe que agrupa os parâmetros de paginação das rotas."""

	def __init__(
		self,
		offset: int = Query(
			default=DESLOCAMENTO_PADRAO_PAGINACAO,
			ge=0,
			description='Quantos registros pular.',
		),
		limit: int = Query(
			default=LIMITE_PADRAO_PAGINACAO,
			ge=1,
			le=LIMITE_MAXIMO_PAGINACAO,
			description='Tamanho máximo da página.',
		),
	):
		"""Função para inicializar a instância com suas dependências."""
		self.offset = offset
		self.limit = limit


DependenciaSessao = Annotated[AsyncSession, Depends(obter_sessao)]
DependenciaPaginacao = Annotated[Paginacao, Depends(Paginacao)]
