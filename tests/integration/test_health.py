import pytest
from httpx import AsyncClient

from tests.conftest import exige_banco


@pytest.mark.asyncio
@exige_banco
async def test_saude_retorna_ok(cliente_http: AsyncClient):
	resposta = await cliente_http.get('/health/db')
	assert resposta.status_code == 200
	assert resposta.json() == {'status': 'ok'}
