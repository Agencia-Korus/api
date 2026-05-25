from core.enums import LeadPrioridade, LeadStatus
from db.base_repository import RepositorioBase
from modules.leads.model import Lead
from sqlalchemy import or_, select


class RepositorioLead(RepositorioBase[Lead]):
	"""Classe responsável pelo acesso aos dados de lead."""

	model = Lead

	async def listar_filtrados(
		self,
		offset: int,
		limit: int,
		status: LeadStatus | None = None,
		prioridade: LeadPrioridade | None = None,
		servico_id: int | None = None,
		search: str | None = None,
	) -> list[Lead]:
		"""Função para listar registros aplicando filtros e paginação."""
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
