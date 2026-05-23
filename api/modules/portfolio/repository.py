from sqlalchemy import select

from db.base_repository import BaseRepository
from modules.portfolio.model import Portfolio


class PortfolioRepository(BaseRepository[Portfolio]):
	model = Portfolio

	async def list_destaques(self) -> list[Portfolio]:
		stmt = (
			select(Portfolio)
			.where(Portfolio.destaque.is_(True))
			.order_by(Portfolio.criado_em.desc())
		)
		result = await self.session.execute(stmt)
		return list(result.scalars().all())

	async def list_filtered(
		self,
		offset: int,
		limit: int,
		categoria: str | None = None,
		destaques: bool = False,
	) -> list[Portfolio]:
		stmt = select(Portfolio)
		if destaques:
			stmt = stmt.where(Portfolio.destaque.is_(True))
		if categoria:
			stmt = stmt.where(Portfolio.categoria.ilike(categoria))
		stmt = stmt.order_by(Portfolio.criado_em.desc()).offset(offset).limit(limit)
		result = await self.session.execute(stmt)
		return list(result.scalars().all())
