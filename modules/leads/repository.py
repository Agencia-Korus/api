from sqlalchemy import or_, select

from core.enums import LeadPrioridade, LeadStatus
from db.base_repository import BaseRepository
from modules.leads.model import Lead


class LeadRepository(BaseRepository[Lead]):
	model = Lead

	async def list_filtered(
		self,
		offset: int,
		limit: int,
		status: LeadStatus | None = None,
		prioridade: LeadPrioridade | None = None,
		servico_id: int | None = None,
		search: str | None = None,
	) -> list[Lead]:
		stmt = select(Lead)
		if status is not None:
			stmt = stmt.where(Lead.status == status)
		if prioridade is not None:
			stmt = stmt.where(Lead.prioridade == prioridade)
		if servico_id is not None:
			stmt = stmt.where(Lead.servico_id == servico_id)
		if search:
			term = f'%{search}%'
			stmt = stmt.where(
				or_(
					Lead.nome.ilike(term),
					Lead.email.ilike(term),
					Lead.empresa.ilike(term),
				)
			)
		stmt = stmt.order_by(Lead.data.desc()).offset(offset).limit(limit)
		result = await self.session.execute(stmt)
		return list(result.scalars().all())
