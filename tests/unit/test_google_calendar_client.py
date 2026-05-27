from datetime import date, datetime, time, timedelta, timezone
from io import BytesIO
from unittest.mock import AsyncMock
from urllib.error import HTTPError, URLError

import pytest
from core.config import Configuracoes
from fastapi import HTTPException
from modules.agenda import google_calendar
from modules.agenda.google_calendar import ClienteGoogleCalendar


def _configuracoes(**substituicoes):
	"""Função para criar configurações isoladas do ambiente local."""
	dados = {
		'google_calendar_enabled': True,
		'google_calendar_id': 'calendario',
		'google_calendar_api_key': None,
		'google_calendar_service_account_file': None,
		'google_calendar_service_account_host_file': None,
		'google_calendar_service_account_json': '{"client_email":"svc@test","private_key":"key"}',
		'google_calendar_delegated_user': None,
	}
	dados.update(substituicoes)
	return Configuracoes(**dados)


@pytest.mark.asyncio
async def test_google_calendar_lista_eventos_configurados(monkeypatch: pytest.MonkeyPatch):
	"""Valida listagem de eventos configurados no Google Calendar."""
	cliente = ClienteGoogleCalendar(
		_configuracoes(google_calendar_id='calendario', google_calendar_api_key='api-key')
	)

	async def requisitar(_metodo, url, **_kwargs):
		assert 'singleEvents=true' in url
		return {
			'items': [
				{
					'id': 'evt-1',
					'summary': 'Reunião',
					'description': 'Briefing',
					'start': {'dateTime': '2026-05-26T10:00:00Z'},
					'end': {'dateTime': '2026-05-26T11:00:00+00:00'},
					'htmlLink': 'https://calendar.test/evt-1',
				},
				{
					'id': 'evt-2',
					'start': {'date': '2026-05-27'},
				},
			]
		}

	monkeypatch.setattr(cliente, '_requisitar_json', requisitar)

	eventos = await cliente.listar_eventos(date(2026, 5, 1), date(2026, 5, 31))

	assert [evento.id for evento in eventos] == ['evt-1', 'evt-2']
	assert eventos[0].inicio.isoformat() == '2026-05-26T10:00:00+00:00'
	assert eventos[1].titulo == 'Reunião'


@pytest.mark.asyncio
async def test_google_calendar_retorna_vazio_sem_configuracao_ou_calendario(
	monkeypatch: pytest.MonkeyPatch,
):
	"""Valida retornos vazios quando configuração ou calendário estão ausentes."""
	desabilitado = ClienteGoogleCalendar(
		_configuracoes(google_calendar_enabled=False, google_calendar_id=None)
	)
	assert desabilitado.esta_configurado() is False
	assert await desabilitado.listar_eventos() == []

	sem_calendario = ClienteGoogleCalendar(_configuracoes(google_calendar_id=None))

	async def resolver_vazio():
		return None

	monkeypatch.setattr(sem_calendario, '_resolver_id_calendario', resolver_vazio)
	assert await sem_calendario.listar_eventos() == []
	assert await sem_calendario.criar_evento('Evento', None, date.today(), None, 30) is None
	assert (
		await sem_calendario.atualizar_evento('google-1', 'Evento', None, date.today(), None, 30)
		is None
	)
	await sem_calendario.deletar_evento('google-1')


@pytest.mark.asyncio
async def test_google_calendar_ignora_escrita_sem_configuracao():
	"""Valida que escrita é ignorada quando credenciais não estão disponíveis."""
	cliente = ClienteGoogleCalendar(
		_configuracoes(
			google_calendar_enabled=False,
			google_calendar_service_account_json=None,
		)
	)

	assert await cliente.criar_evento('Evento', None, date.today(), None, 30) is None
	assert (
		await cliente.atualizar_evento('google-1', 'Evento', None, date.today(), None, 30) is None
	)
	await cliente.deletar_evento('google-1')


