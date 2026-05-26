from typing import Annotated

from core.enums import PapelUsuario, SituacaoUsuario
from core.security import exigir_papel
from core.swagger import exemplo_requisicao_json
from deps import DependenciaPaginacao, DependenciaSessao
from fastapi import APIRouter, Depends, Query, status
from modules.users.schema import (
	UsuarioAtualizar,
	UsuarioCriar,
	UsuarioRegistrar,
	UsuarioResposta,
)
from modules.users.service import ServicoUsuario
from starlette.status import HTTP_201_CREATED

router = APIRouter(prefix='/usuarios', tags=['Usuários'])


def _servico(sessao: DependenciaSessao) -> ServicoUsuario:
	"""Função para criar o serviço de aplicação com a sessão atual."""
	return ServicoUsuario(sessao)


DependenciaServico = Annotated[ServicoUsuario, Depends(_servico)]
GuardaAdmin = Depends(exigir_papel(PapelUsuario.ADMIN.value))


@router.post(
	'',
	response_model=UsuarioResposta,
	status_code=HTTP_201_CREATED,
	dependencies=[GuardaAdmin],
	summary='Cria usuário (somente admin)',
)
async def criar(dados: UsuarioCriar, servico: DependenciaServico):
	"""Função para criar um novo registro."""
	return await servico.criar(dados)


@router.get(
	'',
	response_model=list[UsuarioResposta],
	dependencies=[GuardaAdmin],
	openapi_extra=exemplo_requisicao_json({
		'offset': 0,
		'limit': 20,
		'role': 'cliente',
		'status': 'ativo',
		'search': 'Ana',
	}),
)
async def listar(
	servico: DependenciaServico,
	pagina: DependenciaPaginacao,
	papel: Annotated[PapelUsuario | None, Query(alias='role')] = None,
	filtro_situacao: Annotated[SituacaoUsuario | None, Query(alias='status')] = None,
	busca: Annotated[str | None, Query(alias='search')] = None,
):
	"""Função para listar registros."""
	return await servico.listar_filtrados(
		offset=pagina.offset,
		limit=pagina.limit,
		papel=papel,
		status=filtro_situacao,
		busca=busca,
	)


@router.get(
	'/{usuario_id}',
	response_model=UsuarioResposta,
	dependencies=[GuardaAdmin],
	openapi_extra=exemplo_requisicao_json({'usuario_id': 1}),
)
async def obter(usuario_id: int, servico: DependenciaServico):
	"""Função para obter um registro pelo ID."""
	return await servico.obter(usuario_id)


@router.patch(
	'/{usuario_id}',
	response_model=UsuarioResposta,
	dependencies=[GuardaAdmin],
	summary='Edita dados do usuário (somente admin)',
)
async def atualizar(usuario_id: int, dados: UsuarioAtualizar, servico: DependenciaServico):
	"""Função para atualizar um registro pelo ID."""
	return await servico.atualizar(usuario_id, dados)


@router.post(
	'/{usuario_id}/aprovar',
	response_model=UsuarioResposta,
	dependencies=[GuardaAdmin],
	summary='Aprova cadastro pendente, ativando o usuário (somente admin)',
	openapi_extra=exemplo_requisicao_json({'usuario_id': 1}),
)
async def aprovar(usuario_id: int, servico: DependenciaServico):
	"""Função para aprovar o cadastro de um usuário."""
	return await servico.aprovar(usuario_id)


@router.delete(
	'/{usuario_id}',
	status_code=status.HTTP_204_NO_CONTENT,
	dependencies=[GuardaAdmin],
	summary='Remove usuário (somente admin)',
	openapi_extra=exemplo_requisicao_json({'usuario_id': 1}),
)
async def deletar(usuario_id: int, servico: DependenciaServico):
	"""Função para excluir um registro pelo ID."""
	await servico.deletar(usuario_id)


@router.post(
	'/registro',
	response_model=UsuarioResposta,
	status_code=status.HTTP_201_CREATED,
	summary='Registra um novo usuário pendente de aprovação',
)
async def registrar(dados: UsuarioRegistrar, servico: DependenciaServico):
	"""Função para registrar um novo usuário pendente de aprovação."""
	return await servico.registrar(dados)
