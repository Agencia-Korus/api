from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from modules.lgpd.model import ConsentimentoLgpd
from modules.lgpd.repository import ConsentimentoLgpdRepository
from modules.lgpd.schema import ConsentimentoLgpdCreate


class LgpdService:
	def __init__(self, session: AsyncSession):
		self.session = session
		self.repo = ConsentimentoLgpdRepository(session)

	async def registrar(self, payload: ConsentimentoLgpdCreate) -> ConsentimentoLgpd:
		consentimento = ConsentimentoLgpd(**payload.model_dump())
		consentimento = await self.repo.add(consentimento)
		await self.session.commit()
		return consentimento

	async def listar(self, offset: int, limit: int) -> list[ConsentimentoLgpd]:
		return await self.repo.list_all(offset=offset, limit=limit)
