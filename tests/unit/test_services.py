from datetime import date, datetime, time, timezone
from decimal import Decimal
from types import SimpleNamespace
from typing import Any

import pytest
from core.enums import (
	Complexidade,
	ComunicadoAlvo,
	ConsentimentoTipo,
	EventoTipo,
	LeadPrioridade,
	PapelUsuario,
	Prioridade,
	SituacaoIntegracao,
	SituacaoLead,
	SituacaoProjeto,
	SituacaoTarefa,
	SituacaoUsuario,
	TipoAcademia,
)
from fastapi import HTTPException
from modules.academy.model import Academia
from modules.academy.schema import AcademiaAtualizar, AcademiaCriar
from modules.academy.service import ServicoAcademia
from modules.agenda.google_calendar import EventoGoogleCalendar
from modules.agenda.model import EventoAgenda, SolicitacaoReuniao
from modules.agenda.schema import (
	EventoAgendaAtualizar,
	EventoAgendaCriar,
	SolicitacaoReuniaoAtualizar,
	SolicitacaoReuniaoCriar,
)
from modules.agenda.service import ServicoAgenda
from modules.comunicados.model import Comunicado, ComunicadoLeitura
from modules.comunicados.schema import ComunicadoAtualizar, ComunicadoCriar
from modules.comunicados.service import ServicoComunicado
from modules.gamificacao.model import (
	Conquista,
	FuncionarioConquista,
	HistoricoXp,
	RegraXp,
)
from modules.gamificacao.schema import (
	ConquistaAtualizar,
	ConquistaCriar,
	HistoricoXpCriar,
	RegraXpAtualizar,
	RegraXpCriar,
)
from modules.gamificacao.service import ServicoGamificacao
from modules.integracoes.model import Integracao
from modules.integracoes.schema import IntegracaoAtualizar, IntegracaoCriar
from modules.integracoes.service import ServicoIntegracao
from modules.leads.model import Lead
from modules.leads.schema import LeadAtualizar, LeadCriar
from modules.leads.service import ServicoLead
from modules.lgpd.model import ConsentimentoLgpd
from modules.lgpd.schema import ConsentimentoLgpdCriar
from modules.lgpd.service import ServicoLgpd
from modules.portfolio.model import Portfolio
from modules.portfolio.schema import PortfolioAtualizar, PortfolioCriar
from modules.portfolio.service import ServicoPortfolio
from modules.projetos.model import Projeto, ProjetoFuncionario
from modules.projetos.schema import ProjetoFuncionarioCriar
from modules.projetos.service import ServicoProjeto
from modules.servicos.model import Entregavel, Servico
from modules.servicos.schema import (
	EntregavelAtualizar,
	EntregavelCriar,
	ServicoCriar,
)
from modules.servicos.service import ServicoServico
from modules.tarefas.model import Anexo, Comentario, Tarefa
from modules.tarefas.schema import (
	AnexoCriar,
	ComentarioCriar,
	TarefaAtualizar,
)
from modules.tarefas.service import ServicoTarefa
from modules.users.model import Funcionario, Usuario
from modules.users.schema import (
	DadosCliente,
	DadosFuncionario,
	UsuarioCriar,
	UsuarioRegistrar,
)
from modules.users.service import ServicoUsuario


class SessaoFake:
	def __init__(self):
		self.commits = 0
		self.refreshes: list[Any] = []
		self.entidades: dict[tuple[type[Any], int], Any] = {}
		self.execute_result = None
		self.flushes = 0

	async def commit(self):
		self.commits += 1

	async def flush(self):
		self.flushes += 1

	async def refresh(self, entidade: Any):
		self.refreshes.append(entidade)

	async def get(self, modelo: type[Any], entidade_id: int):
		return self.entidades.get((modelo, entidade_id))

	async def execute(self, _consulta: Any):
		return ResultadoFake(self.execute_result)


class ResultadoFake:
	def __init__(self, valor: Any):
		self.valor = valor

	def scalar_one_or_none(self):
		return self.valor


