import pytest
from core.enums import (
	LeadPrioridade,
	SituacaoLead,
	SituacaoProjeto,
	SituacaoServico,
	SituacaoSolicitacao,
)
from modules.academy.schema import AcademiaAtualizar
from modules.agenda.schema import (
	EventoAgendaAtualizar,
	SolicitacaoReuniaoCriar,
)
from modules.integracoes.schema import IntegracaoAtualizar, IntegracaoCriar
from modules.leads.schema import LeadAtualizar, LeadCriar
from modules.projetos.schema import ProjetoAtualizar, ProjetoCriar
from modules.servicos.schema import EntregavelAtualizar, ServicoAtualizar, ServicoCriar
from modules.users.schema import UsuarioAtualizar
from pydantic import ValidationError


def test_servico_criar_define_status_ativo_por_padrao():
	"""Valida que servico criar define status ativo por padrao."""
	dados = ServicoCriar(
		nome='Identidade Visual',
		slug='identidade-visual',
		descricao='Branding completo.',
	)

	assert dados.status == SituacaoServico.ATIVO


def test_servico_atualizar_permite_patch_parcial():
	"""Valida que servico atualizar permite patch parcial."""
	dados = ServicoAtualizar(descricao='Nova descricao')

	assert dados.nome is None
	assert dados.descricao == 'Nova descricao'


def test_lead_criar_define_status_e_prioridade_padrao():
	"""Valida que lead criar define status e prioridade padrao."""
	dados = LeadCriar(
		nome='Cliente Teste',
		email='cliente@example.com',
		mensagem='Quero conhecer os serviços.',
	)

	assert dados.status == SituacaoLead.NOVO
	assert dados.prioridade == LeadPrioridade.MEDIA
	assert dados.termos_aceitos is False


def test_lead_criar_valida_email():
	"""Valida que lead criar valida email."""
	with pytest.raises(ValidationError):
		LeadCriar(nome='Cliente Teste', email='email-invalido')


@pytest.mark.parametrize(
	'classe_schema',
	[
		AcademiaAtualizar,
		EntregavelAtualizar,
		EventoAgendaAtualizar,
		IntegracaoAtualizar,
		LeadAtualizar,
		ProjetoAtualizar,
		ServicoAtualizar,
		UsuarioAtualizar,
	],
)
def test_schemas_de_atualizacao_permitem_patch_vazio(classe_schema):
	"""Valida que schemas de atualizacao permitem patch vazio."""
	dados = classe_schema()

	assert dados.model_dump(exclude_none=True) == {}


@pytest.mark.parametrize(
	('progresso', 'deve_validar'),
	[(-1, False), (0, True), (45, True), (100, True), (101, False)],
)
def test_projeto_criar_valida_limites_de_progresso(progresso: int, deve_validar: bool):
	"""Valida que projeto criar valida limites de progresso."""
	dados = {
		'nome': 'Redesign do site',
		'cliente_id': 1,
		'status': SituacaoProjeto.PLANEJAMENTO,
		'progresso': progresso,
	}

	if deve_validar:
		assert ProjetoCriar(**dados).progresso == progresso
	else:
		with pytest.raises(ValidationError):
			ProjetoCriar(**dados)


@pytest.mark.parametrize(
	('remetente_id', 'destinatario_id', 'deve_validar'),
	[(1, 2, True), (2, 1, True), (7, 7, False)],
)
def test_solicitacao_reuniao_exige_usuarios_diferentes(
	remetente_id: int, destinatario_id: int, deve_validar: bool
):
	"""Valida que solicitacao reuniao exige usuarios diferentes."""
	dados = {
		'titulo': 'Revisao de layout',
		'data': '2026-05-25',
		'hora': '15:30:00',
		'remetente_id': remetente_id,
		'destinatario_id': destinatario_id,
	}

	if deve_validar:
		assert SolicitacaoReuniaoCriar(**dados).status == SituacaoSolicitacao.PENDENTE
	else:
		with pytest.raises(ValidationError):
			SolicitacaoReuniaoCriar(**dados)


@pytest.mark.parametrize('status', ['conectado', 'desconectado'])
def test_integracao_criar_aceita_status_validos(status: str):
	"""Valida que integracao criar aceita status validos."""
	dados = IntegracaoCriar(status=status)

	assert dados.nome == 'google_calendar'
	assert dados.status.value == status


def test_integracao_criar_rejeita_nome_fora_da_lista_permitida():
	"""Valida que integracao criar rejeita nome fora da lista permitida."""
	with pytest.raises(ValidationError):
		IntegracaoCriar(nome='slack')
