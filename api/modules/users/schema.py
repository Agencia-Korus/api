from datetime import date, datetime

from core.constants import (
	CARGO_MAX_LENGTH,
	DOCUMENTO_MAX_LENGTH,
	NOME_MAX_LENGTH,
	RAZAO_SOCIAL_MAX_LENGTH,
	SEGMENTO_MAX_LENGTH,
	TELEFONE_MAX_LENGTH,
	URL_MAX_LENGTH,
)
from core.enums import UserRole, UserStatus
from pydantic import BaseModel, ConfigDict, EmailStr, Field


class ClientePayload(BaseModel):
	"""Classe que define os dados de cliente usados pela API."""

	razao_social: str = Field(max_length=RAZAO_SOCIAL_MAX_LENGTH)
	cnpj_cpf: str = Field(max_length=DOCUMENTO_MAX_LENGTH)
	segmento: str | None = Field(default=None, max_length=SEGMENTO_MAX_LENGTH)


class FuncionarioPayload(BaseModel):
	"""Classe que define os dados de funcionário usados pela API."""

	cargo: str = Field(max_length=CARGO_MAX_LENGTH)
	especialidade: str | None = Field(default=None, max_length=CARGO_MAX_LENGTH)


class AdminPayload(BaseModel):
	"""Classe que define os dados de admin usados pela API."""

	nivel_acesso: int = 1


class UsuarioCreate(BaseModel):
	"""Classe que define os dados de usuário usados pela API."""

	nome: str = Field(max_length=NOME_MAX_LENGTH)
	email: EmailStr
	senha: str = Field(min_length=8)
	role: UserRole
	telefone: str | None = Field(default=None, max_length=TELEFONE_MAX_LENGTH)
	avatar: str | None = Field(default=None, max_length=URL_MAX_LENGTH)
	status: UserStatus = UserStatus.ATIVO
	cliente: ClientePayload | None = None
	funcionario: FuncionarioPayload | None = None
	admin: AdminPayload | None = None


class UsuarioRegister(BaseModel):
	"""Classe que define os dados de usuario register usados pela API."""

	nome: str = Field(max_length=NOME_MAX_LENGTH)
	email: EmailStr
	senha: str = Field(min_length=8)
	role: UserRole
	telefone: str | None = Field(default=None, max_length=TELEFONE_MAX_LENGTH)
	avatar: str | None = Field(default=None, max_length=URL_MAX_LENGTH)
	cliente: ClientePayload | None = None
	funcionario: FuncionarioPayload | None = None


class UsuarioUpdate(BaseModel):
	"""Classe que define os dados de usuário usados pela API."""

	nome: str | None = Field(default=None, max_length=NOME_MAX_LENGTH)
	email: EmailStr | None = None
	role: UserRole | None = None
	telefone: str | None = Field(default=None, max_length=TELEFONE_MAX_LENGTH)
	avatar: str | None = Field(default=None, max_length=URL_MAX_LENGTH)
	status: UserStatus | None = None


class UsuarioResponse(BaseModel):
	"""Classe que define os dados de usuário usados pela API."""

	id: int
	nome: str
	email: str
	role: UserRole
	status: UserStatus
	avatar: str | None
	telefone: str | None
	criado_em: datetime
	atualizado_em: datetime


class ClienteResponse(ClientePayload):
	"""Classe que define os dados de cliente usados pela API."""

	id: int
	model_config = ConfigDict(from_attributes=True)


class FuncionarioResponse(BaseModel):
	"""Classe que define os dados de funcionário usados pela API."""

	id: int
	cargo: str
	especialidade: str | None
	data_admissao: date
	xp_total: int
	nivel: int
	model_config = ConfigDict(from_attributes=True)


class AdminResponse(BaseModel):
	"""Classe que define os dados de admin usados pela API."""

	id: int
	nivel_acesso: int
	data_promocao: date
	model_config = ConfigDict(from_attributes=True)
