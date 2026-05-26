from __future__ import annotations

from core.enums import TipoAcademia
from core.exceptions import ErroNaoEncontrado
from modules.academy.model import Academia
from modules.academy.repository import RepositorioAcademia
from modules.academy.schema import AcademiaAtualizar, AcademiaCriar
from sqlalchemy.ext.asyncio import AsyncSession

_ENTIDADE = 'Conteúdo Academia'


class ServicoAcademia:
	"""Classe responsável pelas regras de negócio de conteúdo da Academia."""

	def __init__(self, sessao: AsyncSession):
		"""Função para inicializar a instância com suas dependências."""
		self.sessao = sessao
		self.repository = RepositorioAcademia(sessao)

	async def criar(self, dados: AcademiaCriar) -> Academia:
		"""Função para criar um novo registro."""
		item = Academia(**dados.model_dump())
		item = await self.repository.adicionar(item)
		await self.sessao.commit()
		return item

	async def obter(self, item_id: int) -> Academia:
		"""Função para obter um registro pelo ID."""
		item = await self.repository.obter(item_id)
		if not item:
			raise ErroNaoEncontrado(_ENTIDADE, item_id)
		return item

	async def listar(self, offset: int, limit: int) -> list[Academia]:
		"""Função para listar registros."""
		return await self.repository.listar_todos(offset=offset, limit=limit)

	async def listar_filtrados(
		self,
		offset: int,
		limit: int,
		tipo: TipoAcademia | None = None,
		publicado: bool | None = None,
	) -> list[Academia]:
		"""Função para listar registros aplicando filtros e paginação."""
		return await self.repository.listar_todos(
			offset=offset, limit=limit, filtros={'tipo': tipo, 'publicado': publicado}
		)

	async def atualizar(self, item_id: int, dados: AcademiaAtualizar) -> Academia:
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
