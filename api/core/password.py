import bcrypt


def hash_password(plain: str) -> str:
	"""Função para gerar o hash seguro de uma senha."""
	return bcrypt.hashpw(plain.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')


def verify_password(plain: str, hashed: str) -> bool:
	"""Função para validar uma senha contra seu hash."""
	try:
		return bcrypt.checkpw(plain.encode('utf-8'), hashed.encode('utf-8'))
	except ValueError:
		return False
