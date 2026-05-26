from __future__ import annotations

from core.exceptions import ErroConflito, ErroNaoEncontrado
from modules.integracoes.model import Integracao
from modules.integracoes.repository import RepositorioIntegracao
from modules.integracoes.schema import (
	INTEGRACAO_GOOGLE_CALENDAR,
	IntegracaoAtualizar,
	IntegracaoCriar,
)
from sqlalchemy.ext.asyncio import AsyncSession

_ENTIDADE = 'Integração'


class ServicoIntegracao:
	"""Classe responsável pelas regras de negócio de integração."""

	def __init__(self, sessao: AsyncSession):
		"""Função para inicializar a instância com suas dependências."""
		self.sessao = sessao
		self.repository = RepositorioIntegracao(sessao)

	async def criar(self, dados: IntegracaoCriar) -> Integracao:
		"""Função para criar um novo registro."""
		if await self.repository.obter_por_nome(INTEGRACAO_GOOGLE_CALENDAR):
			raise ErroConflito('Integração com Google Calendar já cadastrada')
		integracao = Integracao(**dados.model_dump())
		integracao = await self.repository.adicionar(integracao)
		await self.sessao.commit()
		return integracao

	async def obter(self, integracao_id: int) -> Integracao:
		"""Função para obter um registro pelo ID."""
		integracao = await self.repository.obter_google_calendar(integracao_id)
		if not integracao:
			raise ErroNaoEncontrado(_ENTIDADE, integracao_id)
		return integracao

	async def listar(self, offset: int, limit: int) -> list[Integracao]:
		"""Função para listar registros."""
		return await self.repository.listar_google_calendar(offset=offset, limit=limit)

	async def atualizar(self, integracao_id: int, dados: IntegracaoAtualizar) -> Integracao:
		"""Função para atualizar um registro pelo ID."""
		await self.obter(integracao_id)
		integracao = await self.repository.atualizar(
			integracao_id, dados.model_dump(exclude_none=True)
		)
		if not integracao:
			raise ErroNaoEncontrado(_ENTIDADE, integracao_id)
		await self.sessao.commit()
		return integracao

	async def deletar(self, integracao_id: int) -> None:
		"""Função para excluir um registro pelo ID."""
		await self.obter(integracao_id)
		await self.repository.deletar(integracao_id)
		await self.sessao.commit()
