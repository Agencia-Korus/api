from datetime import date
from typing import Annotated

from fastapi import APIRouter, Depends, status

from api.deps import SessionDep
from core.enums import UserRole
from core.security import CurrentUser, get_current_user, require_role
from modules.agenda.schema import (
	AgendaEventoSiteResponse,
	EventoAgendaCreate,
	EventoAgendaResponse,
	EventoAgendaUpdate,
	EventoGoogleCalendarResponse,
	SolicitacaoReuniaoCreate,
	SolicitacaoReuniaoResponse,
	SolicitacaoReuniaoUpdate,
)
from modules.agenda.service import AgendaService

LoggedUserGuard = Depends(
	require_role(
		UserRole.CLIENTE.value,
		UserRole.FUNCIONARIO.value,
		UserRole.ADMIN.value,
	)
)
CurrentUserDep = Annotated[CurrentUser, Depends(get_current_user)]

router = APIRouter(prefix='/agenda', tags=['Agenda'], dependencies=[LoggedUserGuard])


def _service(session: SessionDep) -> AgendaService:
	return AgendaService(session)


ServiceDep = Annotated[AgendaService, Depends(_service)]


@router.post(
	'/eventos',
	response_model=EventoAgendaResponse,
	status_code=status.HTTP_201_CREATED,
	summary='Cria evento na agenda (usuário autenticado)',
)
async def criar_evento(payload: EventoAgendaCreate, service: ServiceDep):
	return await service.criar_evento(payload)


@router.get(
	'/eventos',
	response_model=list[AgendaEventoSiteResponse],
	summary='Lista eventos do usuário logado unificando agenda local e Google Calendar',
	description=(
		'Endpoint recomendado para o site. Retorna eventos locais do usuário '
		'autenticado e reuniões reais do Google Calendar no mesmo formato.'
	),
)
async def listar_eventos_site(
	current_user: CurrentUserDep,
	service: ServiceDep,
	data_inicio: date | None = None,
	data_fim: date | None = None,
):
	return await service.listar_eventos_site(current_user.id, data_inicio, data_fim)


@router.get(
	'/eventos/usuario/{usuario_id}',
	response_model=list[EventoAgendaResponse],
	summary='Lista eventos locais de um usuário (usuário autenticado)',
)
async def listar_eventos(usuario_id: int, service: ServiceDep):
	return await service.listar_eventos(usuario_id)


@router.get(
	'/eventos/google-calendar',
	response_model=list[EventoGoogleCalendarResponse],
	summary='Lista reuniões reais do Google Calendar',
	description=(
		'Busca eventos diretamente no Google Calendar configurado. Quando a '
		'integração estiver desativada ou sem credenciais, retorna lista vazia.'
	),
)
async def listar_eventos_calendario_google(
	service: ServiceDep,
	data_inicio: date | None = None,
	data_fim: date | None = None,
):
	return await service.listar_eventos_calendario_google(data_inicio, data_fim)


@router.get(
	'/eventos/{evento_id}',
	response_model=EventoAgendaResponse,
	summary='Obtém evento da agenda (usuário autenticado)',
)
async def obter_evento(evento_id: int, service: ServiceDep):
	return await service.get_evento(evento_id)


@router.patch(
	'/eventos/{evento_id}',
	response_model=EventoAgendaResponse,
	summary='Atualiza evento da agenda (usuário autenticado)',
)
async def atualizar_evento(
	evento_id: int, payload: EventoAgendaUpdate, service: ServiceDep
):
	return await service.atualizar_evento(evento_id, payload)


@router.delete(
	'/eventos/{evento_id}',
	status_code=status.HTTP_204_NO_CONTENT,
	summary='Remove evento da agenda (usuário autenticado)',
)
async def deletar_evento(evento_id: int, service: ServiceDep):
	await service.deletar_evento(evento_id)


@router.post(
	'/solicitacoes',
	response_model=SolicitacaoReuniaoResponse,
	status_code=status.HTTP_201_CREATED,
	summary='Solicita reunião (usuário autenticado)',
)
async def criar_solicitacao(payload: SolicitacaoReuniaoCreate, service: ServiceDep):
	return await service.criar_solicitacao(payload)


@router.get(
	'/solicitacoes/recebidas/{destinatario_id}',
	response_model=list[SolicitacaoReuniaoResponse],
	summary='Lista solicitações recebidas (usuário autenticado)',
)
async def listar_solicitacoes(destinatario_id: int, service: ServiceDep):
	return await service.listar_solicitacoes_recebidas(destinatario_id)


@router.patch(
	'/solicitacoes/{solicitacao_id}',
	response_model=SolicitacaoReuniaoResponse,
	summary='Atualiza solicitação de reunião (usuário autenticado)',
)
async def atualizar_solicitacao(
	solicitacao_id: int,
	payload: SolicitacaoReuniaoUpdate,
	service: ServiceDep,
):
	return await service.atualizar_solicitacao(solicitacao_id, payload)


@router.delete(
	'/solicitacoes/{solicitacao_id}',
	status_code=status.HTTP_204_NO_CONTENT,
	summary='Remove solicitação de reunião (usuário autenticado)',
)
async def deletar_solicitacao(solicitacao_id: int, service: ServiceDep):
	await service.deletar_solicitacao(solicitacao_id)
