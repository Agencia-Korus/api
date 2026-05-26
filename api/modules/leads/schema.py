from datetime import date, datetime

from core.constants import (
	TAMANHO_MAXIMO_NOME,
	TAMANHO_MAXIMO_ORCAMENTO,
	TAMANHO_MAXIMO_RAZAO_SOCIAL,
	TAMANHO_MAXIMO_TELEFONE,
)
from core.enums import LeadPrioridade, SituacaoLead
from pydantic import BaseModel, ConfigDict, EmailStr, Field


class LeadBase(BaseModel):
	"""Classe que define os dados de lead usados pela API."""

	nome: str = Field(max_length=TAMANHO_MAXIMO_NOME)
	email: EmailStr
	whatsapp: str | None = Field(default=None, max_length=TAMANHO_MAXIMO_TELEFONE)
	empresa: str | None = Field(default=None, max_length=TAMANHO_MAXIMO_RAZAO_SOCIAL)
	orcamento: str | None = Field(default=None, max_length=TAMANHO_MAXIMO_ORCAMENTO)
	prazo_desejado: date | None = None
	mensagem: str | None = None
	servico_id: int | None = None


class LeadCriar(LeadBase):
	"""Classe que define os dados de lead usados pela API."""

	status: SituacaoLead = SituacaoLead.NOVO
	prioridade: LeadPrioridade = LeadPrioridade.MEDIA
	termos_aceitos: bool = False

	model_config = ConfigDict(
		json_schema_extra={
			'example': {
				'nome': 'Marina Souza',
				'email': 'marina@empresa.com.br',
				'whatsapp': '+5511999999999',
				'empresa': 'Empresa Exemplo',
				'orcamento': 'R$ 10.000,00',
				'prazo_desejado': '2026-06-30',
				'mensagem': 'Gostaria de uma proposta para identidade visual.',
				'servico_id': 1,
				'status': 'novo',
				'prioridade': 'media',
				'termos_aceitos': True,
			}
		}
	)


class LeadAtualizar(BaseModel):
	"""Classe que define os dados de lead usados pela API."""

	nome: str | None = Field(default=None, max_length=TAMANHO_MAXIMO_NOME)
	email: EmailStr | None = None
	whatsapp: str | None = Field(default=None, max_length=TAMANHO_MAXIMO_TELEFONE)
	empresa: str | None = Field(default=None, max_length=TAMANHO_MAXIMO_RAZAO_SOCIAL)
	orcamento: str | None = Field(default=None, max_length=TAMANHO_MAXIMO_ORCAMENTO)
	prazo_desejado: date | None = None
	mensagem: str | None = None
	servico_id: int | None = None
	status: SituacaoLead | None = None
	prioridade: LeadPrioridade | None = None
	termos_aceitos: bool | None = None

	model_config = ConfigDict(
		json_schema_extra={
			'example': {
				'status': 'qualificado',
				'prioridade': 'alta',
				'mensagem': 'Lead pediu retorno por WhatsApp.',
			}
		}
	)


class LeadResposta(LeadBase):
	"""Classe que define os dados de lead usados pela API."""

	id: int
	status: SituacaoLead
	prioridade: LeadPrioridade
	termos_aceitos: bool
	data: datetime
	model_config = ConfigDict(from_attributes=True)
