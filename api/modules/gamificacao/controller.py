from typing import Annotated

from core.enums import PapelUsuario
from core.security import (
	EXCECAO_CREDENCIAIS,
	decodificar_token,
	esquema_bearer,
	exigir_papel,
)
from core.swagger import exemplo_requisicao_json
from deps import DependenciaPaginacao, DependenciaSessao
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials
from modules.gamificacao.schema import (
	ConquistaAtualizar,
	ConquistaCriar,
	ConquistaResposta,
	FuncionarioConquistaResposta,
	HistoricoXpCriar,
	HistoricoXpResposta,
	RegraXpAtualizar,
	RegraXpCriar,
	RegraXpResposta,
)
from modules.gamificacao.service import ServicoGamificacao

router = APIRouter(prefix='/gamificacao', tags=['Gamificação'])


def _servico(sessao: DependenciaSessao) -> ServicoGamificacao:
	"""Função para criar o serviço de aplicação com a sessão atual."""
	return ServicoGamificacao(sessao)


DependenciaServico = Annotated[ServicoGamificacao, Depends(_servico)]
GuardaAdmin = Depends(exigir_papel(PapelUsuario.ADMIN.value))


def _admin_ou_funcionario(
	credenciais: Annotated[
		HTTPAuthorizationCredentials | None,
		Depends(esquema_bearer),
	],
) -> tuple[int, str]:
	"""Função para permitir acesso de admin ou funcionário."""
	if not credenciais:
		raise EXCECAO_CREDENCIAIS
	token = credenciais.credentials
	dados = decodificar_token(token)
	papel = dados.get('role')
	if papel not in {PapelUsuario.ADMIN.value, PapelUsuario.FUNCIONARIO.value}:
		raise HTTPException(
			status_code=status.HTTP_403_FORBIDDEN,
			detail='Acesso negado para este recurso',
		)
	return int(dados['sub']), papel


DependenciaSolicitante = Annotated[tuple[int, str], Depends(_admin_ou_funcionario)]


@router.post(
	'/regras',
	response_model=RegraXpResposta,
	status_code=status.HTTP_201_CREATED,
	dependencies=[GuardaAdmin],
	summary='Cria regra de XP (somente admin)',
)
async def criar_regra(dados: RegraXpCriar, servico: DependenciaServico):
	"""Função para criar uma regra de XP."""
	return await servico.criar_regra(dados)


@router.get(
	'/regras',
	response_model=list[RegraXpResposta],
	dependencies=[GuardaAdmin],
	summary='Lista regras de XP (somente admin)',
	openapi_extra=exemplo_requisicao_json({'offset': 0, 'limit': 20}),
)
async def listar_regras(servico: DependenciaServico, pagina: DependenciaPaginacao):
	"""Função para listar regras de XP."""
	return await servico.listar_regras(offset=pagina.offset, limit=pagina.limit)


@router.patch(
	'/regras/{regra_id}',
	response_model=RegraXpResposta,
	dependencies=[GuardaAdmin],
	summary='Atualiza regra de XP (somente admin)',
)
async def atualizar_regra(regra_id: int, dados: RegraXpAtualizar, servico: DependenciaServico):
	"""Função para atualizar uma regra de XP."""
	return await servico.atualizar_regra(regra_id, dados)


@router.delete(
	'/regras/{regra_id}',
	status_code=status.HTTP_204_NO_CONTENT,
	dependencies=[GuardaAdmin],
	summary='Remove regra de XP (somente admin)',
	openapi_extra=exemplo_requisicao_json({'regra_id': 1}),
)
async def deletar_regra(regra_id: int, servico: DependenciaServico):
	"""Função para excluir uma regra de XP."""
	await servico.deletar_regra(regra_id)


@router.post(
	'/historico',
	response_model=HistoricoXpResposta,
	status_code=status.HTTP_201_CREATED,
	dependencies=[GuardaAdmin],
	summary='Registra XP para funcionário (somente admin)',
)
async def registrar_xp(dados: HistoricoXpCriar, servico: DependenciaServico):
	"""Função para registrar XP para um funcionário."""
	return await servico.registrar_xp(dados)


