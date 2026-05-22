from datetime import datetime

from sqlalchemy import (
	BigInteger,
	CheckConstraint,
	DateTime,
	ForeignKey,
	Integer,
	String,
	Text,
	func,
)
from sqlalchemy import (
	Enum as SAEnum,
)
from sqlalchemy.orm import Mapped, mapped_column

from core.constants import (
	ACAO_XP_MAX_LENGTH,
	ICONE_MAX_LENGTH,
	NOME_MAX_LENGTH,
	XP_MIN,
)
from core.enums import Complexidade, enum_values
from db.base import Base


class RegraXp(Base):
	__tablename__ = 'regra_xp'
	__table_args__ = (CheckConstraint(f'xp >= {XP_MIN}', name='ck_regra_xp_positivo'),)

	id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
	tarefa: Mapped[str] = mapped_column(String(NOME_MAX_LENGTH), nullable=False)
	complexidade: Mapped[Complexidade] = mapped_column(
		SAEnum(
			Complexidade,
			name='complexidade',
			create_type=False,
			values_callable=enum_values,
		),
		nullable=False,
	)
	xp: Mapped[int] = mapped_column(Integer, nullable=False)


class HistoricoXp(Base):
	__tablename__ = 'historico_xp'

	id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
	funcionario_id: Mapped[int] = mapped_column(
		BigInteger, ForeignKey('funcionario.id', ondelete='CASCADE'), nullable=False
	)
	tarefa_id: Mapped[int | None] = mapped_column(
		BigInteger, ForeignKey('tarefa.id', ondelete='SET NULL')
	)
	regra_id: Mapped[int | None] = mapped_column(
		BigInteger, ForeignKey('regra_xp.id', ondelete='SET NULL')
	)
	acao: Mapped[str] = mapped_column(String(ACAO_XP_MAX_LENGTH), nullable=False)
	xp: Mapped[int] = mapped_column(Integer, nullable=False)
	data: Mapped[datetime] = mapped_column(
		DateTime(timezone=True), server_default=func.now(), nullable=False
	)


class Conquista(Base):
	__tablename__ = 'conquista'

	id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
	nome: Mapped[str] = mapped_column(String(NOME_MAX_LENGTH), nullable=False)
	icone: Mapped[str | None] = mapped_column(String(ICONE_MAX_LENGTH))
	descricao: Mapped[str | None] = mapped_column(Text)
	xp_bonus: Mapped[int] = mapped_column(Integer, nullable=False, default=0)


class FuncionarioConquista(Base):
	__tablename__ = 'funcionario_conquista'

	funcionario_id: Mapped[int] = mapped_column(
		BigInteger,
		ForeignKey('funcionario.id', ondelete='CASCADE'),
		primary_key=True,
	)
	conquista_id: Mapped[int] = mapped_column(
		BigInteger,
		ForeignKey('conquista.id', ondelete='CASCADE'),
		primary_key=True,
	)
	desbloqueado_em: Mapped[datetime] = mapped_column(
		DateTime(timezone=True), server_default=func.now(), nullable=False
	)
