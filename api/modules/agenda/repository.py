from sqlalchemy import select

from db.base_repository import BaseRepository
from modules.agenda.model import EventoAgenda, SolicitacaoReuniao


class EventoAgendaRepository(BaseRepository[EventoAgenda]):
	model = EventoAgenda

	async def list_by_usuario(self, usuario_id: int) -> list[EventoAgenda]:
		stmt = (
			select(EventoAgenda)
			.where(EventoAgenda.usuario_id == usuario_id)
			.order_by(EventoAgenda.data, EventoAgenda.hora)
		)
		result = await self.session.execute(stmt)
		return list(result.scalars().all())


class SolicitacaoReuniaoRepository(BaseRepository[SolicitacaoReuniao]):
	model = SolicitacaoReuniao

	async def list_recebidas(self, destinatario_id: int) -> list[SolicitacaoReuniao]:
		stmt = (
			select(SolicitacaoReuniao)
			.where(SolicitacaoReuniao.destinatario_id == destinatario_id)
			.order_by(SolicitacaoReuniao.criado_em.desc())
		)
		result = await self.session.execute(stmt)
		return list(result.scalars().all())
