from datetime import datetime

from core.enums import ServicoStatus, enum_values
from db.base import Base
from sqlalchemy import (
	BigInteger,
	DateTime,
	ForeignKey,
	SmallInteger,
	String,
	Text,
	func,
)
from sqlalchemy import (
	Enum as SAEnum,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.constants import (
	ICONE_MAX_LENGTH,
	NOME_MAX_LENGHT,
	SLUG_MAX_LENGTH,
	URL_MAX_LENGTH,
)


class Servico(Base):
	__tablename__ = 'servico'

	id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
	nome: Mapped[str] = mapped_column(String(NOME_MAX_LENGHT), nullable=False)
	slug: Mapped[str] = mapped_column(
		String(SLUG_MAX_LENGTH), unique=True, nullable=False
	)
	descricao: Mapped[str | None] = mapped_column(Text)
	icone: Mapped[str | None] = mapped_column(String(ICONE_MAX_LENGTH))
	status: Mapped[ServicoStatus] = mapped_column(
		SAEnum(
			ServicoStatus,
			name='servico_status',
			create_type=False,
			values_callable=enum_values,
		),
		nullable=False,
		default=ServicoStatus.ATIVO,
	)
	criado_em: Mapped[datetime] = mapped_column(
		DateTime(timezone=True), server_default=func.now(), nullable=False
	)

	entregaveis: Mapped[list['Entregavel']] = relationship(
		back_populates='servico', cascade='all, delete-orphan'
	)


class Entregavel(Base):
	__tablename__ = 'entregavel'

	id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
	servico_id: Mapped[int] = mapped_column(
		BigInteger,
		ForeignKey('servico.id', ondelete='CASCADE'),
		nullable=False,
	)
	descricao: Mapped[str] = mapped_column(String(URL_MAX_LENGTH), nullable=False)
	ordem: Mapped[int] = mapped_column(SmallInteger, nullable=False, default=0)

	servico: Mapped['Servico'] = relationship(back_populates='entregaveis')
