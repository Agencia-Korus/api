from fastapi import APIRouter
from modules.academy.controller import router as academy_router
from modules.agenda.controller import router as agenda_router
from modules.comunicados.controller import router as comunicados_router
from modules.dashboard.controller import router as dashboard_router
from modules.gamificacao.controller import router as gamificacao_router
from modules.integracoes.controller import router as integracoes_router
from modules.leads.controller import router as leads_router
from modules.lgpd.controller import router as lgpd_router
from modules.portfolio.controller import router as portfolio_router
from modules.projetos.controller import router as projetos_router
from modules.servicos.controller import router as servicos_router
from modules.tarefas.controller import router as tarefas_router
from modules.users.controller import router as users_router

api_router = APIRouter()

for module_router in (
    academy_router,
    agenda_router,
    comunicados_router,
    dashboard_router,
    gamificacao_router,
    integracoes_router,
    leads_router,
    lgpd_router,
    portfolio_router,
    projetos_router,
    servicos_router,
    tarefas_router,
    users_router
):
    api_router.include_router(module_router)
