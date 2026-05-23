from datetime import date, datetime

from core.enums import ProjetoStatus, enum_values
from db.base import Base
from sqlalchemy import (
	BigInteger,
	CheckConstraint,
	Date,
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
	PAPEL_MAX_LENGTH,
	PROGRESSO_MAX,
	PROGRESSO_MIN,
	TITULO_MAX_LENGTH,
)


class Projeto(Base):
	__tablename__ = 'projeto'
	__table_args__ = (
		CheckConstraint(
			f'progresso BETWEEN {PROGRESSO_MIN} AND {PROGRESSO_MAX}',
			name='ck_projeto_progresso',
		),
	)

	id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
	cliente_id: Mapped[int] = mapped_column(
		BigInteger, ForeignKey('cliente.id', ondelete='RESTRICT'), nullable=False
	)
	servico_id: Mapped[int | None] = mapped_column(
		BigInteger, ForeignKey('servico.id', ondelete='SET NULL')
	)
	nome: Mapped[str] = mapped_column(String(TITULO_MAX_LENGTH), nullable=False)
	descricao: Mapped[str | None] = mapped_column(Text)
	status: Mapped[ProjetoStatus] = mapped_column(
		SAEnum(
			ProjetoStatus,
			name='projeto_status',
			create_type=False,
			values_callable=enum_values,
		),
		nullable=False,
		default=ProjetoStatus.PLANEJAMENTO,
	)
	progresso: Mapped[int] = mapped_column(
		SmallInteger, nullable=False, default=PROGRESSO_MIN
	)
	data_inicio: Mapped[date | None] = mapped_column(Date)
	data_fim: Mapped[date | None] = mapped_column(Date)
	criado_em: Mapped[datetime] = mapped_column(
		DateTime(timezone=True), server_default=func.now(), nullable=False
	)

	equipe: Mapped[list['ProjetoFuncionario']] = relationship(
		back_populates='projeto', cascade='all, delete-orphan'
	)


class ProjetoFuncionario(Base):
	__tablename__ = 'projeto_funcionario'

	projeto_id: Mapped[int] = mapped_column(
		BigInteger,
		ForeignKey('projeto.id', ondelete='CASCADE'),
		primary_key=True,
	)
	funcionario_id: Mapped[int] = mapped_column(
		BigInteger,
		ForeignKey('funcionario.id', ondelete='CASCADE'),
		primary_key=True,
	)
	papel: Mapped[str | None] = mapped_column(String(PAPEL_MAX_LENGTH))
	data_entrada: Mapped[date] = mapped_column(
		Date, nullable=False, server_default=func.current_date()
	)

	projeto: Mapped['Projeto'] = relationship(back_populates='equipe')
