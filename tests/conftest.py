import asyncio
import os
import socket
from collections.abc import AsyncGenerator

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient

os.environ.setdefault(
	'DATABASE_URL',
	'postgresql+asyncpg://korus:korus@localhost:5432/korus_test',
)
os.environ.setdefault('JWT_SECRET_KEY', 'test-secret')

from core.security import criar_token_acesso
from db.session import motor
from main import app
from sqlalchemy import text

VARIAVEL_URL_BASE = 'KORUS_BASE_URL'
TEMPO_LIMITE_PADRAO_SEGUNDOS = 30
PORTA_PADRAO_BANCO = 5432
TEMPO_LIMITE_SOCKET = 1


@pytest.fixture(scope='session')
def url_base() -> str | None:
	return os.environ.get(VARIAVEL_URL_BASE)


@pytest_asyncio.fixture
async def cliente_http(url_base: str | None) -> AsyncGenerator[AsyncClient, None]:
	if url_base:
		async with AsyncClient(
			base_url=url_base, timeout=TEMPO_LIMITE_PADRAO_SEGUNDOS
		) as cliente_http_interno:
			yield cliente_http_interno
	else:
		transport = ASGITransport(app=app)
		async with AsyncClient(
			transport=transport,
			base_url='http://testserver',
			timeout=TEMPO_LIMITE_PADRAO_SEGUNDOS,
		) as cliente_http_interno:
			yield cliente_http_interno


@pytest.fixture
def token_admin() -> str:
	return criar_token_acesso(sujeito=1, dados_extras={'role': 'admin'})


@pytest.fixture
def cabecalhos_admin(token_admin: str) -> dict[str, str]:
	return {'Authorization': f'Bearer {token_admin}'}


@pytest_asyncio.fixture
async def cliente_admin(
	url_base: str | None, cabecalhos_admin: dict[str, str]
) -> AsyncGenerator[AsyncClient, None]:
	if url_base:
		async with AsyncClient(
			base_url=url_base,
			timeout=TEMPO_LIMITE_PADRAO_SEGUNDOS,
			headers=cabecalhos_admin,
		) as cliente_http_interno:
			yield cliente_http_interno
	else:
		transport = ASGITransport(app=app)
		async with AsyncClient(
			transport=transport,
			base_url='http://testserver',
			timeout=TEMPO_LIMITE_PADRAO_SEGUNDOS,
			headers=cabecalhos_admin,
		) as cliente_http_interno:
			yield cliente_http_interno


@pytest.fixture
def token_cliente() -> str:
	return criar_token_acesso(sujeito=2, dados_extras={'role': 'cliente'})


@pytest.fixture
def cabecalhos_cliente(token_cliente: str) -> dict[str, str]:
	return {'Authorization': f'Bearer {token_cliente}'}


async def _consultar_banco() -> bool:
	try:
		async with motor.connect() as conexao:
			await conexao.execute(text('SELECT 1 FROM usuario LIMIT 1'))
			return True
	except Exception:
		return False
	finally:
		await motor.dispose()


def postgres_disponivel() -> bool:
	host = os.environ.get('TEST_DB_HOST', 'localhost')
	port = int(os.environ.get('TEST_DB_PORT', str(PORTA_PADRAO_BANCO)))
	try:
		with socket.create_connection((host, port), timeout=TEMPO_LIMITE_SOCKET):
			pass
	except OSError:
		return False
	try:
		return asyncio.run(_consultar_banco())
	except RuntimeError:
		return False


exige_banco = pytest.mark.skipif(
	not postgres_disponivel(),
	reason='Postgres com esquema aplicado é necessário para integração',
)
