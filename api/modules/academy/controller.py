from typing import Annotated

from core.enums import AcademyTipo, UserRole
from core.security import require_role
from deps import DependenciaPaginacao, DependenciaSessao
from fastapi import APIRouter, Depends, Query, status
from modules.academy.schema import AcademyCriar, AcademyResposta, AcademyAtualizar
from modules.academy.service import ServicoAcademy

router = APIRouter(prefix='/academy', tags=['Academy'])


def _service(session: DependenciaSessao) -> ServicoAcademy:
	"""Função para criar o serviço de aplicação com a sessão atual."""
	return ServicoAcademy(session)


DependenciaServico = Annotated[ServicoAcademy, Depends(_service)]
AdminGuard = Depends(require_role(UserRole.ADMIN.value))


@router.post(
	'',
	response_model=AcademyResposta,
	status_code=status.HTTP_201_CREATED,
	dependencies=[AdminGuard],
	summary='Cria conteúdo no Academy (somente admin)',
)
async def criar(dados: AcademyCriar, servico: DependenciaServico):
	"""Função para criar um novo registro."""
	return await servico.criar(dados)


@router.get(
	'',
	response_model=list[AcademyResposta],
	summary='Lista conteúdos publicados do Academy (público/home)',
)
async def listar(
	servico: DependenciaServico,
	pagina: DependenciaPaginacao,
	tipo: AcademyTipo | None = None,
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
	response_model=list[AcademyResposta],
	dependencies=[AdminGuard],
	summary='Lista todos os conteúdos do Academy para gestão (somente admin)',
)
async def listar_admin(
	servico: DependenciaServico,
	pagina: DependenciaPaginacao,
	tipo: AcademyTipo | None = None,
	publicado: bool | None = None,
):
	"""Função para listar registros na visão administrativa."""
	return await servico.listar_filtrados(
		offset=pagina.offset, limit=pagina.limit, tipo=tipo, publicado=publicado
	)


@router.get(
	'/{item_id}',
	response_model=AcademyResposta,
	summary='Obtém conteúdo do Academy (público/home)',
)
async def obter(item_id: int, servico: DependenciaServico):
	"""Função para obter um registro pelo ID."""
	return await servico.obter(item_id)


@router.patch(
	'/{item_id}',
	response_model=AcademyResposta,
	dependencies=[AdminGuard],
	summary='Atualiza conteúdo no Academy (somente admin)',
)
async def atualizar(item_id: int, dados: AcademyAtualizar, servico: DependenciaServico):
	"""Função para atualizar um registro pelo ID."""
	return await servico.atualizar(item_id, dados)


@router.delete(
	'/{item_id}',
	status_code=status.HTTP_204_NO_CONTENT,
	dependencies=[AdminGuard],
	summary='Remove conteúdo do Academy (somente admin)',
)
async def deletar(item_id: int, servico: DependenciaServico):
	"""Função para excluir um registro pelo ID."""
	await servico.deletar(item_id)