class RepositorioFake:  # noqa: PLR0904
	def __init__(self, itens: dict[int, Any] | None = None):
		self.itens = itens or {}
		self.adicionados: list[Any] = []
		self.atualizacoes: list[tuple[int, dict[str, Any]]] = []
		self.delecoes: list[int] = []
		self.filtros_recebidos: list[dict[str, Any]] = []
		self.slug_existente = False
		self.nome_existente = False
		self.email_existente = False

	async def adicionar(self, entidade: Any):
		if getattr(entidade, 'id', None) is None:
			entidade.id = len(self.itens) + len(self.adicionados) + 1
		self.adicionados.append(entidade)
		self.itens[entidade.id] = entidade
		return entidade

	async def obter(self, entidade_id: int):
		return self.itens.get(entidade_id)

	async def listar_todos(self, offset: int = 0, limit: int = 100, filtros=None):
		self.filtros_recebidos.append(
			{'offset': offset, 'limit': limit, 'filtros': filtros}
		)
		return list(self.itens.values())[offset : offset + limit]

	async def atualizar(self, entidade_id: int, dados: dict[str, Any]):
		self.atualizacoes.append((entidade_id, dados))
		entidade = self.itens.get(entidade_id)
		if entidade is None:
			return None
		for campo, valor in dados.items():
			setattr(entidade, campo, valor)
		return entidade

	async def deletar(self, entidade_id: int):
		self.delecoes.append(entidade_id)
		return self.itens.pop(entidade_id, None) is not None

	async def obter_por_slug(self, _slug: str):
		return SimpleNamespace(id=99) if self.slug_existente else None

	async def obter_por_nome(self, _nome: str):
		return SimpleNamespace(id=99) if self.nome_existente else None

	async def obter_por_email(self, _email: str):
		return SimpleNamespace(id=99) if self.email_existente else None

	async def obter_google_calendar(self, integracao_id: int):
		return await self.obter(integracao_id)

	async def listar_google_calendar(self, offset: int, limit: int):
		return await self.listar_todos(offset=offset, limit=limit)

	async def listar_filtrados(self, **filtros: Any):
		self.filtros_recebidos.append(filtros)
		return list(self.itens.values())

	async def listar_por_servico(self, servico_id: int):
		self.filtros_recebidos.append({'servico_id': servico_id})
		return [
			item for item in self.itens.values() if item.servico_id == servico_id
		]

	async def listar_por_projeto(self, projeto_id: int):
		self.filtros_recebidos.append({'projeto_id': projeto_id})
		return [
			item for item in self.itens.values() if item.projeto_id == projeto_id
		]

	async def listar_por_tarefa(self, tarefa_id: int):
		self.filtros_recebidos.append({'tarefa_id': tarefa_id})
		return [
			item for item in self.itens.values() if item.tarefa_id == tarefa_id
		]

	async def listar_por_comunicado(self, comunicado_id: int):
		self.filtros_recebidos.append({'comunicado_id': comunicado_id})
		return [
			item
			for item in self.itens.values()
			if item.comunicado_id == comunicado_id
		]

	async def listar_por_funcionario(self, funcionario_id: int):
		self.filtros_recebidos.append({'funcionario_id': funcionario_id})
		return [
			item
			for item in self.itens.values()
			if item.funcionario_id == funcionario_id
		]

	async def listar_por_usuario(self, usuario_id: int):
		self.filtros_recebidos.append({'usuario_id': usuario_id})
		return [
			item for item in self.itens.values() if item.usuario_id == usuario_id
		]

	async def listar_recebidas(self, destinatario_id: int):
		self.filtros_recebidos.append({'destinatario_id': destinatario_id})
		return [
			item
			for item in self.itens.values()
			if item.destinatario_id == destinatario_id
		]

	async def marcar_lido(self, comunicado_id: int, usuario_id: int):
		leitura = ComunicadoLeitura(
			comunicado_id=comunicado_id,
			usuario_id=usuario_id,
		)
		return await self.adicionar(leitura)

	async def desbloquear(self, funcionario_id: int, conquista_id: int):
		registro = FuncionarioConquista(
			funcionario_id=funcionario_id,
			conquista_id=conquista_id,
		)
		return await self.adicionar(registro)

	async def remover(self, projeto_id: int, funcionario_id: int):
		chave = next(
			(
				item_id
				for item_id, item in self.itens.items()
				if (
					item.projeto_id == projeto_id
					and item.funcionario_id == funcionario_id
				)
			),
			None,
		)
		if chave is None:
			return False
		self.itens.pop(chave)
		return True

	async def contem_membro(self, projeto_id: int, funcionario_id: int):
		return any(
			item.projeto_id == projeto_id and item.funcionario_id == funcionario_id
			for item in self.itens.values()
		)

	async def listar_para_funcionario(self, **filtros: Any):
		self.filtros_recebidos.append(filtros)
		return list(self.itens.values())

	async def listar_visiveis(self, **filtros: Any):
		self.filtros_recebidos.append(filtros)
		return list(self.itens.values())


