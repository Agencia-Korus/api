from datetime import datetime

from core.constants import (
	TAMANHO_MAXIMO_CATEGORIA,
	TAMANHO_MAXIMO_NOME,
	TAMANHO_MAXIMO_TITULO,
	TAMANHO_MAXIMO_URL,
)
from pydantic import BaseModel, ConfigDict, Field


class PortfolioBase(BaseModel):
	"""Classe que define os dados de portfólio usados pela API."""

	nome: str = Field(max_length=TAMANHO_MAXIMO_TITULO)
	projeto_id: int | None = None
	cliente: str | None = Field(default=None, max_length=TAMANHO_MAXIMO_NOME)
	categoria: str | None = Field(default=None, max_length=TAMANHO_MAXIMO_CATEGORIA)
	descricao: str | None = None
	imagem: str | None = Field(default=None, max_length=TAMANHO_MAXIMO_URL)
	ano: int | None = None
	destaque: bool = False
	tags: list[str] = Field(default_factory=list)


class PortfolioCriar(PortfolioBase):
	"""Classe que define os dados de portfólio usados pela API."""

	pass


class PortfolioAtualizar(BaseModel):
	"""Classe que define os dados de portfólio usados pela API."""

	nome: str | None = Field(default=None, max_length=TAMANHO_MAXIMO_TITULO)
	cliente: str | None = Field(default=None, max_length=TAMANHO_MAXIMO_NOME)
	categoria: str | None = Field(default=None, max_length=TAMANHO_MAXIMO_CATEGORIA)
	descricao: str | None = None
	imagem: str | None = Field(default=None, max_length=TAMANHO_MAXIMO_URL)
	ano: int | None = None
	destaque: bool | None = None
	tags: list[str] | None = None


class PortfolioResposta(PortfolioBase):
	"""Classe que define os dados de portfólio usados pela API."""

	id: int
	criado_em: datetime
	model_config = ConfigDict(from_attributes=True)
