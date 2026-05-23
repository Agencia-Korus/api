from __future__ import annotations

from core.enums import ComunicadoAlvo
from core.exceptions import NotFoundError
from modules.comunicados.model import Comunicado, ComunicadoLeitura
from modules.comunicados.repository import (
	ComunicadoLeituraRepository,
	ComunicadoRepository,
)
from modules.comunicados.schema import ComunicadoCreate, ComunicadoUpdate
from sqlalchemy.ext.asyncio import AsyncSession

_ENTITY = 'Comunicado'


class ComunicadoService:
	def __init__(self, session: AsyncSession):
		self.session = session
		self.repo = ComunicadoRepository(session)
		self.leituras = ComunicadoLeituraRepository(session)

	async def create(self, payload: ComunicadoCreate) -> Comunicado:
		comunicado = Comunicado(**payload.model_dump())
		comunicado = await self.repo.add(comunicado)
		await self.session.commit()
		return comunicado

	async def get(self, comunicado_id: int) -> Comunicado:
		comunicado = await self.repo.get(comunicado_id)
		if not comunicado:
			raise NotFoundError(_ENTITY, comunicado_id)
		return comunicado

	async def list(self, offset: int, limit: int) -> list[Comunicado]:
		return await self.repo.list_all(offset=offset, limit=limit)

	async def list_filtered(
		self, offset: int, limit: int, alvo: ComunicadoAlvo | None = None
	) -> list[Comunicado]:
		return await self.repo.list_all(
			offset=offset, limit=limit, filters={'alvo': alvo}
		)

	async def update(self, comunicado_id: int, payload: ComunicadoUpdate) -> Comunicado:
		comunicado = await self.repo.update(
			comunicado_id, payload.model_dump(exclude_none=True)
		)
		if not comunicado:
			raise NotFoundError(_ENTITY, comunicado_id)
		await self.session.commit()
		return comunicado

	async def delete(self, comunicado_id: int) -> None:
		if not await self.repo.delete(comunicado_id):
			raise NotFoundError(_ENTITY, comunicado_id)
		await self.session.commit()

	async def marcar_lido(
		self, comunicado_id: int, usuario_id: int
	) -> ComunicadoLeitura:
		await self.get(comunicado_id)
		leitura = await self.leituras.marcar_lido(comunicado_id, usuario_id)
		await self.session.commit()
		return leitura

	async def list_leituras(self, comunicado_id: int) -> list[ComunicadoLeitura]:
		await self.get(comunicado_id)
		return await self.leituras.list_by_comunicado(comunicado_id)
