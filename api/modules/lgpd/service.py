from __future__ import annotations

from modules.lgpd.model import ConsentimentoLgpd
from modules.lgpd.repository import RepositorioConsentimentoLgpd
from modules.lgpd.schema import ConsentimentoLgpdCriar
from sqlalchemy.ext.asyncio import AsyncSession


class ServicoLgpd:
	"""Classe responsável pelas regras de negócio de lgpd."""

	def __init__(self, session: AsyncSession):
		"""Função para inicializar a instância com suas dependências."""
		self.session = session
		self.repo = RepositorioConsentimentoLgpd(session)

	async def registrar(self, dados: ConsentimentoLgpdCriar) -> ConsentimentoLgpd:
		"""Função para registrar um consentimento LGPD."""
		consentimento = ConsentimentoLgpd(**dados.model_dump())
		consentimento = await self.repo.adicionar(consentimento)
		await self.session.commit()
		return consentimento

	async def listar(self, offset: int, limit: int) -> list[ConsentimentoLgpd]:
		"""Função para listar registros."""
		return await self.repo.listar_todos(offset=offset, limit=limit)
