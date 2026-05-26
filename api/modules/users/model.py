from datetime import date, datetime

from core.constants import (
	NIVEL_ACESSO_INICIAL,
	NIVEL_FUNCIONARIO_INICIAL,
	TAMANHO_MAXIMO_CARGO,
	TAMANHO_MAXIMO_DOCUMENTO,
	TAMANHO_MAXIMO_HASH_SENHA,
	TAMANHO_MAXIMO_NOME,
	TAMANHO_MAXIMO_RAZAO_SOCIAL,
	TAMANHO_MAXIMO_SEGMENTO,
	TAMANHO_MAXIMO_TELEFONE,
	TAMANHO_MAXIMO_URL,
	XP_INICIAL,
)
from core.enums import PapelUsuario, SituacaoUsuario, valores_enum
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
	nome: Mapped[str] = mapped_column(String(TAMANHO_MAXIMO_NOME), nullable=False)
	# CITEXT() -> Lucas@email.com = lucas@email.com
	email: Mapped[str] = mapped_column(CITEXT(), unique=True, nullable=False)
	senha_hash: Mapped[str] = mapped_column(String(TAMANHO_MAXIMO_HASH_SENHA), nullable=False)
	role: Mapped[PapelUsuario] = mapped_column(
		SAEnum(
			PapelUsuario,
			name='user_role',
			create_type=False,
			values_callable=valores_enum,
		),
		nullable=False,
	)
	avatar: Mapped[str | None] = mapped_column(String(TAMANHO_MAXIMO_URL))
	telefone: Mapped[str | None] = mapped_column(String(TAMANHO_MAXIMO_TELEFONE))
	status: Mapped[SituacaoUsuario] = mapped_column(
		SAEnum(
			SituacaoUsuario,
			name='user_status',
			create_type=False,
			values_callable=valores_enum,
		),
		nullable=False,
		default=SituacaoUsuario.ATIVO,
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
	razao_social: Mapped[str] = mapped_column(String(TAMANHO_MAXIMO_RAZAO_SOCIAL), nullable=False)
	cnpj_cpf: Mapped[str] = mapped_column(
		String(TAMANHO_MAXIMO_DOCUMENTO), unique=True, nullable=False
	)
	segmento: Mapped[str | None] = mapped_column(String(TAMANHO_MAXIMO_SEGMENTO))
	usuario: Mapped['Usuario'] = relationship(back_populates='cliente')


class Funcionario(Base):
	"""Classe que representa a tabela de funcionário no banco de dados."""

	__tablename__ = 'funcionario'

	id: Mapped[int] = mapped_column(
		BigInteger, ForeignKey('usuario.id', ondelete='CASCADE'), primary_key=True
	)
	cargo: Mapped[str] = mapped_column(String(TAMANHO_MAXIMO_CARGO), nullable=False)
	especialidade: Mapped[str | None] = mapped_column(String(TAMANHO_MAXIMO_CARGO))
	data_admissao: Mapped[date] = mapped_column(
		Date, nullable=False, server_default=func.current_date()
	)
	xp_total: Mapped[int] = mapped_column(Integer, nullable=False, default=XP_INICIAL)
	nivel: Mapped[int] = mapped_column(Integer, nullable=False, default=NIVEL_FUNCIONARIO_INICIAL)
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
