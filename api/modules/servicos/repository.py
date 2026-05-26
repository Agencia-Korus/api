from db.base_repository import RepositorioBase
from modules.servicos.model import Entregavel, Servico
from sqlalchemy import select


class RepositorioServico(RepositorioBase[Servico]):
	"""Classe responsável pelo acesso aos dados de serviço."""

	modelo = Servico

	async def obter_por_slug(self, slug: str) -> Servico | None:
		"""Função para buscar um serviço pelo slug."""
		consulta = select(Servico).where(Servico.slug == slug)
		resultado = await self.sessao.execute(consulta)
		return resultado.scalar_one_or_none()


class RepositorioEntregavel(RepositorioBase[Entregavel]):
	"""Classe responsável pelo acesso aos dados de entregável."""

	modelo = Entregavel

	async def listar_por_servico(self, servico_id: int) -> list[Entregavel]:
		"""Função para listar entregáveis vinculados a um serviço."""
		consulta = (
			select(Entregavel)
			.where(Entregavel.servico_id == servico_id)
			.order_by(Entregavel.ordem)
		)
		resultado = await self.sessao.execute(consulta)
		return list(resultado.scalars().all())
