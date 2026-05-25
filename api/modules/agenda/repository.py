from db.base_repository import RepositorioBase
from modules.agenda.model import EventoAgenda, SolicitacaoReuniao
from sqlalchemy import select


class RepositorioEventoAgenda(RepositorioBase[EventoAgenda]):
	"""Classe responsável pelo acesso aos dados de evento de agenda."""

	model = EventoAgenda

	async def listar_por_usuario(self, usuario_id: int) -> list[EventoAgenda]:
		"""Função para listar eventos de agenda de um usuário."""
		stmt = (
			select(EventoAgenda)
			.where(EventoAgenda.usuario_id == usuario_id)
			.order_by(EventoAgenda.data, EventoAgenda.hora)
		)
		result = await self.session.execute(stmt)
		return list(result.scalars().all())


class RepositorioSolicitacaoReuniao(RepositorioBase[SolicitacaoReuniao]):
	"""Classe responsável pelo acesso aos dados de solicitação de reunião."""

	model = SolicitacaoReuniao

	async def listar_recebidas(self, destinatario_id: int) -> list[SolicitacaoReuniao]:
		"""Função para listar solicitações recebidas por um usuário."""
		stmt = (
			select(SolicitacaoReuniao)
			.where(SolicitacaoReuniao.destinatario_id == destinatario_id)
			.order_by(SolicitacaoReuniao.criado_em.desc())
		)
		result = await self.session.execute(stmt)
		return list(result.scalars().all())
