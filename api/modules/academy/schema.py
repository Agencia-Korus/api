from datetime import datetime
from decimal import Decimal

from core.constants import TAMANHO_MAXIMO_TITULO, TAMANHO_MAXIMO_URL
from core.enums import TipoAcademia
from pydantic import BaseModel, ConfigDict, Field


class AcademiaBase(BaseModel):
	"""Classe que define os dados de conteúdo da Academia usados pela API."""

	titulo: str = Field(max_length=TAMANHO_MAXIMO_TITULO)
	tipo: TipoAcademia
	descricao: str | None = None
	preco: Decimal = Decimal('0.00')
	imagem: str | None = Field(default=None, max_length=TAMANHO_MAXIMO_URL)
	url_externa: str = Field(max_length=TAMANHO_MAXIMO_URL)
	publicado: bool = False


class AcademiaCriar(AcademiaBase):
	"""Classe que define os dados de conteúdo da Academia usados pela API."""

	model_config = ConfigDict(
		json_schema_extra={
			'example': {
				'titulo': 'Marketing Digital do Zero',
				'tipo': 'curso',
				'descricao': 'Aprenda as bases do marketing digital com a Korus.',
				'preco': '197.00',
				'imagem': 'https://cdn.korus.com.br/academy/marketing.png',
				'url_externa': 'https://korus.com.br/academy/marketing-digital',
				'publicado': True,
			}
		}
	)


class AcademiaAtualizar(BaseModel):
	"""Classe que define os dados de conteúdo da Academia usados pela API."""

	titulo: str | None = Field(default=None, max_length=TAMANHO_MAXIMO_TITULO)
	tipo: TipoAcademia | None = None
	descricao: str | None = None
	preco: Decimal | None = None
	imagem: str | None = Field(default=None, max_length=TAMANHO_MAXIMO_URL)
	url_externa: str | None = Field(default=None, max_length=TAMANHO_MAXIMO_URL)
	publicado: bool | None = None

	model_config = ConfigDict(
		json_schema_extra={
			'example': {
				'titulo': 'Marketing Digital do Zero',
				'descricao': 'Conteúdo atualizado para publicação.',
				'preco': '197.00',
				'publicado': True,
			}
		}
	)


class AcademiaResposta(AcademiaBase):
	"""Classe que define os dados de conteúdo da Academia usados pela API."""

	id: int
	criado_em: datetime
	model_config = ConfigDict(from_attributes=True)
