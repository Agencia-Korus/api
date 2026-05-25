from typing import Annotated

from core.enums import ProjetoStatus, UserRole
from core.security import UsuarioAtual, obter_usuario_atual, require_role
from deps import DependenciaPaginacao, DependenciaSessao
from fastapi import APIRouter, Depends, Query, status
from modules.projetos.schema import (
	ProjetoCriar,
	ProjetoFuncionarioCriar,
	ProjetoFuncionarioResposta,
	ProjetoResposta,
	ProjetoAtualizar,
)
from modules.projetos.service import ServicoProjeto

router = APIRouter(prefix='/projetos', tags=['Projetos'])


def _service(session: DependenciaSessao) -> ServicoProjeto:
	"""Função para criar o serviço de aplicação com a sessão atual."""
	return ServicoProjeto(session)


DependenciaServico = Annotated[ServicoProjeto, Depends(_service)]
AdminGuard = Depends(require_role(UserRole.ADMIN.value))
DependenciaUsuarioAtual = Annotated[UsuarioAtual, Depends(obter_usuario_atual)]


@router.post(
	'',
	response_model=ProjetoResposta,
	status_code=status.HTTP_201_CREATED,
	dependencies=[AdminGuard],
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
)
async def listar(
	servico: DependenciaServico,
	pagina: DependenciaPaginacao,
	usuario_atual: DependenciaUsuarioAtual,
	cliente_id: int | None = None,
	filtro_situacao: Annotated[ProjetoStatus | None, Query(alias='status')] = None,
):
	"""Função para listar registros."""
	return await servico.listar_visible(
		offset=pagina.offset,
		limit=pagina.limit,
		usuario_id=usuario_atual.id,
		role=usuario_atual.role,
		cliente_id=cliente_id,
		status=filtro_situacao,
	)


@router.get(
	'/{projeto_id}',
	response_model=ProjetoResposta,
	summary='Obtém projeto visível ao usuário autenticado',
)
async def obter(projeto_id: int, servico: DependenciaServico, usuario_atual: DependenciaUsuarioAtual):
	"""Função para obter um registro pelo ID."""
	return await servico.obter_visible(projeto_id, usuario_atual.id, usuario_atual.role)


@router.patch(
	'/{projeto_id}',
	response_model=ProjetoResposta,
	dependencies=[AdminGuard],
	summary='Atualiza projeto (somente admin)',
)
async def atualizar(projeto_id: int, dados: ProjetoAtualizar, servico: DependenciaServico):
	"""Função para atualizar um registro pelo ID."""
	return await servico.atualizar(projeto_id, dados)


@router.delete(
	'/{projeto_id}',
	status_code=status.HTTP_204_NO_CONTENT,
	dependencies=[AdminGuard],
	summary='Remove projeto (somente admin)',
)
async def deletar(projeto_id: int, servico: DependenciaServico):
	"""Função para excluir um registro pelo ID."""
	await servico.deletar(projeto_id)


@router.post(
	'/{projeto_id}/equipe',
	response_model=ProjetoFuncionarioResposta,
	status_code=status.HTTP_201_CREATED,
	dependencies=[AdminGuard],
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
)
async def listar_equipe(
	projeto_id: int, servico: DependenciaServico, usuario_atual: DependenciaUsuarioAtual
):
	"""Função para listar a equipe de um projeto."""
	await servico.obter_visible(projeto_id, usuario_atual.id, usuario_atual.role)
	return await servico.listar_equipe(projeto_id)


@router.delete(
	'/{projeto_id}/equipe/{funcionario_id}',
	status_code=status.HTTP_204_NO_CONTENT,
	dependencies=[AdminGuard],
	summary='Remove funcionário do projeto (somente admin)',
)
async def remover_membro(projeto_id: int, funcionario_id: int, servico: DependenciaServico):
	"""Função para remover um funcionário da equipe do projeto."""
	await servico.remover_membro(projeto_id, funcionario_id)
