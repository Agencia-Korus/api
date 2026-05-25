from fastapi import HTTPException, status


class NotFoundError(HTTPException):
	"""Exceção HTTP usada quando um recurso não é encontrado."""

	def __init__(self, entity: str, identifier: str | int):
		"""Função para inicializar a instância com suas dependências."""
		super().__init__(
			status_code=status.HTTP_404_NOT_FOUND,
			detail=f'{entity} com identificador {identifier} não encontrado',
		)


class ConflictError(HTTPException):
	"""Exceção HTTP usada quando há conflito de dados."""

	def __init__(self, message: str):
		"""Função para inicializar a instância com suas dependências."""
		super().__init__(status_code=status.HTTP_409_CONFLICT, detail=message)


class BadRequestError(HTTPException):
	"""Exceção HTTP usada quando a requisição é inválida."""

	def __init__(self, message: str):
		"""Função para inicializar a instância com suas dependências."""
		super().__init__(status_code=status.HTTP_400_BAD_REQUEST, detail=message)
