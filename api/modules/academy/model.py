from datetime import datetime
from decimal import Decimal

from sqlalchemy import (
	BigInteger,
	Boolean,
	DateTime,
	Numeric,
	String,
	Text,
	func,
)
from sqlalchemy import (
	Enum as SAEnum,
)
from sqlalchemy.orm import Mapped, mapped_column

from core.constants import (
	PRECO_DECIMAL_PLACES,
	PRECO_TOTAL_DIGITS,
	TITULO_MAX_LENGTH,
	URL_MAX_LENGTH,
)
from core.enums import AcademyTipo, enum_values
from db.base import Base


class Academy(Base):
	__tablename__ = 'academy'

	id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
	titulo: Mapped[str] = mapped_column(String(TITULO_MAX_LENGTH), nullable=False)
	tipo: Mapped[AcademyTipo] = mapped_column(
		SAEnum(
			AcademyTipo,
			name='academy_tipo',
			create_type=False,
			values_callable=enum_values,
		),
		nullable=False,
	)
	descricao: Mapped[str | None] = mapped_column(Text)
	preco: Mapped[Decimal] = mapped_column(
		Numeric(PRECO_TOTAL_DIGITS, PRECO_DECIMAL_PLACES),
		nullable=False,
		default=Decimal('0.00'),
	)
	imagem: Mapped[str | None] = mapped_column(String(URL_MAX_LENGTH))
	url_externa: Mapped[str] = mapped_column(String(URL_MAX_LENGTH), nullable=False)
	publicado: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
	criado_em: Mapped[datetime] = mapped_column(
		DateTime(timezone=True), server_default=func.now(), nullable=False
	)
