import pytest
from httpx import AsyncClient

from tests.conftest import exige_banco


@pytest.mark.asyncio
@exige_banco
@pytest.mark.parametrize(
	'situacao_entrada',
	['conectado', 'desconectado'],
)
async def test_criar_integracao_status(
	cliente_admin: AsyncClient, situacao_entrada: str
):
	dados = {
		'nome': 'google_calendar',
		'status': situacao_entrada,
	}
	resposta = await cliente_admin.post('/api/v1/integracoes', json=dados)
	assert resposta.status_code in {201, 409}
	if resposta.status_code == 201:
		assert resposta.json()['status'] == situacao_entrada


@pytest.mark.asyncio
@exige_banco
async def test_listar_integracoes(cliente_admin: AsyncClient):
	resposta = await cliente_admin.get('/api/v1/integracoes')
	assert resposta.status_code == 200
	assert isinstance(resposta.json(), list)
