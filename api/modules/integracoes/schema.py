from datetime import datetime
from typing import Literal

from core.enums import IntegracaoStatus
from pydantic import BaseModel, ConfigDict, Field

from core.constants import CHAVE_INTEGRACAO_MAX_LENGTH, SEGMENTO_MAX_LENGTH

GOOGLE_CALENDAR_INTEGRATION = 'google_calendar'


class IntegracaoBase(BaseModel):
	nome: str = Field(max_length=SEGMENTO_MAX_LENGTH)
	chave: str | None = Field(default=None, max_length=CHAVE_INTEGRACAO_MAX_LENGTH)
	status: IntegracaoStatus = IntegracaoStatus.DESCONECTADO


class IntegracaoCreate(IntegracaoBase):
	nome: Literal['google_calendar'] = Field(
		default=GOOGLE_CALENDAR_INTEGRATION,
		description='Única integração permitida: Google Calendar.',
	)
	chave: str | None = Field(
		default=None,
		max_length=CHAVE_INTEGRACAO_MAX_LENGTH,
		description='ID do calendário Google ou identificador de configuração.',
	)
	model_config = ConfigDict(
		json_schema_extra={
			'example': {
				'nome': GOOGLE_CALENDAR_INTEGRATION,
				'chave': 'primary',
				'status': 'conectado',
			}
		}
	)


class IntegracaoUpdate(BaseModel):
	chave: str | None = Field(
		default=None,
		max_length=CHAVE_INTEGRACAO_MAX_LENGTH,
		description='ID do calendário Google ou identificador de configuração.',
	)
	status: IntegracaoStatus | None = None
	model_config = ConfigDict(
		json_schema_extra={'example': {'chave': 'primary', 'status': 'conectado'}}
	)


class IntegracaoResponse(IntegracaoBase):
	id: int
	atualizado_em: datetime
	model_config = ConfigDict(from_attributes=True)
