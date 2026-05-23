from collections.abc import AsyncGenerator

from core.database import normalize_async_database_url
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from core.config import get_settings

settings = get_settings()
database_url, connect_args = normalize_async_database_url(settings.database_url)

engine = create_async_engine(
	url=database_url,
	echo=settings.debug,
	pool_pre_ping=True,
	connect_args=connect_args,
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
