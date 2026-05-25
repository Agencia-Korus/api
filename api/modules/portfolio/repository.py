from db.base_repository import RepositorioBase
from modules.portfolio.model import Portfolio
from sqlalchemy import select


class RepositorioPortfolio(RepositorioBase[Portfolio]):
	"""Classe responsável pelo acesso aos dados de portfólio."""

	model = Portfolio

	async def listar_destaques(self) -> list[Portfolio]:
		"""Função para listar itens de portfólio marcados como destaque."""
		stmt = (
			select(Portfolio)
			.where(Portfolio.destaque.is_(True))
			.order_by(Portfolio.criado_em.desc())
		)
		result = await self.session.execute(stmt)
		return list(result.scalars().all())

	async def listar_filtrados(
		self,
		offset: int,
		limit: int,
		categoria: str | None = None,
		destaques: bool = False,
	) -> list[Portfolio]:
		"""Função para listar registros aplicando filtros e paginação."""
		stmt = select(Portfolio)
		if destaques:
			stmt = stmt.where(Portfolio.destaque.is_(True))
		if categoria:
			stmt = stmt.where(Portfolio.categoria.ilike(categoria))
		stmt = stmt.order_by(Portfolio.criado_em.desc()).offset(offset).limit(limit)
		result = await self.session.execute(stmt)
		return list(result.scalars().all())