class CalendarioGoogleFake:
	def __init__(self):
		self.eventos: list[EventoGoogleCalendar] = []
		self.evento_criado = EventoGoogleCalendar(
			id='google-1',
			titulo='Evento Google',
			descricao=None,
			inicio=datetime(2026, 5, 25, 13, 0, tzinfo=timezone.utc),
			fim=datetime(2026, 5, 25, 14, 0, tzinfo=timezone.utc),
			link='https://calendar.test/google-1',
		)
		self.criados: list[dict[str, Any]] = []
		self.atualizados: list[dict[str, Any]] = []
		self.deletados: list[str] = []

	async def criar_evento(self, **dados: Any):
		self.criados.append(dados)
		return self.evento_criado

	async def atualizar_evento(self, **dados: Any):
		self.atualizados.append(dados)
		return self.evento_criado

	async def deletar_evento(self, google_event_id: str):
		self.deletados.append(google_event_id)

	async def listar_eventos(self, data_inicio=None, data_fim=None):
		return [
			evento
			for evento in self.eventos
			if (data_inicio is None or evento.inicio.date() >= data_inicio)
			and (data_fim is None or evento.inicio.date() <= data_fim)
		]


def servico_academia(sessao: SessaoFake):
	servico = ServicoAcademia(sessao)
	servico.repository = RepositorioFake(
		{
			1: Academia(
				id=1,
				titulo='Marketing',
				tipo=TipoAcademia.CURSO,
				preco=Decimal('10.00'),
				url_externa='https://korus.test/marketing',
			)
		}
	)
	return servico


def servico_lead(sessao: SessaoFake):
	servico = ServicoLead(sessao)
	servico.repository = RepositorioFake(
		{1: Lead(id=1, nome='Maria', email='maria@example.com')}
	)
	return servico


def servico_portfolio(sessao: SessaoFake):
	servico = ServicoPortfolio(sessao)
	servico.repository = RepositorioFake({1: Portfolio(id=1, nome='Case')})
	return servico


def servico_agenda(sessao: SessaoFake):
	servico = ServicoAgenda(sessao)
	servico.eventos = RepositorioFake(
		{
			1: EventoAgenda(
				id=1,
				usuario_id=1,
				titulo='Reunião local',
				tipo=EventoTipo.REUNIAO,
				data=date(2026, 5, 25),
				hora=time(9, 0),
				duracao_min=60,
				google_event_id='sincronizado',
			),
			2: EventoAgenda(
				id=2,
				usuario_id=1,
				titulo='Fora do periodo',
				tipo=EventoTipo.TAREFA,
				data=date(2026, 6, 10),
				hora=time(9, 0),
				duracao_min=30,
			),
		}
	)
	servico.solicitacoes = RepositorioFake(
		{
			1: SolicitacaoReuniao(
				id=1,
				remetente_id=2,
				destinatario_id=1,
				titulo='Revisão',
				data=date(2026, 5, 26),
				hora=time(10, 0),
			)
		}
	)
	servico.calendario_google = CalendarioGoogleFake()
	return servico


@pytest.mark.asyncio
@pytest.mark.parametrize(
	('fabrica_servico', 'dados_criacao', 'tipo_modelo'),
	[
		(
			servico_academia,
			AcademiaCriar(
				titulo='Curso',
				tipo=TipoAcademia.CURSO,
				url_externa='https://korus.test/curso',
			),
			Academia,
		),
		(
			servico_lead,
			LeadCriar(nome='Cliente', email='cliente@example.com'),
			Lead,
		),
		(servico_portfolio, PortfolioCriar(nome='Identidade Aurora'), Portfolio),
	],
)
async def test_services_crud_criam_entidade_e_comitam(
	fabrica_servico, dados_criacao, tipo_modelo
):
	"""Valida que services crud criam entidade e comitam."""
	sessao = SessaoFake()
	servico = fabrica_servico(sessao)

	entidade = await servico.criar(dados_criacao)

	assert isinstance(entidade, tipo_modelo)
	assert sessao.commits == 1
	assert servico.repository.adicionados == [entidade]


@pytest.mark.asyncio
@pytest.mark.parametrize(
	('fabrica_servico', 'dados_atualizacao', 'campo', 'valor'),
	[
		(servico_academia, AcademiaAtualizar(titulo='Novo'), 'titulo', 'Novo'),
		(
			servico_lead,
			LeadAtualizar(status=SituacaoLead.QUALIFICADO),
			'status',
			SituacaoLead.QUALIFICADO,
		),
		(servico_portfolio, PortfolioAtualizar(destaque=True), 'destaque', True),
	],
)
async def test_services_crud_atualizam_e_comitam(
	fabrica_servico, dados_atualizacao, campo: str, valor: Any
):
	"""Valida que services crud atualizam e comitam."""
	sessao = SessaoFake()
	servico = fabrica_servico(sessao)

	entidade = await servico.atualizar(1, dados_atualizacao)

	assert getattr(entidade, campo) == valor
	assert sessao.commits == 1
	assert servico.repository.atualizacoes[-1][0] == 1


