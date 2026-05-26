from datetime import date, datetime, time, timezone
from typing import Any

import pytest
from core.enums import (
	Complexidade,
	ComunicadoAlvo,
	EventoTipo,
	LeadPrioridade,
	PapelUsuario,
	Prioridade,
	SituacaoLead,
	SituacaoProjeto,
	SituacaoTarefa,
)
from fastapi import HTTPException
from modules.agenda.model import EventoAgenda
from modules.comunicados.model import Comunicado
from modules.dashboard.service import ServicoPainel
from modules.gamificacao.model import Conquista, HistoricoXp
from modules.leads.model import Lead
from modules.projetos.model import Projeto
from modules.tarefas.model import Tarefa
from modules.users.model import Cliente, Funcionario, Usuario


class ResultadoPainelCompletoFake:
	"""Resultado fake para helpers do painel."""

	def __init__(
		self,
		valores: list[Any] | None = None,
		linhas: list[Any] | None = None,
		escalar: Any = 0,
	):
		"""Função para inicializar valores de consulta."""
		self.valores = valores or []
		self.linhas = linhas or []
		self.escalar = escalar

	def scalars(self):
		"""Função para retornar interface de escalares."""
		return self

	def all(self):
		"""Função para retornar linhas ou escalares."""
		return self.linhas or self.valores

	def scalar_one(self):
		"""Função para retornar escalar único."""
		return self.escalar


class SessaoPainelCompletaFake:
	"""Sessão fake configurável para o serviço de painel."""

	def __init__(self):
		"""Função para inicializar estado da sessão."""
		self.entidades: dict[tuple[type[Any], int], Any] = {}
		self.resultado = ResultadoPainelCompletoFake()

	async def get(self, modelo: type[Any], entidade_id: int):
		"""Função para obter entidade configurada."""
		return self.entidades.get((modelo, entidade_id))

	async def execute(self, _consulta: Any):
		"""Função para retornar resultado configurado."""
		return self.resultado


def _tarefa() -> Tarefa:
	"""Função para criar tarefa completa usada no painel."""
	return Tarefa(
		id=1,
		projeto_id=1,
		responsavel_id=2,
		titulo='Layout',
		descricao='Criar layout',
		status=SituacaoTarefa.EM_PROGRESSO,
		complexidade=Complexidade.MEDIA,
		prioridade=Prioridade.ALTA,
		categoria='design',
		prazo=date(2026, 6, 1),
		ordem=2,
	)


@pytest.mark.asyncio
async def test_dashboard_helpers_contam_agrupam_e_formatam_listas():
	"""Valida helpers de contagem, séries e listas do dashboard."""
	sessao = SessaoPainelCompletaFake()
	servico = ServicoPainel(sessao)
	agora = datetime(2026, 5, 26, tzinfo=timezone.utc)

	sessao.resultado = ResultadoPainelCompletoFake(escalar=3)
	assert await servico._contar(Lead, Lead.status == SituacaoLead.NOVO) == 3
	assert await servico._xp_do_funcionario(2) == 3

	sessao.resultado = ResultadoPainelCompletoFake(linhas=[(agora, 4)])
	assert await servico._series_por_periodo(
		Lead.data, 'day', Lead.id, Lead.status == SituacaoLead.NOVO
	) == [{'periodo': agora, 'total': 4}]

	lead = Lead(
		id=1,
		nome='Lead',
		email='lead@example.com',
		empresa='Korus',
		status=SituacaoLead.NOVO,
		prioridade=LeadPrioridade.ALTA,
		data=agora,
	)
	sessao.resultado = ResultadoPainelCompletoFake(valores=[lead])
	assert (await servico._leads_recentes())[0]['prioridade'] == 'alta'

	funcionario = Funcionario(id=2, cargo='Dev', xp_total=900, nivel=2)
	usuario = Usuario(
		id=2,
		nome='Bruno',
		email='bruno@example.com',
		senha_hash='hash',
		role=PapelUsuario.FUNCIONARIO,
	)
	sessao.resultado = ResultadoPainelCompletoFake(linhas=[(funcionario, usuario)])
	assert (await servico._ranking())[0]['nome'] == 'Bruno'


