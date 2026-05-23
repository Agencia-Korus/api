from modules.leads import model as leads_model
from modules.portfolio import model as portfolio_model
from modules.servicos import model as servicos_model
from modules.users import model as users_model

ALL_MODELS = (
	users_model,
	leads_model,
	servicos_model,
	portfolio_model,
)
