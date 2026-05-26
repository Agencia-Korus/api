# ruff: noqa: E402

import sys
from http import HTTPStatus
from pathlib import Path

DIRETORIO_APLICACAO = Path(__file__).resolve().parent
if str(DIRETORIO_APLICACAO) not in sys.path:
	sys.path.insert(0, str(DIRETORIO_APLICACAO))

from core.config import obter_configuracoes
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from modules.health.controller import roteador as roteador_saude
from v1.router import roteador_api as roteador_api_v1

configuracoes = obter_configuracoes()

app = FastAPI(
	title='Korus API',
	version='0.1.0',
	description=('Backend principal da Korus.'),
)

app.add_middleware(
	CORSMiddleware,
	allow_origins=[o.strip() for o in configuracoes.cors_allow_origins.split(',')],
	allow_credentials=True,
	allow_methods=['*'],
	allow_headers=['*'],
)

app.include_router(roteador_saude)
app.include_router(roteador_api_v1, prefix='/api/v1')


@app.get('/health', response_class=JSONResponse, status_code=HTTPStatus.OK)
async def saude():
	"""Função para verificar se o serviço está disponível."""
	return {'message': 'API is running...'}
