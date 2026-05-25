from db.base_repository import RepositorioBase
from modules.gamificacao.model import (
	Conquista,
	FuncionarioConquista,
	HistoricoXp,
	RegraXp,
)
from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession


class RepositorioRegraXp(RepositorioBase[RegraXp]):
	"""Classe responsável pelo acesso aos dados de regra de XP."""

	model = RegraXp


class RepositorioHistoricoXp(RepositorioBase[HistoricoXp]):
	"""Classe responsável pelo acesso aos dados de histórico de XP."""

	model = HistoricoXp

	async def listar_por_funcionario(self, funcionario_id: int) -> list[HistoricoXp]:
		"""Função para listar registros vinculados a um funcionário."""
		stmt = (
			select(HistoricoXp)
			.where(HistoricoXp.funcionario_id == funcionario_id)
			.order_by(HistoricoXp.data.desc())
		)
		result = await self.session.execute(stmt)
		return list(result.scalars().all())


class RepositorioConquista(RepositorioBase[Conquista]):
	"""Classe responsável pelo acesso aos dados de conquista."""

	model = Conquista


class RepositorioFuncionarioConquista:
	"""Classe responsável pelo acesso aos dados de conquista do funcionário."""

	def __init__(self, session: AsyncSession):
		"""Função para inicializar a instância com suas dependências."""
		self.session = session

	async def desbloquear(
		self, funcionario_id: int, conquista_id: int
	) -> FuncionarioConquista:
		"""Função para registrar uma conquista desbloqueada por um funcionário."""
		stmt = (
			insert(FuncionarioConquista)
			.values(funcionario_id=funcionario_id, conquista_id=conquista_id)
			.on_conflict_do_nothing(index_elements=['funcionario_id', 'conquista_id'])
		)
		await self.session.execute(stmt)
		await self.session.flush()
		select_stmt = select(FuncionarioConquista).where(
			FuncionarioConquista.funcionario_id == funcionario_id,
			FuncionarioConquista.conquista_id == conquista_id,
		)
		result = await self.session.execute(select_stmt)
		return result.scalar_one()

	async def listar_por_funcionario(
		self, funcionario_id: int
	) -> list[FuncionarioConquista]:
		"""Função para listar registros vinculados a um funcionário."""
		stmt = select(FuncionarioConquista).where(
			FuncionarioConquista.funcionario_id == funcionario_id
		)
		result = await self.session.execute(stmt)
		return list(result.scalars().all())
