import pytest

from core.password import hash_password, verify_password

@pytest.mark.parametrize(
    'plain',
    ['secreta-123', 'outra-coisa-segura!', 'çãoéàü']
)

def test_hash_password_e_verifica(plain: str):
    hashed = hash_password(plain)
    assert hashed != plain
    assert verify_password(plain, hashed) is True
    assert verify_password('senha-errada', hashed) is False

def test_hash_password_gera_hashes_distintos_para_mesma_senha():
    plain = 'mesma-senha'
    assert hash_password(plain) != hash_password(plain)
