# ruff: noqa: E402

import sys
from http import HTTPStatus
from pathlib import Path

APP_DIR = Path(__file__).resolve().parent
if str(APP_DIR) not in sys.path:
	sys.path.insert(0, str(APP_DIR))

from core.config import obter_settings
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from modules.health.controller import router as health_router
from v1.router import api_router as api_v1_router

settings = obter_settings()

app = FastAPI(
	title='Korus API',
	version='0.1.0',
	description=('Backend principal da Korus.'),
)

app.add_middleware(
	CORSMiddleware,
	allow_origins=[o.strip() for o in settings.cors_allow_origins.split(',')],
	allow_credentials=True,
	allow_methods=['*'],
	allow_headers=['*'],
)

app.include_router(health_router)
app.include_router(api_v1_router, prefix='/api/v1')


@app.get('/health', response_class=JSONResponse, status_code=HTTPStatus.OK)
async def health():
	"""Função para verificar se o serviço está disponível."""
	return {'message': 'API is running...'}
