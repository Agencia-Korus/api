from datetime import datetime

from db.base import Base
from sqlalchemy import (
	BigInteger,
	Boolean,
	DateTime,
	ForeignKey,
	SmallInteger,
	String,
	Text,
	func,
)
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import Mapped, mapped_column

from core.constants import (
	CATEGORIA_MAX_LENGTH,
	NOME_MAX_LENGTH,
	TITULO_MAX_LENGTH,
	URL_MAX_LENGTH,
)


class Portfolio(Base):
	__tablename__ = 'portfolio'

	id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
	projeto_id: Mapped[int | None] = mapped_column(
		BigInteger, ForeignKey('projeto.id', ondelete='SET NULL')
	)
	nome: Mapped[str] = mapped_column(String(TITULO_MAX_LENGTH), nullable=False)
	cliente: Mapped[str | None] = mapped_column(String(NOME_MAX_LENGTH))
	categoria: Mapped[str | None] = mapped_column(String(CATEGORIA_MAX_LENGTH))
	descricao: Mapped[str | None] = mapped_column(Text)
	imagem: Mapped[str | None] = mapped_column(String(URL_MAX_LENGTH))
	ano: Mapped[int | None] = mapped_column(SmallInteger)
	destaque: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
	tags: Mapped[list[str]] = mapped_column(
		ARRAY(Text), nullable=False, default=list, server_default='{}'
	)
	criado_em: Mapped[datetime] = mapped_column(
		DateTime(timezone=True), server_default=func.now(), nullable=False
	)
