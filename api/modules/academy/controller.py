from typing import Annotated

from core.enums import AcademyTipo, UserRole
from core.security import require_role
from deps import PaginationDep, SessionDep
from fastapi import APIRouter, Depends, Query, status
from modules.academy.schema import AcademyCriar, AcademyResposta, AcademyAtualizar
from modules.academy.service import ServicoAcademy

router = APIRouter(prefix='/academy', tags=['Academy'])


def _service(session: SessionDep) -> ServicoAcademy:
	"""Função para criar o serviço de aplicação com a sessão atual."""
	return ServicoAcademy(session)


ServiceDep = Annotated[ServicoAcademy, Depends(_service)]
AdminGuard = Depends(require_role(UserRole.ADMIN.value))


@router.post(
	'',
	response_model=AcademyResposta,
	status_code=status.HTTP_201_CREATED,
	dependencies=[AdminGuard],
	summary='Cria conteúdo no Academy (somente admin)',
)
async def criar(payload: AcademyCriar, service: ServiceDep):
	"""Função para criar um novo registro."""
	return await service.criar(payload)


@router.get(
	'',
	response_model=list[AcademyResposta],
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
	return await service.listar_filtrados(
		offset=page.offset, limit=page.limit, tipo=tipo, publicado=publicado
	)


@router.get(
	'/admin',
	response_model=list[AcademyResposta],
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
	return await service.listar_filtrados(
		offset=page.offset, limit=page.limit, tipo=tipo, publicado=publicado
	)


@router.get(
	'/{item_id}',
	response_model=AcademyResposta,
	summary='Obtém conteúdo do Academy (público/home)',
)
async def obter(item_id: int, service: ServiceDep):
	"""Função para obter um registro pelo ID."""
	return await service.obter(item_id)


@router.patch(
	'/{item_id}',
	response_model=AcademyResposta,
	dependencies=[AdminGuard],
	summary='Atualiza conteúdo no Academy (somente admin)',
)
async def atualizar(item_id: int, payload: AcademyAtualizar, service: ServiceDep):
	"""Função para atualizar um registro pelo ID."""
	return await service.atualizar(item_id, payload)


@router.delete(
	'/{item_id}',
	status_code=status.HTTP_204_NO_CONTENT,
	dependencies=[AdminGuard],
	summary='Remove conteúdo do Academy (somente admin)',
)
async def deletar(item_id: int, service: ServiceDep):
	"""Função para excluir um registro pelo ID."""
	await service.deletar(item_id)
