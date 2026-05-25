from datetime import datetime

from core.constants import TITULO_MAX_LENGTH
from core.enums import ComunicadoAlvo
from pydantic import BaseModel, ConfigDict, Field


class ComunicadoBase(BaseModel):
	"""Classe que define os dados de comunicado usados pela API."""

	titulo: str = Field(max_length=TITULO_MAX_LENGTH)
	conteudo: str
	alvo: ComunicadoAlvo = ComunicadoAlvo.TODOS


class ComunicadoCreate(ComunicadoBase):
	"""Classe que define os dados de comunicado usados pela API."""

	autor_id: int

	model_config = ConfigDict(
		json_schema_extra={
			'example': {
				'titulo': 'Novo projeto aprovado!',
				'conteudo': (
					'O projeto de identidade visual foi aprovado. '
					'Equipe de design, preparem-se!'
				),
				'alvo': 'todos',
				'autor_id': 1,
			}
		}
	)


class ComunicadoUpdate(BaseModel):
	"""Classe que define os dados de comunicado usados pela API."""

	titulo: str | None = Field(default=None, max_length=TITULO_MAX_LENGTH)
	conteudo: str | None = None
	alvo: ComunicadoAlvo | None = None


class ComunicadoResponse(ComunicadoBase):
	"""Classe que define os dados de comunicado usados pela API."""

	id: int
	autor_id: int
	data: datetime
	model_config = ConfigDict(from_attributes=True)


class ComunicadoLeituraResponse(BaseModel):
	"""Classe que define os dados de leitura de comunicado usados pela API."""

	comunicado_id: int
	usuario_id: int
	lido_em: datetime
	model_config = ConfigDict(from_attributes=True)
