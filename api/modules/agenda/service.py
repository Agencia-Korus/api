from __future__ import annotations

from datetime import date, datetime, time, timedelta
from zoneinfo import ZoneInfo

from core.config import obter_configuracoes
from core.exceptions import ErroNaoEncontrado
from modules.agenda.google_calendar import ClienteGoogleCalendar, EventoGoogleCalendar
from modules.agenda.model import EventoAgenda, SolicitacaoReuniao
from modules.agenda.repository import (
	RepositorioEventoAgenda,
	RepositorioSolicitacaoReuniao,
)
from modules.agenda.schema import (
	AgendaEventoSiteResposta,
	EventoAgendaAtualizar,
	EventoAgendaCriar,
	SolicitacaoReuniaoAtualizar,
	SolicitacaoReuniaoCriar,
)
from sqlalchemy.ext.asyncio import AsyncSession

_ENTIDADE_EVENTO = 'Evento de agenda'
_ENTIDADE_SOLICITACAO = 'Solicitação de reunião'


class ServicoAgenda:
	"""Classe responsável pelas regras de negócio de agenda."""

	def __init__(self, sessao: AsyncSession):
		"""Função para inicializar a instância com suas dependências."""
		self.sessao = sessao
		self.eventos = RepositorioEventoAgenda(sessao)
		self.solicitacoes = RepositorioSolicitacaoReuniao(sessao)
		self.calendario_google = ClienteGoogleCalendar(obter_configuracoes())

	async def criar_evento(self, dados: EventoAgendaCriar) -> EventoAgenda:
		"""Função para criar um evento na agenda."""
		evento = EventoAgenda(**dados.model_dump())
		evento = await self.eventos.adicionar(evento)
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
			await self.sessao.flush()
		await self.sessao.commit()
		return evento

	async def obter_evento(self, evento_id: int) -> EventoAgenda:
		"""Função para buscar um evento da agenda pelo ID."""
		evento = await self.eventos.obter(evento_id)
		if not evento:
			raise ErroNaoEncontrado(_ENTIDADE_EVENTO, evento_id)
		return evento

	async def listar_eventos(self, usuario_id: int) -> list[EventoAgenda]:
		"""Função para listar eventos de um usuário."""
		return await self.eventos.listar_por_usuario(usuario_id)

	async def listar_eventos_calendario_google(
		self, data_inicio: date | None = None, data_fim: date | None = None
	) -> list[EventoGoogleCalendar]:
		"""Função para listar eventos sincronizados do Google Calendar."""
		return await self.calendario_google.listar_eventos(data_inicio, data_fim)

	async def listar_eventos_site(
		self,
		usuario_id: int,
		data_inicio: date | None = None,
		data_fim: date | None = None,
	) -> list[AgendaEventoSiteResposta]:
		"""Função para listar eventos públicos exibidos no site."""
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
	def _evento_local_para_site(evento: EventoAgenda) -> AgendaEventoSiteResposta:
		"""Função interna para converter evento local para a resposta do site."""
		fuso_horario = ZoneInfo(obter_configuracoes().google_calendar_timezone)
		hora = (evento.hora or time.min).replace(tzinfo=None)
		inicio = datetime.combine(evento.data, hora, tzinfo=fuso_horario)
		fim = inicio + timedelta(minutes=evento.duracao_min)
		return AgendaEventoSiteResposta(
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
	) -> AgendaEventoSiteResposta:
		"""Função interna para converter evento do Google para a resposta do site."""
		duracao_min = None
		if evento.fim:
			duracao_min = int((evento.fim - evento.inicio).total_seconds() // 60)
		return AgendaEventoSiteResposta(
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
		self, evento_id: int, dados: EventoAgendaAtualizar
	) -> EventoAgenda:
		"""Função para atualizar um evento da agenda."""
		evento_atual = await self.eventos.obter(evento_id)
		if not evento_atual:
			raise ErroNaoEncontrado(_ENTIDADE_EVENTO, evento_id)
		evento = await self.eventos.atualizar(
			evento_id, dados.model_dump(exclude_none=True)
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
			await self.sessao.flush()
		await self.sessao.commit()
		return evento

	async def deletar_evento(self, evento_id: int) -> None:
		"""Função para excluir um evento da agenda."""
		evento = await self.eventos.obter(evento_id)
		if not evento:
			raise ErroNaoEncontrado(_ENTIDADE_EVENTO, evento_id)
		if evento.google_event_id:
			await self.calendario_google.deletar_evento(evento.google_event_id)
		await self.eventos.deletar(evento_id)
		await self.sessao.commit()

	async def criar_solicitacao(
		self, dados: SolicitacaoReuniaoCriar
	) -> SolicitacaoReuniao:
		"""Função para criar uma solicitação de reunião."""
		solicitacao = SolicitacaoReuniao(**dados.model_dump())
		solicitacao = await self.solicitacoes.adicionar(solicitacao)
		await self.sessao.commit()
		return solicitacao

	async def obter_solicitacao(self, solicitacao_id: int) -> SolicitacaoReuniao:
		"""Função para buscar uma solicitação de reunião pelo ID."""
		solicitacao = await self.solicitacoes.obter(solicitacao_id)
		if not solicitacao:
			raise ErroNaoEncontrado(_ENTIDADE_SOLICITACAO, solicitacao_id)
		return solicitacao

	async def listar_solicitacoes_recebidas(
		self, destinatario_id: int
	) -> list[SolicitacaoReuniao]:
		"""Função para listar solicitações de reunião recebidas."""
		return await self.solicitacoes.listar_recebidas(destinatario_id)

	async def atualizar_solicitacao(
		self, solicitacao_id: int, dados: SolicitacaoReuniaoAtualizar
	) -> SolicitacaoReuniao:
		"""Função para atualizar uma solicitação de reunião."""
		solicitacao = await self.solicitacoes.atualizar(
			solicitacao_id, dados.model_dump(exclude_none=True)
		)
		if not solicitacao:
			raise ErroNaoEncontrado(_ENTIDADE_SOLICITACAO, solicitacao_id)
		await self.sessao.commit()
		return solicitacao

	async def deletar_solicitacao(self, solicitacao_id: int) -> None:
		"""Função para excluir uma solicitação de reunião."""
		if not await self.solicitacoes.deletar(solicitacao_id):
			raise ErroNaoEncontrado(_ENTIDADE_SOLICITACAO, solicitacao_id)
		await self.sessao.commit()
