from http import HTTPStatus

from deps import SessionDep
from fastapi import APIRouter
from sqlalchemy import text

router = APIRouter(prefix='/health/db', tags=['Saúde'])


@router.get('', status_code=HTTPStatus.OK)
async def health(session: SessionDep):
	await session.execute(text('SELECT 1'))
	return {'status': 'ok'}
