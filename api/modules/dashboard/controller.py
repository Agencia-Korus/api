from typing import Annotated

from core.enums import PapelUsuario
from core.security import UsuarioAtual, exigir_papel, obter_usuario_atual
from core.swagger import exemplo_requisicao_json
from deps import DependenciaSessao
from fastapi import APIRouter, Depends
from modules.dashboard.service import ServicoPainel

router = APIRouter(prefix='/dashboard', tags=['Painel'])


def _servico(sessao: DependenciaSessao) -> ServicoPainel:
	"""Função para criar o serviço de aplicação com a sessão atual."""
	return ServicoPainel(sessao)


DependenciaServico = Annotated[ServicoPainel, Depends(_servico)]
GuardaAdmin = Depends(exigir_papel(PapelUsuario.ADMIN.value))
DependenciaUsuarioAtual = Annotated[UsuarioAtual, Depends(obter_usuario_atual)]


@router.get(
	'/admin',
	dependencies=[GuardaAdmin],
	summary='Painel geral da agência (somente admin)',
	openapi_extra=exemplo_requisicao_json({}),
)
async def admin(servico: DependenciaServico):
	"""Função para montar os indicadores do painel administrativo."""
	return await servico.admin()


@router.get(
	'/clientes/{cliente_id}',
	summary='Painel do cliente autenticado ou admin',
	description=(
		'Admin pode consultar qualquer cliente. Cliente consulta apenas o próprio '
		'painel.'
	),
	openapi_extra=exemplo_requisicao_json({'cliente_id': 1}),
)
async def cliente(
	cliente_id: int, servico: DependenciaServico, usuario_atual: DependenciaUsuarioAtual
):
	"""Função para montar os indicadores do painel do cliente."""
	return await servico.cliente(cliente_id, usuario_atual.id, usuario_atual.papel)


@router.get(
	'/funcionarios/{funcionario_id}',
	summary='Painel do funcionário autenticado ou admin',
	description=(
		'Admin pode consultar qualquer funcionário. Funcionário consulta apenas '
		'o próprio painel.'
	),
	openapi_extra=exemplo_requisicao_json({'funcionario_id': 2}),
)
async def funcionario(
	funcionario_id: int,
	servico: DependenciaServico,
	usuario_atual: DependenciaUsuarioAtual,
):
	"""Função para montar os indicadores do painel do funcionário."""
	return await servico.funcionario(
		funcionario_id, usuario_atual.id, usuario_atual.papel
	)


@router.get(
	'/projetos/{projeto_id}/kanban',
	summary='Kanban do projeto visível ao usuário autenticado',
	description=(
		'Admin vê qualquer projeto. Cliente vê projetos próprios. Funcionário '
		'vê projetos onde participa da equipe.'
	),
	openapi_extra=exemplo_requisicao_json({'projeto_id': 1}),
)
async def projeto_kanban(
	projeto_id: int, servico: DependenciaServico, usuario_atual: DependenciaUsuarioAtual
):
	"""Função para montar os dados do quadro Kanban de um projeto."""
	return await servico.projeto_kanban(
		projeto_id, usuario_atual.id, usuario_atual.papel
	)
