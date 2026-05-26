from typing import Annotated

from core.enums import PapelUsuario, SituacaoTarefa
from core.security import UsuarioAtual, exigir_papel, obter_usuario_atual
from core.swagger import exemplo_requisicao_json
from deps import DependenciaPaginacao, DependenciaSessao
from fastapi import APIRouter, Body, Depends, Query, status
from modules.tarefas.schema import (
	AnexoCriar,
	AnexoResposta,
	ComentarioCriar,
	ComentarioResposta,
	TarefaAtualizar,
	TarefaCriar,
	TarefaResposta,
)
from modules.tarefas.service import ServicoTarefa

router = APIRouter(prefix='/tarefas', tags=['Tarefas'])


def _servico(sessao: DependenciaSessao) -> ServicoTarefa:
	"""Função para criar o serviço de aplicação com a sessão atual."""
	return ServicoTarefa(sessao)


DependenciaServico = Annotated[ServicoTarefa, Depends(_servico)]
GuardaAdmin = Depends(exigir_papel(PapelUsuario.ADMIN.value))
DependenciaUsuarioAtual = Annotated[UsuarioAtual, Depends(obter_usuario_atual)]


@router.post(
	'',
	response_model=TarefaResposta,
	status_code=status.HTTP_201_CREATED,
	dependencies=[GuardaAdmin],
	summary='Cria tarefa (somente admin)',
)
async def criar(dados: TarefaCriar, servico: DependenciaServico):
	"""Função para criar um novo registro."""
	return await servico.criar(dados)


@router.get(
	'',
	response_model=list[TarefaResposta],
	summary='Lista tarefas/Kanban visíveis ao usuário autenticado',
	description=(
		'Admin lista tudo. Cliente lista tarefas dos próprios projetos. '
		'Funcionário lista tarefas em que é responsável ou está na equipe do projeto.'
	),
	openapi_extra=exemplo_requisicao_json({
		'offset': 0,
		'limit': 20,
		'projeto_id': 1,
		'responsavel_id': 2,
		'status': 'em_progresso',
	}),
)
async def listar(
	servico: DependenciaServico,
	pagina: DependenciaPaginacao,
	usuario_atual: DependenciaUsuarioAtual,
	projeto_id: int | None = None,
	responsavel_id: int | None = None,
	filtro_situacao: Annotated[SituacaoTarefa | None, Query(alias='status')] = None,
):
	"""Função para listar registros."""
	return await servico.listar_visiveis(
		offset=pagina.offset,
		limit=pagina.limit,
		usuario_id=usuario_atual.id,
		papel=usuario_atual.papel,
		projeto_id=projeto_id,
		responsavel_id=responsavel_id,
		status=filtro_situacao,
	)


@router.get(
	'/{tarefa_id}',
	response_model=TarefaResposta,
	summary='Obtém tarefa visível ao usuário autenticado',
	openapi_extra=exemplo_requisicao_json({'tarefa_id': 1}),
)
async def obter(
	tarefa_id: int, servico: DependenciaServico, usuario_atual: DependenciaUsuarioAtual
):
	"""Função para obter um registro pelo ID."""
	return await servico.obter_visivel(tarefa_id, usuario_atual.id, usuario_atual.papel)


@router.patch(
	'/{tarefa_id}',
	response_model=TarefaResposta,
	summary='Atualiza card do Kanban (admin ou funcionário envolvido)',
)
async def atualizar(
	tarefa_id: int,
	dados: TarefaAtualizar,
	servico: DependenciaServico,
	usuario_atual: DependenciaUsuarioAtual,
):
	"""Função para atualizar um registro pelo ID."""
	await servico.garantir_permissao_gerenciar_tarefa(
		tarefa_id, usuario_atual.id, usuario_atual.papel
	)
	return await servico.atualizar(tarefa_id, dados)


@router.delete(
	'/{tarefa_id}',
	status_code=status.HTTP_204_NO_CONTENT,
	summary='Remove tarefa (admin ou funcionário envolvido)',
	openapi_extra=exemplo_requisicao_json({'tarefa_id': 1}),
)
async def deletar(
	tarefa_id: int, servico: DependenciaServico, usuario_atual: DependenciaUsuarioAtual
):
	"""Função para excluir um registro pelo ID."""
	await servico.garantir_permissao_gerenciar_tarefa(
		tarefa_id, usuario_atual.id, usuario_atual.papel
	)
	await servico.deletar(tarefa_id)


