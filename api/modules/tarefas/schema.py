from datetime import date, datetime

from core.constants import (
	PAPEL_MAX_LENGTH,
	TIPO_ARQUIVO_MAX_LENGTH,
	TITULO_MAX_LENGTH,
	URL_MAX_LENGTH,
)
from core.enums import Complexidade, Prioridade, TarefaStatus
from pydantic import BaseModel, ConfigDict, Field


class TarefaBase(BaseModel):
	"""Classe que define os dados de tarefa usados pela API."""

	projeto_id: int
	responsavel_id: int | None = None
	titulo: str = Field(max_length=TITULO_MAX_LENGTH)
	descricao: str | None = None
	categoria: str | None = Field(default=None, max_length=PAPEL_MAX_LENGTH)
	prazo: date | None = None
	ordem: int = 0


class TarefaCreate(TarefaBase):
	"""Classe que define os dados de tarefa usados pela API."""

	status: TarefaStatus = TarefaStatus.A_FAZER
	complexidade: Complexidade = Complexidade.MEDIA
	prioridade: Prioridade = Prioridade.MEDIA


class TarefaUpdate(BaseModel):
	"""Classe que define os dados de tarefa usados pela API."""

	responsavel_id: int | None = None
	titulo: str | None = Field(default=None, max_length=TITULO_MAX_LENGTH)
	descricao: str | None = None
	categoria: str | None = Field(default=None, max_length=PAPEL_MAX_LENGTH)
	prazo: date | None = None
	ordem: int | None = None
	status: TarefaStatus | None = None
	complexidade: Complexidade | None = None
	prioridade: Prioridade | None = None


class TarefaResponse(TarefaBase):
	"""Classe que define os dados de tarefa usados pela API."""

	id: int
	status: TarefaStatus
	complexidade: Complexidade
	prioridade: Prioridade
	criado_em: datetime
	concluido_em: datetime | None
	model_config = ConfigDict(from_attributes=True)


class ComentarioCreate(BaseModel):
	"""Classe que define os dados de comentário usados pela API."""

	tarefa_id: int
	conteudo: str


class ComentarioResponse(BaseModel):
	"""Classe que define os dados de comentário usados pela API."""

	id: int
	tarefa_id: int
	autor_id: int
	conteudo: str
	criado_em: datetime
	model_config = ConfigDict(from_attributes=True)


class AnexoCreate(BaseModel):
	"""Classe que define os dados de anexo usados pela API."""

	tarefa_id: int
	nome: str = Field(max_length=TITULO_MAX_LENGTH)
	url: str = Field(max_length=URL_MAX_LENGTH)
	tipo: str | None = Field(default=None, max_length=TIPO_ARQUIVO_MAX_LENGTH)
	tamanho: int | None = None


class AnexoResponse(AnexoCreate):
	"""Classe que define os dados de anexo usados pela API."""

	id: int
	criado_em: datetime
	model_config = ConfigDict(from_attributes=True)
