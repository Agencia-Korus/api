from core.enums import PapelUsuario, SituacaoTarefa
from db.base_repository import RepositorioBase
from modules.projetos.model import Projeto, ProjetoFuncionario
from modules.tarefas.model import Anexo, Comentario, Tarefa
from sqlalchemy import or_, select


class RepositorioTarefa(RepositorioBase[Tarefa]):
	"""Classe responsável pelo acesso aos dados de tarefa."""

	modelo = Tarefa

	async def listar_por_projeto(self, projeto_id: int) -> list[Tarefa]:
		"""Função para listar registros vinculados a um projeto."""
		consulta = (
			select(Tarefa).where(Tarefa.projeto_id == projeto_id).order_by(Tarefa.ordem)
		)
		resultado = await self.sessao.execute(consulta)
		return list(resultado.scalars().all())

	async def listar_filtrados(
		self,
		offset: int,
		limit: int,
		projeto_id: int | None = None,
		responsavel_id: int | None = None,
		status: SituacaoTarefa | None = None,
	) -> list[Tarefa]:
		"""Função para listar registros aplicando filtros e paginação."""
		consulta = select(Tarefa)
		if projeto_id is not None:
			consulta = consulta.where(Tarefa.projeto_id == projeto_id)
		if responsavel_id is not None:
			consulta = consulta.where(Tarefa.responsavel_id == responsavel_id)
		if status is not None:
			consulta = consulta.where(Tarefa.status == status)
		consulta = (
			consulta.order_by(Tarefa.ordem, Tarefa.prazo).offset(offset).limit(limit)
		)
		resultado = await self.sessao.execute(consulta)
		return list(resultado.scalars().all())

	async def listar_visiveis(
		self,
		usuario_id: int,
		papel: str,
		offset: int,
		limit: int,
		projeto_id: int | None = None,
		responsavel_id: int | None = None,
		status: SituacaoTarefa | None = None,
	) -> list[Tarefa]:
		"""Função para listar registros visíveis para o usuário autenticado."""
		consulta = select(Tarefa).join(Projeto, Projeto.id == Tarefa.projeto_id)
		if papel == PapelUsuario.CLIENTE.value:
			consulta = consulta.where(Projeto.cliente_id == usuario_id)
		elif papel == PapelUsuario.FUNCIONARIO.value:
			consulta = (
				consulta
				.outerjoin(
					ProjetoFuncionario,
					ProjetoFuncionario.projeto_id == Tarefa.projeto_id,
				)
				.where(
					or_(
						Tarefa.responsavel_id == usuario_id,
						ProjetoFuncionario.funcionario_id == usuario_id,
					)
				)
				.distinct()
			)
		if projeto_id is not None:
			consulta = consulta.where(Tarefa.projeto_id == projeto_id)
		if responsavel_id is not None:
			consulta = consulta.where(Tarefa.responsavel_id == responsavel_id)
		if status is not None:
			consulta = consulta.where(Tarefa.status == status)
		consulta = (
			consulta.order_by(Tarefa.ordem, Tarefa.prazo).offset(offset).limit(limit)
		)
		resultado = await self.sessao.execute(consulta)
		return list(resultado.scalars().all())


class RepositorioComentario(RepositorioBase[Comentario]):
	"""Classe responsável pelo acesso aos dados de comentário."""

	modelo = Comentario

	async def listar_por_tarefa(self, tarefa_id: int) -> list[Comentario]:
		"""Função para listar registros vinculados a uma tarefa."""
		consulta = (
			select(Comentario)
			.where(Comentario.tarefa_id == tarefa_id)
			.order_by(Comentario.criado_em)
		)
		resultado = await self.sessao.execute(consulta)
		return list(resultado.scalars().all())


class RepositorioAnexo(RepositorioBase[Anexo]):
	"""Classe responsável pelo acesso aos dados de anexo."""

	modelo = Anexo

	async def listar_por_tarefa(self, tarefa_id: int) -> list[Anexo]:
		"""Função para listar registros vinculados a uma tarefa."""
		consulta = select(Anexo).where(Anexo.tarefa_id == tarefa_id)
		resultado = await self.sessao.execute(consulta)
		return list(resultado.scalars().all())
