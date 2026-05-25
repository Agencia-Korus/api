from __future__ import annotations

from core.exceptions import NotFoundError
from modules.portfolio.model import Portfolio
from modules.portfolio.repository import RepositorioPortfolio
from modules.portfolio.schema import PortfolioCriar, PortfolioAtualizar
from sqlalchemy.ext.asyncio import AsyncSession

_ENTITY = 'Item de portfólio'


class ServicoPortfolio:
	"""Classe responsável pelas regras de negócio de portfólio."""

	def __init__(self, session: AsyncSession):
		"""Função para inicializar a instância com suas dependências."""
		self.session = session
		self.repo = RepositorioPortfolio(session)

	async def criar(self, payload: PortfolioCriar) -> Portfolio:
		"""Função para criar um novo registro."""
		item = Portfolio(**payload.model_dump())
		item = await self.repo.adicionar(item)
		await self.session.commit()
		return item

	async def obter(self, item_id: int) -> Portfolio:
		"""Função para obter um registro pelo ID."""
		item = await self.repo.obter(item_id)
		if not item:
			raise NotFoundError(_ENTITY, item_id)
		return item

	async def listar(self, offset: int, limit: int, destaques: bool) -> list[Portfolio]:
		"""Função para listar registros."""
		return await self.repo.listar_filtrados(
			offset=offset, limit=limit, destaques=destaques
		)

	async def listar_filtrados(
		self,
		offset: int,
		limit: int,
		destaques: bool,
		categoria: str | None = None,
	) -> list[Portfolio]:
		"""Função para listar registros aplicando filtros e paginação."""
		return await self.repo.listar_filtrados(
			offset=offset,
			limit=limit,
			destaques=destaques,
			categoria=categoria,
		)

	async def atualizar(self, item_id: int, payload: PortfolioAtualizar) -> Portfolio:
		"""Função para atualizar um registro pelo ID."""
		item = await self.repo.atualizar(item_id, payload.model_dump(exclude_none=True))
		if not item:
			raise NotFoundError(_ENTITY, item_id)
		await self.session.commit()
		return item

	async def deletar(self, item_id: int) -> None:
		"""Função para excluir um registro pelo ID."""
		if not await self.repo.deletar(item_id):
			raise NotFoundError(_ENTITY, item_id)
		await self.session.commit()
