from http import HTTPStatus

from fastapi import FastAPI
from fastapi.responses import JSONResponse

from api.v1.router import api_router as api_v1_router

app = FastAPI(title='API Korus', version='0.1.0')

app.include_router(api_v1_router, prefix='/api/v1')

@app.get('/health', response_class=JSONResponse, status_code=HTTPStatus.OK)
async def health():
	return {'message': 'API is running...'}
