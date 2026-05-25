from typing import Annotated

from core.enums import UserRole
from core.security import (
	CREDENTIALS_EXCEPTION,
	bearer_scheme,
	decode_token,
	require_role,
)
from deps import PaginationDep, SessionDep
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials
from modules.gamificacao.schema import (
	ConquistaCreate,
	ConquistaResponse,
	ConquistaUpdate,
	FuncionarioConquistaResponse,
	HistoricoXpCreate,
	HistoricoXpResponse,
	RegraXpCreate,
	RegraXpResponse,
	RegraXpUpdate,
)
from modules.gamificacao.service import GamificacaoService

router = APIRouter(prefix='/gamificacao', tags=['Gamificação'])


def _service(session: SessionDep) -> GamificacaoService:
	"""Função para criar o serviço de aplicação com a sessão atual."""
	return GamificacaoService(session)


ServiceDep = Annotated[GamificacaoService, Depends(_service)]
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
	payload = decode_token(token)
	role = payload.get('role')
	if role not in {UserRole.ADMIN.value, UserRole.FUNCIONARIO.value}:
		raise HTTPException(
			status_code=status.HTTP_403_FORBIDDEN,
			detail='Acesso negado para este recurso',
		)
	return int(payload['sub']), role


CallerDep = Annotated[tuple[int, str], Depends(_admin_or_funcionario)]


@router.post(
	'/regras',
	response_model=RegraXpResponse,
	status_code=status.HTTP_201_CREATED,
	dependencies=[AdminGuard],
	summary='Cria regra de XP (somente admin)',
)
async def criar_regra(payload: RegraXpCreate, service: ServiceDep):
	"""Função para criar uma regra de XP."""
	return await service.criar_regra(payload)


@router.get(
	'/regras',
	response_model=list[RegraXpResponse],
	dependencies=[AdminGuard],
	summary='Lista regras de XP (somente admin)',
)
async def listar_regras(service: ServiceDep, page: PaginationDep):
	"""Função para listar regras de XP."""
	return await service.listar_regras(offset=page.offset, limit=page.limit)


@router.patch(
	'/regras/{regra_id}',
	response_model=RegraXpResponse,
	dependencies=[AdminGuard],
	summary='Atualiza regra de XP (somente admin)',
)
async def atualizar_regra(regra_id: int, payload: RegraXpUpdate, service: ServiceDep):
	"""Função para atualizar uma regra de XP."""
	return await service.atualizar_regra(regra_id, payload)


@router.delete(
	'/regras/{regra_id}',
	status_code=status.HTTP_204_NO_CONTENT,
	dependencies=[AdminGuard],
	summary='Remove regra de XP (somente admin)',
)
async def deletar_regra(regra_id: int, service: ServiceDep):
	"""Função para excluir uma regra de XP."""
	await service.deletar_regra(regra_id)


@router.post(
	'/historico',
	response_model=HistoricoXpResponse,
	status_code=status.HTTP_201_CREATED,
	dependencies=[AdminGuard],
	summary='Registra XP para funcionário (somente admin)',
)
async def registrar_xp(payload: HistoricoXpCreate, service: ServiceDep):
	"""Função para registrar XP para um funcionário."""
	return await service.registrar_xp(payload)


@router.get(
	'/historico/funcionario/{funcionario_id}',
	response_model=list[HistoricoXpResponse],
	summary='Lista XP do funcionário (admin ou o próprio funcionário)',
)
async def listar_historico(funcionario_id: int, service: ServiceDep, caller: CallerDep):
	"""Função para listar o histórico de XP de um funcionário."""
	caller_id, caller_role = caller
	if caller_role == UserRole.FUNCIONARIO.value and caller_id != funcionario_id:
		raise HTTPException(
			status_code=status.HTTP_403_FORBIDDEN,
			detail='Funcionário só pode listar o próprio XP',
		)
	return await service.listar_historico(funcionario_id)


@router.post(
	'/conquistas',
	response_model=ConquistaResponse,
	status_code=status.HTTP_201_CREATED,
	dependencies=[AdminGuard],
	summary='Cria conquista (somente admin)',
)
async def criar_conquista(payload: ConquistaCreate, service: ServiceDep):
	"""Função para criar uma conquista."""
	return await service.criar_conquista(payload)


@router.get(
	'/conquistas',
	response_model=list[ConquistaResponse],
	summary='Lista conquistas disponíveis (admin ou funcionário)',
)
async def listar_conquistas(
	service: ServiceDep, page: PaginationDep, caller: CallerDep
):
	"""Função para listar conquistas."""
	return await service.listar_conquistas(offset=page.offset, limit=page.limit)


@router.patch(
	'/conquistas/{conquista_id}',
	response_model=ConquistaResponse,
	dependencies=[AdminGuard],
	summary='Atualiza conquista (somente admin)',
)
async def atualizar_conquista(
	conquista_id: int, payload: ConquistaUpdate, service: ServiceDep
):
	"""Função para atualizar uma conquista."""
	return await service.atualizar_conquista(conquista_id, payload)


@router.delete(
	'/conquistas/{conquista_id}',
	status_code=status.HTTP_204_NO_CONTENT,
	dependencies=[AdminGuard],
	summary='Remove conquista (somente admin)',
)
async def deletar_conquista(conquista_id: int, service: ServiceDep):
	"""Função para excluir uma conquista."""
	await service.deletar_conquista(conquista_id)


@router.post(
	'/funcionarios/{funcionario_id}/conquistas/{conquista_id}',
	response_model=FuncionarioConquistaResponse,
	status_code=status.HTTP_201_CREATED,
	dependencies=[AdminGuard],
	summary='Desbloqueia conquista para funcionário (somente admin)',
)
async def desbloquear(funcionario_id: int, conquista_id: int, service: ServiceDep):
	"""Função para registrar uma conquista desbloqueada por um funcionário."""
	return await service.desbloquear_conquista(funcionario_id, conquista_id)


@router.get(
	'/funcionarios/{funcionario_id}/conquistas',
	response_model=list[FuncionarioConquistaResponse],
)
async def listar_funcionario_conquistas(
	funcionario_id: int, service: ServiceDep, caller: CallerDep
):
	"""Função para listar conquistas de um funcionário."""
	caller_id, caller_role = caller
	if caller_role == UserRole.FUNCIONARIO.value and caller_id != funcionario_id:
		raise HTTPException(
			status_code=status.HTTP_403_FORBIDDEN,
			detail='Funcionário só pode listar conquistas próprias',
		)
	return await service.listar_conquistas_funcionario(funcionario_id)
