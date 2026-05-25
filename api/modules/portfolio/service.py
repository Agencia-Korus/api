from __future__ import annotations

from core.exceptions import NotFoundError
from modules.portfolio.model import Portfolio
from modules.portfolio.repository import PortfolioRepository
from modules.portfolio.schema import PortfolioCreate, PortfolioUpdate
from sqlalchemy.ext.asyncio import AsyncSession

_ENTITY = 'Item de portfólio'


class PortfolioService:
	"""Classe responsável pelas regras de negócio de portfólio."""

	def __init__(self, session: AsyncSession):
		"""Função para inicializar a instância com suas dependências."""
		self.session = session
		self.repo = PortfolioRepository(session)

	async def create(self, payload: PortfolioCreate) -> Portfolio:
		"""Função para criar um novo registro."""
		item = Portfolio(**payload.model_dump())
		item = await self.repo.add(item)
		await self.session.commit()
		return item

	async def get(self, item_id: int) -> Portfolio:
		"""Função para obter um registro pelo ID."""
		item = await self.repo.get(item_id)
		if not item:
			raise NotFoundError(_ENTITY, item_id)
		return item

	async def list(self, offset: int, limit: int, destaques: bool) -> list[Portfolio]:
		"""Função para listar registros."""
		return await self.repo.list_filtered(
			offset=offset, limit=limit, destaques=destaques
		)

	async def list_filtered(
		self,
		offset: int,
		limit: int,
		destaques: bool,
		categoria: str | None = None,
	) -> list[Portfolio]:
		"""Função para listar registros aplicando filtros e paginação."""
		return await self.repo.list_filtered(
			offset=offset,
			limit=limit,
			destaques=destaques,
			categoria=categoria,
		)

	async def update(self, item_id: int, payload: PortfolioUpdate) -> Portfolio:
		"""Função para atualizar um registro pelo ID."""
		item = await self.repo.update(item_id, payload.model_dump(exclude_none=True))
		if not item:
			raise NotFoundError(_ENTITY, item_id)
		await self.session.commit()
		return item

	async def delete(self, item_id: int) -> None:
		"""Função para excluir um registro pelo ID."""
		if not await self.repo.delete(item_id):
			raise NotFoundError(_ENTITY, item_id)
		await self.session.commit()
