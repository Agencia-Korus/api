from fastapi import APIRouter
from modules.academy.controller import roteador as roteador_academia
from modules.agenda.controller import roteador as roteador_agenda
from modules.comunicados.controller import roteador as roteador_comunicados
from modules.dashboard.controller import roteador as roteador_painel
from modules.gamificacao.controller import roteador as roteador_gamificacao
from modules.integracoes.controller import roteador as roteador_integracoes
from modules.leads.controller import roteador as roteador_leads
from modules.lgpd.controller import roteador as roteador_lgpd
from modules.portfolio.controller import roteador as roteador_portfolio
from modules.projetos.controller import roteador as roteador_projetos
from modules.servicos.controller import roteador as roteador_servicos
from modules.tarefas.controller import roteador as roteador_tarefas
from modules.users.controller import roteador as roteador_usuarios

roteador_api = APIRouter()

for roteador_modulo in (
	roteador_academia,
	roteador_agenda,
	roteador_comunicados,
	roteador_painel,
	roteador_gamificacao,
	roteador_integracoes,
	roteador_leads,
	roteador_lgpd,
	roteador_portfolio,
	roteador_projetos,
	roteador_servicos,
	roteador_tarefas,
	roteador_usuarios,
):
	roteador_api.include_router(roteador_modulo)
