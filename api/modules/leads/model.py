from datetime import date, datetime

from core.constants import (
	TAMANHO_MAXIMO_NOME,
	TAMANHO_MAXIMO_ORCAMENTO,
	TAMANHO_MAXIMO_RAZAO_SOCIAL,
	TAMANHO_MAXIMO_TELEFONE,
)
from core.enums import LeadPrioridade, SituacaoLead, valores_enum
from db.base import Base
from sqlalchemy import (
	BigInteger,
	Boolean,
	Date,
	DateTime,
	ForeignKey,
	String,
	Text,
	func,
)
from sqlalchemy import (
	Enum as SAEnum,
)
from sqlalchemy.dialects.postgresql import CITEXT
from sqlalchemy.orm import Mapped, mapped_column


class Lead(Base):
	"""Classe que representa a tabela de lead no banco de dados."""

	__tablename__ = 'lead'

	id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
	servico_id: Mapped[int | None] = mapped_column(
		BigInteger, ForeignKey('servico.id', ondelete='SET NULL')
	)
	nome: Mapped[str] = mapped_column(String(TAMANHO_MAXIMO_NOME), nullable=False)
	email: Mapped[str] = mapped_column(CITEXT(), nullable=False)
	whatsapp: Mapped[str | None] = mapped_column(String(TAMANHO_MAXIMO_TELEFONE))
	empresa: Mapped[str | None] = mapped_column(String(TAMANHO_MAXIMO_RAZAO_SOCIAL))
	orcamento: Mapped[str | None] = mapped_column(String(TAMANHO_MAXIMO_ORCAMENTO))
	prazo_desejado: Mapped[date | None] = mapped_column(Date)
	termos_aceitos: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
	status: Mapped[SituacaoLead] = mapped_column(
		SAEnum(
			SituacaoLead,
			name='lead_status',
			create_type=False,
			values_callable=valores_enum,
		),
		nullable=False,
		default=SituacaoLead.NOVO,
	)
	prioridade: Mapped[LeadPrioridade] = mapped_column(
		SAEnum(
			LeadPrioridade,
			name='lead_prioridade',
			create_type=False,
			values_callable=valores_enum,
		),
		nullable=False,
		default=LeadPrioridade.MEDIA,
	)
	mensagem: Mapped[str | None] = mapped_column(Text)
	data: Mapped[datetime] = mapped_column(
		DateTime(timezone=True), server_default=func.now(), nullable=False
	)
