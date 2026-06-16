from pydantic import BaseModel


class UploadResposta(BaseModel):
	"""Resposta com a URL pública da imagem enviada ao storage."""

	url: str
