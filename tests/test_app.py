from http import HTTPStatus

from fastapi.testclient import TestClient

from api.app import app

client = TestClient(app)


def test_health():
	response = client.get('/')
	assert response.status_code == HTTPStatus.OK
	assert response.json() == {'message': 'API is running...'}
