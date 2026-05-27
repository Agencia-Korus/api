import pytest
from core.database import normalizar_url_banco_assincrono


@pytest.mark.parametrize(
	('url_entrada', 'url_esperada', 'argumentos_esperados'),
	[
		(
			'postgresql://usuario:senha@localhost:5432/korus',
			'postgresql+asyncpg://',
			{'dsn': 'postgresql://usuario:senha@localhost:5432/korus'},
		),
		(
			'postgres://usuario:senha@localhost/korus?sslmode=require',
			'postgresql+asyncpg://',
			{'dsn': 'postgresql://usuario:senha@localhost/korus?sslmode=require'},
		),
		(
			'postgresql+asyncpg://usuario:senha@localhost/korus',
			'postgresql+asyncpg://',
			{'dsn': 'postgresql://usuario:senha@localhost/korus'},
		),
		(
			'sqlite+aiosqlite:///tmp/korus.db',
			'sqlite+aiosqlite:///tmp/korus.db',
			{},
		),
	],
)
def test_normalizar_url_banco_assincrono(
	url_entrada: str, url_esperada: str, argumentos_esperados: dict[str, str]
):
	"""Valida que normalizar url banco assincrono."""
	url_normalizada, argumentos = normalizar_url_banco_assincrono(url_entrada)

	assert url_normalizada == url_esperada
	assert argumentos == argumentos_esperados
