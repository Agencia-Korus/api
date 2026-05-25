from __future__ import annotations

from core.enums import LeadPrioridade, LeadStatus
from core.exceptions import NotFoundError
from modules.leads.model import Lead
from modules.leads.repository import RepositorioLead
from modules.leads.schema import LeadCriar, LeadAtualizar
from sqlalchemy.ext.asyncio import AsyncSession

_ENTITY = 'Lead'


class ServicoLead:
	"""Classe responsável pelas regras de negócio de lead."""

	def __init__(self, session: AsyncSession):
		"""Função para inicializar a instância com suas dependências."""
		self.session = session
		self.repo = RepositorioLead(session)

	async def criar(self, payload: LeadCriar) -> Lead:
		"""Função para criar um novo registro."""
		lead = Lead(**payload.model_dump())
		lead = await self.repo.adicionar(lead)
		await self.session.commit()
		return lead

	async def obter(self, lead_id: int) -> Lead:
		"""Função para obter um registro pelo ID."""
		lead = await self.repo.obter(lead_id)
		if not lead:
			raise NotFoundError(_ENTITY, lead_id)
		return lead

	async def listar(self, offset: int, limit: int) -> list[Lead]:
		"""Função para listar registros."""
		return await self.repo.listar_todos(offset=offset, limit=limit)

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
		return await self.repo.listar_filtrados(
			offset=offset,
			limit=limit,
			status=status,
			prioridade=prioridade,
			servico_id=servico_id,
			search=search,
		)

	async def atualizar(self, lead_id: int, payload: LeadAtualizar) -> Lead:
		"""Função para atualizar um registro pelo ID."""
		lead = await self.repo.atualizar(lead_id, payload.model_dump(exclude_none=True))
		if not lead:
			raise NotFoundError(_ENTITY, lead_id)
		await self.session.commit()
		return lead

	async def deletar(self, lead_id: int) -> None:
		"""Função para excluir um registro pelo ID."""
		if not await self.repo.deletar(lead_id):
			raise NotFoundError(_ENTITY, lead_id)
		await self.session.commit()