@pytest.mark.asyncio
@pytest.mark.parametrize(
	('fabrica_servico', 'dados_atualizacao'),
	[
		(servico_academia, AcademiaAtualizar(titulo='Novo')),
		(servico_lead, LeadAtualizar(status=SituacaoLead.PERDIDO)),
		(servico_portfolio, PortfolioAtualizar(destaque=False)),
	],
)
async def test_services_crud_retorna_404_quando_atualizacao_nao_encontra_registro(
	fabrica_servico, dados_atualizacao
):
	"""Valida que services crud retorna 404 quando atualizacao nao encontra registro."""
	sessao = SessaoFake()
	servico = fabrica_servico(sessao)

	with pytest.raises(HTTPException) as exc:
		await servico.atualizar(404, dados_atualizacao)

	assert exc.value.status_code == 404
	assert sessao.commits == 0


@pytest.mark.asyncio
@pytest.mark.parametrize(
	'fabrica_servico', [servico_academia, servico_lead, servico_portfolio]
)
async def test_services_crud_deletam_e_comitam(fabrica_servico):
	"""Valida que services crud deletam e comitam."""
	sessao = SessaoFake()
	servico = fabrica_servico(sessao)

	await servico.deletar(1)

	assert sessao.commits == 1
	assert servico.repository.delecoes == [1]


@pytest.mark.asyncio
@pytest.mark.parametrize(
	'fabrica_servico', [servico_academia, servico_lead, servico_portfolio]
)
async def test_services_crud_retorna_404_quando_delecao_nao_encontra_registro(
	fabrica_servico,
):
	"""Valida que services crud retorna 404 quando delecao nao encontra registro."""
	sessao = SessaoFake()
	servico = fabrica_servico(sessao)

	with pytest.raises(HTTPException) as exc:
		await servico.deletar(404)

	assert exc.value.status_code == 404
	assert sessao.commits == 0


@pytest.mark.asyncio
async def test_servico_academia_lista_com_filtros():
	"""Valida que servico academia lista com filtros."""
	sessao = SessaoFake()
	servico = servico_academia(sessao)

	await servico.listar_filtrados(
		offset=2, limit=10, tipo=TipoAcademia.CURSO, publicado=True
	)

	assert servico.repository.filtros_recebidos[-1] == {
		'offset': 2,
		'limit': 10,
		'filtros': {'tipo': TipoAcademia.CURSO, 'publicado': True},
	}


@pytest.mark.asyncio
async def test_servico_agenda_cria_evento_e_sincroniza_google_calendar():
	"""Valida que servico agenda cria evento e sincroniza google calendar."""
	sessao = SessaoFake()
	servico = servico_agenda(sessao)

	evento = await servico.criar_evento(
		EventoAgendaCriar(
			usuario_id=1,
			titulo='Kickoff',
			tipo=EventoTipo.REUNIAO,
			data=date(2026, 5, 25),
			hora=time(11, 0),
			duracao_min=45,
		)
	)

	assert evento.google_event_id == 'google-1'
	assert evento.google_link == 'https://calendar.test/google-1'
	assert servico.calendario_google.criados[0]['titulo'] == 'Kickoff'
	assert sessao.flushes == 1
	assert sessao.commits == 1


@pytest.mark.asyncio
async def test_servico_agenda_lista_site_filtra_ordena_e_remove_google_duplicado():
	"""Valida que servico agenda lista site filtra ordena e remove google duplicado."""
	sessao = SessaoFake()
	servico = servico_agenda(sessao)
	servico.calendario_google.eventos = [
		EventoGoogleCalendar(
			id='sincronizado',
			titulo='Duplicado',
			descricao=None,
			inicio=datetime(2026, 5, 25, 8, 0, tzinfo=timezone.utc),
			fim=None,
			link=None,
		),
		EventoGoogleCalendar(
			id='externo',
			titulo='Google externo',
			descricao='Descrição',
			inicio=datetime(2026, 5, 25, 7, 0, tzinfo=timezone.utc),
			fim=datetime(2026, 5, 25, 8, 0, tzinfo=timezone.utc),
			link='https://calendar.test/externo',
		),
	]

	eventos = await servico.listar_eventos_site(
		usuario_id=1,
		data_inicio=date(2026, 5, 25),
		data_fim=date(2026, 5, 25),
	)

	assert [evento.id for evento in eventos] == [
		'google_calendar:externo',
		'local:1',
	]
	assert eventos[0].duracao_min == 60
	assert eventos[1].google_event_id == 'sincronizado'


