from __future__ import annotations

from modules.lgpd.model import ConsentimentoLgpd
from modules.lgpd.repository import ConsentimentoLgpdRepository
from modules.lgpd.schema import ConsentimentoLgpdCreate
from sqlalchemy.ext.asyncio import AsyncSession


class LgpdService:
	"""Classe responsável pelas regras de negócio de lgpd."""

	def __init__(self, session: AsyncSession):
		"""Função para inicializar a instância com suas dependências."""
		self.session = session
		self.repo = ConsentimentoLgpdRepository(session)

	async def registrar(self, payload: ConsentimentoLgpdCreate) -> ConsentimentoLgpd:
		"""Função para registrar um consentimento LGPD."""
		consentimento = ConsentimentoLgpd(**payload.model_dump())
		consentimento = await self.repo.add(consentimento)
		await self.session.commit()
		return consentimento

	async def listar(self, offset: int, limit: int) -> list[ConsentimentoLgpd]:
		"""Função para listar registros."""
		return await self.repo.list_all(offset=offset, limit=limit)
