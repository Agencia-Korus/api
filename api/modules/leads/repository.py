from core.enums import LeadPrioridade, SituacaoLead
from db.base_repository import RepositorioBase
from modules.leads.model import Lead
from sqlalchemy import or_, select


class RepositorioLead(RepositorioBase[Lead]):
	"""Classe responsável pelo acesso aos dados de lead."""

	modelo = Lead

	async def listar_filtrados(
		self,
		offset: int,
		limit: int,
		status: SituacaoLead | None = None,
		prioridade: LeadPrioridade | None = None,
		servico_id: int | None = None,
		busca: str | None = None,
	) -> list[Lead]:
		"""Função para listar registros aplicando filtros e paginação."""
		consulta = select(Lead)
		if status is not None:
			consulta = consulta.where(Lead.status == status)
		if prioridade is not None:
			consulta = consulta.where(Lead.prioridade == prioridade)
		if servico_id is not None:
			consulta = consulta.where(Lead.servico_id == servico_id)
		if busca:
			termo = f'%{busca}%'
			consulta = consulta.where(
				or_(
					Lead.nome.ilike(termo),
					Lead.email.ilike(termo),
					Lead.empresa.ilike(termo),
				)
			)
		consulta = consulta.order_by(Lead.data.desc()).offset(offset).limit(limit)
		resultado = await self.sessao.execute(consulta)
		return list(resultado.scalars().all())
