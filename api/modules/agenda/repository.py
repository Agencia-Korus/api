from core.enums import SituacaoUsuario
from db.base_repository import RepositorioBase
from modules.agenda.model import EventoAgenda, SolicitacaoReuniao
from modules.users.model import Usuario
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession


class RepositorioContatoAgenda:
	"""Classe responsável por listar contatos disponíveis para reuniões."""

	def __init__(self, sessao: AsyncSession):
		"""Função para inicializar a instância com suas dependências."""
		self.sessao = sessao

	async def listar(self, excluir_id: int) -> list[Usuario]:
		"""Função para listar usuários ativos, exceto o próprio solicitante."""
		consulta = (
			select(Usuario)
			.where(Usuario.id != excluir_id)
			.where(Usuario.status == SituacaoUsuario.ATIVO)
			.order_by(Usuario.nome)
		)
		resultado = await self.sessao.execute(consulta)
		return list(resultado.scalars().all())


class RepositorioEventoAgenda(RepositorioBase[EventoAgenda]):
	"""Classe responsável pelo acesso aos dados de evento de agenda."""

	modelo = EventoAgenda

	async def listar_por_usuario(self, usuario_id: int) -> list[EventoAgenda]:
		"""Função para listar eventos de agenda de um usuário."""
		consulta = (
			select(EventoAgenda)
			.where(EventoAgenda.usuario_id == usuario_id)
			.order_by(EventoAgenda.data, EventoAgenda.hora)
		)
		resultado = await self.sessao.execute(consulta)
		return list(resultado.scalars().all())


class RepositorioSolicitacaoReuniao(RepositorioBase[SolicitacaoReuniao]):
	"""Classe responsável pelo acesso aos dados de solicitação de reunião."""

	modelo = SolicitacaoReuniao

	async def listar_recebidas(self, destinatario_id: int) -> list[SolicitacaoReuniao]:
		"""Função para listar solicitações recebidas por um usuário."""
		consulta = (
			select(SolicitacaoReuniao)
			.where(SolicitacaoReuniao.destinatario_id == destinatario_id)
			.order_by(SolicitacaoReuniao.criado_em.desc())
		)
		resultado = await self.sessao.execute(consulta)
		return list(resultado.scalars().all())
