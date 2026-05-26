from datetime import datetime

from core.constants import TAMANHO_MAXIMO_AGENTE_USUARIO
from core.enums import ConsentimentoTipo
from pydantic import BaseModel, ConfigDict, Field, IPvAnyAddress


class ConsentimentoLgpdCriar(BaseModel):
	"""Classe que define os dados de consentimento LGPD usados pela API."""

	usuario_id: int | None = None
	tipo: ConsentimentoTipo
	aceito: bool
	ip: IPvAnyAddress | None = None
	user_agent: str | None = Field(
		default=None, max_length=TAMANHO_MAXIMO_AGENTE_USUARIO
	)


class ConsentimentoLgpdResposta(BaseModel):
	"""Classe que define os dados de consentimento LGPD usados pela API."""

	id: int
	usuario_id: int | None
	tipo: ConsentimentoTipo
	aceito: bool
	ip: IPvAnyAddress | None
	user_agent: str | None
	data: datetime
	model_config = ConfigDict(from_attributes=True)
