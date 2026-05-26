from http import HTTPStatus

from fastapi.testclient import TestClient


def test_saude(cliente_teste: TestClient):
	"""Valida que saude."""
	resposta = cliente_teste.get('/health')
	assert resposta.status_code == HTTPStatus.OK
	assert resposta.json() == {'message': 'API is running...'}


def test_swagger_authorize_usa_bearer_sem_chamada_de_login(
	cliente_teste: TestClient,
):
	"""Valida que swagger authorize usa bearer sem chamada de login."""
	openapi = cliente_teste.get('/openapi.json')
	esquema_seguranca = openapi.json()['components']['securitySchemes']['HTTPBearer']
	assert openapi.status_code == HTTPStatus.OK
	assert esquema_seguranca == {'type': 'http', 'scheme': 'bearer'}


def test_swagger_nao_declara_body_em_get(cliente_teste: TestClient):
	"""Valida que Swagger não envia body em endpoints GET."""
	openapi = cliente_teste.get('/openapi.json')
	operacao_listar_usuarios = openapi.json()['paths']['/api/v1/usuarios']['get']

	assert openapi.status_code == HTTPStatus.OK
	assert 'requestBody' not in operacao_listar_usuarios
