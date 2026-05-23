from typing import Any, Generic, TypeVar

from db.base import Base
from sqlalchemy import delete as sa_delete
from sqlalchemy import select
from sqlalchemy import update as sa_update
from sqlalchemy.ext.asyncio import AsyncSession

from core.constants import PAGINATION_DEFAULT_LIMIT, PAGINATION_DEFAULT_OFFSET

ModelT = TypeVar('ModelT', bound=Base)


class BaseRepository(Generic[ModelT]):
	model: type[ModelT]

	def __init__(self, session: AsyncSession):
		self.session = session

	async def add(self, entity: ModelT) -> ModelT:
		self.session.add(entity)
		await self.session.flush()
		await self.session.refresh(entity)
		return entity

	async def get(self, entity_id: int) -> ModelT | None:
		return await self.session.get(self.model, entity_id)

	async def list_all(
		self,
		offset: int = PAGINATION_DEFAULT_OFFSET,
		limit: int = PAGINATION_DEFAULT_LIMIT,
		filters: dict[str, Any] | None = None,
	) -> list[ModelT]:
		stmt = select(self.model)
		if filters:
			for field, value in filters.items():
				if value is not None and hasattr(self.model, field):
					stmt = stmt.where(getattr(self.model, field) == value)
		stmt = stmt.offset(offset).limit(limit)
		result = await self.session.execute(stmt)
		return list(result.scalars().all())

	async def update(self, entity_id: int, data: dict[str, Any]) -> ModelT | None:
		update_data = self._remove_empty_values(data)
		if not update_data:
			return await self.get(entity_id)
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

	async def delete(self, entity_id: int) -> bool:
		id_field = getattr(self.model, 'id')
		statement = sa_delete(self.model).where(id_field == entity_id)
		result = await self.session.execute(statement)
		await self.session.flush()
		deleted_id = result.scalar_one_or_none()
		return deleted_id is not None

	def _apply_filters(self, statement: Any, filters: dict[str, Any] | None) -> Any:
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
	def _remove_empty_values(data: dict[str, Any]) -> dict[str, Any]:
		return {field: value for field, value in data.items() if value is not None}
