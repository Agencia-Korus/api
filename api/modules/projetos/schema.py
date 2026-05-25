from datetime import date, datetime

from core.constants import (
	PAPEL_MAX_LENGTH,
	PROGRESSO_MAX,
	PROGRESSO_MIN,
	TITULO_MAX_LENGTH,
)
from core.enums import ProjetoStatus
from pydantic import BaseModel, ConfigDict, Field


class ProjetoBase(BaseModel):
	"""Classe que define os dados de projeto usados pela API."""

	nome: str = Field(max_length=TITULO_MAX_LENGTH)
	descricao: str | None = None
	cliente_id: int
	servico_id: int | None = None
	data_inicio: date | None = None
	data_fim: date | None = None


class ProjetoCriar(ProjetoBase):
	"""Classe que define os dados de projeto usados pela API."""

	status: ProjetoStatus = ProjetoStatus.PLANEJAMENTO
	progresso: int = Field(default=PROGRESSO_MIN, ge=PROGRESSO_MIN, le=PROGRESSO_MAX)


class ProjetoAtualizar(BaseModel):
	"""Classe que define os dados de projeto usados pela API."""

	nome: str | None = Field(default=None, max_length=TITULO_MAX_LENGTH)
	descricao: str | None = None
	servico_id: int | None = None
	data_inicio: date | None = None
	data_fim: date | None = None
	status: ProjetoStatus | None = None
	progresso: int | None = Field(default=None, ge=PROGRESSO_MIN, le=PROGRESSO_MAX)


class ProjetoResposta(ProjetoBase):
	"""Classe que define os dados de projeto usados pela API."""

	id: int
	status: ProjetoStatus
	progresso: int
	criado_em: datetime
	model_config = ConfigDict(from_attributes=True)


class ProjetoFuncionarioCriar(BaseModel):
	"""Classe que define os dados de membro do projeto usados pela API."""

	funcionario_id: int
	papel: str | None = Field(default=None, max_length=PAPEL_MAX_LENGTH)


class ProjetoFuncionarioResposta(BaseModel):
	"""Classe que define os dados de membro do projeto usados pela API."""

	projeto_id: int
	funcionario_id: int
	papel: str | None
	data_entrada: date
	model_config = ConfigDict(from_attributes=True)
