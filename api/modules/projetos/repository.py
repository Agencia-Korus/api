from core.enums import ProjetoStatus
from db.base_repository import RepositorioBase
from modules.projetos.model import Projeto, ProjetoFuncionario
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession


class RepositorioProjeto(RepositorioBase[Projeto]):
	"""Classe responsável pelo acesso aos dados de projeto."""

	model = Projeto

	async def listar_for_funcionario(
		self,
		funcionario_id: int,
		offset: int,
		limit: int,
		status: ProjetoStatus | None = None,
	) -> list[Projeto]:
		"""Função para listar projetos vinculados a um funcionário."""
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


class RepositorioProjetoFuncionario:
	"""Classe responsável pelo acesso aos dados de membro do projeto."""

	def __init__(self, session: AsyncSession):
		"""Função para inicializar a instância com suas dependências."""
		self.session = session

	async def adicionar(self, entry: ProjetoFuncionario) -> ProjetoFuncionario:
		"""Função para salvar um registro no banco de dados."""
		self.session.add(entry)
		await self.session.flush()
		await self.session.refresh(entry)
		return entry

	async def listar_por_projeto(self, projeto_id: int) -> list[ProjetoFuncionario]:
		"""Função para listar registros vinculados a um projeto."""
		stmt = select(ProjetoFuncionario).where(
			ProjetoFuncionario.projeto_id == projeto_id
		)
		result = await self.session.execute(stmt)
		return list(result.scalars().all())

	async def has_member(self, projeto_id: int, funcionario_id: int) -> bool:
		"""Função para verificar se um funcionário participa de um projeto."""
		stmt = select(ProjetoFuncionario).where(
			ProjetoFuncionario.projeto_id == projeto_id,
			ProjetoFuncionario.funcionario_id == funcionario_id,
		)
		result = await self.session.execute(stmt)
		return result.scalar_one_or_none() is not None

	async def remove(self, projeto_id: int, funcionario_id: int) -> bool:
		"""Função para remover um vínculo entre projeto e funcionário."""
		stmt = delete(ProjetoFuncionario).where(
			ProjetoFuncionario.projeto_id == projeto_id,
			ProjetoFuncionario.funcionario_id == funcionario_id,
		)
		result = await self.session.execute(stmt)
		await self.session.flush()
		return result.rowcount > 0
