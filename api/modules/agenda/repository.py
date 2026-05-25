from db.base_repository import BaseRepository
from modules.agenda.model import EventoAgenda, SolicitacaoReuniao
from sqlalchemy import select


class EventoAgendaRepository(BaseRepository[EventoAgenda]):
	"""Classe responsável pelo acesso aos dados de evento de agenda."""

	model = EventoAgenda

	async def list_by_usuario(self, usuario_id: int) -> list[EventoAgenda]:
		"""Função para listar eventos de agenda de um usuário."""
		stmt = (
			select(EventoAgenda)
			.where(EventoAgenda.usuario_id == usuario_id)
			.order_by(EventoAgenda.data, EventoAgenda.hora)
		)
		result = await self.session.execute(stmt)
		return list(result.scalars().all())


class SolicitacaoReuniaoRepository(BaseRepository[SolicitacaoReuniao]):
	"""Classe responsável pelo acesso aos dados de solicitação de reunião."""

	model = SolicitacaoReuniao

	async def list_recebidas(self, destinatario_id: int) -> list[SolicitacaoReuniao]:
		"""Função para listar solicitações recebidas por um usuário."""
		stmt = (
			select(SolicitacaoReuniao)
			.where(SolicitacaoReuniao.destinatario_id == destinatario_id)
			.order_by(SolicitacaoReuniao.criado_em.desc())
		)
		result = await self.session.execute(stmt)
		return list(result.scalars().all())
