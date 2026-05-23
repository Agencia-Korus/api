from datetime import date, datetime

from core.enums import UserRole, UserStatus
from pydantic import BaseModel, ConfigDict, EmailStr, Field

from core.constants import (
	CARGO_MAX_LENGTH,
	DOCUMENTO_MAX_LENGTH,
	NOME_MAX_LENGTH,
	RAZAO_SOCIAL_MAX_LENGTH,
	SEGMENTO_MAX_LENGTH,
	TELEFONE_MAX_LENGTH,
	URL_MAX_LENGTH,
)


class ClientePayload(BaseModel):
	razao_social: str = Field(max_length=RAZAO_SOCIAL_MAX_LENGTH)
	cnpj_cpf: str = Field(max_length=DOCUMENTO_MAX_LENGTH)
	segmento: str | None = Field(default=None, max_length=SEGMENTO_MAX_LENGTH)


class FuncionarioPayload(BaseModel):
	cargo: str = Field(max_length=CARGO_MAX_LENGTH)
	especialidade: str | None = Field(default=None, max_length=CARGO_MAX_LENGTH)


class AdminPayload(BaseModel):
	nivel_acesso: int = 1


class UsuarioCreate(BaseModel):
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
	nome: str = Field(max_length=NOME_MAX_LENGTH)
	email: EmailStr
	senha: str = Field(min_length=8)
	role: UserRole
	telefone: str | None = Field(default=None, max_length=TELEFONE_MAX_LENGTH)
	avatar: str | None = Field(default=None, max_length=URL_MAX_LENGTH)
	cliente: ClientePayload | None = None
	funcionario: FuncionarioPayload | None = None


class UsuarioUpdate(BaseModel):
	nome: str | None = Field(default=None, max_length=NOME_MAX_LENGTH)
	email: EmailStr | None = None
	role: UserRole | None = None
	telefone: str | None = Field(default=None, max_length=TELEFONE_MAX_LENGTH)
	avatar: str | None = Field(default=None, max_length=URL_MAX_LENGTH)
	status: UserStatus | None = None


class UsuarioResponse(BaseModel):
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
	id: int
	model_config = ConfigDict(from_attributes=True)


class FuncionarioResponse(BaseModel):
	id: int
	cargo: str
	especialidade: str | None
	data_admissao: date
	xp_total: int
	nivel: int
	model_config = ConfigDict(from_attributes=True)


class AdminResponse(BaseModel):
	id: int
	nivel_acesso: int
	data_promocao: date
	model_config = ConfigDict(from_attributes=True)
