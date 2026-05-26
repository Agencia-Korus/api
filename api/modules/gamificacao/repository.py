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

	modelo = RegraXp


class RepositorioHistoricoXp(RepositorioBase[HistoricoXp]):
	"""Classe responsável pelo acesso aos dados de histórico de XP."""

	modelo = HistoricoXp

	async def listar_por_funcionario(self, funcionario_id: int) -> list[HistoricoXp]:
		"""Função para listar registros vinculados a um funcionário."""
		consulta = (
			select(HistoricoXp)
			.where(HistoricoXp.funcionario_id == funcionario_id)
			.order_by(HistoricoXp.data.desc())
		)
		resultado = await self.sessao.execute(consulta)
		return list(resultado.scalars().all())


class RepositorioConquista(RepositorioBase[Conquista]):
	"""Classe responsável pelo acesso aos dados de conquista."""

	modelo = Conquista


class RepositorioFuncionarioConquista:
	"""Classe responsável pelo acesso aos dados de conquista do funcionário."""

	def __init__(self, sessao: AsyncSession):
		"""Função para inicializar a instância com suas dependências."""
		self.sessao = sessao

	async def desbloquear(self, funcionario_id: int, conquista_id: int) -> FuncionarioConquista:
		"""Função para registrar uma conquista desbloqueada por um funcionário."""
		consulta = (
			insert(FuncionarioConquista)
			.values(funcionario_id=funcionario_id, conquista_id=conquista_id)
			.on_conflict_do_nothing(index_elements=['funcionario_id', 'conquista_id'])
		)
		await self.sessao.execute(consulta)
		await self.sessao.flush()
		consulta_selecao = select(FuncionarioConquista).where(
			FuncionarioConquista.funcionario_id == funcionario_id,
			FuncionarioConquista.conquista_id == conquista_id,
		)
		resultado = await self.sessao.execute(consulta_selecao)
		return resultado.scalar_one()

	async def listar_por_funcionario(self, funcionario_id: int) -> list[FuncionarioConquista]:
		"""Função para listar registros vinculados a um funcionário."""
		consulta = select(FuncionarioConquista).where(
			FuncionarioConquista.funcionario_id == funcionario_id
		)
		resultado = await self.sessao.execute(consulta)
		return list(resultado.scalars().all())
