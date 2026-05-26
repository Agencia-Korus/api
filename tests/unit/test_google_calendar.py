from datetime import date, time
from pathlib import Path

import pytest
from core.config import Configuracoes
from core.enums import EventoTipo
from modules.agenda.google_calendar import ClienteGoogleCalendar
from modules.agenda.model import EventoAgenda
from modules.agenda.service import ServicoAgenda


def test_caminho_conta_servico_prioriza_arquivo_local(tmp_path: Path):
	arquivo_local = tmp_path / 'conta-servico.json'
	arquivo_local.write_text('{"client_email":"x","private_key":"y"}', encoding='utf-8')
	arquivo_docker = tmp_path / 'docker.json'

	configuracoes = Configuracoes(
		google_calendar_service_account_host_file=str(arquivo_local),
		google_calendar_service_account_file=str(arquivo_docker),
	)

	assert configuracoes.caminho_conta_servico_google() == arquivo_local.resolve()


def test_criar_evento_ignora_google_quando_arquivo_credencial_nao_existe():
	cliente = ClienteGoogleCalendar(
		Configuracoes(
			google_calendar_enabled=True,
			google_calendar_service_account_file='/caminho/inexistente.json',
		)
	)

	assert cliente._pode_escrever_eventos() is False
	assert cliente.esta_configurado() is False


@pytest.mark.asyncio
async def test_criar_evento_retorna_none_sem_credenciais_validas():
	cliente = ClienteGoogleCalendar(
		Configuracoes(
			google_calendar_enabled=True,
			google_calendar_service_account_file='/caminho/inexistente.json',
		)
	)

	evento = await cliente.criar_evento(
		titulo='Reunião',
		descricao=None,
		data=date(2026, 5, 24),
		hora=time(10, 0),
		duracao_min=30,
	)

	assert evento is None


def test_evento_local_para_site_usa_fuso_horario_configurado():
	evento = EventoAgenda(
		id=1,
		usuario_id=1,
		titulo='Evento local',
		descricao=None,
		tipo=EventoTipo.REUNIAO,
		data=date(2026, 5, 24),
		hora=time(16, 30),
		duracao_min=30,
	)

	resposta = ServicoAgenda._evento_local_para_site(evento)

	assert resposta.inicio.isoformat() == '2026-05-24T16:30:00-03:00'
	assert resposta.fim
	assert resposta.fim.isoformat() == '2026-05-24T17:00:00-03:00'
