import pytest
from httpx import AsyncClient

from tests.conftest import requires_db


@pytest.mark.asyncio
@requires_db
async def test_health_retorna_ok(client: AsyncClient):
	response = await client.get('/health')
	assert response.status_code == 200
	assert response.json() == {'status': 'ok'}
