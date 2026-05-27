from datetime import date, datetime, timezone
from types import SimpleNamespace
from typing import Any

import pytest
from core.enums import LeadPrioridade, PapelUsuario, SituacaoLead
from core.security import criar_token_acesso
from fastapi import HTTPException
from fastapi.security import HTTPAuthorizationCredentials
from modules.academy import controller as academy_controller
from modules.agenda import controller as agenda_controller
from modules.comunicados import controller as comunicados_controller
from modules.dashboard import controller as dashboard_controller
from modules.gamificacao import controller as gamificacao_controller
from modules.integracoes import controller as integracoes_controller
from modules.leads import controller as leads_controller
from modules.lgpd import controller as lgpd_controller
from modules.portfolio import controller as portfolio_controller
from modules.projetos import controller as projetos_controller
from modules.servicos import controller as servicos_controller
from modules.tarefas import controller as tarefas_controller
from modules.users import controller as users_controller


class ServicoControllerFake:
	"""Serviço assíncrono fake que registra chamadas dos controllers."""

	def __init__(self, resposta: Any = None):
		"""Função para inicializar a resposta padrão do fake."""
		self.chamadas: list[tuple[str, tuple[Any, ...], dict[str, Any]]] = []
		self.resposta = resposta if resposta is not None else {'ok': True}

	def __getattr__(self, nome: str):
		"""Função para criar métodos assíncronos sob demanda."""

		async def metodo(*args: Any, **kwargs: Any) -> Any:
			self.chamadas.append((nome, args, kwargs))
			return self.resposta

		return metodo


class PayloadComCopia:
	"""Payload fake compatível com objetos Pydantic usados pelos controllers."""

	def __init__(self, **dados: Any):
		"""Função para armazenar os dados do payload."""
		self.dados = dados

	def model_copy(self, update: dict[str, Any]):
		"""Função para simular cópia de modelo com atualizações."""
		return PayloadComCopia(**{**self.dados, **update})


def _pagina(offset: int = 2, limit: int = 5) -> SimpleNamespace:
	"""Função para criar objeto de paginação usado pelos controllers."""
	return SimpleNamespace(offset=offset, limit=limit)


def _usuario(papel: str = PapelUsuario.ADMIN.value) -> SimpleNamespace:
	"""Função para criar usuário autenticado fake."""
	return SimpleNamespace(id=7, papel=papel)


@pytest.mark.parametrize(
	('modulo', 'nome_classe'),
	[
		(academy_controller, 'ServicoAcademia'),
		(agenda_controller, 'ServicoAgenda'),
		(comunicados_controller, 'ServicoComunicado'),
		(dashboard_controller, 'ServicoPainel'),
		(gamificacao_controller, 'ServicoGamificacao'),
		(integracoes_controller, 'ServicoIntegracao'),
		(leads_controller, 'ServicoLead'),
		(lgpd_controller, 'ServicoLgpd'),
		(portfolio_controller, 'ServicoPortfolio'),
		(projetos_controller, 'ServicoProjeto'),
		(servicos_controller, 'ServicoServico'),
		(tarefas_controller, 'ServicoTarefa'),
		(users_controller, 'ServicoUsuario'),
	],
)
def test_factories_criam_servicos_dos_controllers(modulo, nome_classe: str):
	"""Valida que factories dos controllers instanciam os serviços corretos."""
	servico = modulo._servico(SimpleNamespace())

	assert servico.__class__.__name__ == nome_classe


@pytest.mark.asyncio
async def test_academy_controller_encaminha_operacoes_crud():
	"""Valida que controller de academy encaminha operações para o serviço."""
	servico = ServicoControllerFake()

	assert await academy_controller.criar('dados', servico) == {'ok': True}
	await academy_controller.listar(servico, _pagina(), tipo='curso', publicado=True)
	await academy_controller.listar_admin(servico, _pagina(), publicado=None)
	await academy_controller.obter(1, servico)
	await academy_controller.atualizar(1, 'dados', servico)
	await academy_controller.deletar(1, servico)

	assert [chamada[0] for chamada in servico.chamadas] == [
		'criar',
		'listar_filtrados',
		'listar_filtrados',
		'obter',
		'atualizar',
		'deletar',
	]


