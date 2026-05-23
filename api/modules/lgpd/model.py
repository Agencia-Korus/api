from datetime import datetime

from sqlalchemy import (
	BigInteger,
	Boolean,
	DateTime,
	ForeignKey,
	String,
	func,
)
from sqlalchemy import (
	Enum as SAEnum,
)
from sqlalchemy.dialects.postgresql import INET
from sqlalchemy.orm import Mapped, mapped_column

from core.constants import USER_AGENT_MAX_LENGTH
from core.enums import ConsentimentoTipo, enum_values
from db.base import Base


class ConsentimentoLgpd(Base):
	__tablename__ = 'consentimento_lgpd'

	id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
	usuario_id: Mapped[int | None] = mapped_column(
		BigInteger, ForeignKey('usuario.id', ondelete='SET NULL')
	)
	tipo: Mapped[ConsentimentoTipo] = mapped_column(
		SAEnum(
			ConsentimentoTipo,
			name='consentimento_tipo',
			create_type=False,
			values_callable=enum_values,
		),
		nullable=False,
	)
	aceito: Mapped[bool] = mapped_column(Boolean, nullable=False)
	ip: Mapped[str | None] = mapped_column(INET)
	user_agent: Mapped[str | None] = mapped_column(String(USER_AGENT_MAX_LENGTH))
	data: Mapped[datetime] = mapped_column(
		DateTime(timezone=True), server_default=func.now(), nullable=False
	)
