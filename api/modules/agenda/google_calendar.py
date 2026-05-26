from __future__ import annotations

import asyncio
import json
from dataclasses import dataclass
from datetime import date, datetime, time, timedelta, timezone
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import quote, urlencode
from urllib.request import Request, urlopen
from zoneinfo import ZoneInfo

from core.config import Configuracoes
from fastapi import HTTPException, status
from jose import jwt

URL_TOKEN_GOOGLE = 'https://oauth2.googleapis.com/token'
BASE_API_GOOGLE_CALENDAR = 'https://www.googleapis.com/calendar/v3'
ESCOPO_GOOGLE_CALENDAR = 'https://www.googleapis.com/auth/calendar.events'
TEMPO_LIMITE_REQUISICAO_SEGUNDOS = 10


@dataclass(frozen=True)
class EventoGoogleCalendar:
	"""Classe que representa um evento retornado pelo Google Calendar."""

	id: str
	titulo: str
	descricao: str | None
	inicio: datetime
	fim: datetime | None
	link: str | None


class ClienteGoogleCalendar:
	"""Classe responsável pela comunicação com o Google Calendar."""

	def __init__(self, configuracoes: Configuracoes):
		"""Função para inicializar a instância com suas dependências."""
		self.configuracoes = configuracoes
		self._token_acesso: str | None = None
		self._token_expira_em: datetime | None = None
		self._id_calendario: str | None = None

	def esta_configurado(self) -> bool:
		"""Função para verificar se o Google Calendar está configurado."""
		if not self.configuracoes.google_calendar_enabled:
			return False
		if self._credenciais_conta_servico_disponiveis():
			return True
		return bool(
			self.configuracoes.google_calendar_id and self.configuracoes.google_calendar_api_key
		)

	def _credenciais_conta_servico_disponiveis(self) -> bool:
		"""Função interna para verificar credenciais de conta de serviço."""
		if self.configuracoes.google_calendar_service_account_json:
			return True
		return self.configuracoes.caminho_conta_servico_google() is not None

	async def listar_eventos(
		self, data_inicio: date | None = None, data_fim: date | None = None
	) -> list[EventoGoogleCalendar]:
		"""Função para listar eventos de um usuário."""
		if not self.esta_configurado():
			return []
		hoje = datetime.now(timezone.utc).date()
		data_inicial = data_inicio or (
			hoje - timedelta(days=self.configuracoes.google_calendar_days_past)
		)
		data_final = data_fim or (
			hoje + timedelta(days=self.configuracoes.google_calendar_days_future)
		)
		parametros = {
			'singleEvents': 'true',
			'orderBy': 'startTime',
			'timeMin': datetime.combine(data_inicial, time.min, tzinfo=timezone.utc).isoformat(),
			'timeMax': datetime.combine(data_final, time.max, tzinfo=timezone.utc).isoformat(),
		}
		if self.configuracoes.google_calendar_api_key:
			parametros['key'] = self.configuracoes.google_calendar_api_key
		id_calendario = await self._resolver_id_calendario()
		if not id_calendario:
			return []
		dados = await self._requisitar_json(
			'GET',
			self._url_calendario(id_calendario, 'events', parametros),
			cabecalhos=await self._cabecalhos_autenticacao(),
		)
		return [self._converter_evento(item) for item in dados.get('items', [])]

	async def criar_evento(
		self,
		titulo: str,
		descricao: str | None,
		data: date,
		hora: time | None,
		duracao_min: int,
	) -> EventoGoogleCalendar | None:
		"""Função para criar um evento na agenda."""
		if not self._pode_escrever_eventos():
			return None
		id_calendario = await self._resolver_id_calendario()
		if not id_calendario:
			return None
		corpo = self._corpo_evento(titulo, descricao, data, hora, duracao_min)
		evento_criado = await self._requisitar_json(
			'POST',
			self._url_calendario(id_calendario, 'events'),
			corpo_requisicao=json.dumps(corpo).encode('utf-8'),
			cabecalhos={
				**await self._cabecalhos_autenticacao(),
				'Content-Type': 'application/json',
			},
		)
		return self._converter_evento(evento_criado)

	async def atualizar_evento(
		self,
		id_evento_google: str,
		titulo: str,
		descricao: str | None,
		data: date,
		hora: time | None,
		duracao_min: int,
	) -> EventoGoogleCalendar | None:
		"""Função para atualizar um evento da agenda."""
		if not self._pode_escrever_eventos():
			return None
		id_calendario = await self._resolver_id_calendario()
		if not id_calendario:
			return None
		corpo = self._corpo_evento(titulo, descricao, data, hora, duracao_min)
		try:
			evento_atualizado = await self._requisitar_json(
				'PATCH',
				self._url_calendario(id_calendario, f'events/{quote(id_evento_google, safe="")}'),
				corpo_requisicao=json.dumps(corpo).encode('utf-8'),
				cabecalhos={
					**await self._cabecalhos_autenticacao(),
					'Content-Type': 'application/json',
				},
			)
		except HTTPException as exc:
			if self._erro_recurso_nao_encontrado(exc):
				return await self.criar_evento(
					titulo=titulo,
					descricao=descricao,
					data=data,
					hora=hora,
					duracao_min=duracao_min,
				)
			raise
		return self._converter_evento(evento_atualizado)

	async def deletar_evento(self, id_evento_google: str) -> None:
		"""Função para excluir um evento da agenda."""
		if not self._pode_escrever_eventos():
			return
		id_calendario = await self._resolver_id_calendario()
		if not id_calendario:
			return
		try:
			await self._requisitar_json(
				'DELETE',
				self._url_calendario(id_calendario, f'events/{quote(id_evento_google, safe="")}'),
				cabecalhos=await self._cabecalhos_autenticacao(),
			)
		except HTTPException as exc:
			if self._erro_recurso_nao_encontrado(exc):
				return
			raise

	async def _resolver_id_calendario(self) -> str | None:
		"""Função interna para resolver o ID do calendário configurado."""
		if self.configuracoes.google_calendar_id:
			return self.configuracoes.google_calendar_id
		if self._id_calendario:
			return self._id_calendario
		if self.configuracoes.google_calendar_api_key:
			return None
		dados = await self._requisitar_json(
			'GET',
			f'{BASE_API_GOOGLE_CALENDAR}/users/me/calendarList',
			cabecalhos=await self._cabecalhos_autenticacao(),
		)
		for calendario in dados.get('items', []):
			if calendario.get('accessRole') in {'owner', 'writer', 'reader'}:
				self._id_calendario = calendario.get('id')
				return self._id_calendario
		return None

	@staticmethod
	def _url_calendario(
		id_calendario: str,
		caminho: str,
		parametros: dict[str, Any] | None = None,
	) -> str:
		"""Função interna para montar a URL da API do calendário."""
		id_calendario = quote(id_calendario, safe='')
		url = f'{BASE_API_GOOGLE_CALENDAR}/calendars/{id_calendario}/{caminho}'
		if parametros:
			url = f'{url}?{urlencode(parametros)}'
		return url

	async def _cabecalhos_autenticacao(self) -> dict[str, str]:
		"""Função interna para montar cabeçalhos de autenticação do Google."""
		if self.configuracoes.google_calendar_api_key:
			return {}
		token = await self._obter_token_conta_servico()
		return {'Authorization': f'Bearer {token}'}

	def _pode_escrever_eventos(self) -> bool:
		"""Função interna para verificar se eventos podem ser escritos."""
		return bool(
			self.configuracoes.google_calendar_enabled
			and self._credenciais_conta_servico_disponiveis()
		)

	async def _obter_token_conta_servico(self) -> str:
		"""Função interna para obter token da conta de serviço."""
		agora = datetime.now(timezone.utc)
		if self._token_acesso and self._token_expira_em and agora < self._token_expira_em:
			return self._token_acesso
		info = self._info_conta_servico()
		emitido_em = int(agora.timestamp())
		expira_em = emitido_em + 3600
		declaracoes: dict[str, Any] = {
			'iss': info['client_email'],
			'scope': ESCOPO_GOOGLE_CALENDAR,
			'aud': URL_TOKEN_GOOGLE,
			'iat': emitido_em,
			'exp': expira_em,
		}
		if self.configuracoes.google_calendar_delegated_user:
			declaracoes['sub'] = self.configuracoes.google_calendar_delegated_user
		assercao = jwt.encode(
			declaracoes,
			info['private_key'],
			algorithm='RS256',
		)
		corpo = urlencode({
			'grant_type': 'urn:ietf:params:oauth:grant-type:jwt-bearer',
			'assertion': assercao,
		}).encode()
		dados = await self._requisitar_json(
			'POST',
			URL_TOKEN_GOOGLE,
			corpo_requisicao=corpo,
			cabecalhos={'Content-Type': 'application/x-www-form-urlencoded'},
		)
		self._token_acesso = dados['access_token']
		self._token_expira_em = agora + timedelta(
			seconds=max(60, int(dados.get('expires_in', 3600)) - 60)
		)
		return self._token_acesso

	def _info_conta_servico(self) -> dict[str, Any]:
		"""Função interna para carregar os dados da conta de serviço."""
		if self.configuracoes.google_calendar_service_account_json:
			return json.loads(self.configuracoes.google_calendar_service_account_json)
		caminho = self.configuracoes.caminho_conta_servico_google()
		if caminho:
			with caminho.open(encoding='utf-8') as file:
				return json.load(file)
		caminhos_configurados = [
			self.configuracoes.google_calendar_service_account_host_file,
			self.configuracoes.google_calendar_service_account_file,
		]
		if any(caminhos_configurados):
			raise HTTPException(
				status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
				detail=(
					'Arquivo da conta de serviço do Google Calendar não encontrado. '
					'Para testar localmente com task run, coloque o JSON em '
					'.env.google-calendar-service-account.json na raiz do projeto.'
				),
			)
		raise HTTPException(
			status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
			detail='Google Calendar não configurado',
		)

	def _corpo_evento(
		self,
		titulo: str,
		descricao: str | None,
		data: date,
		hora: time | None,
		duracao_min: int,
	) -> dict[str, Any]:
		"""Função interna para montar o corpo de um evento do Google Calendar."""
		corpo: dict[str, Any] = {
			'summary': titulo,
			'description': descricao,
		}
		if hora:
			nome_fuso_horario = self.configuracoes.google_calendar_timezone
			fuso_horario = ZoneInfo(nome_fuso_horario)
			inicio = datetime.combine(
				data,
				hora.replace(tzinfo=None),
				tzinfo=fuso_horario,
			)
			fim = inicio + timedelta(minutes=duracao_min)
			corpo['start'] = {
				'dateTime': inicio.isoformat(),
				'timeZone': nome_fuso_horario,
			}
			corpo['end'] = {
				'dateTime': fim.isoformat(),
				'timeZone': nome_fuso_horario,
			}
		else:
			corpo['start'] = {'date': data.isoformat()}
			corpo['end'] = {'date': (data + timedelta(days=1)).isoformat()}
		return corpo

	async def _requisitar_json(
		self,
		metodo: str,
		url: str,
		corpo_requisicao: bytes | None = None,
		cabecalhos: dict[str, str] | None = None,
	) -> dict[str, Any]:
		"""Função interna para executar uma requisição JSON assíncrona."""
		return await asyncio.to_thread(
			self._requisitar_json_sincrono,
			metodo,
			url,
			corpo_requisicao,
			cabecalhos or {},
		)

	@staticmethod
	def _requisitar_json_sincrono(
		metodo: str,
		url: str,
		corpo_requisicao: bytes | None,
		cabecalhos: dict[str, str],
	) -> dict[str, Any]:
		"""Função interna para executar uma requisição JSON síncrona."""
		requisicao = Request(
			url=url,
			data=corpo_requisicao,
			headers=cabecalhos,
			method=metodo,
		)
		try:
			with urlopen(
				requisicao,
				timeout=TEMPO_LIMITE_REQUISICAO_SEGUNDOS,
			) as resposta:
				conteudo = resposta.read().decode('utf-8')
				if not conteudo:
					return {}
				return json.loads(conteudo)
		except HTTPError as exc:
			mensagem = exc.read().decode('utf-8') or str(exc)
			if exc.code == status.HTTP_404_NOT_FOUND:
				raise HTTPException(
					status_code=status.HTTP_404_NOT_FOUND,
					detail=f'Google Calendar não encontrou o recurso: {mensagem}',
				) from exc
			raise HTTPException(
				status_code=status.HTTP_502_BAD_GATEWAY,
				detail=f'Falha no Google Calendar: {mensagem}',
			) from exc
		except URLError as exc:
			raise HTTPException(
				status_code=status.HTTP_502_BAD_GATEWAY,
				detail=f'Google Calendar indisponível: {exc.reason}',
			) from exc

	def _converter_evento(self, item: dict[str, Any]) -> EventoGoogleCalendar:
		"""Função interna para converter um evento do Google Calendar."""
		inicio = self._converter_data_hora_evento(item.get('start', {}))
		fim = self._converter_data_hora_evento(item.get('end', {})) if item.get('end') else None
		return EventoGoogleCalendar(
			id=item['id'],
			titulo=item.get('summary') or 'Reunião',
			descricao=item.get('description'),
			inicio=inicio,
			fim=fim,
			link=item.get('htmlLink'),
		)

	@staticmethod
	def _erro_recurso_nao_encontrado(exc: HTTPException) -> bool:
		"""Função interna para identificar erro de recurso não encontrado."""
		return exc.status_code == status.HTTP_404_NOT_FOUND

	@staticmethod
	def _converter_data_hora_evento(dados_data_hora: dict[str, Any]) -> datetime:
		"""Função interna para converter data e hora de um evento."""
		if dados_data_hora.get('dateTime'):
			valor = dados_data_hora['dateTime'].replace('Z', '+00:00')
			return datetime.fromisoformat(valor)
		if dados_data_hora.get('date'):
			return datetime.combine(
				date.fromisoformat(dados_data_hora['date']),
				time.min,
				tzinfo=timezone.utc,
			)
		return datetime.now(timezone.utc)
