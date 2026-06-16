from fastapi import APIRouter
from modules.academy.controller import router as router_academia
from modules.agenda.controller import router as router_agenda
from modules.comunicados.controller import router as router_comunicados
from modules.dashboard.controller import router as router_painel
from modules.gamificacao.controller import router as router_gamificacao
from modules.integracoes.controller import router as router_integracoes
from modules.leads.controller import router as router_leads
from modules.lgpd.controller import router as router_lgpd
from modules.portfolio.controller import router as router_portfolio
from modules.projetos.controller import router as router_projetos
from modules.servicos.controller import router as router_servicos
from modules.tarefas.controller import router as router_tarefas
from modules.uploads.controller import router as router_uploads
from modules.users.controller import router as router_usuarios

router_api = APIRouter()

for router_modulo in (
	router_academia,
	router_agenda,
	router_comunicados,
	router_painel,
	router_gamificacao,
	router_integracoes,
	router_leads,
	router_lgpd,
	router_portfolio,
	router_projetos,
	router_servicos,
	router_tarefas,
	router_uploads,
	router_usuarios,
):
	router_api.include_router(router_modulo)
