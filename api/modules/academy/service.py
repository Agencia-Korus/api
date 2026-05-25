from __future__ import annotations

from core.enums import AcademyTipo
from core.exceptions import NotFoundError
from modules.academy.model import Academy
from modules.academy.repository import RepositorioAcademy
from modules.academy.schema import AcademyCriar, AcademyAtualizar
from sqlalchemy.ext.asyncio import AsyncSession

_ENTITY = 'Conteúdo Academy'


class ServicoAcademy:
	"""Classe responsável pelas regras de negócio de conteúdo da Academy."""

	def __init__(self, session: AsyncSession):
		"""Função para inicializar a instância com suas dependências."""
		self.session = session
		self.repo = RepositorioAcademy(session)

	async def criar(self, dados: AcademyCriar) -> Academy:
		"""Função para criar um novo registro."""
		item = Academy(**dados.model_dump())
		item = await self.repo.adicionar(item)
		await self.session.commit()
		return item

	async def obter(self, item_id: int) -> Academy:
		"""Função para obter um registro pelo ID."""
		item = await self.repo.obter(item_id)
		if not item:
			raise NotFoundError(_ENTITY, item_id)
		return item

	async def listar(self, offset: int, limit: int) -> list[Academy]:
		"""Função para listar registros."""
		return await self.repo.listar_todos(offset=offset, limit=limit)

	async def listar_filtrados(
		self,
		offset: int,
		limit: int,
		tipo: AcademyTipo | None = None,
		publicado: bool | None = None,
	) -> list[Academy]:
		"""Função para listar registros aplicando filtros e paginação."""
		return await self.repo.listar_todos(
			offset=offset, limit=limit, filters={'tipo': tipo, 'publicado': publicado}
		)

	async def atualizar(self, item_id: int, dados: AcademyAtualizar) -> Academy:
		"""Função para atualizar um registro pelo ID."""
		item = await self.repo.atualizar(item_id, dados.model_dump(exclude_none=True))
		if not item:
			raise NotFoundError(_ENTITY, item_id)
		await self.session.commit()
		return item

	async def deletar(self, item_id: int) -> None:
		"""Função para excluir um registro pelo ID."""
		if not await self.repo.deletar(item_id):
			raise NotFoundError(_ENTITY, item_id)
		await self.session.commit()