@router.post(
	'/{tarefa_id}/comentarios',
	response_model=ComentarioResposta,
	status_code=status.HTTP_201_CREATED,
	summary='Comenta no card do Kanban (usuário com acesso à tarefa)',
	openapi_extra={
		'requestBody': {
			'content': {
				'application/json': {
					'example': {
						'conteudo': 'Atualizei o layout com os ajustes combinados.'
					}
				}
			}
		}
	},
)
async def comentar(
	tarefa_id: int,
	servico: DependenciaServico,
	usuario_atual: DependenciaUsuarioAtual,
	conteudo: Annotated[
		str,
		Body(
			...,
			embed=True,
			examples=['Atualizei o layout com os ajustes combinados.'],
		),
	],
):
	"""Função para adicionar um comentário a uma tarefa."""
	await servico.obter_visivel(tarefa_id, usuario_atual.id, usuario_atual.papel)
	dados = ComentarioCriar(tarefa_id=tarefa_id, conteudo=conteudo)
	return await servico.adicionar_comentario(dados, usuario_atual.id)


@router.get(
	'/{tarefa_id}/comentarios',
	response_model=list[ComentarioResposta],
	summary='Lista comentários da tarefa visível ao usuário autenticado',
	openapi_extra=exemplo_requisicao_json({'tarefa_id': 1}),
)
async def listar_comentarios(
	tarefa_id: int, servico: DependenciaServico, usuario_atual: DependenciaUsuarioAtual
):
	"""Função para listar comentários de uma tarefa."""
	await servico.obter_visivel(tarefa_id, usuario_atual.id, usuario_atual.papel)
	return await servico.listar_comentarios(tarefa_id)


@router.delete(
	'/comentarios/{comentario_id}',
	status_code=status.HTTP_204_NO_CONTENT,
	dependencies=[GuardaAdmin],
	summary='Remove comentário (somente admin)',
	openapi_extra=exemplo_requisicao_json({'comentario_id': 1}),
)
async def remover_comentario(comentario_id: int, servico: DependenciaServico):
	"""Função para remover um comentário pelo ID."""
	await servico.deletar_comentario(comentario_id)


@router.post(
	'/{tarefa_id}/anexos',
	response_model=AnexoResposta,
	status_code=status.HTTP_201_CREATED,
	summary='Anexa arquivo à tarefa (admin ou funcionário envolvido)',
)
async def anexar(
	tarefa_id: int,
	dados: AnexoCriar,
	servico: DependenciaServico,
	usuario_atual: DependenciaUsuarioAtual,
):
	"""Função para adicionar um anexo a uma tarefa."""
	await servico.garantir_permissao_gerenciar_tarefa(
		tarefa_id, usuario_atual.id, usuario_atual.papel
	)
	payload_with_id = dados.model_copy(update={'tarefa_id': tarefa_id})
	return await servico.adicionar_anexo(payload_with_id)


@router.get(
	'/{tarefa_id}/anexos',
	response_model=list[AnexoResposta],
	summary='Lista anexos da tarefa visível ao usuário autenticado',
	openapi_extra=exemplo_requisicao_json({'tarefa_id': 1}),
)
async def listar_anexos(
	tarefa_id: int, servico: DependenciaServico, usuario_atual: DependenciaUsuarioAtual
):
	"""Função para listar anexos de uma tarefa."""
	await servico.obter_visivel(tarefa_id, usuario_atual.id, usuario_atual.papel)
	return await servico.listar_anexos(tarefa_id)


@router.delete(
	'/anexos/{anexo_id}',
	status_code=status.HTTP_204_NO_CONTENT,
	dependencies=[GuardaAdmin],
	summary='Remove anexo (somente admin)',
	openapi_extra=exemplo_requisicao_json({'anexo_id': 1}),
)
async def remover_anexo(anexo_id: int, servico: DependenciaServico):
	"""Função para remover um anexo pelo ID."""
	await servico.deletar_anexo(anexo_id)
