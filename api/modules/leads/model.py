from datetime import date, datetime

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

from core.constants import (
	NOME_MAX_LENGTH,
	ORCAMENTO_MAX_LENGTH,
	RAZAO_SOCIAL_MAX_LENGTH,
	TELEFONE_MAX_LENGTH,
)
from core.enums import LeadPrioridade, LeadStatus, enum_values
from db.base import Base


class Lead(Base):
	__tablename__ = 'lead'

	id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
	servico_id: Mapped[int | None] = mapped_column(
		BigInteger, ForeignKey('servico.id', ondelete='SET NULL')
	)
	nome: Mapped[str] = mapped_column(String(NOME_MAX_LENGTH), nullable=False)
	email: Mapped[str] = mapped_column(CITEXT(), nullable=False)
	whatsapp: Mapped[str | None] = mapped_column(String(TELEFONE_MAX_LENGTH))
	empresa: Mapped[str | None] = mapped_column(String(RAZAO_SOCIAL_MAX_LENGTH))
	orcamento: Mapped[str | None] = mapped_column(String(ORCAMENTO_MAX_LENGTH))
	prazo_desejado: Mapped[date | None] = mapped_column(Date)
	termos_aceitos: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
	status: Mapped[LeadStatus] = mapped_column(
		SAEnum(
			LeadStatus,
			name='lead_status',
			create_type=False,
			values_callable=enum_values,
		),
		nullable=False,
		default=LeadStatus.NOVO,
	)
	prioridade: Mapped[LeadPrioridade] = mapped_column(
		SAEnum(
			LeadPrioridade,
			name='lead_prioridade',
			create_type=False,
			values_callable=enum_values,
		),
		nullable=False,
		default=LeadPrioridade.MEDIA,
	)
	mensagem: Mapped[str | None] = mapped_column(Text)
	data: Mapped[datetime] = mapped_column(
		DateTime(timezone=True), server_default=func.now(), nullable=False
	)
