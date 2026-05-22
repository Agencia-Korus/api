from typing import Any, Generic, TypeVar

from sqlalchemy import delete as sa_delete
from sqlalchemy import select
from sqlalchemy import update as sa_update
from sqlalchemy.ext.asyncio import AsyncSession

from core.constants import PAGINATION_DEFAULT_LIMIT, PAGINATION_DEFAULT_OFFSET
from db.base import Base

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
		clean = {k: v for k, v in data.items() if v is not None}
		if not clean:
			return await self.get(entity_id)
		stmt = (
			sa_update(self.model)
			.where(self.model.id == entity_id)
			.values(**clean)
			.returning(self.model)
		)
		result = await self.session.execute(stmt)
		await self.session.flush()
		return result.scalar_one_or_none()

	async def delete(self, entity_id: int) -> bool:
		stmt = sa_delete(self.model).where(self.model.id == entity_id)
		result = await self.session.execute(stmt)
		await self.session.flush()
		return result.rowcount > 0