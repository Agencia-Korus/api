from typing import Annotated

from core.enums import UserRole
from core.security import require_role
from deps import DependenciaPaginacao, DependenciaSessao
from fastapi import APIRouter, Depends, status
from modules.lgpd.schema import ConsentimentoLgpdCriar, ConsentimentoLgpdResposta
from modules.lgpd.service import ServicoLgpd

router = APIRouter(prefix='/lgpd', tags=['LGPD'])


def _service(session: DependenciaSessao) -> ServicoLgpd:
	"""Função para criar o serviço de aplicação com a sessão atual."""
	return ServicoLgpd(session)


DependenciaServico = Annotated[ServicoLgpd, Depends(_service)]
AdminGuard = Depends(require_role(UserRole.ADMIN.value))


@router.post(
	'/consentimentos',
	response_model=ConsentimentoLgpdResposta,
	status_code=status.HTTP_201_CREATED,
	summary='Registra consentimento LGPD',
	description=(
		'Endpoint usado pelo site para registrar consentimento de cookies/LGPD. '
		'Pode ser usado sem login quando ainda não existe usuário autenticado.'
	),
)
async def registrar(dados: ConsentimentoLgpdCriar, servico: DependenciaServico):
	"""Função para registrar um consentimento LGPD."""
	return await servico.registrar(dados)


@router.get(
	'/consentimentos',
	response_model=list[ConsentimentoLgpdResposta],
	dependencies=[AdminGuard],
	summary='Lista consentimentos LGPD (somente admin)',
)
async def listar(servico: DependenciaServico, pagina: DependenciaPaginacao):
	"""Função para listar registros."""
	return await servico.listar(offset=pagina.offset, limit=pagina.limit)
