import asyncio
from logging.config import fileConfig

from alembic import context
from core.config import obter_configuracoes
from core.database import normalizar_url_banco_assincrono
from db.base import Base
from db.registro import TODOS_MODELOS
from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config

configuracoes = obter_configuracoes()
MODELOS_CARREGADOS = TODOS_MODELOS

# Objeto de configuração do Alembic, com acesso ao arquivo .ini em uso.
configuracao_alembic = context.config

# Interpreta a configuração de logging do Python.
if configuracao_alembic.config_file_name is not None:
	fileConfig(configuracao_alembic.config_file_name)

url_banco, argumentos_conexao = normalizar_url_banco_assincrono(
	configuracoes.database_url
)
configuracao_alembic.set_main_option('sqlalchemy.url', url_banco)

# Metadata usado pelo suporte de autogenerate.
target_metadata = Base.metadata


def executar_migracoes_offline() -> None:
	"""Executa migrações em modo offline.

	Configura o contexto apenas com a URL e emite instruções SQL
	diretamente para a saída do script.

	"""
	url = configuracao_alembic.get_main_option('sqlalchemy.url')
	context.configure(
		url=url,
		target_metadata=target_metadata,
		literal_binds=True,
		dialect_opts={'paramstyle': 'named'},
	)

	with context.begin_transaction():
		context.run_migrations()


def executar_migracoes(conexao: Connection) -> None:
	context.configure(connection=conexao, target_metadata=target_metadata)

	with context.begin_transaction():
		context.run_migrations()


async def executar_migracoes_assincronas() -> None:
	"""Cria o engine assíncrono e associa uma conexão ao contexto."""

	conectavel = async_engine_from_config(
		configuracao_alembic.get_section(configuracao_alembic.config_ini_section, {}),
		prefix='sqlalchemy.',
		poolclass=pool.NullPool,
		connect_args=argumentos_conexao,
	)

	async with conectavel.connect() as conexao:
		await conexao.run_sync(executar_migracoes)

	await conectavel.dispose()


def executar_migracoes_online() -> None:
	"""Executa migrações em modo online."""

	asyncio.run(executar_migracoes_assincronas())


if context.is_offline_mode():
	executar_migracoes_offline()
else:
	executar_migracoes_online()