@pytest.mark.asyncio
async def test_dashboard_helpers_validam_acessos_permitidos_e_negados():
	"""Valida helpers de permissão do dashboard."""
	sessao = SessaoPainelCompletaFake()
	cliente = Cliente(id=7, razao_social='Cliente', cnpj_cpf='123')
	funcionario = Funcionario(id=8, cargo='Dev')
	projeto = Projeto(id=1, cliente_id=7, nome='Projeto')
	sessao.entidades[(Cliente, 7)] = cliente
	sessao.entidades[(Funcionario, 8)] = funcionario
	servico = ServicoPainel(sessao)

	assert await servico._garantir_acesso_cliente(7, None, None) is cliente
	assert await servico._garantir_acesso_cliente(7, 99, PapelUsuario.ADMIN.value)
	assert await servico._garantir_acesso_cliente(7, 7, PapelUsuario.CLIENTE.value)
	assert await servico._garantir_acesso_funcionario(8, None, None) is funcionario
	assert await servico._garantir_acesso_funcionario(8, 99, PapelUsuario.ADMIN.value)
	assert await servico._garantir_acesso_funcionario(8, 8, PapelUsuario.FUNCIONARIO.value)
	await servico._garantir_acesso_projeto(projeto, None, None)
	await servico._garantir_acesso_projeto(projeto, 99, PapelUsuario.ADMIN.value)
	await servico._garantir_acesso_projeto(projeto, 7, PapelUsuario.CLIENTE.value)

	sessao.resultado = ResultadoPainelCompletoFake(escalar=1)
	await servico._garantir_acesso_projeto(projeto, 8, PapelUsuario.FUNCIONARIO.value)
	sessao.resultado = ResultadoPainelCompletoFake(escalar=0)
	with pytest.raises(HTTPException):
		await servico._garantir_acesso_projeto(projeto, 99, PapelUsuario.FUNCIONARIO.value)


@pytest.mark.asyncio
async def test_dashboard_helpers_formatam_projetos_tarefas_comunicados_e_eventos():
	"""Valida formatação dos blocos de cliente do dashboard."""
	sessao = SessaoPainelCompletaFake()
	servico = ServicoPainel(sessao)
	projeto = Projeto(
		id=1,
		cliente_id=7,
		nome='Projeto',
		status=SituacaoProjeto.EM_ANDAMENTO,
		progresso=50,
		data_fim=date(2026, 6, 30),
	)
	tarefa = _tarefa()
	comunicado = Comunicado(
		id=1,
		autor_id=1,
		titulo='Aviso',
		conteudo='Conteúdo',
		alvo=ComunicadoAlvo.TODOS,
	)
	evento = EventoAgenda(
		id=1,
		usuario_id=7,
		titulo='Reunião',
		tipo=EventoTipo.REUNIAO,
		data=date(2026, 5, 26),
		hora=time(10),
	)

	sessao.resultado = ResultadoPainelCompletoFake(valores=[projeto])
	assert (await servico._projetos_do_cliente(7))[0]['status'] == 'em_andamento'
	sessao.resultado = ResultadoPainelCompletoFake(valores=[tarefa])
	assert (await servico._tarefas_proximas([1]))[0]['titulo'] == 'Layout'
	assert (await servico._tarefas_do_funcionario(2))[0]['ordem'] == 2
	sessao.resultado = ResultadoPainelCompletoFake(valores=[comunicado])
	assert (await servico._comunicados_recentes())[0]['alvo'] == 'todos'
	sessao.resultado = ResultadoPainelCompletoFake(valores=[evento])
	assert (await servico._eventos_do_usuario(7))[0]['tipo'] == 'reuniao'


@pytest.mark.asyncio
async def test_dashboard_helpers_formatam_historico_e_conquistas():
	"""Valida formatação de histórico de XP e conquistas."""
	sessao = SessaoPainelCompletaFake()
	servico = ServicoPainel(sessao)
	agora = datetime(2026, 5, 26, tzinfo=timezone.utc)
	historico = HistoricoXp(
		id=1,
		funcionario_id=2,
		tarefa_id=3,
		acao='Entrega',
		xp=20,
		data=agora,
	)
	conquista = Conquista(
		id=1,
		nome='Primeira entrega',
		icone='star',
		descricao='Conquista inicial',
		xp_bonus=10,
	)

	sessao.resultado = ResultadoPainelCompletoFake(valores=[historico])
	assert (await servico._historico_xp(2))[0]['acao'] == 'Entrega'
	sessao.resultado = ResultadoPainelCompletoFake(linhas=[(conquista, agora)])
	assert (await servico._conquistas_do_funcionario(2))[0]['xp_bonus'] == 10
