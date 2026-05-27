from datetime import datetime

from core.constants import TAMANHO_MAXIMO_CHAVE_INTEGRACAO, TAMANHO_MAXIMO_SEGMENTO
from core.enums import SituacaoIntegracao, valores_enum
from db.base import Base
from sqlalchemy import (
	BigInteger,
	DateTime,
	String,
	func,
)
from sqlalchemy import (
	Enum as SAEnum,
)
from sqlalchemy.orm import Mapped, mapped_column


class Integracao(Base):
	"""Classe que representa a tabela de integração no banco de dados."""

	__tablename__ = 'integracao'

	id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
	nome: Mapped[str] = mapped_column(String(TAMANHO_MAXIMO_SEGMENTO), unique=True, nullable=False)
	chave: Mapped[str | None] = mapped_column(String(TAMANHO_MAXIMO_CHAVE_INTEGRACAO))
	status: Mapped[SituacaoIntegracao] = mapped_column(
		SAEnum(
			SituacaoIntegracao,
			name='integracao_status',
			create_type=False,
			values_callable=valores_enum,
		),
		nullable=False,
		default=SituacaoIntegracao.DESCONECTADO,
	)
	atualizado_em: Mapped[datetime] = mapped_column(
		DateTime(timezone=True), server_default=func.now(), nullable=False
	)
