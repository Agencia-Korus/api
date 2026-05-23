from typing import Annotated

from fastapi import APIRouter, Depends, status

from api.deps import PaginationDep, SessionDep
from core.enums import UserRole
from core.security import require_role
from modules.lgpd.schema import ConsentimentoLgpdCreate, ConsentimentoLgpdResponse
from modules.lgpd.service import LgpdService

router = APIRouter(prefix='/lgpd', tags=['LGPD'])


def _service(session: SessionDep) -> LgpdService:
	return LgpdService(session)


ServiceDep = Annotated[LgpdService, Depends(_service)]
AdminGuard = Depends(require_role(UserRole.ADMIN.value))


@router.post(
	'/consentimentos',
	response_model=ConsentimentoLgpdResponse,
	status_code=status.HTTP_201_CREATED,
	summary='Registra consentimento LGPD',
	description=(
		'Endpoint usado pelo site para registrar consentimento de cookies/LGPD. '
		'Pode ser usado sem login quando ainda não existe usuário autenticado.'
	),
)
async def registrar(payload: ConsentimentoLgpdCreate, service: ServiceDep):
	return await service.registrar(payload)


@router.get(
	'/consentimentos',
	response_model=list[ConsentimentoLgpdResponse],
	dependencies=[AdminGuard],
	summary='Lista consentimentos LGPD (somente admin)',
)
async def listar(service: ServiceDep, page: PaginationDep):
	return await service.listar(offset=page.offset, limit=page.limit)
