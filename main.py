from http import HTTPStatus

from fastapi import FastAPI
from fastapi.responses import JSONResponse

app = FastAPI(title='API Korus')


@app.get('/health', response_class=JSONResponse, status_code=HTTPStatus.OK)
async def health():
	return {'message': 'API is running...'}
