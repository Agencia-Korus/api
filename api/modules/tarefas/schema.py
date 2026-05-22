from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field

from core.constants import (
	PAPEL_MAX_LENGTH,
	TIPO_ARQUIVO_MAX_LENGTH,
	TITULO_MAX_LENGTH,
	URL_MAX_LENGTH,
)
from core.enums import Complexidade, Prioridade, TarefaStatus


class TarefaBase(BaseModel):
	projeto_id: int
	responsavel_id: int | None = None
	titulo: str = Field(max_length=TITULO_MAX_LENGTH)
	descricao: str | None = None
	categoria: str | None = Field(default=None, max_length=PAPEL_MAX_LENGTH)
	prazo: date | None = None
	ordem: int = 0


class TarefaCreate(TarefaBase):
	status: TarefaStatus = TarefaStatus.A_FAZER
	complexidade: Complexidade = Complexidade.MEDIA
	prioridade: Prioridade = Prioridade.MEDIA


class TarefaUpdate(BaseModel):
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
	id: int
	status: TarefaStatus
	complexidade: Complexidade
	prioridade: Prioridade
	criado_em: datetime
	concluido_em: datetime | None
	model_config = ConfigDict(from_attributes=True)


class ComentarioCreate(BaseModel):
	tarefa_id: int
	conteudo: str


class ComentarioResponse(BaseModel):
	id: int
	tarefa_id: int
	autor_id: int
	conteudo: str
	criado_em: datetime
	model_config = ConfigDict(from_attributes=True)


class AnexoCreate(BaseModel):
	tarefa_id: int
	nome: str = Field(max_length=TITULO_MAX_LENGTH)
	url: str = Field(max_length=URL_MAX_LENGTH)
	tipo: str | None = Field(default=None, max_length=TIPO_ARQUIVO_MAX_LENGTH)
	tamanho: int | None = None


class AnexoResponse(AnexoCreate):
	id: int
	criado_em: datetime
	model_config = ConfigDict(from_attributes=True)