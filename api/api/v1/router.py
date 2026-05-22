from fastapi import APIRouter
from modules.users.controller import router as users_router
from modules.projetos.controller import router as projetos_router
from modules.tarefas.controller import router as tarefas_router
from modules.dashboard.controller import router as dashboard_router



api_router = APIRouter()

api_router.include_router(users_router)
api_router.include_router(projetos_router)
api_router.include_router(tarefas_router)
api_router.include_router(dashboard_router)



