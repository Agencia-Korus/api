from pydantic import BaseModel, ConfigDict, EmailStr, Field

from auth.model import UserRole, UserStatus

NOME_MAX_LENGTH = 150
TELEFONE_MAX_LENGTH = 20
DOCUMENTO_MAX_LENGTH = 20
RAZAO_SOCIAL_MAX_LENGTH = 200
CARGO_MAX_LENGTH = 100
SEGMENTO_MAX_LENGTH = 100
SENHA_MIN_LENGTH = 8


class ClientePayload(BaseModel):
	razao_social: str | None = Field(default=None, max_length=RAZAO_SOCIAL_MAX_LENGTH)
	cnpj_cpf: str | None = Field(default=None, max_length=DOCUMENTO_MAX_LENGTH)
	segmento: str | None = Field(default=None, max_length=SEGMENTO_MAX_LENGTH)


class FuncionarioPayload(BaseModel):
	cargo: str | None = Field(default=None, max_length=CARGO_MAX_LENGTH)
	especialidade: str | None = Field(default=None, max_length=CARGO_MAX_LENGTH)


class AdminPayload(BaseModel):
	nivel_acesso: int = 1


class RegisterRequest(BaseModel):
	nome: str = Field(max_length=NOME_MAX_LENGTH)
	email: EmailStr
	senha: str = Field(min_length=SENHA_MIN_LENGTH)
	role: UserRole = UserRole.CLIENTE
	telefone: str | None = Field(default=None, max_length=TELEFONE_MAX_LENGTH)
	cliente: ClientePayload | None = None
	funcionario: FuncionarioPayload | None = None
	admin: AdminPayload | None = None


class LoginRequest(BaseModel):
	email: EmailStr
	senha: str


class RefreshRequest(BaseModel):
	refresh_token: str


class TokenResponse(BaseModel):
	access_token: str
	refresh_token: str
	token_type: str = 'bearer'


class UsuarioInfo(BaseModel):
	id: int
	nome: str
	email: str
	role: UserRole
	status: UserStatus

	model_config = ConfigDict(from_attributes=True)
