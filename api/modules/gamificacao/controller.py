from typing import Annotated

from core.enums import UserRole
from core.security import (
	CREDENTIALS_EXCEPTION,
	bearer_scheme,
	decode_token,
	require_role,
)
from deps import DependenciaPaginacao, DependenciaSessao
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials
from modules.gamificacao.schema import (
	ConquistaCriar,
	ConquistaResposta,
	ConquistaAtualizar,
	FuncionarioConquistaResposta,
	HistoricoXpCriar,
	HistoricoXpResposta,
	RegraXpCriar,
	RegraXpResposta,
	RegraXpAtualizar,
)
from modules.gamificacao.service import ServicoGamificacao

router = APIRouter(prefix='/gamificacao', tags=['Gamificação'])


def _service(session: DependenciaSessao) -> ServicoGamificacao:
	"""Função para criar o serviço de aplicação com a sessão atual."""
	return ServicoGamificacao(session)


DependenciaServico = Annotated[ServicoGamificacao, Depends(_service)]
AdminGuard = Depends(require_role(UserRole.ADMIN.value))


def _admin_or_funcionario(
	credentials: Annotated[
		HTTPAuthorizationCredentials | None,
		Depends(bearer_scheme),
	],
) -> tuple[int, str]:
	"""Função para permitir acesso de admin ou funcionário."""
	if not credentials:
		raise CREDENTIALS_EXCEPTION
	token = credentials.credentials
	dados = decode_token(token)
	role = dados.get('role')
	if role not in {UserRole.ADMIN.value, UserRole.FUNCIONARIO.value}:
		raise HTTPException(
			status_code=status.HTTP_403_FORBIDDEN,
			detail='Acesso negado para este recurso',
		)
	return int(dados['sub']), role


CallerDep = Annotated[tuple[int, str], Depends(_admin_or_funcionario)]


@router.post(
	'/regras',
	response_model=RegraXpResposta,
	status_code=status.HTTP_201_CREATED,
	dependencies=[AdminGuard],
	summary='Cria regra de XP (somente admin)',
)
async def criar_regra(dados: RegraXpCriar, servico: DependenciaServico):
	"""Função para criar uma regra de XP."""
	return await servico.criar_regra(dados)


@router.get(
	'/regras',
	response_model=list[RegraXpResposta],
	dependencies=[AdminGuard],
	summary='Lista regras de XP (somente admin)',
)
async def listar_regras(servico: DependenciaServico, pagina: DependenciaPaginacao):
	"""Função para listar regras de XP."""
	return await servico.listar_regras(offset=pagina.offset, limit=pagina.limit)


@router.patch(
	'/regras/{regra_id}',
	response_model=RegraXpResposta,
	dependencies=[AdminGuard],
	summary='Atualiza regra de XP (somente admin)',
)
async def atualizar_regra(regra_id: int, dados: RegraXpAtualizar, servico: DependenciaServico):
	"""Função para atualizar uma regra de XP."""
	return await servico.atualizar_regra(regra_id, dados)


@router.delete(
	'/regras/{regra_id}',
	status_code=status.HTTP_204_NO_CONTENT,
	dependencies=[AdminGuard],
	summary='Remove regra de XP (somente admin)',
)
async def deletar_regra(regra_id: int, servico: DependenciaServico):
	"""Função para excluir uma regra de XP."""
	await servico.deletar_regra(regra_id)


@router.post(
	'/historico',
	response_model=HistoricoXpResposta,
	status_code=status.HTTP_201_CREATED,
	dependencies=[AdminGuard],
	summary='Registra XP para funcionário (somente admin)',
)
async def registrar_xp(dados: HistoricoXpCriar, servico: DependenciaServico):
	"""Função para registrar XP para um funcionário."""
	return await servico.registrar_xp(dados)


@router.get(
	'/historico/funcionario/{funcionario_id}',
	response_model=list[HistoricoXpResposta],
	summary='Lista XP do funcionário (admin ou o próprio funcionário)',
)
async def listar_historico(funcionario_id: int, servico: DependenciaServico, caller: CallerDep):
	"""Função para listar o histórico de XP de um funcionário."""
	caller_id, caller_role = caller
	if caller_role == UserRole.FUNCIONARIO.value and caller_id != funcionario_id:
		raise HTTPException(
			status_code=status.HTTP_403_FORBIDDEN,
			detail='Funcionário só pode listar o próprio XP',
		)
	return await servico.listar_historico(funcionario_id)


@router.post(
	'/conquistas',
	response_model=ConquistaResposta,
	status_code=status.HTTP_201_CREATED,
	dependencies=[AdminGuard],
	summary='Cria conquista (somente admin)',
)
async def criar_conquista(dados: ConquistaCriar, servico: DependenciaServico):
	"""Função para criar uma conquista."""
	return await servico.criar_conquista(dados)


@router.get(
	'/conquistas',
	response_model=list[ConquistaResposta],
	summary='Lista conquistas disponíveis (admin ou funcionário)',
)
async def listar_conquistas(
	servico: DependenciaServico, pagina: DependenciaPaginacao, caller: CallerDep
):
	"""Função para listar conquistas."""
	return await servico.listar_conquistas(offset=pagina.offset, limit=pagina.limit)


@router.patch(
	'/conquistas/{conquista_id}',
	response_model=ConquistaResposta,
	dependencies=[AdminGuard],
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
	dependencies=[AdminGuard],
	summary='Remove conquista (somente admin)',
)
async def deletar_conquista(conquista_id: int, servico: DependenciaServico):
	"""Função para excluir uma conquista."""
	await servico.deletar_conquista(conquista_id)


@router.post(
	'/funcionarios/{funcionario_id}/conquistas/{conquista_id}',
	response_model=FuncionarioConquistaResposta,
	status_code=status.HTTP_201_CREATED,
	dependencies=[AdminGuard],
	summary='Desbloqueia conquista para funcionário (somente admin)',
)
async def desbloquear(funcionario_id: int, conquista_id: int, servico: DependenciaServico):
	"""Função para registrar uma conquista desbloqueada por um funcionário."""
	return await servico.desbloquear_conquista(funcionario_id, conquista_id)


@router.get(
	'/funcionarios/{funcionario_id}/conquistas',
	response_model=list[FuncionarioConquistaResposta],
)
async def listar_funcionario_conquistas(
	funcionario_id: int, servico: DependenciaServico, caller: CallerDep
):
	"""Função para listar conquistas de um funcionário."""
	caller_id, caller_role = caller
	if caller_role == UserRole.FUNCIONARIO.value and caller_id != funcionario_id:
		raise HTTPException(
			status_code=status.HTTP_403_FORBIDDEN,
			detail='Funcionário só pode listar conquistas próprias',
		)
	return await servico.listar_conquistas_funcionario(funcionario_id)
