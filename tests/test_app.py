from http import HTTPStatus

from fastapi.testclient import TestClient
from main import app

cliente_http = TestClient(app)


def test_saude():
	resposta = cliente_http.get('/health')
	assert resposta.status_code == HTTPStatus.OK
	assert resposta.json() == {'message': 'API is running...'}


def test_swagger_authorize_usa_bearer_sem_chamada_de_login():
	openapi = cliente_http.get('/openapi.json')
	esquema_seguranca = openapi.json()['components']['securitySchemes']['HTTPBearer']
	assert openapi.status_code == HTTPStatus.OK
	assert esquema_seguranca == {'type': 'http', 'scheme': 'bearer'}
