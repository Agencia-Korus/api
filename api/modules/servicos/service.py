from __future__ import annotations

from core.enums import ServicoStatus
from core.exceptions import ConflictError, NotFoundError
from modules.servicos.model import Entregavel, Servico
from modules.servicos.repository import EntregavelRepository, ServicoRepository
from modules.servicos.schema import (
	EntregavelCreate,
	EntregavelUpdate,
	ServicoCreate,
	ServicoUpdate,
)
from sqlalchemy.ext.asyncio import AsyncSession

_ENTITY_SERVICO = 'Serviço'
_ENTITY_ENTREGAVEL = 'Entregável'


class ServicoService:
	"""Classe responsável pelas regras de negócio de serviço."""

	def __init__(self, session: AsyncSession):
		"""Função para inicializar a instância com suas dependências."""
		self.session = session
		self.repo = ServicoRepository(session)
		self.entregaveis = EntregavelRepository(session)

	async def create(self, payload: ServicoCreate) -> Servico:
		"""Função para criar um novo registro."""
		if await self.repo.get_by_slug(payload.slug):
			raise ConflictError('Slug já utilizado')
		servico = Servico(**payload.model_dump())
		servico = await self.repo.add(servico)
		await self.session.commit()
		return servico

	async def get(self, servico_id: int) -> Servico:
		"""Função para obter um registro pelo ID."""
		servico = await self.repo.get(servico_id)
		if not servico:
			raise NotFoundError(_ENTITY_SERVICO, servico_id)
		return servico

	async def list(self, offset: int, limit: int) -> list[Servico]:
		"""Função para listar registros."""
		return await self.repo.list_all(offset=offset, limit=limit)

	async def list_filtered(
		self, offset: int, limit: int, status: ServicoStatus | None = None
	) -> list[Servico]:
		"""Função para listar registros aplicando filtros e paginação."""
		return await self.repo.list_all(
			offset=offset, limit=limit, filters={'status': status}
		)

	async def update(self, servico_id: int, payload: ServicoUpdate) -> Servico:
		"""Função para atualizar um registro pelo ID."""
		servico = await self.repo.update(
			servico_id, payload.model_dump(exclude_none=True)
		)
		if not servico:
			raise NotFoundError(_ENTITY_SERVICO, servico_id)
		await self.session.commit()
		return servico

	async def delete(self, servico_id: int) -> None:
		"""Função para excluir um registro pelo ID."""
		if not await self.repo.delete(servico_id):
			raise NotFoundError(_ENTITY_SERVICO, servico_id)
		await self.session.commit()

	async def create_entregavel(self, payload: EntregavelCreate) -> Entregavel:
		"""Função para criar um entregável de serviço."""
		await self.get(payload.servico_id)
		entregavel = Entregavel(**payload.model_dump())
		entregavel = await self.entregaveis.add(entregavel)
		await self.session.commit()
		return entregavel

	async def list_entregaveis(self, servico_id: int) -> list[Entregavel]:
		"""Função para listar entregáveis de um serviço."""
		await self.get(servico_id)
		return await self.entregaveis.list_by_servico(servico_id)

	async def update_entregavel(
		self, entregavel_id: int, payload: EntregavelUpdate
	) -> Entregavel:
		"""Função para atualizar um entregável de serviço."""
		entregavel = await self.entregaveis.update(
			entregavel_id, payload.model_dump(exclude_none=True)
		)
		if not entregavel:
			raise NotFoundError(_ENTITY_ENTREGAVEL, entregavel_id)
		await self.session.commit()
		return entregavel

	async def delete_entregavel(self, entregavel_id: int) -> None:
		"""Função para excluir um entregável de serviço."""
		if not await self.entregaveis.delete(entregavel_id):
			raise NotFoundError(_ENTITY_ENTREGAVEL, entregavel_id)
		await self.session.commit()
