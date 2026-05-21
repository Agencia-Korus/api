from datetime import datetime

from pydantic import BaseModel, ConfigDict


class PostCreate(BaseModel):
	title: str
	description: str


class PostResponse(BaseModel):
	id: int
	title: str
	description: str
	created_at: datetime

	model_config = ConfigDict(from_attributes=True)
