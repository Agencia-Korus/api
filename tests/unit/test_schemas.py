import pytest
from core.enums import LeadPrioridade, LeadStatus, ServicoStatus
from modules.leads.schema import LeadCreate
from modules.servicos.schema import ServicoCreate, ServicoUpdate
from pydantic import ValidationError


def test_servico_create_define_status_ativo_por_padrao():
	payload = ServicoCreate(
		nome='Identidade Visual',
		slug='identidade-visual',
		descricao='Branding completo.',
	)

	assert payload.status == ServicoStatus.ATIVO


def test_servico_update_permite_patch_parcial():
	payload = ServicoUpdate(descricao='Nova descricao')

	assert payload.nome is None
	assert payload.descricao == 'Nova descricao'


def test_lead_create_define_status_e_prioridade_padrao():
	payload = LeadCreate(
		nome='Cliente Teste',
		email='cliente@example.com',
		mensagem='Quero conhecer os serviços.',
	)

	assert payload.status == LeadStatus.NOVO
	assert payload.prioridade == LeadPrioridade.MEDIA
	assert payload.termos_aceitos is False


def test_lead_create_valida_email():
	with pytest.raises(ValidationError):
		LeadCreate(nome='Cliente Teste', email='email-invalido')
