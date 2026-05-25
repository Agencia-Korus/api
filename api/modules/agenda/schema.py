from datetime import date, datetime, time
from typing import Literal

from core.constants import DURACAO_EVENTO_PADRAO_MIN, TITULO_MAX_LENGTH
from core.enums import EventoTipo, SolicitacaoStatus
from pydantic import BaseModel, ConfigDict, Field, model_validator


class EventoAgendaBase(BaseModel):
	"""Classe que define os dados de evento de agenda usados pela API."""

	titulo: str = Field(max_length=TITULO_MAX_LENGTH)
	descricao: str | None = None
	tipo: EventoTipo = EventoTipo.REUNIAO
	data: date
	hora: time | None = None
	duracao_min: int = DURACAO_EVENTO_PADRAO_MIN


class EventoAgendaCreate(EventoAgendaBase):
	"""Classe que define os dados de evento de agenda usados pela API."""

	usuario_id: int

	model_config = ConfigDict(
		json_schema_extra={
			'example': {
				'titulo': 'Reunião kickoff',
				'descricao': 'Alinhamento inicial do projeto',
				'tipo': 'reuniao',
				'data': '2026-04-22',
				'hora': '10:00:00',
				'duracao_min': 60,
				'usuario_id': 1,
			}
		}
	)


class EventoAgendaUpdate(BaseModel):
	"""Classe que define os dados de evento de agenda usados pela API."""

	titulo: str | None = Field(default=None, max_length=TITULO_MAX_LENGTH)
	descricao: str | None = None
	tipo: EventoTipo | None = None
	data: date | None = None
	hora: time | None = None
	duracao_min: int | None = None

	model_config = ConfigDict(
		json_schema_extra={
			'example': {
				'titulo': 'Reunião de apresentação',
				'data': '2026-04-30',
				'hora': '16:00:00',
				'duracao_min': 45,
			}
		}
	)


class EventoAgendaResponse(EventoAgendaBase):
	"""Classe que define os dados de evento de agenda usados pela API."""

	id: int
	usuario_id: int
	google_event_id: str | None = None
	google_link: str | None = None
	criado_em: datetime
	model_config = ConfigDict(from_attributes=True)


class AgendaEventoSiteResponse(BaseModel):
	"""Classe que define os dados de agenda evento site usados pela API."""

	id: str
	origem: Literal['local', 'google_calendar']
	titulo: str
	descricao: str | None = None
	tipo: str | None = None
	inicio: datetime
	fim: datetime | None = None
	data: date
	hora: time | None = None
	duracao_min: int | None = None
	usuario_id: int | None = None
	evento_id: int | None = None
	google_event_id: str | None = None
	link: str | None = None

	model_config = ConfigDict(
		json_schema_extra={
			'example': {
				'id': 'google_calendar:abc123',
				'origem': 'google_calendar',
				'titulo': 'Apresentação da identidade',
				'descricao': 'Reunião sincronizada do Google Calendar',
				'tipo': 'reuniao',
				'inicio': '2026-04-30T16:00:00-03:00',
				'fim': '2026-04-30T17:00:00-03:00',
				'data': '2026-04-30',
				'hora': '16:00:00',
				'duracao_min': 60,
				'usuario_id': None,
				'evento_id': None,
				'google_event_id': 'abc123',
				'link': 'https://calendar.google.com/calendar/event?eid=abc123',
			}
		}
	)


class EventoGoogleCalendarResponse(BaseModel):
	"""Classe que define os dados de evento google calendar usados pela API."""

	id: str
	titulo: str
	descricao: str | None = None
	inicio: datetime
	fim: datetime | None = None
	link: str | None = None
	origem: str = 'google_calendar'

	model_config = ConfigDict(
		json_schema_extra={
			'example': {
				'id': 'abc123',
				'titulo': 'Apresentação da identidade',
				'descricao': 'Reunião sincronizada do Google Calendar',
				'inicio': '2026-04-30T16:00:00-03:00',
				'fim': '2026-04-30T17:00:00-03:00',
				'link': 'https://calendar.google.com/calendar/event?eid=abc123',
				'origem': 'google_calendar',
			}
		}
	)


class SolicitacaoReuniaoBase(BaseModel):
	"""Classe que define os dados de solicitação de reunião usados pela API."""

	titulo: str = Field(max_length=TITULO_MAX_LENGTH)
	mensagem: str | None = None
	data: date
	hora: time
	remetente_id: int
	destinatario_id: int

	@model_validator(mode='after')
	def _diferentes(self):
		"""Função para validar se remetente e destinatário são diferentes."""
		if self.remetente_id == self.destinatario_id:
			raise ValueError('remetente e destinatário devem ser diferentes')
		return self


class SolicitacaoReuniaoCreate(SolicitacaoReuniaoBase):
	"""Classe que define os dados de solicitação de reunião usados pela API."""

	status: SolicitacaoStatus = SolicitacaoStatus.PENDENTE

	model_config = ConfigDict(
		json_schema_extra={
			'example': {
				'titulo': 'Solicitar reunião de revisão',
				'mensagem': 'Podemos revisar o moodboard nesta semana?',
				'data': '2026-04-28',
				'hora': '15:00:00',
				'remetente_id': 2,
				'destinatario_id': 1,
				'status': 'pendente',
			}
		}
	)


class SolicitacaoReuniaoUpdate(BaseModel):
	"""Classe que define os dados de solicitação de reunião usados pela API."""

	titulo: str | None = Field(default=None, max_length=TITULO_MAX_LENGTH)
	mensagem: str | None = None
	data: date | None = None
	hora: time | None = None
	status: SolicitacaoStatus | None = None

	model_config = ConfigDict(
		json_schema_extra={
			'example': {
				'status': 'aceita',
				'data': '2026-04-28',
				'hora': '15:00:00',
			}
		}
	)


class SolicitacaoReuniaoResponse(BaseModel):
	"""Classe que define os dados de solicitação de reunião usados pela API."""

	id: int
	titulo: str
	mensagem: str | None
	data: date
	hora: time
	remetente_id: int
	destinatario_id: int
	status: SolicitacaoStatus
	criado_em: datetime
	model_config = ConfigDict(from_attributes=True)
