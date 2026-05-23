from __future__ import annotations

from core.exceptions import ConflictError, NotFoundError
from modules.integracoes.model import Integracao
from modules.integracoes.repository import IntegracaoRepository
from modules.integracoes.schema import (
	GOOGLE_CALENDAR_INTEGRATION,
	IntegracaoCreate,
	IntegracaoUpdate,
)
from sqlalchemy.ext.asyncio import AsyncSession

_ENTITY = 'Integração'


class IntegracaoService:
	def __init__(self, session: AsyncSession):
		self.session = session
		self.repo = IntegracaoRepository(session)

	async def create(self, payload: IntegracaoCreate) -> Integracao:
		if await self.repo.get_by_nome(GOOGLE_CALENDAR_INTEGRATION):
			raise ConflictError('Integração com Google Calendar já cadastrada')
		integracao = Integracao(**payload.model_dump())
		integracao = await self.repo.add(integracao)
		await self.session.commit()
		return integracao

	async def get(self, integracao_id: int) -> Integracao:
		integracao = await self.repo.get_google_calendar(integracao_id)
		if not integracao:
			raise NotFoundError(_ENTITY, integracao_id)
		return integracao

	async def list(self, offset: int, limit: int) -> list[Integracao]:
		return await self.repo.list_google_calendar(offset=offset, limit=limit)

	async def update(self, integracao_id: int, payload: IntegracaoUpdate) -> Integracao:
		await self.get(integracao_id)
		integracao = await self.repo.update(
			integracao_id, payload.model_dump(exclude_none=True)
		)
		if not integracao:
			raise NotFoundError(_ENTITY, integracao_id)
		await self.session.commit()
		return integracao

	async def delete(self, integracao_id: int) -> None:
		await self.get(integracao_id)
		await self.repo.delete(integracao_id)
		await self.session.commit()
