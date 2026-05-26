from typing import Annotated

from core.enums import PapelUsuario, SituacaoUsuario
from core.security import exigir_papel
from deps import DependenciaPaginacao, DependenciaSessao
from fastapi import APIRouter, Depends, Query, status
from modules.users.schema import (
	UsuarioAtualizar,
	UsuarioCriar,
	UsuarioResposta,
)
from modules.users.service import ServicoUsuario
from starlette.status import HTTP_201_CREATED

roteador = APIRouter(prefix='/usuarios', tags=['Usuários'])


def _servico(sessao: DependenciaSessao) -> ServicoUsuario:
	"""Função para criar o serviço de aplicação com a sessão atual."""
	return ServicoUsuario(sessao)


DependenciaServico = Annotated[ServicoUsuario, Depends(_servico)]
GuardaAdmin = Depends(exigir_papel(PapelUsuario.ADMIN.value))


@roteador.post(
	'',
	response_model=UsuarioResposta,
	status_code=HTTP_201_CREATED,
	dependencies=[GuardaAdmin],
	summary='Cria usuário (somente admin)',
)
async def criar(dados: UsuarioCriar, servico: DependenciaServico):
	"""Função para criar um novo registro."""
	return await servico.criar(dados)


@roteador.get('', response_model=list[UsuarioResposta], dependencies=[GuardaAdmin])
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


@roteador.get(
	'/{usuario_id}', response_model=UsuarioResposta, dependencies=[GuardaAdmin]
)
async def obter(usuario_id: int, servico: DependenciaServico):
	"""Função para obter um registro pelo ID."""
	return await servico.obter(usuario_id)


@roteador.patch(
	'/{usuario_id}',
	response_model=UsuarioResposta,
	dependencies=[GuardaAdmin],
	summary='Edita dados do usuário (somente admin)',
)
async def atualizar(
	usuario_id: int, dados: UsuarioAtualizar, servico: DependenciaServico
):
	"""Função para atualizar um registro pelo ID."""
	return await servico.atualizar(usuario_id, dados)


@roteador.post(
	'/{usuario_id}/aprovar',
	response_model=UsuarioResposta,
	dependencies=[GuardaAdmin],
	summary='Aprova cadastro pendente, ativando o usuário (somente admin)',
)
async def aprovar(usuario_id: int, servico: DependenciaServico):
	"""Função para aprovar o cadastro de um usuário."""
	return await servico.aprovar(usuario_id)


@roteador.delete(
	'/{usuario_id}',
	status_code=status.HTTP_204_NO_CONTENT,
	dependencies=[GuardaAdmin],
	summary='Remove usuário (somente admin)',
)
async def deletar(usuario_id: int, servico: DependenciaServico):
	"""Função para excluir um registro pelo ID."""
	await servico.deletar(usuario_id)
