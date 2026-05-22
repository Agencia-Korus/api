from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from db.base_repository import BaseRepository
from modules.comunicados.model import Comunicado, ComunicadoLeitura


class ComunicadoRepository(BaseRepository[Comunicado]):
	model = Comunicado


class ComunicadoLeituraRepository:
	def __init__(self, session: AsyncSession):
		self.session = session

	async def marcar_lido(
		self, comunicado_id: int, usuario_id: int
	) -> ComunicadoLeitura:
		stmt = (
			insert(ComunicadoLeitura)
			.values(comunicado_id=comunicado_id, usuario_id=usuario_id)
			.on_conflict_do_nothing(index_elements=['comunicado_id', 'usuario_id'])
		)
		await self.session.execute(stmt)
		await self.session.flush()
		select_stmt = select(ComunicadoLeitura).where(
			ComunicadoLeitura.comunicado_id == comunicado_id,
			ComunicadoLeitura.usuario_id == usuario_id,
		)
		result = await self.session.execute(select_stmt)
		return result.scalar_one()

	async def list_by_comunicado(self, comunicado_id: int) -> list[ComunicadoLeitura]:
		stmt = select(ComunicadoLeitura).where(
			ComunicadoLeitura.comunicado_id == comunicado_id
		)
		result = await self.session.execute(stmt)
		return list(result.scalars().all())
