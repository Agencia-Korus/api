from db.base_repository import RepositorioBase
from modules.portfolio.model import Portfolio
from sqlalchemy import select


class RepositorioPortfolio(RepositorioBase[Portfolio]):
	"""Classe responsável pelo acesso aos dados de portfólio."""

	modelo = Portfolio

	async def listar_destaques(self) -> list[Portfolio]:
		"""Função para listar itens de portfólio marcados como destaque."""
		consulta = (
			select(Portfolio)
			.where(Portfolio.destaque.is_(True))
			.order_by(Portfolio.criado_em.desc())
		)
		resultado = await self.sessao.execute(consulta)
		return list(resultado.scalars().all())

	async def listar_filtrados(
		self,
		offset: int,
		limit: int,
		categoria: str | None = None,
		destaques: bool = False,
	) -> list[Portfolio]:
		"""Função para listar registros aplicando filtros e paginação."""
		consulta = select(Portfolio)
		if destaques:
			consulta = consulta.where(Portfolio.destaque.is_(True))
		if categoria:
			consulta = consulta.where(Portfolio.categoria.ilike(categoria))
		consulta = (
			consulta.order_by(Portfolio.criado_em.desc()).offset(offset).limit(limit)
		)
		resultado = await self.sessao.execute(consulta)
		return list(resultado.scalars().all())