@pytest.mark.asyncio
async def test_google_calendar_cria_atualiza_e_deleta_eventos(
	monkeypatch: pytest.MonkeyPatch,
):
	"""Valida criação, atualização e remoção de eventos no Google Calendar."""
	cliente = ClienteGoogleCalendar(_configuracoes())
	chamadas: list[tuple[str, str]] = []
	monkeypatch.setattr(google_calendar.jwt, 'encode', lambda *_args, **_kwargs: 'jwt')

	async def requisitar(metodo, url, **_kwargs):
		chamadas.append((metodo, url))
		if 'oauth2' in url:
			return {'access_token': 'token', 'expires_in': 3600}
		if metodo == 'DELETE':
			return {}
		return {
			'id': f'{metodo}-1',
			'summary': 'Evento',
			'start': {'dateTime': '2026-05-26T10:00:00+00:00'},
			'end': {'dateTime': '2026-05-26T11:00:00+00:00'},
		}

	monkeypatch.setattr(cliente, '_requisitar_json', requisitar)

	criado = await cliente.criar_evento('Evento', None, date(2026, 5, 26), time(10), 60)
	atualizado = await cliente.atualizar_evento(
		'google-1', 'Evento', None, date(2026, 5, 26), None, 60
	)
	await cliente.deletar_evento('google-1')

	assert criado is not None
	assert criado.id == 'POST-1'
	assert atualizado is not None
	assert atualizado.id == 'PATCH-1'
	assert [metodo for metodo, _url in chamadas if metodo != 'POST'] == [
		'PATCH',
		'DELETE',
	]


@pytest.mark.asyncio
async def test_google_calendar_trata_fallbacks_e_erros(monkeypatch: pytest.MonkeyPatch):
	"""Valida fallbacks e erros de atualização e remoção de eventos."""
	cliente = ClienteGoogleCalendar(_configuracoes())
	cliente.criar_evento = AsyncMock(return_value='novo-evento')  # type: ignore[method-assign]
	cliente._token_acesso = 'token'
	cliente._token_expira_em = datetime.now(timezone.utc) + timedelta(minutes=10)

	async def atualizar_nao_encontrado(*_args, **_kwargs):
		raise HTTPException(status_code=404, detail='não encontrado')

	monkeypatch.setattr(cliente, '_requisitar_json', atualizar_nao_encontrado)

	assert (
		await cliente.atualizar_evento('ausente', 'Evento', None, date(2026, 5, 26), None, 30)
		== 'novo-evento'
	)
	await cliente.deletar_evento('ausente')

	async def falha_gateway(*_args, **_kwargs):
		raise HTTPException(status_code=502, detail='falha')

	monkeypatch.setattr(cliente, '_requisitar_json', falha_gateway)

	with pytest.raises(HTTPException) as exc:
		await cliente.atualizar_evento('erro', 'Evento', None, date(2026, 5, 26), None, 30)
	assert exc.value.status_code == 502
	with pytest.raises(HTTPException):
		await cliente.deletar_evento('erro')


@pytest.mark.asyncio
async def test_google_calendar_resolve_calendario_e_autenticacao(
	monkeypatch: pytest.MonkeyPatch,
):
	"""Valida resolução de calendário e cabeçalhos de autenticação."""
	cliente = ClienteGoogleCalendar(
		_configuracoes(google_calendar_id=None, google_calendar_delegated_user='user@test')
	)
	monkeypatch.setattr(google_calendar.jwt, 'encode', lambda *_args, **_kwargs: 'jwt')

	async def requisitar(_metodo, url, **_kwargs):
		if 'oauth2' in url:
			return {'access_token': 'token', 'expires_in': 120}
		return {'items': [{'id': 'cal-1', 'accessRole': 'reader'}]}

	monkeypatch.setattr(cliente, '_requisitar_json', requisitar)

	assert await cliente._resolver_id_calendario() == 'cal-1'
	assert await cliente._resolver_id_calendario() == 'cal-1'
	assert await cliente._cabecalhos_autenticacao() == {'Authorization': 'Bearer token'}
	cliente._token_expira_em = datetime.now(timezone.utc) + timedelta(minutes=10)
	assert await cliente._obter_token_conta_servico() == 'token'

	com_chave = ClienteGoogleCalendar(
		_configuracoes(google_calendar_id=None, google_calendar_api_key='key')
	)
	assert await com_chave._resolver_id_calendario() is None
	assert await com_chave._cabecalhos_autenticacao() == {}

	sem_calendario = ClienteGoogleCalendar(_configuracoes(google_calendar_id=None))
	sem_calendario._token_acesso = 'token'
	sem_calendario._token_expira_em = datetime.now(timezone.utc) + timedelta(minutes=10)

	async def sem_items(*_args, **_kwargs):
		return {'items': [{'id': 'sem-acesso', 'accessRole': 'freeBusyReader'}]}

	monkeypatch.setattr(sem_calendario, '_requisitar_json', sem_items)
	assert await sem_calendario._resolver_id_calendario() is None