@pytest.mark.asyncio
async def test_servico_agenda_atualiza_evento_sincronizado_e_deleta_no_google():
	"""Valida que servico agenda atualiza evento sincronizado e deleta no google."""
	sessao = SessaoFake()
	servico = servico_agenda(sessao)

	evento = await servico.atualizar_evento(
		1,
		EventoAgendaAtualizar(titulo='Kickoff atualizado'),
	)
	await servico.deletar_evento(1)

	assert evento.titulo == 'Kickoff atualizado'
	assert (
		servico.calendario_google.atualizados[0]['id_evento_google']
		== 'sincronizado'
	)
	assert servico.calendario_google.deletados == ['google-1']
	assert sessao.flushes == 1
	assert sessao.commits == 2


@pytest.mark.asyncio
async def test_servico_agenda_gerencia_solicitacoes():
	"""Valida que servico agenda gerencia solicitacoes."""
	sessao = SessaoFake()
	servico = servico_agenda(sessao)

	solicitacao = await servico.criar_solicitacao(
		SolicitacaoReuniaoCriar(
			remetente_id=2,
			destinatario_id=1,
			titulo='Reunião',
			data=date(2026, 5, 27),
			hora=time(14, 0),
		)
	)
	recebidas = await servico.listar_solicitacoes_recebidas(1)
	atualizada = await servico.atualizar_solicitacao(
		1, SolicitacaoReuniaoAtualizar(titulo='Reunião remarcada')
	)
	await servico.deletar_solicitacao(1)

	assert solicitacao.destinatario_id == 1
	assert {item.destinatario_id for item in recebidas} == {1}
	assert atualizada.titulo == 'Reunião remarcada'
	assert sessao.commits == 3


@pytest.mark.asyncio
async def test_servico_lead_repassa_filtros_para_repositorio():
	"""Valida que servico lead repassa filtros para repositorio."""
	sessao = SessaoFake()
	servico = servico_lead(sessao)

	await servico.listar_filtrados(
		offset=1,
		limit=5,
		status=SituacaoLead.NOVO,
		prioridade=LeadPrioridade.ALTA,
		servico_id=3,
		busca='maria',
	)

	assert servico.repository.filtros_recebidos[-1] == {
		'offset': 1,
		'limit': 5,
		'status': SituacaoLead.NOVO,
		'prioridade': LeadPrioridade.ALTA,
		'servico_id': 3,
		'busca': 'maria',
	}


@pytest.mark.asyncio
async def test_servico_servico_rejeita_slug_duplicado():
	"""Valida que servico servico rejeita slug duplicado."""
	sessao = SessaoFake()
	servico = ServicoServico(sessao)
	servico.repository = RepositorioFake()
	servico.repository.slug_existente = True
	servico.entregaveis = RepositorioFake()

	with pytest.raises(HTTPException) as exc:
		await servico.criar(ServicoCriar(nome='Site', slug='site'))

	assert exc.value.status_code == 409
	assert sessao.commits == 0


@pytest.mark.asyncio
async def test_servico_servico_gerencia_entregaveis():
	"""Valida que servico servico gerencia entregaveis."""
	sessao = SessaoFake()
	servico = ServicoServico(sessao)
	servico.repository = RepositorioFake({1: Servico(id=1, nome='Site', slug='site')})
	servico.entregaveis = RepositorioFake(
		{1: Entregavel(id=1, servico_id=1, descricao='Wireframe', ordem=1)}
	)

	criado = await servico.criar_entregavel(
		EntregavelCriar(servico_id=1, descricao='Layout', ordem=2)
	)
	listados = await servico.listar_entregaveis(1)
	atualizado = await servico.atualizar_entregavel(
		1, EntregavelAtualizar(descricao='Wireframe revisado')
	)
	await servico.deletar_entregavel(1)

	assert criado.servico_id == 1
	assert listados[0].servico_id == 1
	assert atualizado.descricao == 'Wireframe revisado'
	assert sessao.commits == 3


