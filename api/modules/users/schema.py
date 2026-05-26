from datetime import date, datetime

from core.constants import (
	TAMANHO_MAXIMO_CARGO,
	TAMANHO_MAXIMO_DOCUMENTO,
	TAMANHO_MAXIMO_NOME,
	TAMANHO_MAXIMO_RAZAO_SOCIAL,
	TAMANHO_MAXIMO_SEGMENTO,
	TAMANHO_MAXIMO_TELEFONE,
	TAMANHO_MAXIMO_URL,
)
from core.enums import PapelUsuario, SituacaoUsuario
from pydantic import BaseModel, ConfigDict, EmailStr, Field


class DadosCliente(BaseModel):
	"""Classe que define os dados de cliente usados pela API."""

	razao_social: str = Field(max_length=TAMANHO_MAXIMO_RAZAO_SOCIAL)
	cnpj_cpf: str = Field(max_length=TAMANHO_MAXIMO_DOCUMENTO)
	segmento: str | None = Field(default=None, max_length=TAMANHO_MAXIMO_SEGMENTO)


class DadosFuncionario(BaseModel):
	"""Classe que define os dados de funcionário usados pela API."""

	cargo: str = Field(max_length=TAMANHO_MAXIMO_CARGO)
	especialidade: str | None = Field(default=None, max_length=TAMANHO_MAXIMO_CARGO)


class DadosAdmin(BaseModel):
	"""Classe que define os dados de admin usados pela API."""

	nivel_acesso: int = 1


class UsuarioCriar(BaseModel):
	"""Classe que define os dados de usuário usados pela API."""

	nome: str = Field(max_length=TAMANHO_MAXIMO_NOME)
	email: EmailStr
	senha: str = Field(min_length=8)
	role: PapelUsuario
	telefone: str | None = Field(default=None, max_length=TAMANHO_MAXIMO_TELEFONE)
	avatar: str | None = Field(default=None, max_length=TAMANHO_MAXIMO_URL)
	status: SituacaoUsuario = SituacaoUsuario.ATIVO
	cliente: DadosCliente | None = None
	funcionario: DadosFuncionario | None = None
	admin: DadosAdmin | None = None


class UsuarioRegistrar(BaseModel):
	"""Classe que define os dados de usuario register usados pela API."""

	nome: str = Field(max_length=TAMANHO_MAXIMO_NOME)
	email: EmailStr
	senha: str = Field(min_length=8)
	role: PapelUsuario
	telefone: str | None = Field(default=None, max_length=TAMANHO_MAXIMO_TELEFONE)
	avatar: str | None = Field(default=None, max_length=TAMANHO_MAXIMO_URL)
	cliente: DadosCliente | None = None
	funcionario: DadosFuncionario | None = None


class UsuarioAtualizar(BaseModel):
	"""Classe que define os dados de usuário usados pela API."""

	nome: str | None = Field(default=None, max_length=TAMANHO_MAXIMO_NOME)
	email: EmailStr | None = None
	role: PapelUsuario | None = None
	telefone: str | None = Field(default=None, max_length=TAMANHO_MAXIMO_TELEFONE)
	avatar: str | None = Field(default=None, max_length=TAMANHO_MAXIMO_URL)
	status: SituacaoUsuario | None = None


class UsuarioResposta(BaseModel):
	"""Classe que define os dados de usuário usados pela API."""

	id: int
	nome: str
	email: str
	role: PapelUsuario
	status: SituacaoUsuario
	avatar: str | None
	telefone: str | None
	criado_em: datetime
	atualizado_em: datetime


class ClienteResposta(DadosCliente):
	"""Classe que define os dados de cliente usados pela API."""

	id: int
	model_config = ConfigDict(from_attributes=True)


class FuncionarioResposta(BaseModel):
	"""Classe que define os dados de funcionário usados pela API."""

	id: int
	cargo: str
	especialidade: str | None
	data_admissao: date
	xp_total: int
	nivel: int
	model_config = ConfigDict(from_attributes=True)


class AdminResposta(BaseModel):
	"""Classe que define os dados de admin usados pela API."""

	id: int
	nivel_acesso: int
	data_promocao: date
	model_config = ConfigDict(from_attributes=True)
