from datetime import datetime

from core.constants import (
	TAMANHO_MAXIMO_ICONE,
	TAMANHO_MAXIMO_NOME,
	TAMANHO_MAXIMO_SLUG,
	TAMANHO_MAXIMO_URL,
)
from core.enums import SituacaoServico
from pydantic import BaseModel, ConfigDict, Field


class ServicoBase(BaseModel):
	"""Classe que define os dados de serviço usados pela API."""

	nome: str = Field(max_length=TAMANHO_MAXIMO_NOME)
	slug: str = Field(max_length=TAMANHO_MAXIMO_SLUG)
	descricao: str | None = None
	icone: str | None = Field(default=None, max_length=TAMANHO_MAXIMO_ICONE)
	status: SituacaoServico = SituacaoServico.ATIVO


class ServicoCriar(ServicoBase):
	"""Classe que define os dados de serviço usados pela API."""

	pass


class ServicoAtualizar(BaseModel):
	"""Classe que define os dados de serviço usados pela API."""

	nome: str | None = Field(default=None, max_length=TAMANHO_MAXIMO_NOME)
	slug: str | None = Field(default=None, max_length=TAMANHO_MAXIMO_SLUG)
	descricao: str | None = None
	icone: str | None = Field(default=None, max_length=TAMANHO_MAXIMO_ICONE)
	status: SituacaoServico | None = None


class ServicoResposta(ServicoBase):
	"""Classe que define os dados de serviço usados pela API."""

	id: int
	criado_em: datetime
	model_config = ConfigDict(from_attributes=True)


class EntregavelBase(BaseModel):
	"""Classe que define os dados de entregável usados pela API."""

	descricao: str = Field(max_length=TAMANHO_MAXIMO_URL)
	ordem: int = 0


class EntregavelCriar(EntregavelBase):
	"""Classe que define os dados de entregável usados pela API."""

	servico_id: int


class EntregavelAtualizar(BaseModel):
	"""Classe que define os dados de entregável usados pela API."""

	descricao: str | None = Field(default=None, max_length=TAMANHO_MAXIMO_URL)
	ordem: int | None = None


class EntregavelResposta(EntregavelBase):
	"""Classe que define os dados de entregável usados pela API."""

	id: int
	servico_id: int
	model_config = ConfigDict(from_attributes=True)
