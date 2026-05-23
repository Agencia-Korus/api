from typing import Annotated

from core.enums import UserRole
from core.security import CurrentUser, get_current_user, require_role
from deps import SessionDep
from fastapi import APIRouter, Depends
from modules.dashboard.service import DashboardService

router = APIRouter(prefix='/dashboard', tags=['Dashboard'])


def _service(session: SessionDep) -> DashboardService:
	return DashboardService(session)


ServiceDep = Annotated[DashboardService, Depends(_service)]
AdminGuard = Depends(require_role(UserRole.ADMIN.value))
CurrentUserDep = Annotated[CurrentUser, Depends(get_current_user)]


@router.get(
	'/admin',
	dependencies=[AdminGuard],
	summary='Dashboard geral da agência (somente admin)',
)
async def admin(service: ServiceDep):
	return await service.admin()


@router.get(
	'/clientes/{cliente_id}',
	summary='Dashboard do cliente autenticado ou admin',
	description=(
		'Admin pode consultar qualquer cliente. Cliente consulta apenas o próprio '
		'painel.'
	),
)
async def cliente(
	cliente_id: int, service: ServiceDep, current_user: CurrentUserDep
):
	return await service.cliente(cliente_id, current_user.id, current_user.role)


@router.get(
	'/funcionarios/{funcionario_id}',
	summary='Dashboard do funcionário autenticado ou admin',
	description=(
		'Admin pode consultar qualquer funcionário. Funcionário consulta apenas '
		'o próprio painel.'
	),
)
async def funcionario(
	funcionario_id: int, service: ServiceDep, current_user: CurrentUserDep
):
	return await service.funcionario(
		funcionario_id, current_user.id, current_user.role
	)


@router.get(
	'/projetos/{projeto_id}/kanban',
	summary='Kanban do projeto visível ao usuário autenticado',
	description=(
		'Admin vê qualquer projeto. Cliente vê projetos próprios. Funcionário '
		'vê projetos onde participa da equipe.'
	),
)
async def projeto_kanban(
	projeto_id: int, service: ServiceDep, current_user: CurrentUserDep
):
	return await service.projeto_kanban(
		projeto_id, current_user.id, current_user.role
	)