@pytest.mark.asyncio
async def test_agenda_controller_encaminha_eventos_e_solicitacoes():
	"""Valida que controller de agenda encaminha eventos e solicitações."""
	servico = ServicoControllerFake()
	usuario = _usuario()

	await agenda_controller.criar_evento('dados', servico)
	await agenda_controller.listar_eventos_site(usuario, servico, date.today(), None)
	await agenda_controller.listar_eventos(7, servico)
	await agenda_controller.listar_eventos_calendario_google(servico, None, date.today())
	await agenda_controller.obter_evento(1, servico)
	await agenda_controller.atualizar_evento(1, 'dados', servico)
	await agenda_controller.deletar_evento(1, servico)
	await agenda_controller.criar_solicitacao('dados', servico)
	await agenda_controller.listar_solicitacoes(7, servico)
	await agenda_controller.atualizar_solicitacao(1, 'dados', servico)
	await agenda_controller.deletar_solicitacao(1, servico)

	assert len(servico.chamadas) == 11


@pytest.mark.asyncio
async def test_comunicados_controller_encaminha_crud_e_leituras():
	"""Valida que controller de comunicados encaminha CRUD e leituras."""
	servico = ServicoControllerFake()

	await comunicados_controller.criar('dados', servico)
	await comunicados_controller.listar(servico, _pagina(), alvo=None)
	await comunicados_controller.obter(1, servico)
	await comunicados_controller.atualizar(1, 'dados', servico)
	await comunicados_controller.deletar(1, servico)
	await comunicados_controller.marcar_lido(1, servico, 7)
	await comunicados_controller.listar_leituras(1, servico)

	assert servico.chamadas[-2][1] == (1, 7)


@pytest.mark.asyncio
async def test_dashboard_controller_encaminha_paineis():
	"""Valida que controller de dashboard encaminha painéis ao serviço."""
	servico = ServicoControllerFake()
	usuario = _usuario()

	await dashboard_controller.admin(servico)
	await dashboard_controller.cliente(1, servico, usuario)
	await dashboard_controller.funcionario(2, servico, usuario)
	await dashboard_controller.projeto_kanban(3, servico, usuario)

	assert [chamada[0] for chamada in servico.chamadas] == [
		'admin',
		'cliente',
		'funcionario',
		'projeto_kanban',
	]


@pytest.mark.asyncio
async def test_gamificacao_controller_encaminha_recursos_e_bloqueia_acesso():
	"""Valida controller de gamificação e regras de acesso próprias."""
	servico = ServicoControllerFake()
	credencial = HTTPAuthorizationCredentials(
		scheme='Bearer',
		credentials=criar_token_acesso(7, {'role': PapelUsuario.FUNCIONARIO.value}),
	)

	assert gamificacao_controller._admin_ou_funcionario(credencial) == (
		7,
		PapelUsuario.FUNCIONARIO.value,
	)
	with pytest.raises(HTTPException):
		gamificacao_controller._admin_ou_funcionario(None)
	credencial_cliente = HTTPAuthorizationCredentials(
		scheme='Bearer',
		credentials=criar_token_acesso(7, {'role': PapelUsuario.CLIENTE.value}),
	)
	with pytest.raises(HTTPException):
		gamificacao_controller._admin_ou_funcionario(credencial_cliente)
	with pytest.raises(HTTPException):
		await gamificacao_controller.listar_historico(8, servico, (7, 'funcionario'))
	with pytest.raises(HTTPException):
		await gamificacao_controller.listar_funcionario_conquistas(8, servico, (7, 'funcionario'))

	await gamificacao_controller.criar_regra('dados', servico)
	await gamificacao_controller.listar_regras(servico, _pagina())
	await gamificacao_controller.atualizar_regra(1, 'dados', servico)
	await gamificacao_controller.deletar_regra(1, servico)
	await gamificacao_controller.registrar_xp('dados', servico)
	await gamificacao_controller.listar_historico(7, servico, (7, 'funcionario'))
	await gamificacao_controller.criar_conquista('dados', servico)
	await gamificacao_controller.listar_conquistas(servico, _pagina(), (7, 'admin'))
	await gamificacao_controller.atualizar_conquista(1, 'dados', servico)
	await gamificacao_controller.deletar_conquista(1, servico)
	await gamificacao_controller.desbloquear(7, 1, servico)
	await gamificacao_controller.listar_funcionario_conquistas(7, servico, (7, 'funcionario'))

	assert servico.chamadas[-1][0] == 'listar_conquistas_funcionario'


