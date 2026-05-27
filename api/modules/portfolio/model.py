from datetime import datetime

from core.constants import (
	TAMANHO_MAXIMO_CATEGORIA,
	TAMANHO_MAXIMO_NOME,
	TAMANHO_MAXIMO_TITULO,
	TAMANHO_MAXIMO_URL,
)
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


class Portfolio(Base):
	"""Classe que representa a tabela de portfólio no banco de dados."""

	__tablename__ = 'portfolio'

	id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
	projeto_id: Mapped[int | None] = mapped_column(
		BigInteger, ForeignKey('projeto.id', ondelete='SET NULL')
	)
	nome: Mapped[str] = mapped_column(String(TAMANHO_MAXIMO_TITULO), nullable=False)
	cliente: Mapped[str | None] = mapped_column(String(TAMANHO_MAXIMO_NOME))
	categoria: Mapped[str | None] = mapped_column(String(TAMANHO_MAXIMO_CATEGORIA))
	descricao: Mapped[str | None] = mapped_column(Text)
	imagem: Mapped[str | None] = mapped_column(String(TAMANHO_MAXIMO_URL))
	ano: Mapped[int | None] = mapped_column(SmallInteger)
	destaque: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
	tags: Mapped[list[str]] = mapped_column(
		ARRAY(Text), nullable=False, default=list, server_default='{}'
	)
	criado_em: Mapped[datetime] = mapped_column(
		DateTime(timezone=True), server_default=func.now(), nullable=False
	)
