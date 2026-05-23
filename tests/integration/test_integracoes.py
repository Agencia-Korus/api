import pytest
from httpx import AsyncClient

from tests.conftest import requires_db


@pytest.mark.asyncio
@requires_db
@pytest.mark.parametrize(
	'status_input',
	['conectado', 'desconectado'],
)
async def test_criar_integracao_status(admin_client: AsyncClient, status_input: str):
	payload = {
		'nome': 'google_calendar',
		'status': status_input,
	}
	resp = await admin_client.post('/api/v1/integracoes', json=payload)
	assert resp.status_code in {201, 409}
	if resp.status_code == 201:
		assert resp.json()['status'] == status_input


@pytest.mark.asyncio
@requires_db
async def test_listar_integracoes(admin_client: AsyncClient):
	resp = await admin_client.get('/api/v1/integracoes')
	assert resp.status_code == 200
	assert isinstance(resp.json(), list)