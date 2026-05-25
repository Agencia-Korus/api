from datetime import datetime

from core.constants import USER_AGENT_MAX_LENGTH
from core.enums import ConsentimentoTipo
from pydantic import BaseModel, ConfigDict, Field, IPvAnyAddress


class ConsentimentoLgpdCriar(BaseModel):
	"""Classe que define os dados de consentimento LGPD usados pela API."""

	usuario_id: int | None = None
	tipo: ConsentimentoTipo
	aceito: bool
	ip: IPvAnyAddress | None = None
	user_agent: str | None = Field(default=None, max_length=USER_AGENT_MAX_LENGTH)


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
