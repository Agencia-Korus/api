import uuid

import pytest
from httpx import AsyncClient

from tests.conftest import requires_db


def _payload_servico(**overrides):
	base = {
		'nome': f'Servico {uuid.uuid4().hex[:6]}',
		'slug': f'servico-{uuid.uuid4().hex[:8]}',
		'descricao': 'Servico criado pelos testes de integração.',
		'icone': 'sparkles',
		'status': 'ativo',
	}
	base.update(overrides)
	return base


@pytest.mark.asyncio
@requires_db
@pytest.mark.parametrize('status', ['ativo', 'inativo'])
async def test_criar_servico_com_status(admin_client: AsyncClient, status: str):
	resp = await admin_client.post(
		'/api/v1/servicos', json=_payload_servico(status=status)
	)

	assert resp.status_code == 201
	assert resp.json()['status'] == status


@pytest.mark.asyncio
@requires_db
async def test_adicionar_listar_e_atualizar_entregavel(admin_client: AsyncClient):
	servico = (
		await admin_client.post('/api/v1/servicos', json=_payload_servico())
	).json()

	criado = await admin_client.post(
		f'/api/v1/servicos/{servico["id"]}/entregaveis',
		json={'descricao': 'Primeira entrega', 'ordem': 1, 'servico_id': servico['id']},
	)
	assert criado.status_code == 201

	listagem = await admin_client.get(f'/api/v1/servicos/{servico["id"]}/entregaveis')
	assert listagem.status_code == 200
	assert listagem.json()[0]['descricao'] == 'Primeira entrega'

	entregavel_id = criado.json()['id']
	atualizado = await admin_client.patch(
		f'/api/v1/servicos/entregaveis/{entregavel_id}',
		json={'descricao': 'Entrega revisada'},
	)
	assert atualizado.status_code == 200
	assert atualizado.json()['descricao'] == 'Entrega revisada'


@pytest.mark.asyncio
@requires_db
async def test_servico_nao_encontrado_retorna_404(admin_client: AsyncClient):
	resp = await admin_client.get('/api/v1/servicos/99999999')
	assert resp.status_code == 404
