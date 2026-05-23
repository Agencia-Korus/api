import csv
from io import StringIO
from typing import Annotated

from core.enums import LeadPrioridade, LeadStatus, UserRole
from core.security import require_role
from deps import PaginationDep, SessionDep
from fastapi import APIRouter, Depends, Query, Response, status
from modules.leads.schema import LeadCreate, LeadResponse, LeadUpdate
from modules.leads.service import LeadService

router = APIRouter(
	prefix='/leads',
	tags=['Leads'],
	dependencies=[Depends(require_role(UserRole.ADMIN.value))],
)


def _service(session: SessionDep) -> LeadService:
	return LeadService(session)


ServiceDep = Annotated[LeadService, Depends(_service)]


@router.post('', response_model=LeadResponse, status_code=status.HTTP_201_CREATED)
async def criar(payload: LeadCreate, service: ServiceDep):
	return await service.create(payload)


@router.get('', response_model=list[LeadResponse])
async def listar(
	service: ServiceDep,
	page: PaginationDep,
	status_filter: Annotated[LeadStatus | None, Query(alias='status')] = None,
	prioridade: LeadPrioridade | None = None,
	servico_id: int | None = None,
	search: str | None = None,
):
	return await service.list_filtered(
		offset=page.offset,
		limit=page.limit,
		status=status_filter,
		prioridade=prioridade,
		servico_id=servico_id,
		search=search,
	)


@router.get('/export.csv')
async def exportar_csv(
	service: ServiceDep,
	status_filter: Annotated[LeadStatus | None, Query(alias='status')] = None,
	prioridade: LeadPrioridade | None = None,
	servico_id: int | None = None,
	search: str | None = None,
):
	leads = await service.list_filtered(
		offset=0,
		limit=10_000,
		status=status_filter,
		prioridade=prioridade,
		servico_id=servico_id,
		search=search,
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


@router.get('/{lead_id}', response_model=LeadResponse)
async def obter(lead_id: int, service: ServiceDep):
	return await service.get(lead_id)


@router.patch('/{lead_id}', response_model=LeadResponse)
async def atualizar(lead_id: int, payload: LeadUpdate, service: ServiceDep):
	return await service.update(lead_id, payload)


@router.delete('/{lead_id}', status_code=status.HTTP_204_NO_CONTENT)
async def deletar(lead_id: int, service: ServiceDep):
	await service.delete(lead_id)
