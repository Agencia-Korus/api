from datetime import datetime
from decimal import Decimal

from core.constants import (
	CASAS_DECIMAIS_PRECO,
	DIGITOS_TOTAIS_PRECO,
	TAMANHO_MAXIMO_TITULO,
	TAMANHO_MAXIMO_URL,
)
from core.enums import TipoAcademia, valores_enum
from db.base import Base
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


class Academia(Base):
	"""Classe que representa a tabela de conteúdo da Academia no banco de dados."""

	__tablename__ = 'academy'

	id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
	titulo: Mapped[str] = mapped_column(String(TAMANHO_MAXIMO_TITULO), nullable=False)
	tipo: Mapped[TipoAcademia] = mapped_column(
		SAEnum(
			TipoAcademia,
			name='academy_tipo',
			create_type=False,
			values_callable=valores_enum,
		),
		nullable=False,
	)
	descricao: Mapped[str | None] = mapped_column(Text)
	preco: Mapped[Decimal] = mapped_column(
		Numeric(DIGITOS_TOTAIS_PRECO, CASAS_DECIMAIS_PRECO),
		nullable=False,
		default=Decimal('0.00'),
	)
	imagem: Mapped[str | None] = mapped_column(String(TAMANHO_MAXIMO_URL))
	url_externa: Mapped[str] = mapped_column(String(TAMANHO_MAXIMO_URL), nullable=False)
	publicado: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
	criado_em: Mapped[datetime] = mapped_column(
		DateTime(timezone=True), server_default=func.now(), nullable=False
	)
