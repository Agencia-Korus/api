from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from core.constants import (
	ICONE_MAX_LENGTH,
	NOME_MAX_LENGTH,
	SLUG_MAX_LENGTH,
	URL_MAX_LENGTH,
)
from core.enums import ServicoStatus


class ServicoBase(BaseModel):
	nome: str = Field(max_length=NOME_MAX_LENGTH)
	slug: str = Field(max_length=SLUG_MAX_LENGTH)
	descricao: str | None = None
	icone: str | None = Field(default=None, max_length=ICONE_MAX_LENGTH)
	status: ServicoStatus = ServicoStatus.ATIVO


class ServicoCreate(ServicoBase):
	pass


class ServicoUpdate(BaseModel):
	nome: str | None = Field(default=None, max_length=NOME_MAX_LENGTH)
	slug: str | None = Field(default=None, max_length=SLUG_MAX_LENGTH)
	descricao: str | None = None
	icone: str | None = Field(default=None, max_length=ICONE_MAX_LENGTH)
	status: ServicoStatus | None = None


class ServicoResponse(ServicoBase):
	id: int
	criado_em: datetime
	model_config = ConfigDict(from_attributes=True)


class EntregavelBase(BaseModel):
	descricao: str = Field(max_length=URL_MAX_LENGTH)
	ordem: int = 0


class EntregavelCreate(EntregavelBase):
	servico_id: int


class EntregavelUpdate(BaseModel):
	descricao: str | None = Field(default=None, max_length=URL_MAX_LENGTH)
	ordem: int | None = None


class EntregavelResponse(EntregavelBase):
	id: int
	servico_id: int
	model_config = ConfigDict(from_attributes=True)
