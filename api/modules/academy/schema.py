from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field

from core.constants import TITULO_MAX_LENGTH, URL_MAX_LENGTH
from core.enums import AcademyTipo


class AcademyBase(BaseModel):
	titulo: str = Field(max_length=TITULO_MAX_LENGTH)
	tipo: AcademyTipo
	descricao: str | None = None
	preco: Decimal = Decimal('0.00')
	imagem: str | None = Field(default=None, max_length=URL_MAX_LENGTH)
	url_externa: str = Field(max_length=URL_MAX_LENGTH)
	publicado: bool = False


class AcademyCreate(AcademyBase):
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


class AcademyUpdate(BaseModel):
	titulo: str | None = Field(default=None, max_length=TITULO_MAX_LENGTH)
	tipo: AcademyTipo | None = None
	descricao: str | None = None
	preco: Decimal | None = None
	imagem: str | None = Field(default=None, max_length=URL_MAX_LENGTH)
	url_externa: str | None = Field(default=None, max_length=URL_MAX_LENGTH)
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


class AcademyResponse(AcademyBase):
	id: int
	criado_em: datetime
	model_config = ConfigDict(from_attributes=True)
