import csv
from io import StringIO
from typing import Annotated

from core.enums import LeadPrioridade, PapelUsuario, SituacaoLead
from core.security import exigir_papel
from deps import DependenciaPaginacao, DependenciaSessao
from fastapi import APIRouter, Depends, Query, Response, status
from modules.leads.schema import LeadAtualizar, LeadCriar, LeadResposta
from modules.leads.service import ServicoLead

roteador = APIRouter(
	prefix='/leads',
	tags=['Leads'],
	dependencies=[Depends(exigir_papel(PapelUsuario.ADMIN.value))],
)


def _servico(sessao: DependenciaSessao) -> ServicoLead:
	"""Função para criar o serviço de aplicação com a sessão atual."""
	return ServicoLead(sessao)


DependenciaServico = Annotated[ServicoLead, Depends(_servico)]


@roteador.post('', response_model=LeadResposta, status_code=status.HTTP_201_CREATED)
async def criar(dados: LeadCriar, servico: DependenciaServico):
	"""Função para criar um novo registro."""
	return await servico.criar(dados)


@roteador.get('', response_model=list[LeadResposta])
async def listar(
	servico: DependenciaServico,
	pagina: DependenciaPaginacao,
	filtro_situacao: Annotated[SituacaoLead | None, Query(alias='status')] = None,
	prioridade: LeadPrioridade | None = None,
	servico_id: int | None = None,
	busca: Annotated[str | None, Query(alias='search')] = None,
):
	"""Função para listar registros."""
	return await servico.listar_filtrados(
		offset=pagina.offset,
		limit=pagina.limit,
		status=filtro_situacao,
		prioridade=prioridade,
		servico_id=servico_id,
		busca=busca,
	)


@roteador.get('/export.csv')
async def exportar_csv(
	servico: DependenciaServico,
	filtro_situacao: Annotated[SituacaoLead | None, Query(alias='status')] = None,
	prioridade: LeadPrioridade | None = None,
	servico_id: int | None = None,
	busca: Annotated[str | None, Query(alias='search')] = None,
):
	"""Função para exportar registros em formato CSV."""
	leads = await servico.listar_filtrados(
		offset=0,
		limit=10_000,
		status=filtro_situacao,
		prioridade=prioridade,
		servico_id=servico_id,
		busca=busca,
	)
	buffer = StringIO()
	writer = csv.writer(buffer)
	writer.writerow([
		'id',
		'nome',
		'email',
		'whatsapp',
		'empresa',
		'servico_id',
		'orcamento',
		'prazo_desejado',
		'status',
		'prioridade',
		'data',
	])
	for lead in leads:
		writer.writerow([
			lead.id,
			lead.nome,
			lead.email,
			lead.whatsapp or '',
			lead.empresa or '',
			lead.servico_id or '',
			lead.orcamento or '',
			lead.prazo_desejado.isoformat() if lead.prazo_desejado else '',
			lead.status.value,
			lead.prioridade.value,
			lead.data.isoformat(),
		])
	return Response(
		content=buffer.getvalue(),
		media_type='text/csv; charset=utf-8',
		headers={'Content-Disposition': 'attachment; filename="leads.csv"'},
	)


@roteador.get('/{lead_id}', response_model=LeadResposta)
async def obter(lead_id: int, servico: DependenciaServico):
	"""Função para obter um registro pelo ID."""
	return await servico.obter(lead_id)


@roteador.patch('/{lead_id}', response_model=LeadResposta)
async def atualizar(lead_id: int, dados: LeadAtualizar, servico: DependenciaServico):
	"""Função para atualizar um registro pelo ID."""
	return await servico.atualizar(lead_id, dados)


@roteador.delete('/{lead_id}', status_code=status.HTTP_204_NO_CONTENT)
async def deletar(lead_id: int, servico: DependenciaServico):
	"""Função para excluir um registro pelo ID."""
	await servico.deletar(lead_id)
