import pytest
from core.password import gerar_hash_senha, verificar_senha


@pytest.mark.parametrize(
	'senha_plana', ['secreta-123', 'outra-coisa-segura!', 'çãoéàü']
)
def test_hash_senha_e_verifica(senha_plana: str):
	hash_gerado = gerar_hash_senha(senha_plana)
	assert hash_gerado != senha_plana
	assert verificar_senha(senha_plana, hash_gerado) is True
	assert verificar_senha('senha-errada', hash_gerado) is False


def test_hash_senha_gera_hashes_distintos_para_mesma_senha():
	senha_plana = 'mesma-senha'
	assert gerar_hash_senha(senha_plana) != gerar_hash_senha(senha_plana)
