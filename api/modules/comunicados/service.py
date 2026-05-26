from __future__ import annotations

from core.enums import ComunicadoAlvo
from core.exceptions import ErroNaoEncontrado
from modules.comunicados.model import Comunicado, ComunicadoLeitura
from modules.comunicados.repository import (
	RepositorioComunicado,
	RepositorioComunicadoLeitura,
)
from modules.comunicados.schema import ComunicadoAtualizar, ComunicadoCriar
from sqlalchemy.ext.asyncio import AsyncSession

_ENTIDADE = 'Comunicado'


class ServicoComunicado:
	"""Classe responsável pelas regras de negócio de comunicado."""

	def __init__(self, sessao: AsyncSession):
		"""Função para inicializar a instância com suas dependências."""
		self.sessao = sessao
		self.repository = RepositorioComunicado(sessao)
		self.leituras = RepositorioComunicadoLeitura(sessao)

	async def criar(self, dados: ComunicadoCriar) -> Comunicado:
		"""Função para criar um novo registro."""
		comunicado = Comunicado(**dados.model_dump())
		comunicado = await self.repository.adicionar(comunicado)
		await self.sessao.commit()
		return comunicado

	async def obter(self, comunicado_id: int) -> Comunicado:
		"""Função para obter um registro pelo ID."""
		comunicado = await self.repository.obter(comunicado_id)
		if not comunicado:
			raise ErroNaoEncontrado(_ENTIDADE, comunicado_id)
		return comunicado

	async def listar(self, offset: int, limit: int) -> list[Comunicado]:
		"""Função para listar registros."""
		return await self.repository.listar_todos(offset=offset, limit=limit)

	async def listar_filtrados(
		self, offset: int, limit: int, alvo: ComunicadoAlvo | None = None
	) -> list[Comunicado]:
		"""Função para listar registros aplicando filtros e paginação."""
		return await self.repository.listar_todos(
			offset=offset, limit=limit, filtros={'alvo': alvo}
		)

	async def atualizar(
		self, comunicado_id: int, dados: ComunicadoAtualizar
	) -> Comunicado:
		"""Função para atualizar um registro pelo ID."""
		comunicado = await self.repository.atualizar(
			comunicado_id, dados.model_dump(exclude_none=True)
		)
		if not comunicado:
			raise ErroNaoEncontrado(_ENTIDADE, comunicado_id)
		await self.sessao.commit()
		return comunicado

	async def deletar(self, comunicado_id: int) -> None:
		"""Função para excluir um registro pelo ID."""
		if not await self.repository.deletar(comunicado_id):
			raise ErroNaoEncontrado(_ENTIDADE, comunicado_id)
		await self.sessao.commit()

	async def marcar_lido(
		self, comunicado_id: int, usuario_id: int
	) -> ComunicadoLeitura:
		"""Função para registrar a leitura de um comunicado."""
		await self.obter(comunicado_id)
		leitura = await self.leituras.marcar_lido(comunicado_id, usuario_id)
		await self.sessao.commit()
		return leitura

	async def listar_leituras(self, comunicado_id: int) -> list[ComunicadoLeitura]:
		"""Função para listar leituras de um comunicado."""
		await self.obter(comunicado_id)
		return await self.leituras.listar_por_comunicado(comunicado_id)
