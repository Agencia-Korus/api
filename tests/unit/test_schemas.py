import pytest
from core.enums import LeadPrioridade, LeadStatus, ServicoStatus
from modules.leads.schema import LeadCriar
from modules.servicos.schema import ServicoCriar, ServicoAtualizar
from pydantic import ValidationError


def test_servico_create_define_status_ativo_por_padrao():
	payload = ServicoCriar(
		nome='Identidade Visual',
		slug='identidade-visual',
		descricao='Branding completo.',
	)

	assert payload.status == ServicoStatus.ATIVO


def test_servico_update_permite_patch_parcial():
	payload = ServicoAtualizar(descricao='Nova descricao')

	assert payload.nome is None
	assert payload.descricao == 'Nova descricao'


def test_lead_create_define_status_e_prioridade_padrao():
	payload = LeadCriar(
		nome='Cliente Teste',
		email='cliente@example.com',
		mensagem='Quero conhecer os serviços.',
	)

	assert payload.status == LeadStatus.NOVO
	assert payload.prioridade == LeadPrioridade.MEDIA
	assert payload.termos_aceitos is False


def test_lead_create_valida_email():
	with pytest.raises(ValidationError):
		LeadCriar(nome='Cliente Teste', email='email-invalido')
