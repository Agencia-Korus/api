from __future__ import annotations

from core.exceptions import NotFoundError
from modules.portfolio.model import Portfolio
from modules.portfolio.repository import PortfolioRepository
from modules.portfolio.schema import PortfolioCreate, PortfolioUpdate
from sqlalchemy.ext.asyncio import AsyncSession

_ENTITY = 'Item de portfólio'


class PortfolioService:
	def __init__(self, session: AsyncSession):
		self.session = session
		self.repo = PortfolioRepository(session)

	async def create(self, payload: PortfolioCreate) -> Portfolio:
		item = Portfolio(**payload.model_dump())
		item = await self.repo.add(item)
		await self.session.commit()
		return item

	async def get(self, item_id: int) -> Portfolio:
		item = await self.repo.get(item_id)
		if not item:
			raise NotFoundError(_ENTITY, item_id)
		return item

	async def list(self, offset: int, limit: int, destaques: bool) -> list[Portfolio]:
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
		return await self.repo.list_filtered(
			offset=offset,
			limit=limit,
			destaques=destaques,
			categoria=categoria,
		)

	async def update(self, item_id: int, payload: PortfolioUpdate) -> Portfolio:
		item = await self.repo.update(item_id, payload.model_dump(exclude_none=True))
		if not item:
			raise NotFoundError(_ENTITY, item_id)
		await self.session.commit()
		return item

	async def delete(self, item_id: int) -> None:
		if not await self.repo.delete(item_id):
			raise NotFoundError(_ENTITY, item_id)
		await self.session.commit()
