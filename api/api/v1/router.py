from fastapi import APIRouter
from modules.leads.controller import router as leads_router
from modules.portfolio.controller import router as portfolio_router
from modules.servicos.controller import router as servicos_router
from modules.users.controller import router as users_router

api_router = APIRouter()

api_router.include_router(users_router)
api_router.include_router(leads_router)
api_router.include_router(portfolio_router)
api_router.include_router(servicos_router)
