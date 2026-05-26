from modules.academy import modelo as modelo_academia
from modules.agenda import modelo as modelo_agenda
from modules.comunicados import modelo as modelo_comunicados
from modules.gamificacao import modelo as modelo_gamificacao
from modules.integracoes import modelo as modelo_integracoes
from modules.leads import modelo as modelo_leads
from modules.lgpd import modelo as modelo_lgpd
from modules.portfolio import modelo as modelo_portfolio
from modules.projetos import modelo as modelo_projetos
from modules.servicos import modelo as modelo_servicos
from modules.tarefas import modelo as modelo_tarefas
from modules.users import modelo as modelo_usuarios

# utilizado na env de migração do allembic
TODOS_MODELOS = (
	modelo_academia,
	modelo_agenda,
	modelo_comunicados,
	modelo_gamificacao,
	modelo_integracoes,
	modelo_leads,
	modelo_lgpd,
	modelo_portfolio,
	modelo_projetos,
	modelo_servicos,
	modelo_tarefas,
	modelo_usuarios,
)
