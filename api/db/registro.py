from modules.academy import model as modelo_academia
from modules.agenda import model as modelo_agenda
from modules.comunicados import model as modelo_comunicados
from modules.gamificacao import model as modelo_gamificacao
from modules.integracoes import model as modelo_integracoes
from modules.leads import model as modelo_leads
from modules.lgpd import model as modelo_lgpd
from modules.portfolio import model as modelo_portfolio
from modules.projetos import model as modelo_projetos
from modules.servicos import model as modelo_servicos
from modules.tarefas import model as modelo_tarefas
from modules.users import model as modelo_usuarios

# utilizado na env de migração do Alembic
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
