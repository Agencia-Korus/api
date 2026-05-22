from fastapi import APIRouter

from modules.portfolio.controller import router as portfolio_router
from modules.posts.controller import router as posts_router
from modules.servicos.controller import router as servicos_router

api_router = APIRouter()

api_router.include_router(portfolio_router)
api_router.include_router(posts_router)
api_router.include_router(servicos_router)