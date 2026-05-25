from datetime import date
from typing import Annotated

from core.enums import UserRole
from core.security import CurrentUser, get_current_user, require_role
from deps import SessionDep
from fastapi import APIRouter, Depends, status
from modules.agenda.schema import (
	AgendaEventoSiteResposta,
	EventoAgendaCriar,
	EventoAgendaResposta,
	EventoAgendaAtualizar,
	EventoGoogleCalendarResposta,
	SolicitacaoReuniaoCriar,
	SolicitacaoReuniaoResposta,
	SolicitacaoReuniaoAtualizar,
)
from modules.agenda.service import ServicoAgenda

LoggedUserGuard = Depends(
	require_role(
		UserRole.CLIENTE.value,
		UserRole.FUNCIONARIO.value,
		UserRole.ADMIN.value,
	)
)
CurrentUserDep = Annotated[CurrentUser, Depends(get_current_user)]

router = APIRouter(prefix='/agenda', tags=['Agenda'], dependencies=[LoggedUserGuard])


def _service(session: SessionDep) -> ServicoAgenda:
	"""Função para criar o serviço de aplicação com a sessão atual."""
	return ServicoAgenda(session)


ServiceDep = Annotated[ServicoAgenda, Depends(_service)]


@router.post(
	'/eventos',
	response_model=EventoAgendaResposta,
	status_code=status.HTTP_201_CREATED,
	summary='Cria evento na agenda (usuário autenticado)',
)
async def criar_evento(payload: EventoAgendaCriar, service: ServiceDep):
	"""Função para criar um evento na agenda."""
	return await service.criar_evento(payload)


@router.get(
	'/eventos',
	response_model=list[AgendaEventoSiteResposta],
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
	"""Função para listar eventos públicos exibidos no site."""
	return await service.listar_eventos_site(current_user.id, data_inicio, data_fim)


@router.get(
	'/eventos/usuario/{usuario_id}',
	response_model=list[EventoAgendaResposta],
	summary='Lista eventos locais de um usuário (usuário autenticado)',
)
async def listar_eventos(usuario_id: int, service: ServiceDep):
	"""Função para listar eventos de um usuário."""
	return await service.listar_eventos(usuario_id)


@router.get(
	'/eventos/google-calendar',
	response_model=list[EventoGoogleCalendarResposta],
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
	"""Função para listar eventos sincronizados do Google Calendar."""
	return await service.listar_eventos_calendario_google(data_inicio, data_fim)


@router.get(
	'/eventos/{evento_id}',
	response_model=EventoAgendaResposta,
	summary='Obtém evento da agenda (usuário autenticado)',
)
async def obter_evento(evento_id: int, service: ServiceDep):
	"""Função para obter um evento da agenda pelo ID."""
	return await service.obter_evento(evento_id)


@router.patch(
	'/eventos/{evento_id}',
	response_model=EventoAgendaResposta,
	summary='Atualiza evento da agenda (usuário autenticado)',
)
async def atualizar_evento(
	evento_id: int, payload: EventoAgendaAtualizar, service: ServiceDep
):
	"""Função para atualizar um evento da agenda."""
	return await service.atualizar_evento(evento_id, payload)


@router.delete(
	'/eventos/{evento_id}',
	status_code=status.HTTP_204_NO_CONTENT,
	summary='Remove evento da agenda (usuário autenticado)',
)
async def deletar_evento(evento_id: int, service: ServiceDep):
	"""Função para excluir um evento da agenda."""
	await service.deletar_evento(evento_id)


@router.post(
	'/solicitacoes',
	response_model=SolicitacaoReuniaoResposta,
	status_code=status.HTTP_201_CREATED,
	summary='Solicita reunião (usuário autenticado)',
)
async def criar_solicitacao(payload: SolicitacaoReuniaoCriar, service: ServiceDep):
	"""Função para criar uma solicitação de reunião."""
	return await service.criar_solicitacao(payload)


@router.get(
	'/solicitacoes/recebidas/{destinatario_id}',
	response_model=list[SolicitacaoReuniaoResposta],
	summary='Lista solicitações recebidas (usuário autenticado)',
)
async def listar_solicitacoes(destinatario_id: int, service: ServiceDep):
	"""Função para listar solicitações de reunião recebidas."""
	return await service.listar_solicitacoes_recebidas(destinatario_id)


@router.patch(
	'/solicitacoes/{solicitacao_id}',
	response_model=SolicitacaoReuniaoResposta,
	summary='Atualiza solicitação de reunião (usuário autenticado)',
)
async def atualizar_solicitacao(
	solicitacao_id: int,
	payload: SolicitacaoReuniaoAtualizar,
	service: ServiceDep,
):
	"""Função para atualizar uma solicitação de reunião."""
	return await service.atualizar_solicitacao(solicitacao_id, payload)


@router.delete(
	'/solicitacoes/{solicitacao_id}',
	status_code=status.HTTP_204_NO_CONTENT,
	summary='Remove solicitação de reunião (usuário autenticado)',
)
async def deletar_solicitacao(solicitacao_id: int, service: ServiceDep):
	"""Função para excluir uma solicitação de reunião."""
	await service.deletar_solicitacao(solicitacao_id)
