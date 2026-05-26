from db.base_repository import RepositorioBase
from modules.comunicados.model import Comunicado, ComunicadoLeitura
from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession


class RepositorioComunicado(RepositorioBase[Comunicado]):
	"""Classe responsável pelo acesso aos dados de comunicado."""

	modelo = Comunicado


class RepositorioComunicadoLeitura:
	"""Classe responsável pelo acesso aos dados de leitura de comunicado."""

	def __init__(self, sessao: AsyncSession):
		"""Função para inicializar a instância com suas dependências."""
		self.sessao = sessao

	async def marcar_lido(self, comunicado_id: int, usuario_id: int) -> ComunicadoLeitura:
		"""Função para registrar a leitura de um comunicado."""
		consulta = (
			insert(ComunicadoLeitura)
			.values(comunicado_id=comunicado_id, usuario_id=usuario_id)
			.on_conflict_do_nothing(index_elements=['comunicado_id', 'usuario_id'])
		)
		await self.sessao.execute(consulta)
		await self.sessao.flush()
		consulta_selecao = select(ComunicadoLeitura).where(
			ComunicadoLeitura.comunicado_id == comunicado_id,
			ComunicadoLeitura.usuario_id == usuario_id,
		)
		resultado = await self.sessao.execute(consulta_selecao)
		return resultado.scalar_one()

	async def listar_por_comunicado(self, comunicado_id: int) -> list[ComunicadoLeitura]:
		"""Função para listar leituras vinculadas a um comunicado."""
		consulta = select(ComunicadoLeitura).where(
			ComunicadoLeitura.comunicado_id == comunicado_id
		)
		resultado = await self.sessao.execute(consulta)
		return list(resultado.scalars().all())
