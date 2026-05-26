from typing import Any, Generic, TypeVar

from core.constants import DESLOCAMENTO_PADRAO_PAGINACAO, LIMITE_PADRAO_PAGINACAO
from db.base import Base
from sqlalchemy import delete as sa_delete
from sqlalchemy import select
from sqlalchemy import update as sa_update
from sqlalchemy.ext.asyncio import AsyncSession

ModelT = TypeVar('ModelT', bound=Base)


class RepositorioBase(Generic[ModelT]):
	"""Classe responsável pelo acesso aos dados de base."""

	modelo: type[ModelT]

	def __init__(self, sessao: AsyncSession):
		"""Função para inicializar a instância com suas dependências."""
		self.sessao = sessao

	async def adicionar(self, entidade: ModelT) -> ModelT:
		"""Função para salvar um registro no banco de dados."""
		self.sessao.add(entidade)
		await self.sessao.flush()
		await self.sessao.refresh(entidade)
		return entidade

	async def obter(self, entidade_id: int) -> ModelT | None:
		"""Função para obter um registro pelo ID."""
		return await self.sessao.get(self.modelo, entidade_id)

	async def listar_todos(
		self,
		offset: int = DESLOCAMENTO_PADRAO_PAGINACAO,
		limit: int = LIMITE_PADRAO_PAGINACAO,
		filtros: dict[str, Any] | None = None,
	) -> list[ModelT]:
		"""Função para listar registros com paginação e filtros opcionais."""
		consulta = select(self.modelo)
		if filtros:
			for campo, valor in filtros.items():
				if valor is not None and hasattr(self.modelo, campo):
					consulta = consulta.where(getattr(self.modelo, campo) == valor)
		consulta = consulta.offset(offset).limit(limit)
		resultado = await self.sessao.execute(consulta)
		return list(resultado.scalars().all())

	async def atualizar(self, entidade_id: int, dados: dict[str, Any]) -> ModelT | None:
		"""Função para atualizar um registro pelo ID."""
		dados_atualizacao = self._remover_valores_vazios(dados)
		if not dados_atualizacao:
			return await self.obter(entidade_id)
		campo_id = getattr(self.modelo, 'id')
		instrucao = (
			sa_update(self.modelo)
			.where(campo_id == entidade_id)
			.values(**dados_atualizacao)
			.returning(self.modelo)
		)

		resultado = await self.sessao.execute(instrucao)

		await self.sessao.flush()

		return resultado.scalar_one_or_none()

	async def deletar(self, entidade_id: int) -> bool:
		"""Função para excluir um registro pelo ID."""
		campo_id = getattr(self.modelo, 'id')
		instrucao = (
			sa_delete(self.modelo).where(campo_id == entidade_id).returning(campo_id)
		)
		resultado = await self.sessao.execute(instrucao)
		await self.sessao.flush()
		return resultado.scalar_one_or_none() is not None

	def _aplicar_filtros(self, instrucao: Any, filtros: dict[str, Any] | None) -> Any:
		"""Função interna para aplicar filtros em uma consulta."""
		if not filtros:
			return instrucao

		for campo, valor in filtros.items():
			if valor is None:
				continue

			if not hasattr(self.modelo, campo):
				continue

			campo_modelo = getattr(self.modelo, campo)
			instrucao = instrucao.where(campo_modelo == valor)

		return instrucao

	@staticmethod
	def _remover_valores_vazios(dados: dict[str, Any]) -> dict[str, Any]:
		"""Função interna para remover campos vazios de um dicionário."""
		return {campo: valor for campo, valor in dados.items() if valor is not None}
