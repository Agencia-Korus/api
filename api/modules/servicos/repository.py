from db.base_repository import BaseRepository
from modules.servicos.model import Entregavel, Servico
from sqlalchemy import select


class ServicoRepository(BaseRepository[Servico]):
	model = Servico

	async def get_by_slug(self, slug: str) -> Servico | None:
		stmt = select(Servico).where(Servico.slug == slug)
		result = await self.session.execute(stmt)
		return result.scalar_one_or_none()


class EntregavelRepository(BaseRepository[Entregavel]):
	model = Entregavel

	async def list_by_servico(self, servico_id: int) -> list[Entregavel]:
		stmt = (
			select(Entregavel)
			.where(Entregavel.servico_id == servico_id)
			.order_by(Entregavel.ordem)
		)
		result = await self.session.execute(stmt)
		return list(result.scalars().all())
