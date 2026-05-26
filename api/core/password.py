import bcrypt


def gerar_hash_senha(senha_plana: str) -> str:
	"""Função para gerar o hash seguro de uma senha."""
	return bcrypt.hashpw(senha_plana.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')


def verificar_senha(senha_plana: str, hash_gerado: str) -> bool:
	"""Função para validar uma senha contra seu hash."""
	try:
		return bcrypt.checkpw(senha_plana.encode('utf-8'), hash_gerado.encode('utf-8'))
	except ValueError:
		return False
