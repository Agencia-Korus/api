from datetime import datetime

from core.constants import (
	TAMANHO_MAXIMO_ICONE,
	TAMANHO_MAXIMO_NOME,
	TAMANHO_MAXIMO_SLUG,
	TAMANHO_MAXIMO_URL,
)
from core.enums import SituacaoServico, valores_enum
from db.base import Base
from sqlalchemy import (
	BigInteger,
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


class Servico(Base):
	"""Classe que representa a tabela de serviço no banco de dados."""

	__tablename__ = 'servico'

	id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
	nome: Mapped[str] = mapped_column(String(TAMANHO_MAXIMO_NOME), nullable=False)
	slug: Mapped[str] = mapped_column(String(TAMANHO_MAXIMO_SLUG), unique=True, nullable=False)
	descricao: Mapped[str | None] = mapped_column(Text)
	icone: Mapped[str | None] = mapped_column(String(TAMANHO_MAXIMO_ICONE))
	status: Mapped[SituacaoServico] = mapped_column(
		SAEnum(
			SituacaoServico,
			name='servico_status',
			create_type=False,
			values_callable=valores_enum,
		),
		nullable=False,
		default=SituacaoServico.ATIVO,
	)
	criado_em: Mapped[datetime] = mapped_column(
		DateTime(timezone=True), server_default=func.now(), nullable=False
	)

	entregaveis: Mapped[list['Entregavel']] = relationship(
		back_populates='servico', cascade='all, delete-orphan'
	)


class Entregavel(Base):
	"""Classe que representa a tabela de entregável no banco de dados."""

	__tablename__ = 'entregavel'

	id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
	servico_id: Mapped[int] = mapped_column(
		BigInteger,
		ForeignKey('servico.id', ondelete='CASCADE'),
		nullable=False,
	)
	descricao: Mapped[str] = mapped_column(String(TAMANHO_MAXIMO_URL), nullable=False)
	ordem: Mapped[int] = mapped_column(SmallInteger, nullable=False, default=0)

	servico: Mapped['Servico'] = relationship(back_populates='entregaveis')
