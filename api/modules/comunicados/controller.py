from typing import Annotated

from core.enums import ComunicadoAlvo, UserRole
from core.security import obter_usuario_atual_id, require_role
from deps import DependenciaPaginacao, DependenciaSessao
from fastapi import APIRouter, Depends, Query, status
from modules.comunicados.schema import (
	ComunicadoCriar,
	ComunicadoLeituraResposta,
	ComunicadoResposta,
	ComunicadoAtualizar,
)
from modules.comunicados.service import ServicoComunicado

router = APIRouter(prefix='/comunicados', tags=['Comunicados'])


def _service(session: DependenciaSessao) -> ServicoComunicado:
	"""Função para criar o serviço de aplicação com a sessão atual."""
	return ServicoComunicado(session)


DependenciaServico = Annotated[ServicoComunicado, Depends(_service)]
CurrentUserId = Annotated[int, Depends(obter_usuario_atual_id)]
AdminGuard = Depends(require_role(UserRole.ADMIN.value))
AuthenticatedGuard = Depends(
	require_role(
		UserRole.CLIENTE.value,
		UserRole.FUNCIONARIO.value,
		UserRole.ADMIN.value,
	)
)


@router.post(
	'',
	response_model=ComunicadoResposta,
	status_code=status.HTTP_201_CREATED,
	dependencies=[AdminGuard],
	summary='Cria comunicado (somente admin)',
)
async def criar(dados: ComunicadoCriar, servico: DependenciaServico):
	"""Função para criar um novo registro."""
	return await servico.criar(dados)


@router.get(
	'',
	response_model=list[ComunicadoResposta],
	dependencies=[AuthenticatedGuard],
	summary='Lista comunicados (clientes, funcionários e admins)',
)
async def listar(
	servico: DependenciaServico,
	pagina: DependenciaPaginacao,
	alvo: Annotated[ComunicadoAlvo | None, Query()] = None,
):
	"""Função para listar registros."""
	return await servico.listar_filtrados(offset=pagina.offset, limit=pagina.limit, alvo=alvo)


@router.get(
	'/{comunicado_id}',
	response_model=ComunicadoResposta,
	dependencies=[AuthenticatedGuard],
	summary='Obtém comunicado (clientes, funcionários e admins)',
)
async def obter(comunicado_id: int, servico: DependenciaServico):
	"""Função para obter um registro pelo ID."""
	return await servico.obter(comunicado_id)


@router.patch(
	'/{comunicado_id}',
	response_model=ComunicadoResposta,
	dependencies=[AdminGuard],
	summary='Atualiza comunicado (somente admin)',
)
async def atualizar(comunicado_id: int, dados: ComunicadoAtualizar, servico: DependenciaServico):
	"""Função para atualizar um registro pelo ID."""
	return await servico.atualizar(comunicado_id, dados)


@router.delete(
	'/{comunicado_id}',
	status_code=status.HTTP_204_NO_CONTENT,
	dependencies=[AdminGuard],
	summary='Remove comunicado (somente admin)',
)
async def deletar(comunicado_id: int, servico: DependenciaServico):
	"""Função para excluir um registro pelo ID."""
	await servico.deletar(comunicado_id)


@router.post(
	'/{comunicado_id}/leituras',
	response_model=ComunicadoLeituraResposta,
	status_code=status.HTTP_201_CREATED,
	summary='Marca comunicado como lido (usuário autenticado)',
)
async def marcar_lido(
	comunicado_id: int, servico: DependenciaServico, current_user_id: CurrentUserId
):
	"""Função para registrar a leitura de um comunicado."""
	return await servico.marcar_lido(comunicado_id, current_user_id)


@router.get(
	'/{comunicado_id}/leituras',
	response_model=list[ComunicadoLeituraResposta],
	dependencies=[AdminGuard],
	summary='Lista leituras do comunicado (somente admin)',
)
async def listar_leituras(comunicado_id: int, servico: DependenciaServico):
	"""Função para listar leituras de um comunicado."""
	return await servico.listar_leituras(comunicado_id)
