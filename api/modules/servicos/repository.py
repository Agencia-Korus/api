from db.base_repository import RepositorioBase
from modules.servicos.model import Entregavel, Servico
from sqlalchemy import select


class RepositorioServico(RepositorioBase[Servico]):
	"""Classe responsável pelo acesso aos dados de serviço."""

	model = Servico

	async def obter_por_slug(self, slug: str) -> Servico | None:
		"""Função para buscar um serviço pelo slug."""
		stmt = select(Servico).where(Servico.slug == slug)
		result = await self.session.execute(stmt)
		return result.scalar_one_or_none()


class RepositorioEntregavel(RepositorioBase[Entregavel]):
	"""Classe responsável pelo acesso aos dados de entregável."""

	model = Entregavel

	async def listar_por_servico(self, servico_id: int) -> list[Entregavel]:
		"""Função para listar entregáveis vinculados a um serviço."""
		stmt = (
			select(Entregavel)
			.where(Entregavel.servico_id == servico_id)
			.order_by(Entregavel.ordem)
		)
		result = await self.session.execute(stmt)
		return list(result.scalars().all())
