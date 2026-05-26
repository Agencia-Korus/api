from datetime import date
from typing import Annotated

from core.enums import PapelUsuario
from core.security import UsuarioAtual, exigir_papel, obter_usuario_atual
from core.swagger import exemplo_requisicao_json
from deps import DependenciaSessao
from fastapi import APIRouter, Depends, status
from modules.agenda.schema import (
	AgendaEventoSiteResposta,
	EventoAgendaAtualizar,
	EventoAgendaCriar,
	EventoAgendaResposta,
	EventoGoogleCalendarResposta,
	SolicitacaoReuniaoAtualizar,
	SolicitacaoReuniaoCriar,
	SolicitacaoReuniaoResposta,
)
from modules.agenda.service import ServicoAgenda

GuardaUsuarioAutenticado = Depends(
	exigir_papel(
		PapelUsuario.CLIENTE.value,
		PapelUsuario.FUNCIONARIO.value,
		PapelUsuario.ADMIN.value,
	)
)
DependenciaUsuarioAtual = Annotated[UsuarioAtual, Depends(obter_usuario_atual)]

router = APIRouter(
	prefix='/agenda', tags=['Agenda'], dependencies=[GuardaUsuarioAutenticado]
)


def _servico(sessao: DependenciaSessao) -> ServicoAgenda:
	"""Função para criar o serviço de aplicação com a sessão atual."""
	return ServicoAgenda(sessao)


DependenciaServico = Annotated[ServicoAgenda, Depends(_servico)]


@router.post(
	'/eventos',
	response_model=EventoAgendaResposta,
	status_code=status.HTTP_201_CREATED,
	summary='Cria evento na agenda (usuário autenticado)',
)
async def criar_evento(dados: EventoAgendaCriar, servico: DependenciaServico):
	"""Função para criar um evento na agenda."""
	return await servico.criar_evento(dados)


@router.get(
	'/eventos',
	response_model=list[AgendaEventoSiteResposta],
	summary='Lista eventos do usuário logado unificando agenda local e Google Calendar',
	description=(
		'Endpoint recomendado para o site. Retorna eventos locais do usuário '
		'autenticado e reuniões reais do Google Calendar no mesmo formato.'
	),
	openapi_extra=exemplo_requisicao_json({
		'data_inicio': '2026-05-01',
		'data_fim': '2026-05-31',
	}),
)
async def listar_eventos_site(
	usuario_atual: DependenciaUsuarioAtual,
	servico: DependenciaServico,
	data_inicio: date | None = None,
	data_fim: date | None = None,
):
	"""Função para listar eventos públicos exibidos no site."""
	return await servico.listar_eventos_site(usuario_atual.id, data_inicio, data_fim)


@router.get(
	'/eventos/usuario/{usuario_id}',
	response_model=list[EventoAgendaResposta],
	summary='Lista eventos locais de um usuário (usuário autenticado)',
	openapi_extra=exemplo_requisicao_json({'usuario_id': 1}),
)
async def listar_eventos(usuario_id: int, servico: DependenciaServico):
	"""Função para listar eventos de um usuário."""
	return await servico.listar_eventos(usuario_id)


@router.get(
	'/eventos/google-calendar',
	response_model=list[EventoGoogleCalendarResposta],
	summary='Lista reuniões reais do Google Calendar',
	description=(
		'Busca eventos diretamente no Google Calendar configurado. Quando a '
		'integração estiver desativada ou sem credenciais, retorna lista vazia.'
	),
	openapi_extra=exemplo_requisicao_json({
		'data_inicio': '2026-05-01',
		'data_fim': '2026-05-31',
	}),
)
async def listar_eventos_calendario_google(
	servico: DependenciaServico,
	data_inicio: date | None = None,
	data_fim: date | None = None,
):
	"""Função para listar eventos sincronizados do Google Calendar."""
	return await servico.listar_eventos_calendario_google(data_inicio, data_fim)


@router.get(
	'/eventos/{evento_id}',
	response_model=EventoAgendaResposta,
	summary='Obtém evento da agenda (usuário autenticado)',
	openapi_extra=exemplo_requisicao_json({'evento_id': 1}),
)
async def obter_evento(evento_id: int, servico: DependenciaServico):
	"""Função para obter um evento da agenda pelo ID."""
	return await servico.obter_evento(evento_id)


@router.patch(
	'/eventos/{evento_id}',
	response_model=EventoAgendaResposta,
	summary='Atualiza evento da agenda (usuário autenticado)',
)
async def atualizar_evento(
	evento_id: int, dados: EventoAgendaAtualizar, servico: DependenciaServico
):
	"""Função para atualizar um evento da agenda."""
	return await servico.atualizar_evento(evento_id, dados)


@router.delete(
	'/eventos/{evento_id}',
	status_code=status.HTTP_204_NO_CONTENT,
	summary='Remove evento da agenda (usuário autenticado)',
	openapi_extra=exemplo_requisicao_json({'evento_id': 1}),
)
async def deletar_evento(evento_id: int, servico: DependenciaServico):
	"""Função para excluir um evento da agenda."""
	await servico.deletar_evento(evento_id)


@router.post(
	'/solicitacoes',
	response_model=SolicitacaoReuniaoResposta,
	status_code=status.HTTP_201_CREATED,
	summary='Solicita reunião (usuário autenticado)',
)
async def criar_solicitacao(
	dados: SolicitacaoReuniaoCriar, servico: DependenciaServico
):
	"""Função para criar uma solicitação de reunião."""
	return await servico.criar_solicitacao(dados)


@router.get(
	'/solicitacoes/recebidas/{destinatario_id}',
	response_model=list[SolicitacaoReuniaoResposta],
	summary='Lista solicitações recebidas (usuário autenticado)',
	openapi_extra=exemplo_requisicao_json({'destinatario_id': 1}),
)
async def listar_solicitacoes(destinatario_id: int, servico: DependenciaServico):
	"""Função para listar solicitações de reunião recebidas."""
	return await servico.listar_solicitacoes_recebidas(destinatario_id)


@router.patch(
	'/solicitacoes/{solicitacao_id}',
	response_model=SolicitacaoReuniaoResposta,
	summary='Atualiza solicitação de reunião (usuário autenticado)',
)
async def atualizar_solicitacao(
	solicitacao_id: int,
	dados: SolicitacaoReuniaoAtualizar,
	servico: DependenciaServico,
):
	"""Função para atualizar uma solicitação de reunião."""
	return await servico.atualizar_solicitacao(solicitacao_id, dados)


@router.delete(
	'/solicitacoes/{solicitacao_id}',
	status_code=status.HTTP_204_NO_CONTENT,
	summary='Remove solicitação de reunião (usuário autenticado)',
	openapi_extra=exemplo_requisicao_json({'solicitacao_id': 1}),
)
async def deletar_solicitacao(solicitacao_id: int, servico: DependenciaServico):
	"""Função para excluir uma solicitação de reunião."""
	await servico.deletar_solicitacao(solicitacao_id)
