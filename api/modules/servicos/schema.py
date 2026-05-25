from datetime import datetime

from core.constants import (
	ICONE_MAX_LENGTH,
	NOME_MAX_LENGTH,
	SLUG_MAX_LENGTH,
	URL_MAX_LENGTH,
)
from core.enums import ServicoStatus
from pydantic import BaseModel, ConfigDict, Field


class ServicoBase(BaseModel):
	"""Classe que define os dados de serviço usados pela API."""

	nome: str = Field(max_length=NOME_MAX_LENGTH)
	slug: str = Field(max_length=SLUG_MAX_LENGTH)
	descricao: str | None = None
	icone: str | None = Field(default=None, max_length=ICONE_MAX_LENGTH)
	status: ServicoStatus = ServicoStatus.ATIVO


class ServicoCreate(ServicoBase):
	"""Classe que define os dados de serviço usados pela API."""

	pass


class ServicoUpdate(BaseModel):
	"""Classe que define os dados de serviço usados pela API."""

	nome: str | None = Field(default=None, max_length=NOME_MAX_LENGTH)
	slug: str | None = Field(default=None, max_length=SLUG_MAX_LENGTH)
	descricao: str | None = None
	icone: str | None = Field(default=None, max_length=ICONE_MAX_LENGTH)
	status: ServicoStatus | None = None


class ServicoResponse(ServicoBase):
	"""Classe que define os dados de serviço usados pela API."""

	id: int
	criado_em: datetime
	model_config = ConfigDict(from_attributes=True)


class EntregavelBase(BaseModel):
	"""Classe que define os dados de entregável usados pela API."""

	descricao: str = Field(max_length=URL_MAX_LENGTH)
	ordem: int = 0


class EntregavelCreate(EntregavelBase):
	"""Classe que define os dados de entregável usados pela API."""

	servico_id: int


class EntregavelUpdate(BaseModel):
	"""Classe que define os dados de entregável usados pela API."""

	descricao: str | None = Field(default=None, max_length=URL_MAX_LENGTH)
	ordem: int | None = None


class EntregavelResponse(EntregavelBase):
	"""Classe que define os dados de entregável usados pela API."""

	id: int
	servico_id: int
	model_config = ConfigDict(from_attributes=True)
