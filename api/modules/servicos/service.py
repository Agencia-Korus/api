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
	def __init__(self, session: AsyncSession):
		self.session = session
		self.repo = ServicoRepository(session)
		self.entregaveis = EntregavelRepository(session)

	async def create(self, payload: ServicoCreate) -> Servico:
		if await self.repo.get_by_slug(payload.slug):
			raise ConflictError('Slug já utilizado')
		servico = Servico(**payload.model_dump())
		servico = await self.repo.add(servico)
		await self.session.commit()
		return servico

	async def get(self, servico_id: int) -> Servico:
		servico = await self.repo.get(servico_id)
		if not servico:
			raise NotFoundError(_ENTITY_SERVICO, servico_id)
		return servico

	async def list(self, offset: int, limit: int) -> list[Servico]:
		return await self.repo.list_all(offset=offset, limit=limit)

	async def list_filtered(
		self, offset: int, limit: int, status: ServicoStatus | None = None
	) -> list[Servico]:
		return await self.repo.list_all(
			offset=offset, limit=limit, filters={'status': status}
		)

	async def update(self, servico_id: int, payload: ServicoUpdate) -> Servico:
		servico = await self.repo.update(
			servico_id, payload.model_dump(exclude_none=True)
		)
		if not servico:
			raise NotFoundError(_ENTITY_SERVICO, servico_id)
		await self.session.commit()
		return servico

	async def delete(self, servico_id: int) -> None:
		if not await self.repo.delete(servico_id):
			raise NotFoundError(_ENTITY_SERVICO, servico_id)
		await self.session.commit()

	async def create_entregavel(self, payload: EntregavelCreate) -> Entregavel:
		await self.get(payload.servico_id)
		entregavel = Entregavel(**payload.model_dump())
		entregavel = await self.entregaveis.add(entregavel)
		await self.session.commit()
		return entregavel

	async def list_entregaveis(self, servico_id: int) -> list[Entregavel]:
		await self.get(servico_id)
		return await self.entregaveis.list_by_servico(servico_id)

	async def update_entregavel(
		self, entregavel_id: int, payload: EntregavelUpdate
	) -> Entregavel:
		entregavel = await self.entregaveis.update(
			entregavel_id, payload.model_dump(exclude_none=True)
		)
		if not entregavel:
			raise NotFoundError(_ENTITY_ENTREGAVEL, entregavel_id)
		await self.session.commit()
		return entregavel

	async def delete_entregavel(self, entregavel_id: int) -> None:
		if not await self.entregaveis.delete(entregavel_id):
			raise NotFoundError(_ENTITY_ENTREGAVEL, entregavel_id)
		await self.session.commit()
