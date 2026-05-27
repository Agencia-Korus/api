from __future__ import annotations

from core.enums import LeadPrioridade, SituacaoLead
from core.exceptions import ErroNaoEncontrado
from modules.leads.model import Lead
from modules.leads.repository import RepositorioLead
from modules.leads.schema import LeadAtualizar, LeadCriar
from sqlalchemy.ext.asyncio import AsyncSession

_ENTIDADE = 'Lead'


class ServicoLead:
	"""Classe responsável pelas regras de negócio de lead."""

	def __init__(self, sessao: AsyncSession):
		"""Função para inicializar a instância com suas dependências."""
		self.sessao = sessao
		self.repository = RepositorioLead(sessao)

	async def criar(self, dados: LeadCriar) -> Lead:
		"""Função para criar um novo registro."""
		lead = Lead(**dados.model_dump())
		lead = await self.repository.adicionar(lead)
		await self.sessao.commit()
		return lead

	async def obter(self, lead_id: int) -> Lead:
		"""Função para obter um registro pelo ID."""
		lead = await self.repository.obter(lead_id)
		if not lead:
			raise ErroNaoEncontrado(_ENTIDADE, lead_id)
		return lead

	async def listar(self, offset: int, limit: int) -> list[Lead]:
		"""Função para listar registros."""
		return await self.repository.listar_todos(offset=offset, limit=limit)

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
		return await self.repository.listar_filtrados(
			offset=offset,
			limit=limit,
			status=status,
			prioridade=prioridade,
			servico_id=servico_id,
			busca=busca,
		)

	async def atualizar(self, lead_id: int, dados: LeadAtualizar) -> Lead:
		"""Função para atualizar um registro pelo ID."""
		lead = await self.repository.atualizar(lead_id, dados.model_dump(exclude_none=True))
		if not lead:
			raise ErroNaoEncontrado(_ENTIDADE, lead_id)
		await self.sessao.commit()
		return lead

	async def deletar(self, lead_id: int) -> None:
		"""Função para excluir um registro pelo ID."""
		if not await self.repository.deletar(lead_id):
			raise ErroNaoEncontrado(_ENTIDADE, lead_id)
		await self.sessao.commit()
