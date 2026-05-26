from typing import Annotated

from core.enums import ComunicadoAlvo, PapelUsuario
from core.security import exigir_papel, obter_usuario_atual_id
from core.swagger import exemplo_requisicao_json
from deps import DependenciaPaginacao, DependenciaSessao
from fastapi import APIRouter, Depends, Query, status
from modules.comunicados.schema import (
	ComunicadoAtualizar,
	ComunicadoCriar,
	ComunicadoLeituraResposta,
	ComunicadoResposta,
)
from modules.comunicados.service import ServicoComunicado

router = APIRouter(prefix='/comunicados', tags=['Comunicados'])


def _servico(sessao: DependenciaSessao) -> ServicoComunicado:
	"""Função para criar o serviço de aplicação com a sessão atual."""
	return ServicoComunicado(sessao)


DependenciaServico = Annotated[ServicoComunicado, Depends(_servico)]
IdUsuarioAtual = Annotated[int, Depends(obter_usuario_atual_id)]
GuardaAdmin = Depends(exigir_papel(PapelUsuario.ADMIN.value))
AuthenticatedGuard = Depends(
	exigir_papel(
		PapelUsuario.CLIENTE.value,
		PapelUsuario.FUNCIONARIO.value,
		PapelUsuario.ADMIN.value,
	)
)


@router.post(
	'',
	response_model=ComunicadoResposta,
	status_code=status.HTTP_201_CREATED,
	dependencies=[GuardaAdmin],
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
	openapi_extra=exemplo_requisicao_json({
		'offset': 0,
		'limit': 20,
		'alvo': 'todos',
	}),
)
async def listar(
	servico: DependenciaServico,
	pagina: DependenciaPaginacao,
	alvo: Annotated[ComunicadoAlvo | None, Query()] = None,
):
	"""Função para listar registros."""
	return await servico.listar_filtrados(
		offset=pagina.offset, limit=pagina.limit, alvo=alvo
	)


@router.get(
	'/{comunicado_id}',
	response_model=ComunicadoResposta,
	dependencies=[AuthenticatedGuard],
	summary='Obtém comunicado (clientes, funcionários e admins)',
	openapi_extra=exemplo_requisicao_json({'comunicado_id': 1}),
)
async def obter(comunicado_id: int, servico: DependenciaServico):
	"""Função para obter um registro pelo ID."""
	return await servico.obter(comunicado_id)


@router.patch(
	'/{comunicado_id}',
	response_model=ComunicadoResposta,
	dependencies=[GuardaAdmin],
	summary='Atualiza comunicado (somente admin)',
)
async def atualizar(
	comunicado_id: int, dados: ComunicadoAtualizar, servico: DependenciaServico
):
	"""Função para atualizar um registro pelo ID."""
	return await servico.atualizar(comunicado_id, dados)


@router.delete(
	'/{comunicado_id}',
	status_code=status.HTTP_204_NO_CONTENT,
	dependencies=[GuardaAdmin],
	summary='Remove comunicado (somente admin)',
	openapi_extra=exemplo_requisicao_json({'comunicado_id': 1}),
)
async def deletar(comunicado_id: int, servico: DependenciaServico):
	"""Função para excluir um registro pelo ID."""
	await servico.deletar(comunicado_id)


@router.post(
	'/{comunicado_id}/leituras',
	response_model=ComunicadoLeituraResposta,
	status_code=status.HTTP_201_CREATED,
	summary='Marca comunicado como lido (usuário autenticado)',
	openapi_extra=exemplo_requisicao_json({'comunicado_id': 1}),
)
async def marcar_lido(
	comunicado_id: int, servico: DependenciaServico, id_usuario_atual: IdUsuarioAtual
):
	"""Função para registrar a leitura de um comunicado."""
	return await servico.marcar_lido(comunicado_id, id_usuario_atual)


@router.get(
	'/{comunicado_id}/leituras',
	response_model=list[ComunicadoLeituraResposta],
	dependencies=[GuardaAdmin],
	summary='Lista leituras do comunicado (somente admin)',
	openapi_extra=exemplo_requisicao_json({'comunicado_id': 1}),
)
async def listar_leituras(comunicado_id: int, servico: DependenciaServico):
	"""Função para listar leituras de um comunicado."""
	return await servico.listar_leituras(comunicado_id)
