from datetime import date, datetime

from core.enums import LeadPrioridade, LeadStatus
from pydantic import BaseModel, ConfigDict, EmailStr, Field

from core.constants import (
	NOME_MAX_LENGTH,
	ORCAMENTO_MAX_LENGTH,
	RAZAO_SOCIAL_MAX_LENGTH,
	TELEFONE_MAX_LENGTH,
)


class LeadBase(BaseModel):
	nome: str = Field(max_length=NOME_MAX_LENGTH)
	email: EmailStr
	whatsapp: str | None = Field(default=None, max_length=TELEFONE_MAX_LENGTH)
	empresa: str | None = Field(default=None, max_length=RAZAO_SOCIAL_MAX_LENGTH)
	orcamento: str | None = Field(default=None, max_length=ORCAMENTO_MAX_LENGTH)
	prazo_desejado: date | None = None
	mensagem: str | None = None
	servico_id: int | None = None


class LeadCreate(LeadBase):
	status: LeadStatus = LeadStatus.NOVO
	prioridade: LeadPrioridade = LeadPrioridade.MEDIA
	termos_aceitos: bool = False


class LeadUpdate(BaseModel):
	nome: str | None = Field(default=None, max_length=NOME_MAX_LENGTH)
	email: EmailStr | None = None
	whatsapp: str | None = Field(default=None, max_length=TELEFONE_MAX_LENGTH)
	empresa: str | None = Field(default=None, max_length=RAZAO_SOCIAL_MAX_LENGTH)
	orcamento: str | None = Field(default=None, max_length=ORCAMENTO_MAX_LENGTH)
	prazo_desejado: date | None = None
	mensagem: str | None = None
	servico_id: int | None = None
	status: LeadStatus | None = None
	prioridade: LeadPrioridade | None = None
	termos_aceitos: bool | None = None


class LeadResponse(LeadBase):
	id: int
	status: LeadStatus
	prioridade: LeadPrioridade
	termos_aceitos: bool
	data: datetime
	model_config = ConfigDict(from_attributes=True)