@pytest.mark.asyncio
async def test_integracoes_lgpd_portfolio_e_users_controllers_encaminham_crud():
	"""Valida controllers simples de integrações, LGPD, portfolio e usuários."""
	servico = ServicoControllerFake()

	await integracoes_controller.criar('dados', servico)
	await integracoes_controller.listar(servico, _pagina())
	await integracoes_controller.obter(1, servico)
	await integracoes_controller.atualizar(1, 'dados', servico)
	await integracoes_controller.deletar(1, servico)
	await lgpd_controller.registrar('dados', servico)
	await lgpd_controller.listar(servico, _pagina())
	await portfolio_controller.criar('dados', servico)
	await portfolio_controller.listar(servico, _pagina(), destaques=True)
	await portfolio_controller.obter(1, servico)
	await portfolio_controller.atualizar(1, 'dados', servico)
	await portfolio_controller.deletar(1, servico)
	await users_controller.criar('dados', servico)
	await users_controller.listar(servico, _pagina())
	await users_controller.obter(1, servico)
	await users_controller.atualizar(1, 'dados', servico)
	await users_controller.aprovar(1, servico)
	await users_controller.deletar(1, servico)
	await users_controller.registrar('dados', servico)

	assert len(servico.chamadas) == 19


@pytest.mark.asyncio
async def test_leads_controller_lista_exporta_e_encaminha_crud():
	"""Valida controller de leads incluindo exportação CSV."""
	lead = SimpleNamespace(
		id=1,
		nome='Lead',
		email='lead@example.com',
		whatsapp=None,
		empresa=None,
		servico_id=None,
		orcamento=None,
		prazo_desejado=None,
		status=SituacaoLead.NOVO,
		prioridade=LeadPrioridade.MEDIA,
		data=datetime(2026, 5, 26, tzinfo=timezone.utc),
	)
	servico = ServicoControllerFake([lead])

	await leads_controller.criar('dados', servico)
	await leads_controller.listar(servico, _pagina(), None, None, None, None)
	resposta = await leads_controller.exportar_csv(servico)
	await leads_controller.obter(1, servico)
	await leads_controller.atualizar(1, 'dados', servico)
	await leads_controller.deletar(1, servico)

	assert 'lead@example.com' in resposta.body.decode()


@pytest.mark.asyncio
async def test_projetos_servicos_e_tarefas_controllers_encaminham_fluxos_compostos():
	"""Valida controllers com payloads compostos e verificações prévias."""
	servico = ServicoControllerFake()
	usuario = _usuario()

	await projetos_controller.criar('dados', servico)
	await projetos_controller.listar(servico, _pagina(), usuario, cliente_id=1)
	await projetos_controller.obter(1, servico, usuario)
	await projetos_controller.atualizar(1, 'dados', servico)
	await projetos_controller.deletar(1, servico)
	await projetos_controller.adicionar_membro(1, 'dados', servico)
	await projetos_controller.listar_equipe(1, servico, usuario)
	await projetos_controller.remover_membro(1, 7, servico)
	await servicos_controller.criar('dados', servico)
	await servicos_controller.listar(servico, _pagina())
	await servicos_controller.obter(1, servico)
	await servicos_controller.atualizar(1, 'dados', servico)
	await servicos_controller.deletar(1, servico)
	await servicos_controller.adicionar_entregavel(1, PayloadComCopia(), servico)
	await servicos_controller.listar_entregaveis(1, servico)
	await servicos_controller.atualizar_entregavel(1, 'dados', servico)
	await servicos_controller.remover_entregavel(1, servico)
	await tarefas_controller.criar('dados', servico)
	await tarefas_controller.listar(servico, _pagina(), usuario)
	await tarefas_controller.obter(1, servico, usuario)
	await tarefas_controller.atualizar(1, 'dados', servico, usuario)
	await tarefas_controller.deletar(1, servico, usuario)
	await tarefas_controller.comentar(1, servico, usuario, 'comentario')
	await tarefas_controller.listar_comentarios(1, servico, usuario)
	await tarefas_controller.remover_comentario(1, servico)
	await tarefas_controller.anexar(1, PayloadComCopia(), servico, usuario)
	await tarefas_controller.listar_anexos(1, servico, usuario)
	await tarefas_controller.remover_anexo(1, servico)

	assert servico.chamadas[-1][0] == 'deletar_anexo'
