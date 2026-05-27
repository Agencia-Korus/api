from datetime import date, datetime

from core.constants import (
	TAMANHO_MAXIMO_PAPEL,
	TAMANHO_MAXIMO_TIPO_ARQUIVO,
	TAMANHO_MAXIMO_TITULO,
	TAMANHO_MAXIMO_URL,
)
from core.enums import Complexidade, Prioridade, SituacaoTarefa, valores_enum
from db.base import Base
from sqlalchemy import (
	BigInteger,
	Date,
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
from sqlalchemy.orm import Mapped, mapped_column, relationship


class Tarefa(Base):
	"""Classe que representa a tabela de tarefa no banco de dados."""

	__tablename__ = 'tarefa'

	id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
	projeto_id: Mapped[int] = mapped_column(
		BigInteger, ForeignKey('projeto.id', ondelete='CASCADE'), nullable=False
	)
	responsavel_id: Mapped[int | None] = mapped_column(
		BigInteger, ForeignKey('funcionario.id', ondelete='SET NULL')
	)
	titulo: Mapped[str] = mapped_column(String(TAMANHO_MAXIMO_TITULO), nullable=False)
	descricao: Mapped[str | None] = mapped_column(Text)
	status: Mapped[SituacaoTarefa] = mapped_column(
		SAEnum(
			SituacaoTarefa,
			name='tarefa_status',
			create_type=False,
			values_callable=valores_enum,
		),
		nullable=False,
		default=SituacaoTarefa.A_FAZER,
	)
	complexidade: Mapped[Complexidade] = mapped_column(
		SAEnum(
			Complexidade,
			name='complexidade',
			create_type=False,
			values_callable=valores_enum,
		),
		nullable=False,
		default=Complexidade.MEDIA,
	)
	prioridade: Mapped[Prioridade] = mapped_column(
		SAEnum(
			Prioridade,
			name='prioridade',
			create_type=False,
			values_callable=valores_enum,
		),
		nullable=False,
		default=Prioridade.MEDIA,
	)
	categoria: Mapped[str | None] = mapped_column(String(TAMANHO_MAXIMO_PAPEL))
	prazo: Mapped[date | None] = mapped_column(Date)
	ordem: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
	criado_em: Mapped[datetime] = mapped_column(
		DateTime(timezone=True), server_default=func.now(), nullable=False
	)
	concluido_em: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

	comentarios: Mapped[list['Comentario']] = relationship(
		back_populates='tarefa', cascade='all, delete-orphan'
	)
	anexos: Mapped[list['Anexo']] = relationship(
		back_populates='tarefa', cascade='all, delete-orphan'
	)


class Comentario(Base):
	"""Classe que representa a tabela de comentário no banco de dados."""

	__tablename__ = 'comentario'

	id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
	tarefa_id: Mapped[int] = mapped_column(
		BigInteger, ForeignKey('tarefa.id', ondelete='CASCADE'), nullable=False
	)
	autor_id: Mapped[int] = mapped_column(
		BigInteger, ForeignKey('usuario.id', ondelete='CASCADE'), nullable=False
	)
	conteudo: Mapped[str] = mapped_column(Text, nullable=False)
	criado_em: Mapped[datetime] = mapped_column(
		DateTime(timezone=True), server_default=func.now(), nullable=False
	)

	tarefa: Mapped['Tarefa'] = relationship(back_populates='comentarios')


class Anexo(Base):
	"""Classe que representa a tabela de anexo no banco de dados."""

	__tablename__ = 'anexo'

	id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
	tarefa_id: Mapped[int] = mapped_column(
		BigInteger, ForeignKey('tarefa.id', ondelete='CASCADE'), nullable=False
	)
	nome: Mapped[str] = mapped_column(String(TAMANHO_MAXIMO_TITULO), nullable=False)
	url: Mapped[str] = mapped_column(String(TAMANHO_MAXIMO_URL), nullable=False)
	tipo: Mapped[str | None] = mapped_column(String(TAMANHO_MAXIMO_TIPO_ARQUIVO))
	tamanho: Mapped[int | None] = mapped_column(Integer)
	criado_em: Mapped[datetime] = mapped_column(
		DateTime(timezone=True), server_default=func.now(), nullable=False
	)

	tarefa: Mapped['Tarefa'] = relationship(back_populates='anexos')
