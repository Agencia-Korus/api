from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from db.session import get_session
from modules.posts.schema import PostCreate, PostResponse
from modules.posts.service import PostService

router = APIRouter(prefix='/posts', tags=['Posts'])

SessionDep = Annotated[AsyncSession, Depends(get_session)]


def get_post_service(session: SessionDep) -> PostService:
	return PostService(session)


PostServiceDep = Annotated[PostService, Depends(get_post_service)]


@router.post(
	'',
	response_model=PostResponse,
	status_code=status.HTTP_201_CREATED,
)
async def create_post(payload: PostCreate, service: PostServiceDep):
	return await service.create_post(payload)


@router.get('', response_model=list[PostResponse])
async def list_posts(service: PostServiceDep):
	return await service.get_posts()


@router.get('/{post_id}', response_model=PostResponse)
async def get_post(post_id: int, service: PostServiceDep):
	return await service.get_post_by_id(post_id)
