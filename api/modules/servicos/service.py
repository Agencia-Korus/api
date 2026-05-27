from __future__ import annotations

from core.enums import SituacaoServico
from core.exceptions import ErroConflito, ErroNaoEncontrado
from modules.servicos.model import Entregavel, Servico
from modules.servicos.repository import RepositorioEntregavel, RepositorioServico
from modules.servicos.schema import (
	EntregavelAtualizar,
	EntregavelCriar,
	ServicoAtualizar,
	ServicoCriar,
)
from sqlalchemy.ext.asyncio import AsyncSession

_ENTITY_SERVICO = 'Serviço'
_ENTITY_ENTREGAVEL = 'Entregável'


class ServicoServico:
	"""Classe responsável pelas regras de negócio de serviço."""

	def __init__(self, sessao: AsyncSession):
		"""Função para inicializar a instância com suas dependências."""
		self.sessao = sessao
		self.repository = RepositorioServico(sessao)
		self.entregaveis = RepositorioEntregavel(sessao)

	async def criar(self, dados: ServicoCriar) -> Servico:
		"""Função para criar um novo registro."""
		if await self.repository.obter_por_slug(dados.slug):
			raise ErroConflito('Slug já utilizado')
		servico = Servico(**dados.model_dump())
		servico = await self.repository.adicionar(servico)
		await self.sessao.commit()
		return servico

	async def obter(self, servico_id: int) -> Servico:
		"""Função para obter um registro pelo ID."""
		servico = await self.repository.obter(servico_id)
		if not servico:
			raise ErroNaoEncontrado(_ENTITY_SERVICO, servico_id)
		return servico

	async def listar(self, offset: int, limit: int) -> list[Servico]:
		"""Função para listar registros."""
		return await self.repository.listar_todos(offset=offset, limit=limit)

	async def listar_filtrados(
		self, offset: int, limit: int, status: SituacaoServico | None = None
	) -> list[Servico]:
		"""Função para listar registros aplicando filtros e paginação."""
		return await self.repository.listar_todos(
			offset=offset, limit=limit, filtros={'status': status}
		)

	async def atualizar(self, servico_id: int, dados: ServicoAtualizar) -> Servico:
		"""Função para atualizar um registro pelo ID."""
		servico = await self.repository.atualizar(servico_id, dados.model_dump(exclude_none=True))
		if not servico:
			raise ErroNaoEncontrado(_ENTITY_SERVICO, servico_id)
		await self.sessao.commit()
		return servico

	async def deletar(self, servico_id: int) -> None:
		"""Função para excluir um registro pelo ID."""
		if not await self.repository.deletar(servico_id):
			raise ErroNaoEncontrado(_ENTITY_SERVICO, servico_id)
		await self.sessao.commit()

	async def criar_entregavel(self, dados: EntregavelCriar) -> Entregavel:
		"""Função para criar um entregável de serviço."""
		await self.obter(dados.servico_id)
		entregavel = Entregavel(**dados.model_dump())
		entregavel = await self.entregaveis.adicionar(entregavel)
		await self.sessao.commit()
		return entregavel

	async def listar_entregaveis(self, servico_id: int) -> list[Entregavel]:
		"""Função para listar entregáveis de um serviço."""
		await self.obter(servico_id)
		return await self.entregaveis.listar_por_servico(servico_id)

	async def atualizar_entregavel(
		self, entregavel_id: int, dados: EntregavelAtualizar
	) -> Entregavel:
		"""Função para atualizar um entregável de serviço."""
		entregavel = await self.entregaveis.atualizar(
			entregavel_id, dados.model_dump(exclude_none=True)
		)
		if not entregavel:
			raise ErroNaoEncontrado(_ENTITY_ENTREGAVEL, entregavel_id)
		await self.sessao.commit()
		return entregavel

	async def deletar_entregavel(self, entregavel_id: int) -> None:
		"""Função para excluir um entregável de serviço."""
		if not await self.entregaveis.deletar(entregavel_id):
			raise ErroNaoEncontrado(_ENTITY_ENTREGAVEL, entregavel_id)
		await self.sessao.commit()
