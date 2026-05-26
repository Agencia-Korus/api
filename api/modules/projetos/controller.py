from typing import Annotated

from core.enums import PapelUsuario, SituacaoProjeto
from core.security import UsuarioAtual, exigir_papel, obter_usuario_atual
from core.swagger import exemplo_requisicao_json
from deps import DependenciaPaginacao, DependenciaSessao
from fastapi import APIRouter, Depends, Query, status
from modules.projetos.schema import (
	ProjetoAtualizar,
	ProjetoCriar,
	ProjetoFuncionarioCriar,
	ProjetoFuncionarioResposta,
	ProjetoResposta,
)
from modules.projetos.service import ServicoProjeto

router = APIRouter(prefix='/projetos', tags=['Projetos'])


def _servico(sessao: DependenciaSessao) -> ServicoProjeto:
	"""Função para criar o serviço de aplicação com a sessão atual."""
	return ServicoProjeto(sessao)


DependenciaServico = Annotated[ServicoProjeto, Depends(_servico)]
GuardaAdmin = Depends(exigir_papel(PapelUsuario.ADMIN.value))
DependenciaUsuarioAtual = Annotated[UsuarioAtual, Depends(obter_usuario_atual)]


@router.post(
	'',
	response_model=ProjetoResposta,
	status_code=status.HTTP_201_CREATED,
	dependencies=[GuardaAdmin],
	summary='Cria projeto e define cliente vinculado (somente admin)',
)
async def criar(dados: ProjetoCriar, servico: DependenciaServico):
	"""Função para criar um novo registro."""
	return await servico.criar(dados)


@router.get(
	'',
	response_model=list[ProjetoResposta],
	summary='Lista projetos visíveis ao usuário autenticado',
	description=(
		'Admin lista todos. Cliente lista os próprios projetos. Funcionário '
		'lista projetos onde participa da equipe.'
	),
	openapi_extra=exemplo_requisicao_json({
		'offset': 0,
		'limit': 20,
		'cliente_id': 1,
		'status': 'em_andamento',
	}),
)
async def listar(
	servico: DependenciaServico,
	pagina: DependenciaPaginacao,
	usuario_atual: DependenciaUsuarioAtual,
	cliente_id: int | None = None,
	filtro_situacao: Annotated[SituacaoProjeto | None, Query(alias='status')] = None,
):
	"""Função para listar registros."""
	return await servico.listar_visiveis(
		offset=pagina.offset,
		limit=pagina.limit,
		usuario_id=usuario_atual.id,
		papel=usuario_atual.papel,
		cliente_id=cliente_id,
		status=filtro_situacao,
	)


@router.get(
	'/{projeto_id}',
	response_model=ProjetoResposta,
	summary='Obtém projeto visível ao usuário autenticado',
	openapi_extra=exemplo_requisicao_json({'projeto_id': 1}),
)
async def obter(
	projeto_id: int, servico: DependenciaServico, usuario_atual: DependenciaUsuarioAtual
):
	"""Função para obter um registro pelo ID."""
	return await servico.obter_visivel(
		projeto_id, usuario_atual.id, usuario_atual.papel
	)


@router.patch(
	'/{projeto_id}',
	response_model=ProjetoResposta,
	dependencies=[GuardaAdmin],
	summary='Atualiza projeto (somente admin)',
)
async def atualizar(
	projeto_id: int, dados: ProjetoAtualizar, servico: DependenciaServico
):
	"""Função para atualizar um registro pelo ID."""
	return await servico.atualizar(projeto_id, dados)


@router.delete(
	'/{projeto_id}',
	status_code=status.HTTP_204_NO_CONTENT,
	dependencies=[GuardaAdmin],
	summary='Remove projeto (somente admin)',
	openapi_extra=exemplo_requisicao_json({'projeto_id': 1}),
)
async def deletar(projeto_id: int, servico: DependenciaServico):
	"""Função para excluir um registro pelo ID."""
	await servico.deletar(projeto_id)


@router.post(
	'/{projeto_id}/equipe',
	response_model=ProjetoFuncionarioResposta,
	status_code=status.HTTP_201_CREATED,
	dependencies=[GuardaAdmin],
	summary='Adiciona funcionário ao projeto (somente admin)',
)
async def adicionar_membro(
	projeto_id: int, dados: ProjetoFuncionarioCriar, servico: DependenciaServico
):
	"""Função para adicionar um funcionário à equipe do projeto."""
	return await servico.adicionar_membro(projeto_id, dados)


@router.get(
	'/{projeto_id}/equipe',
	response_model=list[ProjetoFuncionarioResposta],
	summary='Lista equipe do projeto visível ao usuário autenticado',
	openapi_extra=exemplo_requisicao_json({'projeto_id': 1}),
)
async def listar_equipe(
	projeto_id: int, servico: DependenciaServico, usuario_atual: DependenciaUsuarioAtual
):
	"""Função para listar a equipe de um projeto."""
	await servico.obter_visivel(projeto_id, usuario_atual.id, usuario_atual.papel)
	return await servico.listar_equipe(projeto_id)


@router.delete(
	'/{projeto_id}/equipe/{funcionario_id}',
	status_code=status.HTTP_204_NO_CONTENT,
	dependencies=[GuardaAdmin],
	summary='Remove funcionário do projeto (somente admin)',
	openapi_extra=exemplo_requisicao_json({
		'projeto_id': 1,
		'funcionario_id': 2,
	}),
)
async def remover_membro(
	projeto_id: int, funcionario_id: int, servico: DependenciaServico
):
	"""Função para remover um funcionário da equipe do projeto."""
	await servico.remover_membro(projeto_id, funcionario_id)
