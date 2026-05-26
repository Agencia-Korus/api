import uuid

import pytest
from httpx import AsyncClient

from tests.conftest import exige_banco


def _dados(**substituicoes):
	dados_base = {
		'nome': f'Lead {uuid.uuid4().hex[:6]}',
		'email': f'{uuid.uuid4().hex[:8]}@example.com',
		'whatsapp': '+5561999990000',
		'orcamento': 'R$5k-R$10k',
		'mensagem': 'Quero saber sobre identidade visual',
		'status': 'novo',
		'prioridade': 'media',
	}
	dados_base.update(substituicoes)
	return dados_base


@pytest.mark.asyncio
@exige_banco
@pytest.mark.parametrize('prioridade', ['baixa', 'media', 'alta'])
async def test_criar_lead_com_prioridades(cliente_admin: AsyncClient, prioridade: str):
	resposta = await cliente_admin.post(
		'/api/v1/leads', json=_dados(prioridade=prioridade)
	)
	assert resposta.status_code == 201
	assert resposta.json()['prioridade'] == prioridade


@pytest.mark.asyncio
@exige_banco
@pytest.mark.parametrize(
	('situacao_inicial', 'nova_situacao'),
	[
		('novo', 'em_contato'),
		('em_contato', 'qualificado'),
		('qualificado', 'convertido'),
	],
)
async def test_atualizar_status_lead(
	cliente_admin: AsyncClient, situacao_inicial: str, nova_situacao: str
):
	criado = (
		await cliente_admin.post('/api/v1/leads', json=_dados(status=situacao_inicial))
	).json()
	resposta = await cliente_admin.patch(
		f'/api/v1/leads/{criado["id"]}', json={'status': nova_situacao}
	)
	assert resposta.status_code == 200
	assert resposta.json()['status'] == nova_situacao


@pytest.mark.asyncio
@exige_banco
async def test_lead_nao_encontrado_retorna_404(cliente_admin: AsyncClient):
	resposta = await cliente_admin.get('/api/v1/leads/99999999')
	assert resposta.status_code == 404
