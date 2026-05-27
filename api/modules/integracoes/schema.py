from datetime import datetime
from typing import Literal

from core.constants import TAMANHO_MAXIMO_CHAVE_INTEGRACAO, TAMANHO_MAXIMO_SEGMENTO
from core.enums import SituacaoIntegracao
from pydantic import BaseModel, ConfigDict, Field

INTEGRACAO_GOOGLE_CALENDAR = 'google_calendar'


class IntegracaoBase(BaseModel):
	"""Classe que define os dados de integração usados pela API."""

	nome: str = Field(max_length=TAMANHO_MAXIMO_SEGMENTO)
	chave: str | None = Field(default=None, max_length=TAMANHO_MAXIMO_CHAVE_INTEGRACAO)
	status: SituacaoIntegracao = SituacaoIntegracao.DESCONECTADO


class IntegracaoCriar(IntegracaoBase):
	"""Classe que define os dados de integração usados pela API."""

	nome: Literal['google_calendar'] = Field(
		default=INTEGRACAO_GOOGLE_CALENDAR,
		description='Única integração permitida: Google Calendar.',
	)
	chave: str | None = Field(
		default=None,
		max_length=TAMANHO_MAXIMO_CHAVE_INTEGRACAO,
		description='ID do calendário Google ou identificador de configuração.',
	)
	model_config = ConfigDict(
		json_schema_extra={
			'example': {
				'nome': INTEGRACAO_GOOGLE_CALENDAR,
				'chave': 'primary',
				'status': 'conectado',
			}
		}
	)


class IntegracaoAtualizar(BaseModel):
	"""Classe que define os dados de integração usados pela API."""

	chave: str | None = Field(
		default=None,
		max_length=TAMANHO_MAXIMO_CHAVE_INTEGRACAO,
		description='ID do calendário Google ou identificador de configuração.',
	)
	status: SituacaoIntegracao | None = None
	model_config = ConfigDict(
		json_schema_extra={'example': {'chave': 'primary', 'status': 'conectado'}}
	)


class IntegracaoResposta(IntegracaoBase):
	"""Classe que define os dados de integração usados pela API."""

	id: int
	atualizado_em: datetime
	model_config = ConfigDict(from_attributes=True)
