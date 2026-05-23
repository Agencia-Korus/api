import uuid

import pytest
from httpx import AsyncClient

from tests.conftest import requires_db


def _payload(**overrides):
	base = {
		'nome': f'Lead {uuid.uuid4().hex[:6]}',
		'email': f'{uuid.uuid4().hex[:8]}@example.com',
		'whatsapp': '+5561999990000',
		'orcamento': 'R$5k-R$10k',
		'mensagem': 'Quero saber sobre identidade visual',
		'status': 'novo',
		'prioridade': 'media',
	}
	base.update(overrides)
	return base


@pytest.mark.asyncio
@requires_db
@pytest.mark.parametrize('prioridade', ['baixa', 'media', 'alta'])
async def test_criar_lead_com_prioridades(admin_client: AsyncClient, prioridade: str):
	resp = await admin_client.post(
		'/api/v1/leads', json=_payload(prioridade=prioridade)
	)
	assert resp.status_code == 201
	assert resp.json()['prioridade'] == prioridade


@pytest.mark.asyncio
@requires_db
@pytest.mark.parametrize(
	('status_inicial', 'novo_status'),
	[
		('novo', 'em_contato'),
		('em_contato', 'qualificado'),
		('qualificado', 'convertido'),
	],
)
async def test_atualizar_status_lead(
	admin_client: AsyncClient, status_inicial: str, novo_status: str
):
	criado = (
		await admin_client.post('/api/v1/leads', json=_payload(status=status_inicial))
	).json()
	resp = await admin_client.patch(
		f'/api/v1/leads/{criado["id"]}', json={'status': novo_status}
	)
	assert resp.status_code == 200
	assert resp.json()['status'] == novo_status


@pytest.mark.asyncio
@requires_db
async def test_lead_nao_encontrado_retorna_404(admin_client: AsyncClient):
	resp = await admin_client.get('/api/v1/leads/99999999')
	assert resp.status_code == 404
