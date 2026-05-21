from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from modules.posts.repository import PostRepository
from modules.posts.schema import PostCreate, PostResponse


class PostService:
	def __init__(self, session: AsyncSession):
		self.session = session
		self.repository = PostRepository(session)

	async def create_post(self, payload: PostCreate) -> PostResponse:
		post = await self.repository.create(payload)
		await self.session.commit()
		return post

	async def get_posts(self) -> list[PostResponse]:
		return await self.repository.get_all()

	async def get_post_by_id(self, post_id: int) -> PostResponse:
		post = await self.repository.get_by_id(post_id)

		if not post:
			raise HTTPException(
				status_code=status.HTTP_404_NOT_FOUND, detail='Post não encontrado'
			)
		return post
