from http import HTTPStatus

from fastapi import APIRouter
from sqlalchemy import text

from api.deps import SessionDep

router = APIRouter(prefix='/health', tags=['Saúde'])


@router.get('', status_code=HTTPStatus.OK)
async def health(session: SessionDep):
	await session.execute(text('SELECT 1'))
	return {'status': 'ok'}
