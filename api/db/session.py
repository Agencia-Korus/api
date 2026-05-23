from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from core.config import get_settings

settings = get_settings()

engine = create_async_engine(
	url=settings.database_url, echo=settings.debug, pool_pre_ping=True
)

AsyncSessionLocal = async_sessionmaker(
	bind=engine, class_=AsyncSession, autoflush=False, expire_on_commit=False
)


async def get_session() -> AsyncGenerator[AsyncSession, None]:
	async with AsyncSessionLocal() as session:
		try:
			yield session
		except Exception:
			await session.rollback()
			raise
