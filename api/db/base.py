from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import DeclarativeBase


class Base(AsyncAttrs, DeclarativeBase):
	"""Classe base declarativa dos modelos SQLAlchemy."""

	pass
