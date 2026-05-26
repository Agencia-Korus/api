from collections.abc import AsyncGenerator
from functools import lru_cache

from core.config import obter_configuracoes
from core.database import normalizar_url_banco_assincrono
from sqlalchemy.ext.asyncio import (
	AsyncEngine,
	AsyncSession,
	async_sessionmaker,
	create_async_engine,
)


@lru_cache
def obter_motor() -> AsyncEngine:  # pragma: no cover
	"""Função para criar o engine assíncrono sob demanda."""
	configuracoes = obter_configuracoes()
	url_banco, argumentos_conexao = normalizar_url_banco_assincrono(
		configuracoes.database_url
	)
	return create_async_engine(
		url=url_banco,
		echo=configuracoes.debug,
		pool_pre_ping=True,
		connect_args=argumentos_conexao,
	)


@lru_cache
def obter_fabrica_sessao() -> async_sessionmaker[AsyncSession]:  # pragma: no cover
	"""Função para criar a fábrica de sessões sob demanda."""
	return async_sessionmaker(
		bind=obter_motor(),
		class_=AsyncSession,
		autoflush=False,
		expire_on_commit=False,
	)


async def obter_sessao() -> AsyncGenerator[AsyncSession, None]:  # pragma: no cover
	"""Função para fornecer uma sessão assíncrona do banco de dados."""
	fabrica_sessao = obter_fabrica_sessao()
	async with fabrica_sessao() as sessao:
		try:
			yield sessao
		except Exception:
			await sessao.rollback()
			raise
