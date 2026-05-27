from fastapi import HTTPException, status


class ErroNaoEncontrado(HTTPException):
	"""Exceção HTTP usada quando um recurso não é encontrado."""

	def __init__(self, entidade: str, identificador: str | int):
		"""Função para inicializar a instância com suas dependências."""
		super().__init__(
			status_code=status.HTTP_404_NOT_FOUND,
			detail=f'{entidade} com identificador {identificador} não encontrado',
		)


class ErroConflito(HTTPException):
	"""Exceção HTTP usada quando há conflito de dados."""

	def __init__(self, mensagem: str):
		"""Função para inicializar a instância com suas dependências."""
		super().__init__(status_code=status.HTTP_409_CONFLICT, detail=mensagem)


class ErroRequisicaoInvalida(HTTPException):
	"""Exceção HTTP usada quando a requisição é inválida."""

	def __init__(self, mensagem: str):
		"""Função para inicializar a instância com suas dependências."""
		super().__init__(status_code=status.HTTP_400_BAD_REQUEST, detail=mensagem)
