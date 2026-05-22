from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from core.constants import TITULO_MAX_LENGTH
from core.enums import ComunicadoAlvo


class ComunicadoBase(BaseModel):
	titulo: str = Field(max_length=TITULO_MAX_LENGTH)
	conteudo: str
	alvo: ComunicadoAlvo = ComunicadoAlvo.TODOS


class ComunicadoCreate(ComunicadoBase):
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
	titulo: str | None = Field(default=None, max_length=TITULO_MAX_LENGTH)
	conteudo: str | None = None
	alvo: ComunicadoAlvo | None = None


class ComunicadoResponse(ComunicadoBase):
	id: int
	autor_id: int
	data: datetime
	model_config = ConfigDict(from_attributes=True)


class ComunicadoLeituraResponse(BaseModel):
	comunicado_id: int
	usuario_id: int
	lido_em: datetime
	model_config = ConfigDict(from_attributes=True)