@router.get(
	'/historico/funcionario/{funcionario_id}',
	response_model=list[HistoricoXpResposta],
	summary='Lista XP do funcionário (admin ou o próprio funcionário)',
	openapi_extra=exemplo_requisicao_json({'funcionario_id': 2}),
)
async def listar_historico(
	funcionario_id: int,
	servico: DependenciaServico,
	solicitante: DependenciaSolicitante,
):
	"""Função para listar o histórico de XP de um funcionário."""
	id_solicitante, papel_solicitante = solicitante
	if papel_solicitante == PapelUsuario.FUNCIONARIO.value and id_solicitante != funcionario_id:
		raise HTTPException(
			status_code=status.HTTP_403_FORBIDDEN,
			detail='Funcionário só pode listar o próprio XP',
		)
	return await servico.listar_historico(funcionario_id)


@router.post(
	'/conquistas',
	response_model=ConquistaResposta,
	status_code=status.HTTP_201_CREATED,
	dependencies=[GuardaAdmin],
	summary='Cria conquista (somente admin)',
)
async def criar_conquista(dados: ConquistaCriar, servico: DependenciaServico):
	"""Função para criar uma conquista."""
	return await servico.criar_conquista(dados)


@router.get(
	'/conquistas',
	response_model=list[ConquistaResposta],
	summary='Lista conquistas disponíveis (admin ou funcionário)',
	openapi_extra=exemplo_requisicao_json({'offset': 0, 'limit': 20}),
)
async def listar_conquistas(
	servico: DependenciaServico,
	pagina: DependenciaPaginacao,
	solicitante: DependenciaSolicitante,
):
	"""Função para listar conquistas."""
	return await servico.listar_conquistas(offset=pagina.offset, limit=pagina.limit)


@router.patch(
	'/conquistas/{conquista_id}',
	response_model=ConquistaResposta,
	dependencies=[GuardaAdmin],
	summary='Atualiza conquista (somente admin)',
)
async def atualizar_conquista(
	conquista_id: int, dados: ConquistaAtualizar, servico: DependenciaServico
):
	"""Função para atualizar uma conquista."""
	return await servico.atualizar_conquista(conquista_id, dados)


@router.delete(
	'/conquistas/{conquista_id}',
	status_code=status.HTTP_204_NO_CONTENT,
	dependencies=[GuardaAdmin],
	summary='Remove conquista (somente admin)',
	openapi_extra=exemplo_requisicao_json({'conquista_id': 1}),
)
async def deletar_conquista(conquista_id: int, servico: DependenciaServico):
	"""Função para excluir uma conquista."""
	await servico.deletar_conquista(conquista_id)


@router.post(
	'/funcionarios/{funcionario_id}/conquistas/{conquista_id}',
	response_model=FuncionarioConquistaResposta,
	status_code=status.HTTP_201_CREATED,
	dependencies=[GuardaAdmin],
	summary='Desbloqueia conquista para funcionário (somente admin)',
	openapi_extra=exemplo_requisicao_json({
		'funcionario_id': 2,
		'conquista_id': 1,
	}),
)
async def desbloquear(funcionario_id: int, conquista_id: int, servico: DependenciaServico):
	"""Função para registrar uma conquista desbloqueada por um funcionário."""
	return await servico.desbloquear_conquista(funcionario_id, conquista_id)


@router.get(
	'/funcionarios/{funcionario_id}/conquistas',
	response_model=list[FuncionarioConquistaResposta],
	openapi_extra=exemplo_requisicao_json({'funcionario_id': 2}),
)
async def listar_funcionario_conquistas(
	funcionario_id: int,
	servico: DependenciaServico,
	solicitante: DependenciaSolicitante,
):
	"""Função para listar conquistas de um funcionário."""
	id_solicitante, papel_solicitante = solicitante
	if papel_solicitante == PapelUsuario.FUNCIONARIO.value and id_solicitante != funcionario_id:
		raise HTTPException(
			status_code=status.HTTP_403_FORBIDDEN,
			detail='Funcionário só pode listar conquistas próprias',
		)
	return await servico.listar_conquistas_funcionario(funcionario_id)
