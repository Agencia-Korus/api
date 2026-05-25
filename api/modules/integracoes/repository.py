from db.base_repository import BaseRepository
from modules.integracoes.model import Integracao
from modules.integracoes.schema import GOOGLE_CALENDAR_INTEGRATION
from sqlalchemy import select


class IntegracaoRepository(BaseRepository[Integracao]):
	"""Classe responsável pelo acesso aos dados de integração."""

	model = Integracao

	async def get_by_nome(self, nome: str) -> Integracao | None:
		"""Função para buscar uma integração pelo nome."""
		stmt = select(Integracao).where(Integracao.nome == nome)
		result = await self.session.execute(stmt)
		return result.scalar_one_or_none()

	async def get_google_calendar(self, integracao_id: int) -> Integracao | None:
		"""Função para buscar a integração do Google Calendar pelo ID."""
		stmt = select(Integracao).where(
			Integracao.id == integracao_id,
			Integracao.nome == GOOGLE_CALENDAR_INTEGRATION,
		)
		result = await self.session.execute(stmt)
		return result.scalar_one_or_none()

	async def list_google_calendar(self, offset: int, limit: int) -> list[Integracao]:
		"""Função para listar a integração do Google Calendar com paginação."""
		stmt = (
			select(Integracao)
			.where(Integracao.nome == GOOGLE_CALENDAR_INTEGRATION)
			.offset(offset)
			.limit(limit)
		)
		result = await self.session.execute(stmt)
		return list(result.scalars().all())
