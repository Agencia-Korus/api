from __future__ import annotations

from core.enums import ServicoStatus
from core.exceptions import ConflictError, NotFoundError
from modules.servicos.model import Entregavel, Servico
from modules.servicos.repository import RepositorioEntregavel, RepositorioServico
from modules.servicos.schema import (
	EntregavelCriar,
	EntregavelAtualizar,
	ServicoCriar,
	ServicoAtualizar,
)
from sqlalchemy.ext.asyncio import AsyncSession

_ENTITY_SERVICO = 'Serviço'
_ENTITY_ENTREGAVEL = 'Entregável'


class ServicoServico:
	"""Classe responsável pelas regras de negócio de serviço."""

	def __init__(self, session: AsyncSession):
		"""Função para inicializar a instância com suas dependências."""
		self.session = session
		self.repo = RepositorioServico(session)
		self.entregaveis = RepositorioEntregavel(session)

	async def criar(self, payload: ServicoCriar) -> Servico:
		"""Função para criar um novo registro."""
		if await self.repo.obter_por_slug(payload.slug):
			raise ConflictError('Slug já utilizado')
		servico = Servico(**payload.model_dump())
		servico = await self.repo.adicionar(servico)
		await self.session.commit()
		return servico

	async def obter(self, servico_id: int) -> Servico:
		"""Função para obter um registro pelo ID."""
		servico = await self.repo.obter(servico_id)
		if not servico:
			raise NotFoundError(_ENTITY_SERVICO, servico_id)
		return servico

	async def listar(self, offset: int, limit: int) -> list[Servico]:
		"""Função para listar registros."""
		return await self.repo.listar_todos(offset=offset, limit=limit)

	async def listar_filtrados(
		self, offset: int, limit: int, status: ServicoStatus | None = None
	) -> list[Servico]:
		"""Função para listar registros aplicando filtros e paginação."""
		return await self.repo.listar_todos(
			offset=offset, limit=limit, filters={'status': status}
		)

	async def atualizar(self, servico_id: int, payload: ServicoAtualizar) -> Servico:
		"""Função para atualizar um registro pelo ID."""
		servico = await self.repo.atualizar(
			servico_id, payload.model_dump(exclude_none=True)
		)
		if not servico:
			raise NotFoundError(_ENTITY_SERVICO, servico_id)
		await self.session.commit()
		return servico

	async def deletar(self, servico_id: int) -> None:
		"""Função para excluir um registro pelo ID."""
		if not await self.repo.deletar(servico_id):
			raise NotFoundError(_ENTITY_SERVICO, servico_id)
		await self.session.commit()

	async def criar_entregavel(self, payload: EntregavelCriar) -> Entregavel:
		"""Função para criar um entregável de serviço."""
		await self.obter(payload.servico_id)
		entregavel = Entregavel(**payload.model_dump())
		entregavel = await self.entregaveis.adicionar(entregavel)
		await self.session.commit()
		return entregavel

	async def listar_entregaveis(self, servico_id: int) -> list[Entregavel]:
		"""Função para listar entregáveis de um serviço."""
		await self.obter(servico_id)
		return await self.entregaveis.listar_por_servico(servico_id)

	async def atualizar_entregavel(
		self, entregavel_id: int, payload: EntregavelAtualizar
	) -> Entregavel:
		"""Função para atualizar um entregável de serviço."""
		entregavel = await self.entregaveis.atualizar(
			entregavel_id, payload.model_dump(exclude_none=True)
		)
		if not entregavel:
			raise NotFoundError(_ENTITY_ENTREGAVEL, entregavel_id)
		await self.session.commit()
		return entregavel

	async def deletar_entregavel(self, entregavel_id: int) -> None:
		"""Função para excluir um entregável de serviço."""
		if not await self.entregaveis.deletar(entregavel_id):
			raise NotFoundError(_ENTITY_ENTREGAVEL, entregavel_id)
		await self.session.commit()
