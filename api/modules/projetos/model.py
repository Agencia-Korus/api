from datetime import date, datetime

from core.constants import (
	PROGRESSO_MAXIMO,
	PROGRESSO_MINIMO,
	TAMANHO_MAXIMO_PAPEL,
	TAMANHO_MAXIMO_TITULO,
)
from core.enums import SituacaoProjeto, valores_enum
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


class Projeto(Base):
	"""Classe que representa a tabela de projeto no banco de dados."""

	__tablename__ = 'projeto'
	__table_args__ = (
		CheckConstraint(
			f'progresso BETWEEN {PROGRESSO_MINIMO} AND {PROGRESSO_MAXIMO}',
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
	nome: Mapped[str] = mapped_column(String(TAMANHO_MAXIMO_TITULO), nullable=False)
	descricao: Mapped[str | None] = mapped_column(Text)
	status: Mapped[SituacaoProjeto] = mapped_column(
		SAEnum(
			SituacaoProjeto,
			name='projeto_status',
			create_type=False,
			values_callable=valores_enum,
		),
		nullable=False,
		default=SituacaoProjeto.PLANEJAMENTO,
	)
	progresso: Mapped[int] = mapped_column(SmallInteger, nullable=False, default=PROGRESSO_MINIMO)
	data_inicio: Mapped[date | None] = mapped_column(Date)
	data_fim: Mapped[date | None] = mapped_column(Date)
	criado_em: Mapped[datetime] = mapped_column(
		DateTime(timezone=True), server_default=func.now(), nullable=False
	)

	equipe: Mapped[list['ProjetoFuncionario']] = relationship(
		back_populates='projeto', cascade='all, delete-orphan'
	)


class ProjetoFuncionario(Base):
	"""Classe que representa a tabela de membro do projeto no banco de dados."""

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
	papel: Mapped[str | None] = mapped_column(String(TAMANHO_MAXIMO_PAPEL))
	data_entrada: Mapped[date] = mapped_column(
		Date, nullable=False, server_default=func.current_date()
	)

	projeto: Mapped['Projeto'] = relationship(back_populates='equipe')
