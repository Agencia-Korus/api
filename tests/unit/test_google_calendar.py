from datetime import date, time

from core.enums import EventoTipo
from modules.agenda.model import EventoAgenda
from modules.agenda.service import AgendaService


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

	resposta = AgendaService._evento_local_para_site(evento)

	assert resposta.inicio.isoformat() == '2026-05-24T16:30:00-03:00'
	assert resposta.fim
	assert resposta.fim.isoformat() == '2026-05-24T17:00:00-03:00'