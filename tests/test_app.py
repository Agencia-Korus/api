from http import HTTPStatus

from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_health():
	response = client.get('/health')
	assert response.status_code == HTTPStatus.OK
	assert response.json() == {'message': 'API is running...'}


def test_swagger_authorize_usa_bearer_sem_chamada_de_login():
	openapi = client.get('/openapi.json')
	security_scheme = openapi.json()['components']['securitySchemes']['HTTPBearer']
	assert openapi.status_code == HTTPStatus.OK
	assert security_scheme == {'type': 'http', 'scheme': 'bearer'}
