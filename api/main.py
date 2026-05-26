# ruff: noqa: E402

import sys
from http import HTTPStatus
from pathlib import Path
from urllib.parse import parse_qsl, urlencode

DIRETORIO_APLICACAO = Path(__file__).resolve().parent
if str(DIRETORIO_APLICACAO) not in sys.path:
	sys.path.insert(0, str(DIRETORIO_APLICACAO))

from core.config import obter_configuracoes
from core.swagger import exemplo_requisicao_json
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from modules.health.controller import router as router_saude
from v1.router import router_api as router_api_v1

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


def _valor_query(valor):
	"""Função para converter valores JSON para parâmetros de query HTTP."""
	if isinstance(valor, bool):
		return str(valor).lower()
	return str(valor)


@app.middleware('http')
async def aplicar_json_como_filtros_get(request: Request, chamar_proximo):
	"""Função para aceitar no GET o JSON de filtros exibido no Swagger."""
	if request.method == 'GET' and 'application/json' in request.headers.get('content-type', ''):
		try:
			dados = await request.json()
		except ValueError:
			dados = None
		if isinstance(dados, dict):
			parametros = parse_qsl(
				request.scope.get('query_string', b'').decode(),
				keep_blank_values=True,
			)
			nomes_existentes = {nome for nome, _ in parametros}
			parametros.extend(
				(nome, _valor_query(valor))
				for nome, valor in dados.items()
				if valor is not None and nome not in nomes_existentes
			)
			request.scope['query_string'] = urlencode(parametros).encode()
	return await chamar_proximo(request)


app.include_router(router_saude)
app.include_router(router_api_v1, prefix='/api/v1')


@app.get(
	'/health',
	response_class=JSONResponse,
	status_code=HTTPStatus.OK,
	openapi_extra=exemplo_requisicao_json({}),
)
async def saude():
	"""Função para verificar se o serviço está disponível."""
	return {'message': 'API is running...'}
