from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from modules.posts.model import Post
from modules.posts.schema import PostCreate, PostResponse


class PostRepository:
	def __init__(self, session: AsyncSession):
		self.session = session

	async def create(self, payload: PostCreate):
		post = Post(title=payload.title, description=payload.description)
		self.session.add(post)
		await self.session.flush()
		await self.session.refresh(post)

		return post

	async def get_all(self) -> list[PostResponse]:
		stmt = select(Post).order_by(Post.created_at.desc())
		result = await self.session.execute(stmt)

		return list(result.scalars().all())

	async def get_by_id(self, post_id: int) -> PostResponse | None:
		return await self.session.get(Post, post_id)
