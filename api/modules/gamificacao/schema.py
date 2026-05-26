from datetime import datetime

from core.constants import (
	TAMANHO_MAXIMO_ACAO_XP,
	TAMANHO_MAXIMO_ICONE,
	TAMANHO_MAXIMO_NOME,
	XP_MINIMO,
)
from core.enums import Complexidade
from pydantic import BaseModel, ConfigDict, Field


class RegraXpBase(BaseModel):
	"""Classe que define os dados de regra de XP usados pela API."""

	tarefa: str = Field(max_length=TAMANHO_MAXIMO_NOME)
	complexidade: Complexidade
	xp: int = Field(ge=XP_MINIMO)


class RegraXpCriar(RegraXpBase):
	"""Classe que define os dados de regra de XP usados pela API."""

	pass


class RegraXpAtualizar(BaseModel):
	"""Classe que define os dados de regra de XP usados pela API."""

	tarefa: str | None = Field(default=None, max_length=TAMANHO_MAXIMO_NOME)
	complexidade: Complexidade | None = None
	xp: int | None = Field(default=None, ge=XP_MINIMO)


class RegraXpResposta(RegraXpBase):
	"""Classe que define os dados de regra de XP usados pela API."""

	id: int
	model_config = ConfigDict(from_attributes=True)


class HistoricoXpCriar(BaseModel):
	"""Classe que define os dados de histórico de XP usados pela API."""

	funcionario_id: int
	tarefa_id: int | None = None
	regra_id: int | None = None
	acao: str = Field(max_length=TAMANHO_MAXIMO_ACAO_XP)
	xp: int


class HistoricoXpResposta(HistoricoXpCriar):
	"""Classe que define os dados de histórico de XP usados pela API."""

	id: int
	data: datetime
	model_config = ConfigDict(from_attributes=True)


class ConquistaBase(BaseModel):
	"""Classe que define os dados de conquista usados pela API."""

	nome: str = Field(max_length=TAMANHO_MAXIMO_NOME)
	icone: str | None = Field(default=None, max_length=TAMANHO_MAXIMO_ICONE)
	descricao: str | None = None
	xp_bonus: int = 0


class ConquistaCriar(ConquistaBase):
	"""Classe que define os dados de conquista usados pela API."""

	pass


class ConquistaAtualizar(BaseModel):
	"""Classe que define os dados de conquista usados pela API."""

	nome: str | None = Field(default=None, max_length=TAMANHO_MAXIMO_NOME)
	icone: str | None = Field(default=None, max_length=TAMANHO_MAXIMO_ICONE)
	descricao: str | None = None
	xp_bonus: int | None = None


class ConquistaResposta(ConquistaBase):
	"""Classe que define os dados de conquista usados pela API."""

	id: int
	model_config = ConfigDict(from_attributes=True)


class FuncionarioConquistaResposta(BaseModel):
	"""Classe que define os dados de conquista do funcionário usados pela API."""

	funcionario_id: int
	conquista_id: int
	desbloqueado_em: datetime
	model_config = ConfigDict(from_attributes=True)
