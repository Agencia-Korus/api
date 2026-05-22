from sqlalchemy import or_, select

from core.enums import TarefaStatus, UserRole
from db.base_repository import BaseRepository
from modules.projetos.model import Projeto, ProjetoFuncionario
from modules.tarefas.model import Anexo, Comentario, Tarefa


class TarefaRepository(BaseRepository[Tarefa]):
	model = Tarefa

	async def list_by_projeto(self, projeto_id: int) -> list[Tarefa]:
		stmt = (
			select(Tarefa).where(Tarefa.projeto_id == projeto_id).order_by(Tarefa.ordem)
		)
		result = await self.session.execute(stmt)
		return list(result.scalars().all())

	async def list_filtered(
		self,
		offset: int,
		limit: int,
		projeto_id: int | None = None,
		responsavel_id: int | None = None,
		status: TarefaStatus | None = None,
	) -> list[Tarefa]:
		stmt = select(Tarefa)
		if projeto_id is not None:
			stmt = stmt.where(Tarefa.projeto_id == projeto_id)
		if responsavel_id is not None:
			stmt = stmt.where(Tarefa.responsavel_id == responsavel_id)
		if status is not None:
			stmt = stmt.where(Tarefa.status == status)
		stmt = stmt.order_by(Tarefa.ordem, Tarefa.prazo).offset(offset).limit(limit)
		result = await self.session.execute(stmt)
		return list(result.scalars().all())

	async def list_visible(
		self,
		usuario_id: int,
		role: str,
		offset: int,
		limit: int,
		projeto_id: int | None = None,
		responsavel_id: int | None = None,
		status: TarefaStatus | None = None,
	) -> list[Tarefa]:
		stmt = select(Tarefa).join(Projeto, Projeto.id == Tarefa.projeto_id)
		if role == UserRole.CLIENTE.value:
			stmt = stmt.where(Projeto.cliente_id == usuario_id)
		elif role == UserRole.FUNCIONARIO.value:
			stmt = (
				stmt.outerjoin(
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
			stmt = stmt.where(Tarefa.projeto_id == projeto_id)
		if responsavel_id is not None:
			stmt = stmt.where(Tarefa.responsavel_id == responsavel_id)
		if status is not None:
			stmt = stmt.where(Tarefa.status == status)
		stmt = stmt.order_by(Tarefa.ordem, Tarefa.prazo).offset(offset).limit(limit)
		result = await self.session.execute(stmt)
		return list(result.scalars().all())


class ComentarioRepository(BaseRepository[Comentario]):
	model = Comentario

	async def list_by_tarefa(self, tarefa_id: int) -> list[Comentario]:
		stmt = (
			select(Comentario)
			.where(Comentario.tarefa_id == tarefa_id)
			.order_by(Comentario.criado_em)
		)
		result = await self.session.execute(stmt)
		return list(result.scalars().all())


class AnexoRepository(BaseRepository[Anexo]):
	model = Anexo

	async def list_by_tarefa(self, tarefa_id: int) -> list[Anexo]:
		stmt = select(Anexo).where(Anexo.tarefa_id == tarefa_id)
		result = await self.session.execute(stmt)
		return list(result.scalars().all())