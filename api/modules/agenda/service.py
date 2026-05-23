from __future__ import annotations

from datetime import date, datetime, time, timedelta
from zoneinfo import ZoneInfo

from core.exceptions import NotFoundError
from modules.agenda.google_calendar import ClienteGoogleCalendar, EventoGoogleCalendar
from modules.agenda.model import EventoAgenda, SolicitacaoReuniao
from modules.agenda.repository import (
	EventoAgendaRepository,
	SolicitacaoReuniaoRepository,
)
from modules.agenda.schema import (
	AgendaEventoSiteResponse,
	EventoAgendaCreate,
	EventoAgendaUpdate,
	SolicitacaoReuniaoCreate,
	SolicitacaoReuniaoUpdate,
)
from sqlalchemy.ext.asyncio import AsyncSession

from core.config import get_settings

_ENTITY_EVENTO = 'Evento de agenda'
_ENTITY_SOLICITACAO = 'Solicitação de reunião'


class AgendaService:
	def __init__(self, session: AsyncSession):
		self.session = session
		self.eventos = EventoAgendaRepository(session)
		self.solicitacoes = SolicitacaoReuniaoRepository(session)
		self.calendario_google = ClienteGoogleCalendar(get_settings())

	async def criar_evento(self, payload: EventoAgendaCreate) -> EventoAgenda:
		evento = EventoAgenda(**payload.model_dump())
		evento = await self.eventos.add(evento)
		evento_google = await self.calendario_google.criar_evento(
			titulo=evento.titulo,
			descricao=evento.descricao,
			data=evento.data,
			hora=evento.hora,
			duracao_min=evento.duracao_min,
		)
		if evento_google:
			evento.google_event_id = evento_google.id
			evento.google_link = evento_google.link
			await self.session.flush()
		await self.session.commit()
		return evento

	async def get_evento(self, evento_id: int) -> EventoAgenda:
		evento = await self.eventos.get(evento_id)
		if not evento:
			raise NotFoundError(_ENTITY_EVENTO, evento_id)
		return evento

	async def listar_eventos(self, usuario_id: int) -> list[EventoAgenda]:
		return await self.eventos.list_by_usuario(usuario_id)

	async def listar_eventos_calendario_google(
		self, data_inicio: date | None = None, data_fim: date | None = None
	) -> list[EventoGoogleCalendar]:
		return await self.calendario_google.listar_eventos(data_inicio, data_fim)

	async def listar_eventos_site(
		self,
		usuario_id: int,
		data_inicio: date | None = None,
		data_fim: date | None = None,
	) -> list[AgendaEventoSiteResponse]:
		eventos_locais = await self.listar_eventos(usuario_id)
		if data_inicio:
			eventos_locais = [
				evento for evento in eventos_locais if evento.data >= data_inicio
			]
		if data_fim:
			eventos_locais = [
				evento for evento in eventos_locais if evento.data <= data_fim
			]
		eventos_google = await self.listar_eventos_calendario_google(
			data_inicio, data_fim
		)
		ids_google_sincronizados = {
			evento.google_event_id
			for evento in eventos_locais
			if evento.google_event_id
		}
		eventos_google = [
			evento
			for evento in eventos_google
			if evento.id not in ids_google_sincronizados
		]
		eventos = [
			self._evento_local_para_site(evento) for evento in eventos_locais
		] + [self._evento_google_para_site(evento) for evento in eventos_google]
		return sorted(eventos, key=lambda evento: evento.inicio)

	@staticmethod
	def _evento_local_para_site(evento: EventoAgenda) -> AgendaEventoSiteResponse:
		fuso_horario = ZoneInfo(get_settings().google_calendar_timezone)
		hora = (evento.hora or time.min).replace(tzinfo=None)
		inicio = datetime.combine(evento.data, hora, tzinfo=fuso_horario)
		fim = inicio + timedelta(minutes=evento.duracao_min)
		return AgendaEventoSiteResponse(
			id=f'local:{evento.id}',
			origem='local',
			titulo=evento.titulo,
			descricao=evento.descricao,
			tipo=evento.tipo.value,
			inicio=inicio,
			fim=fim,
			data=evento.data,
			hora=evento.hora,
			duracao_min=evento.duracao_min,
			usuario_id=evento.usuario_id,
			evento_id=evento.id,
			google_event_id=evento.google_event_id,
			link=evento.google_link,
		)

	@staticmethod
	def _evento_google_para_site(
		evento: EventoGoogleCalendar,
	) -> AgendaEventoSiteResponse:
		duracao_min = None
		if evento.fim:
			duracao_min = int((evento.fim - evento.inicio).total_seconds() // 60)
		return AgendaEventoSiteResponse(
			id=f'google_calendar:{evento.id}',
			origem='google_calendar',
			titulo=evento.titulo,
			descricao=evento.descricao,
			tipo='reuniao',
			inicio=evento.inicio,
			fim=evento.fim,
			data=evento.inicio.date(),
			hora=evento.inicio.time().replace(tzinfo=None),
			duracao_min=duracao_min,
			usuario_id=None,
			evento_id=None,
			google_event_id=evento.id,
			link=evento.link,
		)

	async def atualizar_evento(
		self, evento_id: int, payload: EventoAgendaUpdate
	) -> EventoAgenda:
		evento_atual = await self.eventos.get(evento_id)
		if not evento_atual:
			raise NotFoundError(_ENTITY_EVENTO, evento_id)
		evento = await self.eventos.update(
			evento_id, payload.model_dump(exclude_none=True)
		)
		if evento.google_event_id:
			evento_google = await self.calendario_google.atualizar_evento(
				id_evento_google=evento.google_event_id,
				titulo=evento.titulo,
				descricao=evento.descricao,
				data=evento.data,
				hora=evento.hora,
				duracao_min=evento.duracao_min,
			)
		else:
			evento_google = await self.calendario_google.criar_evento(
				titulo=evento.titulo,
				descricao=evento.descricao,
				data=evento.data,
				hora=evento.hora,
				duracao_min=evento.duracao_min,
			)
		if evento_google:
			evento.google_event_id = evento_google.id
			evento.google_link = evento_google.link
			await self.session.flush()
		await self.session.commit()
		return evento

	async def deletar_evento(self, evento_id: int) -> None:
		evento = await self.eventos.get(evento_id)
		if not evento:
			raise NotFoundError(_ENTITY_EVENTO, evento_id)
		if evento.google_event_id:
			await self.calendario_google.deletar_evento(evento.google_event_id)
		await self.eventos.delete(evento_id)
		await self.session.commit()

	async def criar_solicitacao(
		self, payload: SolicitacaoReuniaoCreate
	) -> SolicitacaoReuniao:
		solicitacao = SolicitacaoReuniao(**payload.model_dump())
		solicitacao = await self.solicitacoes.add(solicitacao)
		await self.session.commit()
		return solicitacao

	async def get_solicitacao(self, solicitacao_id: int) -> SolicitacaoReuniao:
		solicitacao = await self.solicitacoes.get(solicitacao_id)
		if not solicitacao:
			raise NotFoundError(_ENTITY_SOLICITACAO, solicitacao_id)
		return solicitacao

	async def listar_solicitacoes_recebidas(
		self, destinatario_id: int
	) -> list[SolicitacaoReuniao]:
		return await self.solicitacoes.list_recebidas(destinatario_id)

	async def atualizar_solicitacao(
		self, solicitacao_id: int, payload: SolicitacaoReuniaoUpdate
	) -> SolicitacaoReuniao:
		solicitacao = await self.solicitacoes.update(
			solicitacao_id, payload.model_dump(exclude_none=True)
		)
		if not solicitacao:
			raise NotFoundError(_ENTITY_SOLICITACAO, solicitacao_id)
		await self.session.commit()
		return solicitacao

	async def deletar_solicitacao(self, solicitacao_id: int) -> None:
		if not await self.solicitacoes.delete(solicitacao_id):
			raise NotFoundError(_ENTITY_SOLICITACAO, solicitacao_id)
		await self.session.commit()
