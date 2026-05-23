from datetime import datetime

from core.enums import IntegracaoStatus, enum_values
from db.base import Base
from sqlalchemy import (
	BigInteger,
	DateTime,
	String,
	func,
)
from sqlalchemy import (
	Enum as SAEnum,
)
from sqlalchemy.orm import Mapped, mapped_column

from core.constants import CHAVE_INTEGRACAO_MAX_LENGTH, SEGMENTO_MAX_LENGTH


class Integracao(Base):
	__tablename__ = 'integracao'

	id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
	nome: Mapped[str] = mapped_column(
		String(SEGMENTO_MAX_LENGTH), unique=True, nullable=False
	)
	chave: Mapped[str | None] = mapped_column(String(CHAVE_INTEGRACAO_MAX_LENGTH))
	status: Mapped[IntegracaoStatus] = mapped_column(
		SAEnum(
			IntegracaoStatus,
			name='integracao_status',
			create_type=False,
			values_callable=enum_values,
		),
		nullable=False,
		default=IntegracaoStatus.DESCONECTADO,
	)
	atualizado_em: Mapped[datetime] = mapped_column(
		DateTime(timezone=True), server_default=func.now(), nullable=False
	)
