# ruff: noqa: PLC2701

import httpx
import pytest
from core.enums import UserRole, UserStatus
from core.password import hash_password
from fastapi import HTTPException
from modules.auth_proxy.controller import (
	_extract_credentials,
	_login_local,
)


class _FakeResult:
	"""Classe que simula o resultado de uma consulta de usuário."""

	def __init__(self, user):
		"""Função para guardar o usuário retornado pela consulta."""
		self.user = user

	def scalar_one_or_none(self):
		"""Função para retornar o usuário simulado ou None."""
		return self.user


class _FakeSession:
	"""Classe que simula uma sessão assíncrona do banco."""

	def __init__(self, user):
		"""Função para guardar o usuário usado no teste."""
		self.user = user

	async def execute(self, _statement):
		"""Função para simular uma consulta ao banco de dados."""
		return _FakeResult(self.user)


class _FakeUser:
	"""Classe que representa um usuário ativo usado no teste."""

	id = 1
	role = UserRole.ADMIN
	status = UserStatus.ATIVO
	senha_hash = hash_password('AdminKorus@2026')


def test_extract_credentials_formulario_swagger():
	body = b'username=admin%40email.com&password=AdminKorus%402026'
	email, senha = _extract_credentials(body, 'application/x-www-form-urlencoded')
	assert email == 'admin@email.com'
	assert senha == 'AdminKorus@2026'


@pytest.mark.asyncio
async def test_login_local_retorna_tokens_quando_auth_indisponivel():
	response = await _login_local(
		b'username=admin%40email.com&password=AdminKorus%402026',
		'application/x-www-form-urlencoded',
		_FakeSession(_FakeUser()),
		httpx.ConnectError('auth indisponivel'),
	)

	assert response.status_code == 200
	assert response.body


@pytest.mark.asyncio
async def test_login_local_rejeita_senha_incorreta():
	with pytest.raises(HTTPException) as exc:
		await _login_local(
			b'username=admin%40email.com&password=errada',
			'application/x-www-form-urlencoded',
			_FakeSession(_FakeUser()),
			httpx.ConnectError('auth indisponivel'),
		)

	assert exc.value.status_code == 401
