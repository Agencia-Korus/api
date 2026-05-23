from datetime import datetime

from core.enums import ConsentimentoTipo
from pydantic import BaseModel, ConfigDict, Field

from core.constants import USER_AGENT_MAX_LENGTH


class ConsentimentoLgpdCreate(BaseModel):
	usuario_id: int | None = None
	tipo: ConsentimentoTipo
	aceito: bool
	ip: str | None = None
	user_agent: str | None = Field(default=None, max_length=USER_AGENT_MAX_LENGTH)


class ConsentimentoLgpdResponse(BaseModel):
	id: int
	usuario_id: int | None
	tipo: ConsentimentoTipo
	aceito: bool
	ip: str | None
	user_agent: str | None
	data: datetime
	model_config = ConfigDict(from_attributes=True)
