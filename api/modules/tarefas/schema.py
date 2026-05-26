from datetime import date, datetime

from core.constants import (
	TAMANHO_MAXIMO_PAPEL,
	TAMANHO_MAXIMO_TIPO_ARQUIVO,
	TAMANHO_MAXIMO_TITULO,
	TAMANHO_MAXIMO_URL,
)
from core.enums import Complexidade, Prioridade, SituacaoTarefa
from pydantic import BaseModel, ConfigDict, Field


class TarefaBase(BaseModel):
	"""Classe que define os dados de tarefa usados pela API."""

	projeto_id: int
	responsavel_id: int | None = None
	titulo: str = Field(max_length=TAMANHO_MAXIMO_TITULO)
	descricao: str | None = None
	categoria: str | None = Field(default=None, max_length=TAMANHO_MAXIMO_PAPEL)
	prazo: date | None = None
	ordem: int = 0


class TarefaCriar(TarefaBase):
	"""Classe que define os dados de tarefa usados pela API."""

	status: SituacaoTarefa = SituacaoTarefa.A_FAZER
	complexidade: Complexidade = Complexidade.MEDIA
	prioridade: Prioridade = Prioridade.MEDIA


class TarefaAtualizar(BaseModel):
	"""Classe que define os dados de tarefa usados pela API."""

	responsavel_id: int | None = None
	titulo: str | None = Field(default=None, max_length=TAMANHO_MAXIMO_TITULO)
	descricao: str | None = None
	categoria: str | None = Field(default=None, max_length=TAMANHO_MAXIMO_PAPEL)
	prazo: date | None = None
	ordem: int | None = None
	status: SituacaoTarefa | None = None
	complexidade: Complexidade | None = None
	prioridade: Prioridade | None = None


class TarefaResposta(TarefaBase):
	"""Classe que define os dados de tarefa usados pela API."""

	id: int
	status: SituacaoTarefa
	complexidade: Complexidade
	prioridade: Prioridade
	criado_em: datetime
	concluido_em: datetime | None
	model_config = ConfigDict(from_attributes=True)


class ComentarioCriar(BaseModel):
	"""Classe que define os dados de comentário usados pela API."""

	tarefa_id: int
	conteudo: str


class ComentarioResposta(BaseModel):
	"""Classe que define os dados de comentário usados pela API."""

	id: int
	tarefa_id: int
	autor_id: int
	conteudo: str
	criado_em: datetime
	model_config = ConfigDict(from_attributes=True)


class AnexoCriar(BaseModel):
	"""Classe que define os dados de anexo usados pela API."""

	tarefa_id: int
	nome: str = Field(max_length=TAMANHO_MAXIMO_TITULO)
	url: str = Field(max_length=TAMANHO_MAXIMO_URL)
	tipo: str | None = Field(default=None, max_length=TAMANHO_MAXIMO_TIPO_ARQUIVO)
	tamanho: int | None = None


class AnexoResposta(AnexoCriar):
	"""Classe que define os dados de anexo usados pela API."""

	id: int
	criado_em: datetime
	model_config = ConfigDict(from_attributes=True)
