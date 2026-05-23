from __future__ import annotations

from core.enums import AcademyTipo
from core.exceptions import NotFoundError
from modules.academy.model import Academy
from modules.academy.repository import AcademyRepository
from modules.academy.schema import AcademyCreate, AcademyUpdate
from sqlalchemy.ext.asyncio import AsyncSession

_ENTITY = 'Conteúdo Academy'


class AcademyService:
	def __init__(self, session: AsyncSession):
		self.session = session
		self.repo = AcademyRepository(session)

	async def create(self, payload: AcademyCreate) -> Academy:
		item = Academy(**payload.model_dump())
		item = await self.repo.add(item)
		await self.session.commit()
		return item

	async def get(self, item_id: int) -> Academy:
		item = await self.repo.get(item_id)
		if not item:
			raise NotFoundError(_ENTITY, item_id)
		return item

	async def list(self, offset: int, limit: int) -> list[Academy]:
		return await self.repo.list_all(offset=offset, limit=limit)

	async def list_filtered(
		self,
		offset: int,
		limit: int,
		tipo: AcademyTipo | None = None,
		publicado: bool | None = None,
	) -> list[Academy]:
		return await self.repo.list_all(
			offset=offset, limit=limit, filters={'tipo': tipo, 'publicado': publicado}
		)

	async def update(self, item_id: int, payload: AcademyUpdate) -> Academy:
		item = await self.repo.update(item_id, payload.model_dump(exclude_none=True))
		if not item:
			raise NotFoundError(_ENTITY, item_id)
		await self.session.commit()
		return item

	async def delete(self, item_id: int) -> None:
		if not await self.repo.delete(item_id):
			raise NotFoundError(_ENTITY, item_id)
		await self.session.commit()
