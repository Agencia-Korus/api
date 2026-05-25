from typing import Annotated

from core.enums import AcademyTipo, UserRole
from core.security import require_role
from deps import PaginationDep, SessionDep
from fastapi import APIRouter, Depends, Query, status
from modules.academy.schema import AcademyCreate, AcademyResponse, AcademyUpdate
from modules.academy.service import AcademyService

router = APIRouter(prefix='/academy', tags=['Academy'])


def _service(session: SessionDep) -> AcademyService:
	"""Função para criar o serviço de aplicação com a sessão atual."""
	return AcademyService(session)


ServiceDep = Annotated[AcademyService, Depends(_service)]
AdminGuard = Depends(require_role(UserRole.ADMIN.value))


@router.post(
	'',
	response_model=AcademyResponse,
	status_code=status.HTTP_201_CREATED,
	dependencies=[AdminGuard],
	summary='Cria conteúdo no Academy (somente admin)',
)
async def criar(payload: AcademyCreate, service: ServiceDep):
	"""Função para criar um novo registro."""
	return await service.create(payload)


@router.get(
	'',
	response_model=list[AcademyResponse],
	summary='Lista conteúdos publicados do Academy (público/home)',
)
async def listar(
	service: ServiceDep,
	page: PaginationDep,
	tipo: AcademyTipo | None = None,
	publicado: Annotated[
		bool,
		Query(description='Por padrão a home lista somente conteúdos publicados.'),
	] = True,
):
	"""Função para listar registros."""
	return await service.list_filtered(
		offset=page.offset, limit=page.limit, tipo=tipo, publicado=publicado
	)


@router.get(
	'/admin',
	response_model=list[AcademyResponse],
	dependencies=[AdminGuard],
	summary='Lista todos os conteúdos do Academy para gestão (somente admin)',
)
async def listar_admin(
	service: ServiceDep,
	page: PaginationDep,
	tipo: AcademyTipo | None = None,
	publicado: bool | None = None,
):
	"""Função para listar registros na visão administrativa."""
	return await service.list_filtered(
		offset=page.offset, limit=page.limit, tipo=tipo, publicado=publicado
	)


@router.get(
	'/{item_id}',
	response_model=AcademyResponse,
	summary='Obtém conteúdo do Academy (público/home)',
)
async def obter(item_id: int, service: ServiceDep):
	"""Função para obter um registro pelo ID."""
	return await service.get(item_id)


@router.patch(
	'/{item_id}',
	response_model=AcademyResponse,
	dependencies=[AdminGuard],
	summary='Atualiza conteúdo no Academy (somente admin)',
)
async def atualizar(item_id: int, payload: AcademyUpdate, service: ServiceDep):
	"""Função para atualizar um registro pelo ID."""
	return await service.update(item_id, payload)


@router.delete(
	'/{item_id}',
	status_code=status.HTTP_204_NO_CONTENT,
	dependencies=[AdminGuard],
	summary='Remove conteúdo do Academy (somente admin)',
)
async def deletar(item_id: int, service: ServiceDep):
	"""Função para excluir um registro pelo ID."""
	await service.delete(item_id)
