import pytest
from core.enums import LeadPrioridade, SituacaoLead, SituacaoServico
from modules.leads.schema import LeadCriar
from modules.servicos.schema import ServicoAtualizar, ServicoCriar
from pydantic import ValidationError


def test_servico_criar_define_status_ativo_por_padrao():
	dados = ServicoCriar(
		nome='Identidade Visual',
		slug='identidade-visual',
		descricao='Branding completo.',
	)

	assert dados.status == SituacaoServico.ATIVO


def test_servico_atualizar_permite_patch_parcial():
	dados = ServicoAtualizar(descricao='Nova descricao')

	assert dados.nome is None
	assert dados.descricao == 'Nova descricao'


def test_lead_criar_define_status_e_prioridade_padrao():
	dados = LeadCriar(
		nome='Cliente Teste',
		email='cliente@example.com',
		mensagem='Quero conhecer os serviços.',
	)

	assert dados.status == SituacaoLead.NOVO
	assert dados.prioridade == LeadPrioridade.MEDIA
	assert dados.termos_aceitos is False


def test_lead_criar_valida_email():
	with pytest.raises(ValidationError):
		LeadCriar(nome='Cliente Teste', email='email-invalido')