@pytest.mark.asyncio
async def test_servico_integracao_cria_atualiza_e_deleta_google_calendar():
	"""Valida que servico integracao cria atualiza e deleta google calendar."""
	sessao = SessaoFake()
	servico = ServicoIntegracao(sessao)
	servico.repository = RepositorioFake(
		{
			1: Integracao(
				id=1,
				nome='google_calendar',
				status=SituacaoIntegracao.DESCONECTADO,
			)
		}
	)

	criado = await servico.criar(IntegracaoCriar(status=SituacaoIntegracao.CONECTADO))
	atualizado = await servico.atualizar(
		1, IntegracaoAtualizar(status=SituacaoIntegracao.CONECTADO)
	)
	await servico.deletar(1)

	assert criado.nome == 'google_calendar'
	assert atualizado.status == SituacaoIntegracao.CONECTADO
	assert sessao.commits == 3


@pytest.mark.asyncio
async def test_servico_integracao_rejeita_google_calendar_duplicado():
	"""Valida que servico integracao rejeita google calendar duplicado."""
	sessao = SessaoFake()
	servico = ServicoIntegracao(sessao)
	servico.repository = RepositorioFake()
	servico.repository.nome_existente = True

	with pytest.raises(HTTPException) as exc:
		await servico.criar(IntegracaoCriar())

	assert exc.value.status_code == 409


@pytest.mark.asyncio
async def test_servico_comunicado_marca_e_lista_leituras():
	"""Valida que servico comunicado marca e lista leituras."""
	sessao = SessaoFake()
	servico = ServicoComunicado(sessao)
	servico.repository = RepositorioFake(
		{
			1: Comunicado(
				id=1,
				autor_id=1,
				titulo='Aviso',
				conteudo='Conteudo',
				alvo=ComunicadoAlvo.TODOS,
			)
		}
	)
	servico.leituras = RepositorioFake()

	criado = await servico.criar(
		ComunicadoCriar(autor_id=1, titulo='Novo', conteudo='Texto')
	)
	atualizado = await servico.atualizar(
		1, ComunicadoAtualizar(alvo=ComunicadoAlvo.CLIENTES)
	)
	leitura = await servico.marcar_lido(1, usuario_id=7)
	leituras = await servico.listar_leituras(1)

	assert criado.autor_id == 1
	assert atualizado.alvo == ComunicadoAlvo.CLIENTES
	assert leitura.usuario_id == 7
	assert leituras == [leitura]
	assert sessao.commits == 3


@pytest.mark.asyncio
async def test_servico_lgpd_registra_e_lista_consentimentos():
	"""Valida que servico lgpd registra e lista consentimentos."""
	sessao = SessaoFake()
	servico = ServicoLgpd(sessao)
	servico.repository = RepositorioFake()

	consentimento = await servico.registrar(
		ConsentimentoLgpdCriar(
			usuario_id=1,
			tipo=ConsentimentoTipo.ESSENCIAL,
			aceito=True,
		)
	)
	listados = await servico.listar(offset=0, limit=10)

	assert isinstance(consentimento, ConsentimentoLgpd)
	assert listados == [consentimento]
	assert sessao.commits == 1


@pytest.mark.asyncio
async def test_servico_gamificacao_atualiza_xp_e_nivel_do_funcionario():
	"""Valida que servico gamificacao atualiza xp e nivel do funcionario."""
	sessao = SessaoFake()
	funcionario = Funcionario(id=2, cargo='Dev', xp_total=450, nivel=1)
	sessao.entidades[(Funcionario, 2)] = funcionario
	servico = ServicoGamificacao(sessao)
	servico.historicos = RepositorioFake()

	historico = await servico.registrar_xp(
		HistoricoXpCriar(funcionario_id=2, acao='Entrega', xp=100)
	)

	assert isinstance(historico, HistoricoXp)
	assert funcionario.xp_total == 550
	assert funcionario.nivel == 2
	assert sessao.commits == 1


@pytest.mark.asyncio
async def test_servico_gamificacao_retorna_404_quando_funcionario_nao_existe():
	"""Valida que servico gamificacao retorna 404 quando funcionario nao existe."""
	sessao = SessaoFake()
	servico = ServicoGamificacao(sessao)
	servico.historicos = RepositorioFake()

	with pytest.raises(HTTPException) as exc:
		await servico.registrar_xp(
			HistoricoXpCriar(funcionario_id=404, acao='Entrega', xp=10)
		)

	assert exc.value.status_code == 404
	assert sessao.commits == 0


