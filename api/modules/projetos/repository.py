from core.enums import SituacaoProjeto
from db.base_repository import RepositorioBase
from modules.projetos.model import Projeto, ProjetoFuncionario
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession


class RepositorioProjeto(RepositorioBase[Projeto]):
	"""Classe responsável pelo acesso aos dados de projeto."""

	modelo = Projeto

	async def listar_para_funcionario(
		self,
		funcionario_id: int,
		offset: int,
		limit: int,
		status: SituacaoProjeto | None = None,
	) -> list[Projeto]:
		"""Função para listar projetos vinculados a um funcionário."""
		consulta = (
			select(Projeto)
			.join(ProjetoFuncionario, ProjetoFuncionario.projeto_id == Projeto.id)
			.where(ProjetoFuncionario.funcionario_id == funcionario_id)
		)
		if status is not None:
			consulta = consulta.where(Projeto.status == status)
		consulta = (
			consulta.order_by(Projeto.criado_em.desc()).offset(offset).limit(limit)
		)
		resultado = await self.sessao.execute(consulta)
		return list(resultado.scalars().all())


class RepositorioProjetoFuncionario:
	"""Classe responsável pelo acesso aos dados de membro do projeto."""

	def __init__(self, sessao: AsyncSession):
		"""Função para inicializar a instância com suas dependências."""
		self.sessao = sessao

	async def adicionar(self, registro: ProjetoFuncionario) -> ProjetoFuncionario:
		"""Função para salvar um registro no banco de dados."""
		self.sessao.add(registro)
		await self.sessao.flush()
		await self.sessao.refresh(registro)
		return registro

	async def listar_por_projeto(self, projeto_id: int) -> list[ProjetoFuncionario]:
		"""Função para listar registros vinculados a um projeto."""
		consulta = select(ProjetoFuncionario).where(
			ProjetoFuncionario.projeto_id == projeto_id
		)
		resultado = await self.sessao.execute(consulta)
		return list(resultado.scalars().all())

	async def contem_membro(self, projeto_id: int, funcionario_id: int) -> bool:
		"""Função para verificar se um funcionário participa de um projeto."""
		consulta = select(ProjetoFuncionario).where(
			ProjetoFuncionario.projeto_id == projeto_id,
			ProjetoFuncionario.funcionario_id == funcionario_id,
		)
		resultado = await self.sessao.execute(consulta)
		return resultado.scalar_one_or_none() is not None

	async def remover(self, projeto_id: int, funcionario_id: int) -> bool:
		"""Função para remover um vínculo entre projeto e funcionário."""
		consulta = delete(ProjetoFuncionario).where(
			ProjetoFuncionario.projeto_id == projeto_id,
			ProjetoFuncionario.funcionario_id == funcionario_id,
		)
		resultado = await self.sessao.execute(consulta)
		await self.sessao.flush()
		return resultado.rowcount > 0
