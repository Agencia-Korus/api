from __future__ import annotations

from core.exceptions import NotFoundError
from modules.gamificacao.model import (
	Conquista,
	FuncionarioConquista,
	HistoricoXp,
	RegraXp,
)
from modules.gamificacao.repository import (
	RepositorioConquista,
	RepositorioFuncionarioConquista,
	RepositorioHistoricoXp,
	RepositorioRegraXp,
)
from modules.gamificacao.schema import (
	ConquistaCriar,
	ConquistaAtualizar,
	HistoricoXpCriar,
	RegraXpCriar,
	RegraXpAtualizar,
)
from modules.users.model import Funcionario
from sqlalchemy.ext.asyncio import AsyncSession

_ENTITY_REGRA = 'Regra XP'
_ENTITY_CONQUISTA = 'Conquista'


class ServicoGamificacao:
	"""Classe responsável pelas regras de negócio de gamificacao."""

	def __init__(self, session: AsyncSession):
		"""Função para inicializar a instância com suas dependências."""
		self.session = session
		self.regras = RepositorioRegraXp(session)
		self.historicos = RepositorioHistoricoXp(session)
		self.conquistas = RepositorioConquista(session)
		self.fc = RepositorioFuncionarioConquista(session)

	async def criar_regra(self, dados: RegraXpCriar) -> RegraXp:
		"""Função para criar uma regra de XP."""
		regra = RegraXp(**dados.model_dump())
		regra = await self.regras.adicionar(regra)
		await self.session.commit()
		return regra

	async def listar_regras(self, offset: int, limit: int) -> list[RegraXp]:
		"""Função para listar regras de XP."""
		return await self.regras.listar_todos(offset=offset, limit=limit)

	async def atualizar_regra(self, regra_id: int, dados: RegraXpAtualizar) -> RegraXp:
		"""Função para atualizar uma regra de XP."""
		regra = await self.regras.atualizar(
			regra_id, dados.model_dump(exclude_none=True)
		)
		if not regra:
			raise NotFoundError(_ENTITY_REGRA, regra_id)
		await self.session.commit()
		return regra

	async def deletar_regra(self, regra_id: int) -> None:
		"""Função para excluir uma regra de XP."""
		if not await self.regras.deletar(regra_id):
			raise NotFoundError(_ENTITY_REGRA, regra_id)
		await self.session.commit()

	async def registrar_xp(self, dados: HistoricoXpCriar) -> HistoricoXp:
		"""Função para registrar XP para um funcionário."""
		funcionario = await self.session.obter(Funcionario, dados.funcionario_id)
		if not funcionario:
			raise NotFoundError('Funcionario', dados.funcionario_id)
		registro = HistoricoXp(**dados.model_dump())
		registro = await self.historicos.adicionar(registro)
		funcionario.xp_total += dados.xp
		funcionario.nivel = max(1, (funcionario.xp_total // 500) + 1)
		await self.session.commit()
		return registro

	async def listar_historico(self, funcionario_id: int) -> list[HistoricoXp]:
		"""Função para listar o histórico de XP de um funcionário."""
		return await self.historicos.listar_por_funcionario(funcionario_id)

	async def criar_conquista(self, dados: ConquistaCriar) -> Conquista:
		"""Função para criar uma conquista."""
		conquista = Conquista(**dados.model_dump())
		conquista = await self.conquistas.adicionar(conquista)
		await self.session.commit()
		return conquista

	async def listar_conquistas(self, offset: int, limit: int) -> list[Conquista]:
		"""Função para listar conquistas."""
		return await self.conquistas.listar_todos(offset=offset, limit=limit)

	async def atualizar_conquista(
		self, conquista_id: int, dados: ConquistaAtualizar
	) -> Conquista:
		"""Função para atualizar uma conquista."""
		conquista = await self.conquistas.atualizar(
			conquista_id, dados.model_dump(exclude_none=True)
		)
		if not conquista:
			raise NotFoundError(_ENTITY_CONQUISTA, conquista_id)
		await self.session.commit()
		return conquista

	async def deletar_conquista(self, conquista_id: int) -> None:
		"""Função para excluir uma conquista."""
		if not await self.conquistas.deletar(conquista_id):
			raise NotFoundError(_ENTITY_CONQUISTA, conquista_id)
		await self.session.commit()

	async def desbloquear_conquista(
		self, funcionario_id: int, conquista_id: int
	) -> FuncionarioConquista:
		"""Função para desbloquear uma conquista para um funcionário."""
		entry = await self.fc.desbloquear(funcionario_id, conquista_id)
		await self.session.commit()
		return entry

	async def listar_conquistas_funcionario(
		self, funcionario_id: int
	) -> list[FuncionarioConquista]:
		"""Função para listar conquistas de um funcionário."""
		return await self.fc.listar_por_funcionario(funcionario_id)
