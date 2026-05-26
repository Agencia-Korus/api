from typing import Any

import pytest
from core.enums import (
	LeadPrioridade,
	PapelUsuario,
	SituacaoLead,
	SituacaoProjeto,
	SituacaoTarefa,
	SituacaoUsuario,
)
from modules.agenda.model import EventoAgenda, SolicitacaoReuniao
from modules.agenda.repository import (
	RepositorioEventoAgenda,
	RepositorioSolicitacaoReuniao,
)
from modules.comunicados.model import ComunicadoLeitura
from modules.comunicados.repository import RepositorioComunicadoLeitura
from modules.gamificacao.model import FuncionarioConquista, HistoricoXp
from modules.gamificacao.repository import (
	RepositorioFuncionarioConquista,
	RepositorioHistoricoXp,
)
from modules.integracoes.model import Integracao
from modules.integracoes.repository import RepositorioIntegracao
from modules.leads.model import Lead
from modules.leads.repository import RepositorioLead
from modules.portfolio.model import Portfolio
from modules.portfolio.repository import RepositorioPortfolio
from modules.projetos.model import Projeto, ProjetoFuncionario
from modules.projetos.repository import (
	RepositorioProjeto,
	RepositorioProjetoFuncionario,
)
from modules.tarefas.model import Anexo, Comentario, Tarefa
from modules.tarefas.repository import (
	RepositorioAnexo,
	RepositorioComentario,
	RepositorioTarefa,
)
from modules.users.model import Cliente, Usuario
from modules.users.repository import RepositorioCliente, RepositorioUsuario


class ResultadoRepositorioFake:
	"""Resultado fake para consultas SQLAlchemy usadas pelos repositories."""

	def __init__(self, valores: list[Any] | None = None, escalar: Any = None):
		"""Função para inicializar valores escalares e listas."""
		self.valores = valores or []
		self.escalar = escalar
		self.rowcount = 1

	def scalars(self):
		"""Função para retornar interface de escalares."""
		return self

	def all(self):
		"""Função para retornar todos os valores."""
		return self.valores

	def scalar_one_or_none(self):
		"""Função para retornar escalar opcional."""
		return self.escalar

	def scalar_one(self):
		"""Função para retornar escalar obrigatório."""
		return self.escalar


class SessaoRepositorioFake:
	"""Sessão fake que registra operações dos repositories."""

	def __init__(self, resultado: ResultadoRepositorioFake):
		"""Função para inicializar o resultado padrão."""
		self.resultado = resultado
		self.consultas: list[Any] = []
		self.adicionados: list[Any] = []
		self.flushes = 0
		self.refreshes: list[Any] = []

	def add(self, entidade: Any) -> None:
		"""Função para registrar entidade adicionada."""
		self.adicionados.append(entidade)

	async def execute(self, consulta: Any):
		"""Função para registrar consulta executada."""
		self.consultas.append(consulta)
		return self.resultado

	async def flush(self) -> None:
		"""Função para registrar flush."""
		self.flushes += 1

	async def refresh(self, entidade: Any) -> None:
		"""Função para registrar refresh."""
		self.refreshes.append(entidade)


@pytest.mark.asyncio
async def test_repositories_de_agenda_listam_por_usuario_e_destinatario():
	"""Valida filtros específicos dos repositories de agenda."""
	resultado = ResultadoRepositorioFake([EventoAgenda(id=1), SolicitacaoReuniao(id=2)])
	sessao = SessaoRepositorioFake(resultado)

	eventos = await RepositorioEventoAgenda(sessao).listar_por_usuario(7)
	solicitacoes = await RepositorioSolicitacaoReuniao(sessao).listar_recebidas(8)

	assert eventos[0].id == 1
	assert solicitacoes[1].id == 2
	assert len(sessao.consultas) == 2


@pytest.mark.asyncio
async def test_repositories_de_comunicados_marcam_e_listam_leituras():
	"""Valida gravação idempotente e listagem de leituras."""
	leitura = ComunicadoLeitura(comunicado_id=1, usuario_id=7)
	sessao = SessaoRepositorioFake(ResultadoRepositorioFake([leitura], leitura))
	repositorio = RepositorioComunicadoLeitura(sessao)

	assert await repositorio.marcar_lido(1, 7) is leitura
	assert await repositorio.listar_por_comunicado(1) == [leitura]
	assert sessao.flushes == 1


@pytest.mark.asyncio
async def test_repositories_de_gamificacao_listam_e_desbloqueiam():
	"""Valida repositories específicos de gamificação."""
	historico = HistoricoXp(id=1, funcionario_id=7, acao='entrega', xp=10)
	conquista = FuncionarioConquista(funcionario_id=7, conquista_id=2)
	sessao_historico = SessaoRepositorioFake(ResultadoRepositorioFake([historico]))
	sessao_conquista = SessaoRepositorioFake(ResultadoRepositorioFake([conquista], conquista))

	assert await RepositorioHistoricoXp(sessao_historico).listar_por_funcionario(7) == [historico]
	repositorio = RepositorioFuncionarioConquista(sessao_conquista)
	assert await repositorio.desbloquear(7, 2) is conquista
	assert await repositorio.listar_por_funcionario(7) == [conquista]