@pytest.mark.asyncio
async def test_servico_gamificacao_crud_regras_conquistas_e_desbloqueio():
	"""Valida que servico gamificacao crud regras conquistas e desbloqueio."""
	sessao = SessaoFake()
	servico = ServicoGamificacao(sessao)
	servico.regras = RepositorioFake(
		{1: RegraXp(id=1, tarefa='Entrega', complexidade=Complexidade.MEDIA, xp=50)}
	)
	servico.conquistas = RepositorioFake(
		{1: Conquista(id=1, nome='Primeira entrega', xp_bonus=100)}
	)
	servico.fc = RepositorioFake()

	regra = await servico.criar_regra(
		RegraXpCriar(tarefa='Review', complexidade=Complexidade.BAIXA, xp=5)
	)
	regra_atualizada = await servico.atualizar_regra(1, RegraXpAtualizar(xp=80))
	conquista = await servico.criar_conquista(ConquistaCriar(nome='Bravo'))
	conquista_atualizada = await servico.atualizar_conquista(
		1, ConquistaAtualizar(xp_bonus=150)
	)
	desbloqueio = await servico.desbloquear_conquista(2, 1)

	assert regra.tarefa == 'Review'
	assert regra_atualizada.xp == 80
	assert conquista.nome == 'Bravo'
	assert conquista_atualizada.xp_bonus == 150
	assert desbloqueio.funcionario_id == 2
	assert sessao.commits == 5


@pytest.mark.asyncio
async def test_servico_projeto_aplica_permissoes_de_visibilidade():
	"""Valida que servico projeto aplica permissoes de visibilidade."""
	sessao = SessaoFake()
	projeto = Projeto(
		id=1,
		cliente_id=10,
		nome='Site',
		status=SituacaoProjeto.PLANEJAMENTO,
		progresso=0,
	)
	servico = ServicoProjeto(sessao)
	servico.repository = RepositorioFake({1: projeto})
	servico.equipe = RepositorioFake(
		{
			1: ProjetoFuncionario(
				projeto_id=1,
				funcionario_id=20,
				papel='Designer',
			)
		}
	)

	assert await servico.obter_visivel(1, 99, PapelUsuario.ADMIN.value) is projeto
	assert await servico.obter_visivel(1, 10, PapelUsuario.CLIENTE.value) is projeto
	assert await servico.obter_visivel(1, 20, PapelUsuario.FUNCIONARIO.value) is projeto
	with pytest.raises(HTTPException) as exc:
		await servico.obter_visivel(1, 30, PapelUsuario.FUNCIONARIO.value)

	assert exc.value.status_code == 403


@pytest.mark.asyncio
async def test_servico_projeto_gerencia_equipe():
	"""Valida que servico projeto gerencia equipe."""
	sessao = SessaoFake()
	servico = ServicoProjeto(sessao)
	servico.repository = RepositorioFake(
		{
			1: Projeto(
				id=1,
				cliente_id=10,
				nome='Site',
				status=SituacaoProjeto.PLANEJAMENTO,
				progresso=0,
			)
		}
	)
	servico.equipe = RepositorioFake(
		{1: ProjetoFuncionario(projeto_id=1, funcionario_id=7, papel='Dev')}
	)

	membro = await servico.adicionar_membro(
		1, ProjetoFuncionarioCriar(funcionario_id=8, papel='Design')
	)
	equipe = await servico.listar_equipe(1)
	await servico.remover_membro(1, 7)

	assert membro.funcionario_id == 8
	assert {item.funcionario_id for item in equipe} == {7, 8}
	assert sessao.commits == 2


@pytest.mark.asyncio
async def test_servico_tarefa_conclui_com_data_e_gerencia_comentarios_anexos():
	"""Valida que servico tarefa conclui com data e gerencia comentarios anexos."""
	sessao = SessaoFake()
	servico = ServicoTarefa(sessao)
	servico.repository = RepositorioFake(
		{
			1: Tarefa(
				id=1,
				projeto_id=1,
				titulo='Layout',
				status=SituacaoTarefa.A_FAZER,
				complexidade=Complexidade.MEDIA,
				prioridade=Prioridade.MEDIA,
			)
		}
	)
	servico.comentarios = RepositorioFake()
	servico.anexos = RepositorioFake()

	tarefa = await servico.atualizar(
		1, TarefaAtualizar(status=SituacaoTarefa.CONCLUIDO)
	)
	comentario = await servico.adicionar_comentario(
		ComentarioCriar(tarefa_id=1, conteudo='feito'), autor_id=2
	)
	comentarios = await servico.listar_comentarios(1)
	anexo = await servico.adicionar_anexo(
		AnexoCriar(tarefa_id=1, nome='arquivo.pdf', url='https://arquivo.test/pdf')
	)
	anexos = await servico.listar_anexos(1)

	assert tarefa.concluido_em is not None
	assert isinstance(comentario, Comentario)
	assert comentarios == [comentario]
	assert isinstance(anexo, Anexo)
	assert anexos == [anexo]
	assert sessao.commits == 3


