from typing import Annotated

from fastapi import APIRouter, Body, Depends, Query, status

from api.deps import PaginationDep, SessionDep
from core.enums import TarefaStatus, UserRole
from core.security import CurrentUser, get_current_user, require_role
from modules.tarefas.schema import (
	AnexoCreate,
	AnexoResponse,
	ComentarioCreate,
	ComentarioResponse,
	TarefaCreate,
	TarefaResponse,
	TarefaUpdate,
)
from modules.tarefas.service import TarefaService

router = APIRouter(prefix='/tarefas', tags=['Tarefas'])


def _service(session: SessionDep) -> TarefaService:
	return TarefaService(session)


ServiceDep = Annotated[TarefaService, Depends(_service)]
AdminGuard = Depends(require_role(UserRole.ADMIN.value))
CurrentUserDep = Annotated[CurrentUser, Depends(get_current_user)]


@router.post(
	'',
	response_model=TarefaResponse,
	status_code=status.HTTP_201_CREATED,
	dependencies=[AdminGuard],
	summary='Cria tarefa (somente admin)',
)
async def criar(payload: TarefaCreate, service: ServiceDep):
	return await service.create(payload)


@router.get(
	'',
	response_model=list[TarefaResponse],
	summary='Lista tarefas/Kanban visíveis ao usuário autenticado',
	description=(
		'Admin lista tudo. Cliente lista tarefas dos próprios projetos. '
		'Funcionário lista tarefas em que é responsável ou está na equipe do projeto.'
	),
)
async def listar(
	service: ServiceDep,
	page: PaginationDep,
	current_user: CurrentUserDep,
	projeto_id: int | None = None,
	responsavel_id: int | None = None,
	status_filter: Annotated[TarefaStatus | None, Query(alias='status')] = None,
):
	return await service.list_visible(
		offset=page.offset,
		limit=page.limit,
		usuario_id=current_user.id,
		role=current_user.role,
		projeto_id=projeto_id,
		responsavel_id=responsavel_id,
		status=status_filter,
	)


@router.get(
	'/{tarefa_id}',
	response_model=TarefaResponse,
	summary='Obtém tarefa visível ao usuário autenticado',
)
async def obter(tarefa_id: int, service: ServiceDep, current_user: CurrentUserDep):
	return await service.get_visible(tarefa_id, current_user.id, current_user.role)


@router.patch(
	'/{tarefa_id}',
	response_model=TarefaResponse,
	summary='Atualiza card do Kanban (admin ou funcionário envolvido)',
)
async def atualizar(
	tarefa_id: int,
	payload: TarefaUpdate,
	service: ServiceDep,
	current_user: CurrentUserDep,
):
	await service.ensure_can_manage_tarefa(
		tarefa_id, current_user.id, current_user.role
	)
	return await service.update(tarefa_id, payload)


@router.delete(
	'/{tarefa_id}',
	status_code=status.HTTP_204_NO_CONTENT,
	summary='Remove tarefa (admin ou funcionário envolvido)',
)
async def deletar(tarefa_id: int, service: ServiceDep, current_user: CurrentUserDep):
	await service.ensure_can_manage_tarefa(
		tarefa_id, current_user.id, current_user.role
	)
	await service.delete(tarefa_id)


@router.post(
	'/{tarefa_id}/comentarios',
	response_model=ComentarioResponse,
	status_code=status.HTTP_201_CREATED,
	summary='Comenta no card do Kanban (usuário com acesso à tarefa)',
)
async def comentar(
	tarefa_id: int,
	service: ServiceDep,
	current_user: CurrentUserDep,
	conteudo: Annotated[str, Body(..., embed=True)],
):
	await service.get_visible(tarefa_id, current_user.id, current_user.role)
	payload = ComentarioCreate(tarefa_id=tarefa_id, conteudo=conteudo)
	return await service.add_comentario(payload, current_user.id)


@router.get(
	'/{tarefa_id}/comentarios',
	response_model=list[ComentarioResponse],
	summary='Lista comentários da tarefa visível ao usuário autenticado',
)
async def listar_comentarios(
	tarefa_id: int, service: ServiceDep, current_user: CurrentUserDep
):
	await service.get_visible(tarefa_id, current_user.id, current_user.role)
	return await service.list_comentarios(tarefa_id)


@router.delete(
	'/comentarios/{comentario_id}',
	status_code=status.HTTP_204_NO_CONTENT,
	dependencies=[AdminGuard],
	summary='Remove comentário (somente admin)',
)
async def remover_comentario(comentario_id: int, service: ServiceDep):
	await service.delete_comentario(comentario_id)


@router.post(
	'/{tarefa_id}/anexos',
	response_model=AnexoResponse,
	status_code=status.HTTP_201_CREATED,
	summary='Anexa arquivo à tarefa (admin ou funcionário envolvido)',
)
async def anexar(
	tarefa_id: int,
	payload: AnexoCreate,
	service: ServiceDep,
	current_user: CurrentUserDep,
):
	await service.ensure_can_manage_tarefa(
		tarefa_id, current_user.id, current_user.role
	)
	payload_with_id = payload.model_copy(update={'tarefa_id': tarefa_id})
	return await service.add_anexo(payload_with_id)


@router.get(
	'/{tarefa_id}/anexos',
	response_model=list[AnexoResponse],
	summary='Lista anexos da tarefa visível ao usuário autenticado',
)
async def listar_anexos(
	tarefa_id: int, service: ServiceDep, current_user: CurrentUserDep
):
	await service.get_visible(tarefa_id, current_user.id, current_user.role)
	return await service.list_anexos(tarefa_id)


@router.delete(
	'/anexos/{anexo_id}',
	status_code=status.HTTP_204_NO_CONTENT,
	dependencies=[AdminGuard],
	summary='Remove anexo (somente admin)',
)
async def remover_anexo(anexo_id: int, service: ServiceDep):
	await service.delete_anexo(anexo_id)
