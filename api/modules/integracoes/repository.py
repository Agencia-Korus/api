from sqlalchemy import select

from db.base_repository import BaseRepository
from modules.integracoes.model import Integracao
from modules.integracoes.schema import GOOGLE_CALENDAR_INTEGRATION


class IntegracaoRepository(BaseRepository[Integracao]):
	model = Integracao

	async def get_by_nome(self, nome: str) -> Integracao | None:
		stmt = select(Integracao).where(Integracao.nome == nome)
		result = await self.session.execute(stmt)
		return result.scalar_one_or_none()

	async def get_google_calendar(self, integracao_id: int) -> Integracao | None:
		stmt = select(Integracao).where(
			Integracao.id == integracao_id,
			Integracao.nome == GOOGLE_CALENDAR_INTEGRATION,
		)
		result = await self.session.execute(stmt)
		return result.scalar_one_or_none()

	async def list_google_calendar(self, offset: int, limit: int) -> list[Integracao]:
		stmt = (
			select(Integracao)
			.where(Integracao.nome == GOOGLE_CALENDAR_INTEGRATION)
			.offset(offset)
			.limit(limit)
		)
		result = await self.session.execute(stmt)
		return list(result.scalars().all())
