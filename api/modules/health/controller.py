from http import HTTPStatus

from deps import DependenciaSessao
from fastapi import APIRouter
from sqlalchemy import text

roteador = APIRouter(prefix='/health/db', tags=['Saúde'])


@roteador.get('', status_code=HTTPStatus.OK)
async def saude(sessao: DependenciaSessao):
	"""Função para verificar se o serviço está disponível."""
	await sessao.execute(text('SELECT 1'))
	return {'status': 'ok'}