@pytest.mark.asyncio
async def test_servico_tarefa_aplica_permissoes_de_acesso_e_gerenciamento():
	"""Valida que servico tarefa aplica permissoes de acesso e gerenciamento."""
	sessao = SessaoFake()
	tarefa = Tarefa(
		id=1,
		projeto_id=1,
		responsavel_id=20,
		titulo='Layout',
		status=SituacaoTarefa.A_FAZER,
		complexidade=Complexidade.MEDIA,
		prioridade=Prioridade.MEDIA,
	)
	sessao.entidades[(Projeto, 1)] = Projeto(
		id=1,
		cliente_id=10,
		nome='Site',
		status=SituacaoProjeto.PLANEJAMENTO,
		progresso=0,
	)
	servico = ServicoTarefa(sessao)
	servico.repository = RepositorioFake({1: tarefa})

	assert await servico.obter_visivel(1, 99, PapelUsuario.ADMIN.value) is tarefa
	assert await servico.obter_visivel(1, 10, PapelUsuario.CLIENTE.value) is tarefa
	assert (
		await servico.garantir_permissao_gerenciar_tarefa(
			1, 20, PapelUsuario.FUNCIONARIO.value
		)
		is tarefa
	)
	with pytest.raises(HTTPException) as exc:
		await servico.garantir_permissao_gerenciar_tarefa(
			1, 30, PapelUsuario.CLIENTE.value
		)

	assert exc.value.status_code == 403


@pytest.mark.asyncio
async def test_servico_usuario_cria_perfis_e_aprova_cadastro():
	"""Valida que servico usuario cria perfis e aprova cadastro."""
	sessao = SessaoFake()
	servico = ServicoUsuario(sessao)
	servico.usuarios = RepositorioFake(
		{
			1: Usuario(
				id=1,
				nome='Ana',
				email='ana@example.com',
				senha_hash='x',
				role=PapelUsuario.CLIENTE,
				status=SituacaoUsuario.PENDENTE,
			)
		}
	)
	servico.clientes = RepositorioFake()
	servico.funcionarios = RepositorioFake()
	servico.admins = RepositorioFake()

	usuario = await servico.criar(
		UsuarioCriar(
			nome='Cliente',
			email='cliente@example.com',
			senha='senha-segura',
			role=PapelUsuario.CLIENTE,
			cliente=DadosCliente(razao_social='Cliente LTDA', cnpj_cpf='123'),
		)
	)
	funcionario = await servico.criar(
		UsuarioCriar(
			nome='Func',
			email='func@example.com',
			senha='senha-segura',
			role=PapelUsuario.FUNCIONARIO,
			funcionario=DadosFuncionario(cargo='Dev'),
		)
	)
	aprovado = await servico.aprovar(1)

	assert usuario.role == PapelUsuario.CLIENTE
	assert funcionario.role == PapelUsuario.FUNCIONARIO
	assert servico.clientes.adicionados[0].id == usuario.id
	assert servico.funcionarios.adicionados[0].id == funcionario.id
	assert aprovado.status == SituacaoUsuario.ATIVO
	assert sessao.commits == 3
	assert sessao.refreshes == [usuario, funcionario]


@pytest.mark.asyncio
async def test_servico_usuario_rejeita_email_duplicado_e_autocadastro_admin():
	"""Valida que servico usuario rejeita email duplicado e autocadastro admin."""
	sessao = SessaoFake()
	servico = ServicoUsuario(sessao)
	servico.usuarios = RepositorioFake()
	servico.usuarios.email_existente = True

	with pytest.raises(HTTPException) as conflito:
		await servico.criar(
			UsuarioCriar(
				nome='Duplicado',
				email='duplicado@example.com',
				senha='senha-segura',
				role=PapelUsuario.CLIENTE,
			)
		)

	servico.usuarios.email_existente = False
	with pytest.raises(HTTPException) as invalido:
		await servico.registrar(
			UsuarioRegistrar(
				nome='Admin',
				email='admin@example.com',
				senha='senha-segura',
				role=PapelUsuario.ADMIN,
			)
		)

	assert conflito.value.status_code == 409
	assert invalido.value.status_code == 400
