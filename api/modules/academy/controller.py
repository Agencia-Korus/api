from typing import Annotated

from core.enums import PapelUsuario, TipoAcademia
from core.security import exigir_papel
from core.swagger import exemplo_requisicao_json
from deps import DependenciaPaginacao, DependenciaSessao
from fastapi import APIRouter, Depends, Query, status
from modules.academy.schema import AcademiaAtualizar, AcademiaCriar, AcademiaResposta
from modules.academy.service import ServicoAcademia

router = APIRouter(prefix='/academy', tags=['Academia'])


def _servico(sessao: DependenciaSessao) -> ServicoAcademia:
	"""Função para criar o serviço de aplicação com a sessão atual."""
	return ServicoAcademia(sessao)


DependenciaServico = Annotated[ServicoAcademia, Depends(_servico)]
GuardaAdmin = Depends(exigir_papel(PapelUsuario.ADMIN.value))


@router.post(
	'',
	response_model=AcademiaResposta,
	status_code=status.HTTP_201_CREATED,
	dependencies=[GuardaAdmin],
	summary='Cria conteúdo no Academia (somente admin)',
)
async def criar(dados: AcademiaCriar, servico: DependenciaServico):
	"""Função para criar um novo registro."""
	return await servico.criar(dados)


@router.get(
	'',
	response_model=list[AcademiaResposta],
	summary='Lista conteúdos publicados do Academia (público/home)',
	openapi_extra=exemplo_requisicao_json({
		'offset': 0,
		'limit': 20,
		'tipo': 'curso',
		'publicado': True,
	}),
)
async def listar(
	servico: DependenciaServico,
	pagina: DependenciaPaginacao,
	tipo: TipoAcademia | None = None,
	publicado: Annotated[
		bool,
		Query(description='Por padrão a home lista somente conteúdos publicados.'),
	] = True,
):
	"""Função para listar registros."""
	return await servico.listar_filtrados(
		offset=pagina.offset, limit=pagina.limit, tipo=tipo, publicado=publicado
	)


@router.get(
	'/admin',
	response_model=list[AcademiaResposta],
	dependencies=[GuardaAdmin],
	summary='Lista todos os conteúdos do Academia para gestão (somente admin)',
	openapi_extra=exemplo_requisicao_json({
		'offset': 0,
		'limit': 20,
		'tipo': 'curso',
		'publicado': True,
	}),
)
async def listar_admin(
	servico: DependenciaServico,
	pagina: DependenciaPaginacao,
	tipo: TipoAcademia | None = None,
	publicado: bool | None = None,
):
	"""Função para listar registros na visão administrativa."""
	return await servico.listar_filtrados(
		offset=pagina.offset, limit=pagina.limit, tipo=tipo, publicado=publicado
	)


@router.get(
	'/{item_id}',
	response_model=AcademiaResposta,
	summary='Obtém conteúdo do Academia (público/home)',
	openapi_extra=exemplo_requisicao_json({'item_id': 1}),
)
async def obter(item_id: int, servico: DependenciaServico):
	"""Função para obter um registro pelo ID."""
	return await servico.obter(item_id)


@router.patch(
	'/{item_id}',
	response_model=AcademiaResposta,
	dependencies=[GuardaAdmin],
	summary='Atualiza conteúdo no Academia (somente admin)',
)
async def atualizar(
	item_id: int, dados: AcademiaAtualizar, servico: DependenciaServico
):
	"""Função para atualizar um registro pelo ID."""
	return await servico.atualizar(item_id, dados)


@router.delete(
	'/{item_id}',
	status_code=status.HTTP_204_NO_CONTENT,
	dependencies=[GuardaAdmin],
	summary='Remove conteúdo do Academia (somente admin)',
	openapi_extra=exemplo_requisicao_json({'item_id': 1}),
)
async def deletar(item_id: int, servico: DependenciaServico):
	"""Função para excluir um registro pelo ID."""
	await servico.deletar(item_id)
