from datetime import datetime

from core.constants import TITULO_MAX_LENGTH
from core.enums import ComunicadoAlvo, enum_values
from db.base import Base
from sqlalchemy import (
	BigInteger,
	DateTime,
	ForeignKey,
	String,
	Text,
	func,
)
from sqlalchemy import (
	Enum as SAEnum,
)
from sqlalchemy.orm import Mapped, mapped_column


class Comunicado(Base):
	"""Classe que representa a tabela de comunicado no banco de dados."""

	__tablename__ = 'comunicado'

	id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
	autor_id: Mapped[int] = mapped_column(
		BigInteger, ForeignKey('admin.id', ondelete='RESTRICT'), nullable=False
	)
	titulo: Mapped[str] = mapped_column(String(TITULO_MAX_LENGTH), nullable=False)
	conteudo: Mapped[str] = mapped_column(Text, nullable=False)
	alvo: Mapped[ComunicadoAlvo] = mapped_column(
		SAEnum(
			ComunicadoAlvo,
			name='comunicado_alvo',
			create_type=False,
			values_callable=enum_values,
		),
		nullable=False,
		default=ComunicadoAlvo.TODOS,
	)
	data: Mapped[datetime] = mapped_column(
		DateTime(timezone=True), server_default=func.now(), nullable=False
	)


class ComunicadoLeitura(Base):
	"""Classe que representa a tabela de leitura de comunicado no banco de dados."""

	__tablename__ = 'comunicado_leitura'

	comunicado_id: Mapped[int] = mapped_column(
		BigInteger,
		ForeignKey('comunicado.id', ondelete='CASCADE'),
		primary_key=True,
	)
	usuario_id: Mapped[int] = mapped_column(
		BigInteger,
		ForeignKey('usuario.id', ondelete='CASCADE'),
		primary_key=True,
	)
	lido_em: Mapped[datetime] = mapped_column(
		DateTime(timezone=True), server_default=func.now(), nullable=False
	)