def test_google_calendar_monta_urls_corpos_e_credenciais(tmp_path):
	"""Valida helpers de URL, corpo de evento e credenciais."""
	arquivo = tmp_path / 'service-account.json'
	arquivo.write_text('{"client_email":"file@test","private_key":"file-key"}')
	cliente = ClienteGoogleCalendar(
		_configuracoes(
			google_calendar_service_account_json=None,
			google_calendar_service_account_file=str(arquivo),
		)
	)

	url = cliente._url_calendario('cal/endario', 'events', {'key': 'valor teste'})
	corpo_com_hora = cliente._corpo_evento('Reunião', 'Descrição', date(2026, 5, 26), time(10), 45)
	corpo_dia_todo = cliente._corpo_evento('Feriado', None, date(2026, 5, 26), None, 60)

	assert 'cal%2Fendario/events?key=valor+teste' in url
	assert corpo_com_hora['end']['dateTime'].endswith('10:45:00-03:00')
	assert corpo_dia_todo['end'] == {'date': '2026-05-27'}
	assert cliente._info_conta_servico()['client_email'] == 'file@test'
	assert cliente._converter_data_hora_evento({}).tzinfo is not None


@pytest.mark.parametrize(
	'configuracoes',
	[
		_configuracoes(
			google_calendar_service_account_json=None,
			google_calendar_service_account_file='/arquivo/inexistente.json',
		),
		_configuracoes(
			google_calendar_service_account_json=None,
			google_calendar_id=None,
		),
	],
)
def test_google_calendar_falha_ao_carregar_credenciais_invalidas(
	configuracoes: Configuracoes, tmp_path, monkeypatch: pytest.MonkeyPatch
):
	"""Valida erros ao carregar credenciais ausentes."""
	monkeypatch.chdir(tmp_path)
	cliente = ClienteGoogleCalendar(configuracoes)

	with pytest.raises(HTTPException):
		cliente._info_conta_servico()


@pytest.mark.asyncio
async def test_google_calendar_requisitar_json_usa_executor():
	"""Valida ponte assíncrona para requisição JSON síncrona."""
	cliente = ClienteGoogleCalendar(_configuracoes())
	cliente._requisitar_json_sincrono = lambda *_args: {'ok': True}  # type: ignore[method-assign]

	assert await cliente._requisitar_json('GET', 'https://example.test') == {'ok': True}


def test_google_calendar_requisitar_json_sincrono_sucesso(monkeypatch):
	"""Valida requisição síncrona com corpo JSON e corpo vazio."""
	respostas = [b'{"ok": true}', b'']

	class RespostaFake:
		"""Resposta fake compatível com context manager."""

		def __enter__(self):
			"""Função para entrar no contexto."""
			return self

		def __exit__(self, *_args):
			"""Função para sair do contexto."""
			return False

		@staticmethod
		def read():
			"""Função para retornar o próximo corpo configurado."""
			return respostas.pop(0)

	monkeypatch.setattr(google_calendar, 'urlopen', lambda *_args, **_kwargs: RespostaFake())

	assert ClienteGoogleCalendar._requisitar_json_sincrono(
		'GET', 'https://example.test', None, {}
	) == {'ok': True}
	assert (
		ClienteGoogleCalendar._requisitar_json_sincrono('DELETE', 'https://example.test', None, {})
		== {}
	)


@pytest.mark.parametrize(
	('erro', 'status_esperado'),
	[
		(HTTPError('https://example.test', 404, 'not found', {}, BytesIO(b'ausente')), 404),
		(HTTPError('https://example.test', 500, 'erro', {}, BytesIO(b'falhou')), 502),
		(URLError('offline'), 502),
	],
)
def test_google_calendar_requisitar_json_sincrono_trata_erros(
	erro, status_esperado: int, monkeypatch
):
	"""Valida tradução de erros HTTP e de conexão."""

	def falhar(*_args, **_kwargs):
		raise erro

	monkeypatch.setattr(google_calendar, 'urlopen', falhar)

	with pytest.raises(HTTPException) as exc:
		ClienteGoogleCalendar._requisitar_json_sincrono('GET', 'https://example.test', None, {})

	assert exc.value.status_code == status_esperado
