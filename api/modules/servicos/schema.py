from datetime import datetime

from core.constants import (
	TAMANHO_MAXIMO_ICONE,
	TAMANHO_MAXIMO_NOME,
	TAMANHO_MAXIMO_SLUG,
	TAMANHO_MAXIMO_URL,
)
from core.enums import SituacaoServico
from pydantic import BaseModel, ConfigDict, Field


class ServicoBase(BaseModel):
	"""Classe que define os dados de serviço usados pela API."""

	nome: str = Field(max_length=TAMANHO_MAXIMO_NOME)
	slug: str = Field(max_length=TAMANHO_MAXIMO_SLUG)
	descricao: str | None = None
	icone: str | None = Field(default=None, max_length=TAMANHO_MAXIMO_ICONE)
	status: SituacaoServico = SituacaoServico.ATIVO


class ServicoCriar(ServicoBase):
	"""Classe que define os dados de serviço usados pela API."""

	model_config = ConfigDict(
		json_schema_extra={
			'example': {
				'nome': 'Identidade Visual',
				'slug': 'identidade-visual',
				'descricao': 'Criação de marca, manual e aplicações.',
				'icone': 'palette',
				'status': 'ativo',
			}
		}
	)


class ServicoAtualizar(BaseModel):
	"""Classe que define os dados de serviço usados pela API."""

	nome: str | None = Field(default=None, max_length=TAMANHO_MAXIMO_NOME)
	slug: str | None = Field(default=None, max_length=TAMANHO_MAXIMO_SLUG)
	descricao: str | None = None
	icone: str | None = Field(default=None, max_length=TAMANHO_MAXIMO_ICONE)
	status: SituacaoServico | None = None

	model_config = ConfigDict(
		json_schema_extra={
			'example': {
				'nome': 'Branding completo',
				'slug': 'branding-completo',
				'descricao': 'Pacote completo de estratégia e identidade.',
				'status': 'ativo',
			}
		}
	)


class ServicoResposta(ServicoBase):
	"""Classe que define os dados de serviço usados pela API."""

	id: int
	criado_em: datetime
	model_config = ConfigDict(from_attributes=True)


class EntregavelBase(BaseModel):
	"""Classe que define os dados de entregável usados pela API."""

	descricao: str = Field(max_length=TAMANHO_MAXIMO_URL)
	ordem: int = 0


class EntregavelCriar(EntregavelBase):
	"""Classe que define os dados de entregável usados pela API."""

	servico_id: int

	model_config = ConfigDict(
		json_schema_extra={
			'example': {
				'descricao': 'Manual de marca em PDF',
				'ordem': 1,
				'servico_id': 1,
			}
		}
	)


class EntregavelAtualizar(BaseModel):
	"""Classe que define os dados de entregável usados pela API."""

	descricao: str | None = Field(default=None, max_length=TAMANHO_MAXIMO_URL)
	ordem: int | None = None

	model_config = ConfigDict(
		json_schema_extra={
			'example': {
				'descricao': 'Manual de marca revisado',
				'ordem': 2,
			}
		}
	)


class EntregavelResposta(EntregavelBase):
	"""Classe que define os dados de entregável usados pela API."""

	id: int
	servico_id: int
	model_config = ConfigDict(from_attributes=True)
