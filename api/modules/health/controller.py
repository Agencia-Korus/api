from http import HTTPStatus

from core.swagger import exemplo_requisicao_json
from deps import DependenciaSessao
from fastapi import APIRouter
from sqlalchemy import text

router = APIRouter(prefix='/health/db', tags=['Saúde'])


@router.get('', status_code=HTTPStatus.OK, openapi_extra=exemplo_requisicao_json({}))
async def saude(sessao: DependenciaSessao):
	"""Função para verificar se o serviço está disponível."""
	await sessao.execute(text('SELECT 1'))
	return {'status': 'ok'}
