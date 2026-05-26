import os
from collections.abc import AsyncGenerator, Generator
from importlib import import_module
from pathlib import Path
from typing import cast

import pytest
import pytest_asyncio
from alembic import command
from alembic.config import Config
from core.config import obter_configuracoes
from fastapi import FastAPI
from fastapi.testclient import TestClient
from httpx import ASGITransport, AsyncClient
from testcontainers.postgres import PostgresContainer

VARIAVEL_URL_BASE = 'KORUS_BASE_URL'
TEMPO_LIMITE_PADRAO_SEGUNDOS = 30
POSTGRES_IMAGE = os.environ.get('POSTGRES_IMAGE', 'postgres:16-alpine')
CAMINHO_ALEMBIC = Path(__file__).resolve().parents[1] / 'alembic.ini'

os.environ.setdefault('JWT_SECRET_KEY', 'test-secret')


def _executar_migracoes() -> None:
	configuracao = Config(str(CAMINHO_ALEMBIC))
	command.upgrade(configuracao, 'head')


@pytest.fixture(scope='session')
def postgres_container() -> Generator[PostgresContainer, None, None]:
	"""Sobe um Postgres efêmero para a sessão de testes."""
	with PostgresContainer(POSTGRES_IMAGE, driver='asyncpg') as postgres:
		os.environ['DATABASE_URL'] = postgres.get_connection_url()
		obter_configuracoes.cache_clear()
		_executar_migracoes()
		yield postgres
	obter_configuracoes.cache_clear()


@pytest.fixture(scope='session')
def url_base() -> str | None:
	return os.environ.get(VARIAVEL_URL_BASE)


@pytest.fixture(scope='session')
def app_teste(postgres_container: PostgresContainer) -> FastAPI:
	return cast(FastAPI, import_module('main').app)


@pytest.fixture
def cliente_teste(app_teste: FastAPI) -> Generator[TestClient, None, None]:
	with TestClient(app_teste) as cliente_http_interno:
		yield cliente_http_interno


@pytest_asyncio.fixture
async def cliente_http(
	url_base: str | None, app_teste: FastAPI
) -> AsyncGenerator[AsyncClient, None]:
	if url_base:
		async with AsyncClient(
			base_url=url_base, timeout=TEMPO_LIMITE_PADRAO_SEGUNDOS
		) as cliente_http_interno:
			yield cliente_http_interno
	else:
		transport = ASGITransport(app=app_teste)
		async with AsyncClient(
			transport=transport,
			base_url='http://testserver',
			timeout=TEMPO_LIMITE_PADRAO_SEGUNDOS,
		) as cliente_http_interno:
			yield cliente_http_interno


@pytest.fixture
def token_admin() -> str:
	criar_token_acesso = import_module('core.security').criar_token_acesso
	return criar_token_acesso(sujeito=1, dados_extras={'role': 'admin'})


@pytest.fixture
def cabecalhos_admin(token_admin: str) -> dict[str, str]:
	return {'Authorization': f'Bearer {token_admin}'}


@pytest_asyncio.fixture
async def cliente_admin(
	url_base: str | None, app_teste: FastAPI, cabecalhos_admin: dict[str, str]
) -> AsyncGenerator[AsyncClient, None]:
	if url_base:
		async with AsyncClient(
			base_url=url_base,
			timeout=TEMPO_LIMITE_PADRAO_SEGUNDOS,
			headers=cabecalhos_admin,
		) as cliente_http_interno:
			yield cliente_http_interno
	else:
		transport = ASGITransport(app=app_teste)
		async with AsyncClient(
			transport=transport,
			base_url='http://testserver',
			timeout=TEMPO_LIMITE_PADRAO_SEGUNDOS,
			headers=cabecalhos_admin,
		) as cliente_http_interno:
			yield cliente_http_interno


@pytest.fixture
def token_cliente() -> str:
	criar_token_acesso = import_module('core.security').criar_token_acesso
	return criar_token_acesso(sujeito=2, dados_extras={'role': 'cliente'})


@pytest.fixture
def cabecalhos_cliente(token_cliente: str) -> dict[str, str]:
	return {'Authorization': f'Bearer {token_cliente}'}


exige_banco = pytest.mark.usefixtures('postgres_container')
