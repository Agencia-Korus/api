import os
import subprocess
import sys


def test_alembic_gera_sql_offline_com_modelos_registrados():
	"""Valida que alembic gera sql offline com modelos registrados."""
	ambiente = {
		**os.environ,
		'DATABASE_URL': 'postgresql+asyncpg://korus:korus@localhost:5432/korus_test',
		'JWT_SECRET_KEY': 'test-secret',
	}

	resultado = subprocess.run(
		[sys.executable, '-m', 'alembic', 'upgrade', 'head', '--sql'],
		check=False,
		capture_output=True,
		env=ambiente,
		text=True,
	)

	assert resultado.returncode == 0, resultado.stderr
	assert 'CREATE TABLE usuario' in resultado.stdout
	assert 'google_event_id' in resultado.stdout
