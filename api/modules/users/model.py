from datetime import date, datetime

from core.constants import (
	CARGO_MAX_LENGTH,
	DOCUMENTO_MAX_LENGTH,
	NIVEL_ACESSO_INICIAL,
	NIVEL_FUNCIONARIO_INICIAL,
	NOME_MAX_LENGTH,
	RAZAO_SOCIAL_MAX_LENGTH,
	SEGMENTO_MAX_LENGTH,
	SENHA_HASH_MAX_LENGTH,
	TELEFONE_MAX_LENGTH,
	URL_MAX_LENGTH,
	XP_INICIAL,
)
from core.enums import UserRole, UserStatus, enum_values
from db.base import Base
from sqlalchemy import (
	BigInteger,
	Date,
	DateTime,
	ForeignKey,
	Integer,
	SmallInteger,
	String,
	func,
)
from sqlalchemy import Enum as SAEnum
from sqlalchemy.dialects.postgresql import CITEXT
from sqlalchemy.orm import Mapped, mapped_column, relationship


class Usuario(Base):
	"""Classe que representa a tabela de usuário no banco de dados."""

	__tablename__ = 'usuario'

	id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
	nome: Mapped[str] = mapped_column(String(NOME_MAX_LENGTH), nullable=False)
	# CITEXT() -> Lucas@email.com = lucas@email.com
	email: Mapped[str] = mapped_column(CITEXT(), unique=True, nullable=False)
	senha_hash: Mapped[str] = mapped_column(
		String(SENHA_HASH_MAX_LENGTH), nullable=False
	)
	role: Mapped[UserRole] = mapped_column(
		SAEnum(
			UserRole, name='user_role', create_type=False, values_callable=enum_values
		),
		nullable=False,
	)
	avatar: Mapped[str | None] = mapped_column(String(URL_MAX_LENGTH))
	telefone: Mapped[str | None] = mapped_column(String(TELEFONE_MAX_LENGTH))
	status: Mapped[UserStatus] = mapped_column(
		SAEnum(
			UserStatus,
			name='user_status',
			create_type=False,
			values_callable=enum_values,
		),
		nullable=False,
		default=UserStatus.ATIVO,
	)
	criado_em: Mapped[datetime] = mapped_column(
		DateTime(timezone=True), server_default=func.now(), nullable=False
	)
	atualizado_em: Mapped[datetime] = mapped_column(
		DateTime(timezone=True), server_default=func.now(), nullable=False
	)
	cliente: Mapped['Cliente | None'] = relationship(
		back_populates='usuario', uselist=False, cascade='all, delete-orphan'
	)
	funcionario: Mapped['Funcionario | None'] = relationship(
		back_populates='usuario', uselist=False, cascade='all, delete-orphan'
	)
	admin: Mapped['Admin | None'] = relationship(
		back_populates='usuario', uselist=False, cascade='all, delete-orphan'
	)


class Cliente(Base):
	"""Classe que representa a tabela de cliente no banco de dados."""

	__tablename__ = 'cliente'

	id: Mapped[int] = mapped_column(
		BigInteger, ForeignKey('usuario.id', ondelete='CASCADE'), primary_key=True
	)
	razao_social: Mapped[str] = mapped_column(
		String(RAZAO_SOCIAL_MAX_LENGTH), nullable=False
	)
	cnpj_cpf: Mapped[str] = mapped_column(
		String(DOCUMENTO_MAX_LENGTH), unique=True, nullable=False
	)
	segmento: Mapped[str | None] = mapped_column(String(SEGMENTO_MAX_LENGTH))
	usuario: Mapped['Usuario'] = relationship(back_populates='cliente')


class Funcionario(Base):
	"""Classe que representa a tabela de funcionário no banco de dados."""

	__tablename__ = 'funcionario'

	id: Mapped[int] = mapped_column(
		BigInteger, ForeignKey('usuario.id', ondelete='CASCADE'), primary_key=True
	)
	cargo: Mapped[str] = mapped_column(String(CARGO_MAX_LENGTH), nullable=False)
	especialidade: Mapped[str | None] = mapped_column(String(CARGO_MAX_LENGTH))
	data_admissao: Mapped[date] = mapped_column(
		Date, nullable=False, server_default=func.current_date()
	)
	xp_total: Mapped[int] = mapped_column(Integer, nullable=False, default=XP_INICIAL)
	nivel: Mapped[int] = mapped_column(
		Integer, nullable=False, default=NIVEL_FUNCIONARIO_INICIAL
	)
	usuario: Mapped['Usuario'] = relationship(back_populates='funcionario')


class Admin(Base):
	"""Classe que representa a tabela de admin no banco de dados."""

	__tablename__ = 'admin'

	id: Mapped[int] = mapped_column(
		BigInteger,
		ForeignKey('usuario.id', ondelete='CASCADE'),
		primary_key=True,
	)
	nivel_acesso: Mapped[int] = mapped_column(
		SmallInteger, nullable=False, default=NIVEL_ACESSO_INICIAL
	)
	data_promocao: Mapped[date] = mapped_column(
		Date, nullable=False, server_default=func.current_date()
	)
	usuario: Mapped['Usuario'] = relationship(back_populates='admin')
