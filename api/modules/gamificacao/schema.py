from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from core.constants import (
	ACAO_XP_MAX_LENGTH,
	ICONE_MAX_LENGTH,
	NOME_MAX_LENGTH,
	XP_MIN,
)
from core.enums import Complexidade


class RegraXpBase(BaseModel):
	tarefa: str = Field(max_length=NOME_MAX_LENGTH)
	complexidade: Complexidade
	xp: int = Field(ge=XP_MIN)


class RegraXpCreate(RegraXpBase):
	pass


class RegraXpUpdate(BaseModel):
	tarefa: str | None = Field(default=None, max_length=NOME_MAX_LENGTH)
	complexidade: Complexidade | None = None
	xp: int | None = Field(default=None, ge=XP_MIN)


class RegraXpResponse(RegraXpBase):
	id: int
	model_config = ConfigDict(from_attributes=True)


class HistoricoXpCreate(BaseModel):
	funcionario_id: int
	tarefa_id: int | None = None
	regra_id: int | None = None
	acao: str = Field(max_length=ACAO_XP_MAX_LENGTH)
	xp: int


class HistoricoXpResponse(HistoricoXpCreate):
	id: int
	data: datetime
	model_config = ConfigDict(from_attributes=True)


class ConquistaBase(BaseModel):
	nome: str = Field(max_length=NOME_MAX_LENGTH)
	icone: str | None = Field(default=None, max_length=ICONE_MAX_LENGTH)
	descricao: str | None = None
	xp_bonus: int = 0


class ConquistaCreate(ConquistaBase):
	pass


class ConquistaUpdate(BaseModel):
	nome: str | None = Field(default=None, max_length=NOME_MAX_LENGTH)
	icone: str | None = Field(default=None, max_length=ICONE_MAX_LENGTH)
	descricao: str | None = None
	xp_bonus: int | None = None


class ConquistaResponse(ConquistaBase):
	id: int
	model_config = ConfigDict(from_attributes=True)


class FuncionarioConquistaResponse(BaseModel):
	funcionario_id: int
	conquista_id: int
	desbloqueado_em: datetime
	model_config = ConfigDict(from_attributes=True)
