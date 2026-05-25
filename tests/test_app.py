from http import HTTPStatus

from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_health():
	response = client.get('/health')
	assert response.status_code == HTTPStatus.OK
	assert response.json() == {'message': 'API is running...'}


def test_swagger_authorize_usa_endpoint_do_auth_service():
	openapi = client.get('/openapi.json')
	token_url = openapi.json()['components']['securitySchemes']['OAuth2PasswordBearer'][
		'flows'
	]['password']['tokenUrl']
	assert openapi.status_code == HTTPStatus.OK
	assert token_url == '/api/v1/auth/login'
