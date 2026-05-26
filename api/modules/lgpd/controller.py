from typing import Annotated

from core.enums import PapelUsuario
from core.security import exigir_papel
from deps import DependenciaPaginacao, DependenciaSessao
from fastapi import APIRouter, Depends, status
from modules.lgpd.schema import ConsentimentoLgpdCriar, ConsentimentoLgpdResposta
from modules.lgpd.service import ServicoLgpd

roteador = APIRouter(prefix='/lgpd', tags=['LGPD'])


def _servico(sessao: DependenciaSessao) -> ServicoLgpd:
	"""Função para criar o serviço de aplicação com a sessão atual."""
	return ServicoLgpd(sessao)


DependenciaServico = Annotated[ServicoLgpd, Depends(_servico)]
GuardaAdmin = Depends(exigir_papel(PapelUsuario.ADMIN.value))


@roteador.post(
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


@roteador.get(
	'/consentimentos',
	response_model=list[ConsentimentoLgpdResposta],
	dependencies=[GuardaAdmin],
	summary='Lista consentimentos LGPD (somente admin)',
)
async def listar(servico: DependenciaServico, pagina: DependenciaPaginacao):
	"""Função para listar registros."""
	return await servico.listar(offset=pagina.offset, limit=pagina.limit)
