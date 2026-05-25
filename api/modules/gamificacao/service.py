from __future__ import annotations

from core.exceptions import NotFoundError
from modules.gamificacao.model import (
	Conquista,
	FuncionarioConquista,
	HistoricoXp,
	RegraXp,
)
from modules.gamificacao.repository import (
	ConquistaRepository,
	FuncionarioConquistaRepository,
	HistoricoXpRepository,
	RegraXpRepository,
)
from modules.gamificacao.schema import (
	ConquistaCreate,
	ConquistaUpdate,
	HistoricoXpCreate,
	RegraXpCreate,
	RegraXpUpdate,
)
from modules.users.model import Funcionario
from sqlalchemy.ext.asyncio import AsyncSession

_ENTITY_REGRA = 'Regra XP'
_ENTITY_CONQUISTA = 'Conquista'


class GamificacaoService:
	"""Classe responsável pelas regras de negócio de gamificacao."""

	def __init__(self, session: AsyncSession):
		"""Função para inicializar a instância com suas dependências."""
		self.session = session
		self.regras = RegraXpRepository(session)
		self.historicos = HistoricoXpRepository(session)
		self.conquistas = ConquistaRepository(session)
		self.fc = FuncionarioConquistaRepository(session)

	async def criar_regra(self, payload: RegraXpCreate) -> RegraXp:
		"""Função para criar uma regra de XP."""
		regra = RegraXp(**payload.model_dump())
		regra = await self.regras.add(regra)
		await self.session.commit()
		return regra

	async def listar_regras(self, offset: int, limit: int) -> list[RegraXp]:
		"""Função para listar regras de XP."""
		return await self.regras.list_all(offset=offset, limit=limit)

	async def atualizar_regra(self, regra_id: int, payload: RegraXpUpdate) -> RegraXp:
		"""Função para atualizar uma regra de XP."""
		regra = await self.regras.update(
			regra_id, payload.model_dump(exclude_none=True)
		)
		if not regra:
			raise NotFoundError(_ENTITY_REGRA, regra_id)
		await self.session.commit()
		return regra

	async def deletar_regra(self, regra_id: int) -> None:
		"""Função para excluir uma regra de XP."""
		if not await self.regras.delete(regra_id):
			raise NotFoundError(_ENTITY_REGRA, regra_id)
		await self.session.commit()

	async def registrar_xp(self, payload: HistoricoXpCreate) -> HistoricoXp:
		"""Função para registrar XP para um funcionário."""
		funcionario = await self.session.get(Funcionario, payload.funcionario_id)
		if not funcionario:
			raise NotFoundError('Funcionario', payload.funcionario_id)
		registro = HistoricoXp(**payload.model_dump())
		registro = await self.historicos.add(registro)
		funcionario.xp_total += payload.xp
		funcionario.nivel = max(1, (funcionario.xp_total // 500) + 1)
		await self.session.commit()
		return registro

	async def listar_historico(self, funcionario_id: int) -> list[HistoricoXp]:
		"""Função para listar o histórico de XP de um funcionário."""
		return await self.historicos.list_by_funcionario(funcionario_id)

	async def criar_conquista(self, payload: ConquistaCreate) -> Conquista:
		"""Função para criar uma conquista."""
		conquista = Conquista(**payload.model_dump())
		conquista = await self.conquistas.add(conquista)
		await self.session.commit()
		return conquista

	async def listar_conquistas(self, offset: int, limit: int) -> list[Conquista]:
		"""Função para listar conquistas."""
		return await self.conquistas.list_all(offset=offset, limit=limit)

	async def atualizar_conquista(
		self, conquista_id: int, payload: ConquistaUpdate
	) -> Conquista:
		"""Função para atualizar uma conquista."""
		conquista = await self.conquistas.update(
			conquista_id, payload.model_dump(exclude_none=True)
		)
		if not conquista:
			raise NotFoundError(_ENTITY_CONQUISTA, conquista_id)
		await self.session.commit()
		return conquista

	async def deletar_conquista(self, conquista_id: int) -> None:
		"""Função para excluir uma conquista."""
		if not await self.conquistas.delete(conquista_id):
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
		return await self.fc.list_by_funcionario(funcionario_id)
