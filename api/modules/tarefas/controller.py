from typing import Annotated

from core.enums import TarefaStatus, UserRole
from core.security import CurrentUser, get_current_user, require_role
from deps import PaginationDep, SessionDep
from fastapi import APIRouter, Body, Depends, Query, status
from modules.tarefas.schema import (
	AnexoCriar,
	AnexoResposta,
	ComentarioCriar,
	ComentarioResposta,
	TarefaCriar,
	TarefaResposta,
	TarefaAtualizar,
)
from modules.tarefas.service import ServicoTarefa

router = APIRouter(prefix='/tarefas', tags=['Tarefas'])


def _service(session: SessionDep) -> ServicoTarefa:
	"""Função para criar o serviço de aplicação com a sessão atual."""
	return ServicoTarefa(session)


ServiceDep = Annotated[ServicoTarefa, Depends(_service)]
AdminGuard = Depends(require_role(UserRole.ADMIN.value))
CurrentUserDep = Annotated[CurrentUser, Depends(get_current_user)]


@router.post(
	'',
	response_model=TarefaResposta,
	status_code=status.HTTP_201_CREATED,
	dependencies=[AdminGuard],
	summary='Cria tarefa (somente admin)',
)
async def criar(payload: TarefaCriar, service: ServiceDep):
	"""Função para criar um novo registro."""
	return await service.criar(payload)


@router.get(
	'',
	response_model=list[TarefaResposta],
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
	"""Função para listar registros."""
	return await service.listar_visible(
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
	response_model=TarefaResposta,
	summary='Obtém tarefa visível ao usuário autenticado',
)
async def obter(tarefa_id: int, service: ServiceDep, current_user: CurrentUserDep):
	"""Função para obter um registro pelo ID."""
	return await service.obter_visible(tarefa_id, current_user.id, current_user.role)


@router.patch(
	'/{tarefa_id}',
	response_model=TarefaResposta,
	summary='Atualiza card do Kanban (admin ou funcionário envolvido)',
)
async def atualizar(
	tarefa_id: int,
	payload: TarefaAtualizar,
	service: ServiceDep,
	current_user: CurrentUserDep,
):
	"""Função para atualizar um registro pelo ID."""
	await service.ensure_can_manage_tarefa(
		tarefa_id, current_user.id, current_user.role
	)
	return await service.atualizar(tarefa_id, payload)


@router.delete(
	'/{tarefa_id}',
	status_code=status.HTTP_204_NO_CONTENT,
	summary='Remove tarefa (admin ou funcionário envolvido)',
)
async def deletar(tarefa_id: int, service: ServiceDep, current_user: CurrentUserDep):
	"""Função para excluir um registro pelo ID."""
	await service.ensure_can_manage_tarefa(
		tarefa_id, current_user.id, current_user.role
	)
	await service.deletar(tarefa_id)


@router.post(
	'/{tarefa_id}/comentarios',
	response_model=ComentarioResposta,
	status_code=status.HTTP_201_CREATED,
	summary='Comenta no card do Kanban (usuário com acesso à tarefa)',
)
async def comentar(
	tarefa_id: int,
	service: ServiceDep,
	current_user: CurrentUserDep,
	conteudo: Annotated[str, Body(..., embed=True)],
):
	"""Função para adicionar um comentário a uma tarefa."""
	await service.obter_visible(tarefa_id, current_user.id, current_user.role)
	payload = ComentarioCriar(tarefa_id=tarefa_id, conteudo=conteudo)
	return await service.adicionar_comentario(payload, current_user.id)


@router.get(
	'/{tarefa_id}/comentarios',
	response_model=list[ComentarioResposta],
	summary='Lista comentários da tarefa visível ao usuário autenticado',
)
async def listar_comentarios(
	tarefa_id: int, service: ServiceDep, current_user: CurrentUserDep
):
	"""Função para listar comentários de uma tarefa."""
	await service.obter_visible(tarefa_id, current_user.id, current_user.role)
	return await service.listar_comentarios(tarefa_id)


@router.delete(
	'/comentarios/{comentario_id}',
	status_code=status.HTTP_204_NO_CONTENT,
	dependencies=[AdminGuard],
	summary='Remove comentário (somente admin)',
)
async def remover_comentario(comentario_id: int, service: ServiceDep):
	"""Função para remover um comentário pelo ID."""
	await service.deletar_comentario(comentario_id)


@router.post(
	'/{tarefa_id}/anexos',
	response_model=AnexoResposta,
	status_code=status.HTTP_201_CREATED,
	summary='Anexa arquivo à tarefa (admin ou funcionário envolvido)',
)
async def anexar(
	tarefa_id: int,
	payload: AnexoCriar,
	service: ServiceDep,
	current_user: CurrentUserDep,
):
	"""Função para adicionar um anexo a uma tarefa."""
	await service.ensure_can_manage_tarefa(
		tarefa_id, current_user.id, current_user.role
	)
	payload_with_id = payload.model_copy(update={'tarefa_id': tarefa_id})
	return await service.adicionar_anexo(payload_with_id)


@router.get(
	'/{tarefa_id}/anexos',
	response_model=list[AnexoResposta],
	summary='Lista anexos da tarefa visível ao usuário autenticado',
)
async def listar_anexos(
	tarefa_id: int, service: ServiceDep, current_user: CurrentUserDep
):
	"""Função para listar anexos de uma tarefa."""
	await service.obter_visible(tarefa_id, current_user.id, current_user.role)
	return await service.listar_anexos(tarefa_id)


@router.delete(
	'/anexos/{anexo_id}',
	status_code=status.HTTP_204_NO_CONTENT,
	dependencies=[AdminGuard],
	summary='Remove anexo (somente admin)',
)
async def remover_anexo(anexo_id: int, service: ServiceDep):
	"""Função para remover um anexo pelo ID."""
	await service.deletar_anexo(anexo_id)
