import uuid

import pytest
from httpx import AsyncClient

from tests.conftest import exige_banco


def _dados_servico(**substituicoes):
	dados_base = {
		'nome': f'Servico {uuid.uuid4().hex[:6]}',
		'slug': f'servico-{uuid.uuid4().hex[:8]}',
		'descricao': 'Servico criado pelos testes de integração.',
		'icone': 'sparkles',
		'status': 'ativo',
	}
	dados_base.update(substituicoes)
	return dados_base


@pytest.mark.asyncio
@exige_banco
@pytest.mark.parametrize('status', ['ativo', 'inativo'])
async def test_criar_servico_com_status(cliente_admin: AsyncClient, status: str):
	resposta = await cliente_admin.post(
		'/api/v1/servicos', json=_dados_servico(status=status)
	)

	assert resposta.status_code == 201
	assert resposta.json()['status'] == status


@pytest.mark.asyncio
@exige_banco
async def test_adicionar_listar_e_atualizar_entregavel(cliente_admin: AsyncClient):
	servico = (
		await cliente_admin.post('/api/v1/servicos', json=_dados_servico())
	).json()

	criado = await cliente_admin.post(
		f'/api/v1/servicos/{servico["id"]}/entregaveis',
		json={'descricao': 'Primeira entrega', 'ordem': 1, 'servico_id': servico['id']},
	)
	assert criado.status_code == 201

	listagem = await cliente_admin.get(f'/api/v1/servicos/{servico["id"]}/entregaveis')
	assert listagem.status_code == 200
	assert listagem.json()[0]['descricao'] == 'Primeira entrega'

	entregavel_id = criado.json()['id']
	atualizado = await cliente_admin.patch(
		f'/api/v1/servicos/entregaveis/{entregavel_id}',
		json={'descricao': 'Entrega revisada'},
	)
	assert atualizado.status_code == 200
	assert atualizado.json()['descricao'] == 'Entrega revisada'


@pytest.mark.asyncio
@exige_banco
async def test_servico_nao_encontrado_retorna_404(cliente_admin: AsyncClient):
	resposta = await cliente_admin.get('/api/v1/servicos/99999999')
	assert resposta.status_code == 404
