from __future__ import annotations

from core.enums import ComunicadoAlvo
from core.exceptions import NotFoundError
from modules.comunicados.model import Comunicado, ComunicadoLeitura
from modules.comunicados.repository import (
	RepositorioComunicadoLeitura,
	RepositorioComunicado,
)
from modules.comunicados.schema import ComunicadoCriar, ComunicadoAtualizar
from sqlalchemy.ext.asyncio import AsyncSession

_ENTITY = 'Comunicado'


class ServicoComunicado:
	"""Classe responsável pelas regras de negócio de comunicado."""

	def __init__(self, session: AsyncSession):
		"""Função para inicializar a instância com suas dependências."""
		self.session = session
		self.repo = RepositorioComunicado(session)
		self.leituras = RepositorioComunicadoLeitura(session)

	async def criar(self, dados: ComunicadoCriar) -> Comunicado:
		"""Função para criar um novo registro."""
		comunicado = Comunicado(**dados.model_dump())
		comunicado = await self.repo.adicionar(comunicado)
		await self.session.commit()
		return comunicado

	async def obter(self, comunicado_id: int) -> Comunicado:
		"""Função para obter um registro pelo ID."""
		comunicado = await self.repo.obter(comunicado_id)
		if not comunicado:
			raise NotFoundError(_ENTITY, comunicado_id)
		return comunicado

	async def listar(self, offset: int, limit: int) -> list[Comunicado]:
		"""Função para listar registros."""
		return await self.repo.listar_todos(offset=offset, limit=limit)

	async def listar_filtrados(
		self, offset: int, limit: int, alvo: ComunicadoAlvo | None = None
	) -> list[Comunicado]:
		"""Função para listar registros aplicando filtros e paginação."""
		return await self.repo.listar_todos(
			offset=offset, limit=limit, filters={'alvo': alvo}
		)

	async def atualizar(self, comunicado_id: int, dados: ComunicadoAtualizar) -> Comunicado:
		"""Função para atualizar um registro pelo ID."""
		comunicado = await self.repo.atualizar(
			comunicado_id, dados.model_dump(exclude_none=True)
		)
		if not comunicado:
			raise NotFoundError(_ENTITY, comunicado_id)
		await self.session.commit()
		return comunicado

	async def deletar(self, comunicado_id: int) -> None:
		"""Função para excluir um registro pelo ID."""
		if not await self.repo.deletar(comunicado_id):
			raise NotFoundError(_ENTITY, comunicado_id)
		await self.session.commit()

	async def marcar_lido(
		self, comunicado_id: int, usuario_id: int
	) -> ComunicadoLeitura:
		"""Função para registrar a leitura de um comunicado."""
		await self.obter(comunicado_id)
		leitura = await self.leituras.marcar_lido(comunicado_id, usuario_id)
		await self.session.commit()
		return leitura

	async def listar_leituras(self, comunicado_id: int) -> list[ComunicadoLeitura]:
		"""Função para listar leituras de um comunicado."""
		await self.obter(comunicado_id)
		return await self.leituras.listar_por_comunicado(comunicado_id)
