import pytest
from core.security import criar_token_acesso, decodificar_token
from fastapi import HTTPException


@pytest.mark.parametrize(
	('sujeito', 'papel'), [(1, 'admin'), (42, 'cliente'), (99, 'funcionario')]
)
def test_criar_e_decodificar_token_acesso(sujeito: int, papel: 'str'):
	token = criar_token_acesso(sujeito, dados_extras={'role': papel})
	dados = decodificar_token(token)
	assert dados['sub'] == str(sujeito)
	assert dados['type'] == 'access'
	assert dados['role'] == papel


def test_decodificar_token_invalido_lanca_excecao():
	with pytest.raises(HTTPException) as exc:
		decodificar_token('token-invalido')
	assert exc.value.status_code == 401