@pytest.mark.asyncio
async def test_repository_integracao_busca_google_calendar():
	"""Valida consultas específicas da integração Google Calendar."""
	integracao = Integracao(id=1, nome='google_calendar')
	sessao = SessaoRepositorioFake(ResultadoRepositorioFake([integracao], integracao))
	repositorio = RepositorioIntegracao(sessao)

	assert await repositorio.obter_por_nome('google_calendar') is integracao
	assert await repositorio.obter_google_calendar(1) is integracao
	assert await repositorio.listar_google_calendar(0, 10) == [integracao]


@pytest.mark.asyncio
async def test_repositories_filtrados_de_leads_portfolio_usuarios_e_tarefas():
	"""Valida repositories com filtros opcionais combinados."""
	resultado = ResultadoRepositorioFake([
		Lead(id=1, nome='Lead', email='lead@example.com'),
		Portfolio(id=1, nome='Case', destaque=True, categoria='Branding'),
		Usuario(id=1, nome='Ana', email='ana@example.com'),
		Tarefa(id=1, projeto_id=1, titulo='Layout'),
	])
	sessao = SessaoRepositorioFake(resultado)

	assert await RepositorioLead(sessao).listar_filtrados(
		0,
		10,
		status=SituacaoLead.NOVO,
		prioridade=LeadPrioridade.ALTA,
		servico_id=1,
		busca='Ana',
	)
	assert await RepositorioPortfolio(sessao).listar_destaques()
	assert await RepositorioPortfolio(sessao).listar_filtrados(
		0, 10, categoria='Branding', destaques=True
	)
	assert await RepositorioUsuario(sessao).obter_por_email('ana@example.com') is None
	assert await RepositorioUsuario(sessao).listar_filtrados(
		0,
		10,
		papel=PapelUsuario.CLIENTE,
		status=SituacaoUsuario.ATIVO,
		busca='Ana',
	)
	assert await RepositorioTarefa(sessao).listar_por_projeto(1)
	assert await RepositorioTarefa(sessao).listar_filtrados(
		0,
		10,
		projeto_id=1,
		responsavel_id=2,
		status=SituacaoTarefa.EM_PROGRESSO,
	)
	assert await RepositorioTarefa(sessao).listar_visiveis(
		7,
		PapelUsuario.CLIENTE.value,
		0,
		10,
		projeto_id=1,
		responsavel_id=2,
		status=SituacaoTarefa.EM_PROGRESSO,
	)
	assert await RepositorioTarefa(sessao).listar_visiveis(
		7,
		PapelUsuario.FUNCIONARIO.value,
		0,
		10,
		projeto_id=1,
		responsavel_id=2,
		status=SituacaoTarefa.EM_PROGRESSO,
	)


@pytest.mark.asyncio
async def test_repositories_de_projetos_e_vinculos_executam_operacoes():
	"""Valida repositories de projetos e vínculos de equipe."""
	projeto = Projeto(id=1, cliente_id=7, nome='Projeto')
	membro = ProjetoFuncionario(projeto_id=1, funcionario_id=2)
	resultado = ResultadoRepositorioFake([projeto, membro], membro)
	sessao = SessaoRepositorioFake(resultado)

	assert await RepositorioProjeto(sessao).listar_para_funcionario(
		2, 0, 10, SituacaoProjeto.EM_ANDAMENTO
	)
	repositorio = RepositorioProjetoFuncionario(sessao)
	assert await repositorio.adicionar(membro) is membro
	assert await repositorio.listar_por_projeto(1)
	assert await repositorio.contem_membro(1, 2) is True
	assert await repositorio.remover(1, 2) is True
	assert sessao.adicionados == [membro]
	assert sessao.refreshes == [membro]


@pytest.mark.asyncio
async def test_repositories_de_tarefas_listam_comentarios_anexos_e_documentos():
	"""Valida repositories auxiliares de tarefas e clientes."""
	comentario = Comentario(id=1, tarefa_id=1, autor_id=7, conteudo='ok')
	anexo = Anexo(id=1, tarefa_id=1, nome='arquivo', url='https://example.test')
	cliente = Cliente(id=7, razao_social='Cliente', cnpj_cpf='123')
	sessao = SessaoRepositorioFake(ResultadoRepositorioFake([comentario, anexo], cliente))

	assert await RepositorioComentario(sessao).listar_por_tarefa(1) == [
		comentario,
		anexo,
	]
	assert await RepositorioAnexo(sessao).listar_por_tarefa(1) == [comentario, anexo]
	assert await RepositorioCliente(sessao).obter_por_documento('123') is cliente
