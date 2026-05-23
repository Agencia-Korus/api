<<<<<<< HEAD
=======
from http import HTTPStatus

from api.v1.router import api_router as api_v1_router
>>>>>>> main
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

<<<<<<< HEAD
from api.v1.router import api_router as api_v1_router
from core.config import get_settings
from modules.health.controller import router as health_router

settings = get_settings()
=======
app = FastAPI(title='API Korus', version='0.1.0')
>>>>>>> main

app = FastAPI(
	title='Korus API',
	version='0.1.0',
	description=(
		'Backend principal da Korus.'
	),
)

<<<<<<< HEAD
app.add_middleware(
	CORSMiddleware,
	allow_origins=[o.strip() for o in settings.cors_allow_origins.split(',')],
	allow_credentials=True,
	allow_methods=['*'],
	allow_headers=['*'],
)

app.include_router(health_router)
app.include_router(api_v1_router, prefix='/api/v1')
=======

@app.get('/health', response_class=JSONResponse, status_code=HTTPStatus.OK)
async def health():
	return {'message': 'API is running...'}
>>>>>>> main
