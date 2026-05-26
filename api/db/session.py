from collections.abc import AsyncGenerator

from core.config import obter_configuracoes
from core.database import normalizar_url_banco_assincrono
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

configuracoes = obter_configuracoes()
url_banco, argumentos_conexao = normalizar_url_banco_assincrono(
	configuracoes.database_url
)

motor = create_async_engine(
	url=url_banco,
	echo=configuracoes.debug,
	pool_pre_ping=True,
	connect_args=argumentos_conexao,
)

FabricaSessaoAssincrona = async_sessionmaker(
	bind=motor, class_=AsyncSession, autoflush=False, expire_on_commit=False
)


async def obter_sessao() -> AsyncGenerator[AsyncSession, None]:
	"""Função para fornecer uma sessão assíncrona do banco de dados."""
	async with FabricaSessaoAssincrona() as sessao:
		try:
			yield sessao
		except Exception:
			await sessao.rollback()
			raise
