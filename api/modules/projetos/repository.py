from core.enums import ProjetoStatus
from db.base_repository import BaseRepository
from modules.projetos.model import Projeto, ProjetoFuncionario
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession


class ProjetoRepository(BaseRepository[Projeto]):
	model = Projeto

	async def list_for_funcionario(
		self,
		funcionario_id: int,
		offset: int,
		limit: int,
		status: ProjetoStatus | None = None,
	) -> list[Projeto]:
		stmt = (
			select(Projeto)
			.join(ProjetoFuncionario, ProjetoFuncionario.projeto_id == Projeto.id)
			.where(ProjetoFuncionario.funcionario_id == funcionario_id)
		)
		if status is not None:
			stmt = stmt.where(Projeto.status == status)
		stmt = stmt.order_by(Projeto.criado_em.desc()).offset(offset).limit(limit)
		result = await self.session.execute(stmt)
		return list(result.scalars().all())


class ProjetoFuncionarioRepository:
	def __init__(self, session: AsyncSession):
		self.session = session

	async def add(self, entry: ProjetoFuncionario) -> ProjetoFuncionario:
		self.session.add(entry)
		await self.session.flush()
		await self.session.refresh(entry)
		return entry

	async def list_by_projeto(self, projeto_id: int) -> list[ProjetoFuncionario]:
		stmt = select(ProjetoFuncionario).where(
			ProjetoFuncionario.projeto_id == projeto_id
		)
		result = await self.session.execute(stmt)
		return list(result.scalars().all())

	async def has_member(self, projeto_id: int, funcionario_id: int) -> bool:
		stmt = select(ProjetoFuncionario).where(
			ProjetoFuncionario.projeto_id == projeto_id,
			ProjetoFuncionario.funcionario_id == funcionario_id,
		)
		result = await self.session.execute(stmt)
		return result.scalar_one_or_none() is not None

	async def remove(self, projeto_id: int, funcionario_id: int) -> bool:
		stmt = delete(ProjetoFuncionario).where(
			ProjetoFuncionario.projeto_id == projeto_id,
			ProjetoFuncionario.funcionario_id == funcionario_id,
		)
		result = await self.session.execute(stmt)
		await self.session.flush()
		return result.rowcount > 0
