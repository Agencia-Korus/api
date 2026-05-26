from __future__ import annotations

from core.exceptions import ErroNaoEncontrado
from modules.portfolio.model import Portfolio
from modules.portfolio.repository import RepositorioPortfolio
from modules.portfolio.schema import PortfolioAtualizar, PortfolioCriar
from sqlalchemy.ext.asyncio import AsyncSession

_ENTIDADE = 'Item de portfólio'


class ServicoPortfolio:
	"""Classe responsável pelas regras de negócio de portfólio."""

	def __init__(self, sessao: AsyncSession):
		"""Função para inicializar a instância com suas dependências."""
		self.sessao = sessao
		self.repository = RepositorioPortfolio(sessao)

	async def criar(self, dados: PortfolioCriar) -> Portfolio:
		"""Função para criar um novo registro."""
		item = Portfolio(**dados.model_dump())
		item = await self.repository.adicionar(item)
		await self.sessao.commit()
		return item

	async def obter(self, item_id: int) -> Portfolio:
		"""Função para obter um registro pelo ID."""
		item = await self.repository.obter(item_id)
		if not item:
			raise ErroNaoEncontrado(_ENTIDADE, item_id)
		return item

	async def listar(self, offset: int, limit: int, destaques: bool) -> list[Portfolio]:
		"""Função para listar registros."""
		return await self.repository.listar_filtrados(
			offset=offset, limit=limit, destaques=destaques
		)

	async def listar_filtrados(
		self,
		offset: int,
		limit: int,
		destaques: bool,
		categoria: str | None = None,
	) -> list[Portfolio]:
		"""Função para listar registros aplicando filtros e paginação."""
		return await self.repository.listar_filtrados(
			offset=offset,
			limit=limit,
			destaques=destaques,
			categoria=categoria,
		)

	async def atualizar(self, item_id: int, dados: PortfolioAtualizar) -> Portfolio:
		"""Função para atualizar um registro pelo ID."""
		item = await self.repository.atualizar(
			item_id, dados.model_dump(exclude_none=True)
		)
		if not item:
			raise ErroNaoEncontrado(_ENTIDADE, item_id)
		await self.sessao.commit()
		return item

	async def deletar(self, item_id: int) -> None:
		"""Função para excluir um registro pelo ID."""
		if not await self.repository.deletar(item_id):
			raise ErroNaoEncontrado(_ENTIDADE, item_id)
		await self.sessao.commit()
