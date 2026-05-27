import pytest
from core.security import (
	criar_token_acesso,
	criar_token_atualizacao,
	decodificar_token,
	exigir_papel,
	obter_usuario_atual,
	obter_usuario_atual_id,
)
from fastapi import HTTPException
from fastapi.security import HTTPAuthorizationCredentials


@pytest.mark.parametrize(
	('sujeito', 'papel'), [(1, 'admin'), (42, 'cliente'), (99, 'funcionario')]
)
def test_criar_e_decodificar_token_acesso(sujeito: int, papel: 'str'):
	"""Valida que criar e decodificar token acesso."""
	token = criar_token_acesso(sujeito, dados_extras={'role': papel})
	dados = decodificar_token(token)
	assert dados['sub'] == str(sujeito)
	assert dados['type'] == 'access'
	assert dados['role'] == papel


def test_decodificar_token_invalido_lanca_excecao():
	"""Valida que decodificar token invalido lanca excecao."""
	with pytest.raises(HTTPException) as exc:
		decodificar_token('token-invalido')
	assert exc.value.status_code == 401


def _credenciais(token: str) -> HTTPAuthorizationCredentials:
	return HTTPAuthorizationCredentials(scheme='Bearer', credentials=token)


def test_criar_token_atualizacao_define_tipo_refresh():
	"""Valida que criar token atualizacao define tipo refresh."""
	token = criar_token_atualizacao(123)
	dados = decodificar_token(token)

	assert dados['sub'] == '123'
	assert dados['type'] == 'refresh'


def test_obter_usuario_atual_id_extrai_sub_do_token():
	"""Valida que obter usuario atual id extrai sub do token."""
	token = criar_token_acesso(77, dados_extras={'role': 'admin'})

	assert obter_usuario_atual_id(_credenciais(token)) == 77


def test_obter_usuario_atual_id_rejeita_token_sem_sub():
	"""Valida que obter usuario atual id rejeita token sem sujeito."""
	token = criar_token_acesso('', dados_extras={'role': 'admin'})

	with pytest.raises(HTTPException):
		obter_usuario_atual_id(_credenciais(token))


def test_obter_usuario_atual_extrai_id_e_papel():
	"""Valida que obter usuario atual extrai id e papel."""
	token = criar_token_acesso(88, dados_extras={'role': 'funcionario'})

	usuario = obter_usuario_atual(_credenciais(token))

	assert usuario.id == 88
	assert usuario.papel == 'funcionario'


@pytest.mark.parametrize('dependencia', [obter_usuario_atual_id, obter_usuario_atual])
def test_dependencias_de_usuario_rejeitam_credenciais_ausentes(dependencia):
	"""Valida que dependencias de usuario rejeitam credenciais ausentes."""
	with pytest.raises(HTTPException) as exc:
		dependencia(None)

	assert exc.value.status_code == 401


def test_obter_usuario_atual_rejeita_token_sem_role():
	"""Valida que obter usuario atual rejeita token sem role."""
	token = criar_token_acesso(88)

	with pytest.raises(HTTPException) as exc:
		obter_usuario_atual(_credenciais(token))

	assert exc.value.status_code == 401


def test_exigir_papel_permite_papel_autorizado():
	"""Valida que exigir papel permite papel autorizado."""
	token = criar_token_acesso(99, dados_extras={'role': 'admin'})
	verificar_admin = exigir_papel('admin')

	assert verificar_admin(_credenciais(token)) == 99


def test_exigir_papel_bloqueia_papel_nao_autorizado():
	"""Valida que exigir papel bloqueia papel nao autorizado."""
	token = criar_token_acesso(99, dados_extras={'role': 'cliente'})
	verificar_admin = exigir_papel('admin')

	with pytest.raises(HTTPException) as exc:
		verificar_admin(_credenciais(token))

	assert exc.value.status_code == 403
