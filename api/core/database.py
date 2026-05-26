from typing import Any

from sqlalchemy.engine import make_url

NOMES_DRIVERS_POSTGRES = {'postgres', 'postgresql', 'postgresql+asyncpg'}


def normalizar_url_banco_assincrono(url: str) -> tuple[str, dict[str, Any]]:
	"""Função para normalizar a URL assíncrona do banco de dados."""
	url_analisada = make_url(url)
	if url_analisada.drivername not in NOMES_DRIVERS_POSTGRES:
		return str(url_analisada), {}

	dsn_asyncpg = url_analisada.set(drivername='postgresql')

	return 'postgresql+asyncpg://', {
		'dsn': dsn_asyncpg.render_as_string(hide_password=False)
	}
