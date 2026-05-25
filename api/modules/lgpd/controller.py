from typing import Annotated

from core.enums import UserRole
from core.security import require_role
from deps import PaginationDep, SessionDep
from fastapi import APIRouter, Depends, status
from modules.lgpd.schema import ConsentimentoLgpdCriar, ConsentimentoLgpdResposta
from modules.lgpd.service import ServicoLgpd

router = APIRouter(prefix='/lgpd', tags=['LGPD'])


def _service(session: SessionDep) -> ServicoLgpd:
	"""Função para criar o serviço de aplicação com a sessão atual."""
	return ServicoLgpd(session)


ServiceDep = Annotated[ServicoLgpd, Depends(_service)]
AdminGuard = Depends(require_role(UserRole.ADMIN.value))


@router.post(
	'/consentimentos',
	response_model=ConsentimentoLgpdResposta,
	status_code=status.HTTP_201_CREATED,
	summary='Registra consentimento LGPD',
	description=(
		'Endpoint usado pelo site para registrar consentimento de cookies/LGPD. '
		'Pode ser usado sem login quando ainda não existe usuário autenticado.'
	),
)
async def registrar(payload: ConsentimentoLgpdCriar, service: ServiceDep):
	"""Função para registrar um consentimento LGPD."""
	return await service.registrar(payload)


@router.get(
	'/consentimentos',
	response_model=list[ConsentimentoLgpdResposta],
	dependencies=[AdminGuard],
	summary='Lista consentimentos LGPD (somente admin)',
)
async def listar(service: ServiceDep, page: PaginationDep):
	"""Função para listar registros."""
	return await service.listar(offset=page.offset, limit=page.limit)
