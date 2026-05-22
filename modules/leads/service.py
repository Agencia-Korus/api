from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from core.enums import LeadPrioridade, LeadStatus
from core.exceptions import NotFoundError
from modules.leads.model import Lead
from modules.leads.repository import LeadRepository
from modules.leads.schema import LeadCreate, LeadUpdate

_ENTITY = 'Lead'


class LeadService:
	def __init__(self, session: AsyncSession):
		self.session = session
		self.repo = LeadRepository(session)

	async def create(self, payload: LeadCreate) -> Lead:
		lead = Lead(**payload.model_dump())
		lead = await self.repo.add(lead)
		await self.session.commit()
		return lead

	async def get(self, lead_id: int) -> Lead:
		lead = await self.repo.get(lead_id)
		if not lead:
			raise NotFoundError(_ENTITY, lead_id)
		return lead

	async def list(self, offset: int, limit: int) -> list[Lead]:
		return await self.repo.list_all(offset=offset, limit=limit)

	async def list_filtered(
		self,
		offset: int,
		limit: int,
		status: LeadStatus | None = None,
		prioridade: LeadPrioridade | None = None,
		servico_id: int | None = None,
		search: str | None = None,
	) -> list[Lead]:
		return await self.repo.list_filtered(
			offset=offset,
			limit=limit,
			status=status,
			prioridade=prioridade,
			servico_id=servico_id,
			search=search,
		)

	async def update(self, lead_id: int, payload: LeadUpdate) -> Lead:
		lead = await self.repo.update(lead_id, payload.model_dump(exclude_none=True))
		if not lead:
			raise NotFoundError(_ENTITY, lead_id)
		await self.session.commit()
		return lead

	async def delete(self, lead_id: int) -> None:
		if not await self.repo.delete(lead_id):
			raise NotFoundError(_ENTITY, lead_id)
		await self.session.commit()
