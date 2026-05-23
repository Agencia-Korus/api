from db.base_repository import BaseRepository
from modules.gamificacao.model import (
	Conquista,
	FuncionarioConquista,
	HistoricoXp,
	RegraXp,
)
from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession


class RegraXpRepository(BaseRepository[RegraXp]):
	model = RegraXp


class HistoricoXpRepository(BaseRepository[HistoricoXp]):
	model = HistoricoXp

	async def list_by_funcionario(self, funcionario_id: int) -> list[HistoricoXp]:
		stmt = (
			select(HistoricoXp)
			.where(HistoricoXp.funcionario_id == funcionario_id)
			.order_by(HistoricoXp.data.desc())
		)
		result = await self.session.execute(stmt)
		return list(result.scalars().all())


class ConquistaRepository(BaseRepository[Conquista]):
	model = Conquista


class FuncionarioConquistaRepository:
	def __init__(self, session: AsyncSession):
		self.session = session

	async def desbloquear(
		self, funcionario_id: int, conquista_id: int
	) -> FuncionarioConquista:
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

	async def list_by_funcionario(
		self, funcionario_id: int
	) -> list[FuncionarioConquista]:
		stmt = select(FuncionarioConquista).where(
			FuncionarioConquista.funcionario_id == funcionario_id
		)
		result = await self.session.execute(stmt)
		return list(result.scalars().all())
