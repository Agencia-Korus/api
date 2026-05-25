from __future__ import annotations

from core.exceptions import ConflictError, NotFoundError
from modules.integracoes.model import Integracao
from modules.integracoes.repository import RepositorioIntegracao
from modules.integracoes.schema import (
	GOOGLE_CALENDAR_INTEGRATION,
	IntegracaoCriar,
	IntegracaoAtualizar,
)
from sqlalchemy.ext.asyncio import AsyncSession

_ENTITY = 'Integração'


class ServicoIntegracao:
	"""Classe responsável pelas regras de negócio de integração."""

	def __init__(self, session: AsyncSession):
		"""Função para inicializar a instância com suas dependências."""
		self.session = session
		self.repo = RepositorioIntegracao(session)

	async def criar(self, payload: IntegracaoCriar) -> Integracao:
		"""Função para criar um novo registro."""
		if await self.repo.obter_por_nome(GOOGLE_CALENDAR_INTEGRATION):
			raise ConflictError('Integração com Google Calendar já cadastrada')
		integracao = Integracao(**payload.model_dump())
		integracao = await self.repo.adicionar(integracao)
		await self.session.commit()
		return integracao

	async def obter(self, integracao_id: int) -> Integracao:
		"""Função para obter um registro pelo ID."""
		integracao = await self.repo.obter_google_calendar(integracao_id)
		if not integracao:
			raise NotFoundError(_ENTITY, integracao_id)
		return integracao

	async def listar(self, offset: int, limit: int) -> list[Integracao]:
		"""Função para listar registros."""
		return await self.repo.listar_google_calendar(offset=offset, limit=limit)

	async def atualizar(self, integracao_id: int, payload: IntegracaoAtualizar) -> Integracao:
		"""Função para atualizar um registro pelo ID."""
		await self.obter(integracao_id)
		integracao = await self.repo.atualizar(
			integracao_id, payload.model_dump(exclude_none=True)
		)
		if not integracao:
			raise NotFoundError(_ENTITY, integracao_id)
		await self.session.commit()
		return integracao

	async def deletar(self, integracao_id: int) -> None:
		"""Função para excluir um registro pelo ID."""
		await self.obter(integracao_id)
		await self.repo.deletar(integracao_id)
		await self.session.commit()
