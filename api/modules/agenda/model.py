from datetime import date, datetime, time

from core.constants import DURACAO_MINIMA_EVENTO_PADRAO, TAMANHO_MAXIMO_TITULO
from core.enums import EventoTipo, SituacaoSolicitacao, valores_enum
from db.base import Base
from sqlalchemy import (
	BigInteger,
	CheckConstraint,
	Date,
	DateTime,
	ForeignKey,
	Index,
	Integer,
	String,
	Text,
	Time,
	func,
	text,
)
from sqlalchemy import (
	Enum as SAEnum,
)
from sqlalchemy.orm import Mapped, mapped_column


class EventoAgenda(Base):
	"""Classe que representa a tabela de evento de agenda no banco de dados."""

	__tablename__ = 'evento_agenda'
	__table_args__ = (
		Index('idx_evento_usuario_data', 'usuario_id', 'data'),
		Index(
			'ux_evento_agenda_google_event_id',
			'google_event_id',
			unique=True,
			postgresql_where=text('google_event_id IS NOT NULL'),
		),
	)

	id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
	usuario_id: Mapped[int] = mapped_column(
		BigInteger, ForeignKey('usuario.id', ondelete='CASCADE'), nullable=False
	)
	titulo: Mapped[str] = mapped_column(String(TAMANHO_MAXIMO_TITULO), nullable=False)
	descricao: Mapped[str | None] = mapped_column(Text)
	tipo: Mapped[EventoTipo] = mapped_column(
		SAEnum(
			EventoTipo,
			name='evento_tipo',
			create_type=False,
			values_callable=valores_enum,
		),
		nullable=False,
		default=EventoTipo.REUNIAO,
	)
	data: Mapped[date] = mapped_column(Date, nullable=False)
	hora: Mapped[time | None] = mapped_column(Time)
	duracao_min: Mapped[int] = mapped_column(
		Integer, nullable=False, default=DURACAO_MINIMA_EVENTO_PADRAO
	)
	google_event_id: Mapped[str | None] = mapped_column(String(255))
	google_link: Mapped[str | None] = mapped_column(String(500))
	criado_em: Mapped[datetime] = mapped_column(
		DateTime(timezone=True), server_default=func.now(), nullable=False
	)


class SolicitacaoReuniao(Base):
	"""Classe que representa a tabela de solicitação de reunião no banco de dados."""

	__tablename__ = 'solicitacao_reuniao'
	__table_args__ = (
		CheckConstraint('remetente_id <> destinatario_id', name='ck_solicitacao_diferentes'),
		Index('idx_solicitacao_destinatario', 'destinatario_id', 'status'),
	)

	id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
	remetente_id: Mapped[int] = mapped_column(
		BigInteger, ForeignKey('usuario.id', ondelete='CASCADE'), nullable=False
	)
	destinatario_id: Mapped[int] = mapped_column(
		BigInteger, ForeignKey('usuario.id', ondelete='CASCADE'), nullable=False
	)
	titulo: Mapped[str] = mapped_column(String(TAMANHO_MAXIMO_TITULO), nullable=False)
	mensagem: Mapped[str | None] = mapped_column(Text)
	data: Mapped[date] = mapped_column(Date, nullable=False)
	hora: Mapped[time] = mapped_column(Time, nullable=False)
	status: Mapped[SituacaoSolicitacao] = mapped_column(
		SAEnum(
			SituacaoSolicitacao,
			name='solicitacao_status',
			create_type=False,
			values_callable=valores_enum,
		),
		nullable=False,
		default=SituacaoSolicitacao.PENDENTE,
	)
	criado_em: Mapped[datetime] = mapped_column(
		DateTime(timezone=True), server_default=func.now(), nullable=False
	)
