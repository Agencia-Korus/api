from __future__ import annotations

from core.enums import AcademyTipo
from core.exceptions import NotFoundError
from modules.academy.model import Academy
from modules.academy.repository import AcademyRepository
from modules.academy.schema import AcademyCreate, AcademyUpdate
from sqlalchemy.ext.asyncio import AsyncSession

_ENTITY = 'Conteúdo Academy'


class AcademyService:
	"""Classe responsável pelas regras de negócio de conteúdo da Academy."""

	def __init__(self, session: AsyncSession):
		"""Função para inicializar a instância com suas dependências."""
		self.session = session
		self.repo = AcademyRepository(session)

	async def create(self, payload: AcademyCreate) -> Academy:
		"""Função para criar um novo registro."""
		item = Academy(**payload.model_dump())
		item = await self.repo.add(item)
		await self.session.commit()
		return item

	async def get(self, item_id: int) -> Academy:
		"""Função para obter um registro pelo ID."""
		item = await self.repo.get(item_id)
		if not item:
			raise NotFoundError(_ENTITY, item_id)
		return item

	async def list(self, offset: int, limit: int) -> list[Academy]:
		"""Função para listar registros."""
		return await self.repo.list_all(offset=offset, limit=limit)

	async def list_filtered(
		self,
		offset: int,
		limit: int,
		tipo: AcademyTipo | None = None,
		publicado: bool | None = None,
	) -> list[Academy]:
		"""Função para listar registros aplicando filtros e paginação."""
		return await self.repo.list_all(
			offset=offset, limit=limit, filters={'tipo': tipo, 'publicado': publicado}
		)

	async def update(self, item_id: int, payload: AcademyUpdate) -> Academy:
		"""Função para atualizar um registro pelo ID."""
		item = await self.repo.update(item_id, payload.model_dump(exclude_none=True))
		if not item:
			raise NotFoundError(_ENTITY, item_id)
		await self.session.commit()
		return item

	async def delete(self, item_id: int) -> None:
		"""Função para excluir um registro pelo ID."""
		if not await self.repo.delete(item_id):
			raise NotFoundError(_ENTITY, item_id)
		await self.session.commit()
