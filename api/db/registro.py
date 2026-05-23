from modules.academy import model as academy_model
from modules.agenda import model as agenda_model
from modules.comunicados import model as comunicados_model
from modules.gamificacao import model as gamificacao_model
from modules.integracoes import model as integracoes_model
from modules.leads import model as leads_model
from modules.lgpd import model as lgpd_model
from modules.portfolio import model as portfolio_model
from modules.projetos import model as projetos_model
from modules.servicos import model as servicos_model
from modules.tarefas import model as tarefas_model
from modules.users import model as users_model

# utilizado na env de migração do allembic
ALL_MODELS = (
	academy_model,
	agenda_model,
	comunicados_model,
	gamificacao_model,
	integracoes_model,
	leads_model,
	lgpd_model,
	portfolio_model,
	projetos_model,
	servicos_model,
	tarefas_model,
	users_model,
)
