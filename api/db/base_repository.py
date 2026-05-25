from typing import Any, Generic, TypeVar

from core.constants import PAGINATION_DEFAULT_LIMIT, PAGINATION_DEFAULT_OFFSET
from db.base import Base
from sqlalchemy import delete as sa_delete
from sqlalchemy import select
from sqlalchemy import update as sa_update
from sqlalchemy.ext.asyncio import AsyncSession

ModelT = TypeVar('ModelT', bound=Base)


class RepositorioBase(Generic[ModelT]):
	"""Classe responsável pelo acesso aos dados de base."""

	model: type[ModelT]

	def __init__(self, session: AsyncSession):
		"""Função para inicializar a instância com suas dependências."""
		self.session = session

	async def adicionar(self, entity: ModelT) -> ModelT:
		"""Função para salvar um registro no banco de dados."""
		self.session.add(entity)
		await self.session.flush()
		await self.session.refresh(entity)
		return entity

	async def obter(self, entity_id: int) -> ModelT | None:
		"""Função para obter um registro pelo ID."""
		return await self.session.obter(self.model, entity_id)

	async def listar_todos(
		self,
		offset: int = PAGINATION_DEFAULT_OFFSET,
		limit: int = PAGINATION_DEFAULT_LIMIT,
		filters: dict[str, Any] | None = None,
	) -> list[ModelT]:
		"""Função para listar registros com paginação e filtros opcionais."""
		stmt = select(self.model)
		if filters:
			for field, value in filters.items():
				if value is not None and hasattr(self.model, field):
					stmt = stmt.where(getattr(self.model, field) == value)
		stmt = stmt.offset(offset).limit(limit)
		result = await self.session.execute(stmt)
		return list(result.scalars().all())

	async def atualizar(self, entity_id: int, data: dict[str, Any]) -> ModelT | None:
		"""Função para atualizar um registro pelo ID."""
		update_data = self._remover_valores_vazios(data)
		if not update_data:
			return await self.obter(entity_id)
		id_field = getattr(self.model, 'id')
		statement = (
			sa_update(self.model)
			.where(id_field == entity_id)
			.values(**update_data)
			.returning(self.model)
		)

		result = await self.session.execute(statement)

		await self.session.flush()

		return result.scalar_one_or_none()

	async def deletar(self, entity_id: int) -> bool:
		"""Função para excluir um registro pelo ID."""
		id_field = getattr(self.model, 'id')
		statement = (
			sa_delete(self.model).where(id_field == entity_id).returning(id_field)
		)
		result = await self.session.execute(statement)
		await self.session.flush()
		return result.scalar_one_or_none() is not None

	def _aplicar_filtros(self, statement: Any, filters: dict[str, Any] | None) -> Any:
		"""Função interna para aplicar filtros em uma consulta."""
		if not filters:
			return statement

		for field, value in filters.items():
			if value is None:
				continue

			if not hasattr(self.model, field):
				continue

			model_field = getattr(self.model, field)
			statement = statement.where(model_field == value)

		return statement

	@staticmethod
	def _remover_valores_vazios(data: dict[str, Any]) -> dict[str, Any]:
		"""Função interna para remover campos vazios de um dicionário."""
		return {field: value for field, value in data.items() if value is not None}
