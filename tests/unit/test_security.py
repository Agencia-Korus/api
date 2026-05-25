import pytest
from core.security import criar_access_token, decode_token
from fastapi import HTTPException


@pytest.mark.parametrize(
	('subject', 'role'), [(1, 'admin'), (42, 'cliente'), (99, 'funcionario')]
)
def test_create_and_decode_access_token(subject: int, role: 'str'):
	token = criar_access_token(subject, extra={'role': role})
	dados = decode_token(token)
	assert dados['sub'] == str(subject)
	assert dados['type'] == 'access'
	assert dados['role'] == role


def test_decode_token_invalido_lanca_excecao():
	with pytest.raises(HTTPException) as exc:
		decode_token('token-invalido')
	assert exc.value.status_code == 401
