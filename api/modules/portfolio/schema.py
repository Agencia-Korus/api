from datetime import datetime

from core.constants import (
	CATEGORIA_MAX_LENGTH,
	NOME_MAX_LENGTH,
	TITULO_MAX_LENGTH,
	URL_MAX_LENGTH,
)
from pydantic import BaseModel, ConfigDict, Field


class PortfolioBase(BaseModel):
	"""Classe que define os dados de portfólio usados pela API."""

	nome: str = Field(max_length=TITULO_MAX_LENGTH)
	projeto_id: int | None = None
	cliente: str | None = Field(default=None, max_length=NOME_MAX_LENGTH)
	categoria: str | None = Field(default=None, max_length=CATEGORIA_MAX_LENGTH)
	descricao: str | None = None
	imagem: str | None = Field(default=None, max_length=URL_MAX_LENGTH)
	ano: int | None = None
	destaque: bool = False
	tags: list[str] = Field(default_factory=list)


class PortfolioCreate(PortfolioBase):
	"""Classe que define os dados de portfólio usados pela API."""

	pass


class PortfolioUpdate(BaseModel):
	"""Classe que define os dados de portfólio usados pela API."""

	nome: str | None = Field(default=None, max_length=TITULO_MAX_LENGTH)
	cliente: str | None = Field(default=None, max_length=NOME_MAX_LENGTH)
	categoria: str | None = Field(default=None, max_length=CATEGORIA_MAX_LENGTH)
	descricao: str | None = None
	imagem: str | None = Field(default=None, max_length=URL_MAX_LENGTH)
	ano: int | None = None
	destaque: bool | None = None
	tags: list[str] | None = None


class PortfolioResponse(PortfolioBase):
	"""Classe que define os dados de portfólio usados pela API."""

	id: int
	criado_em: datetime
	model_config = ConfigDict(from_attributes=True)
