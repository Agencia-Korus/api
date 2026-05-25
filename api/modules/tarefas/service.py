from __future__ import annotations

from datetime import datetime, timezone

from core.enums import TarefaStatus, UserRole
from core.exceptions import NotFoundError
from fastapi import HTTPException, status
from modules.projetos.model import Projeto, ProjetoFuncionario
from modules.tarefas.model import Anexo, Comentario, Tarefa
from modules.tarefas.repository import (
	AnexoRepository,
	ComentarioRepository,
	TarefaRepository,
)
from modules.tarefas.schema import (
	AnexoCreate,
	ComentarioCreate,
	TarefaCreate,
	TarefaUpdate,
)
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

_ENTITY_TAREFA = 'Tarefa'
_ENTITY_COMENTARIO = 'Comentário'
_ENTITY_ANEXO = 'Anexo'


class TarefaService:
	"""Classe responsável pelas regras de negócio de tarefa."""

	def __init__(self, session: AsyncSession):
		"""Função para inicializar a instância com suas dependências."""
		self.session = session
		self.repo = TarefaRepository(session)
		self.comentarios = ComentarioRepository(session)
		self.anexos = AnexoRepository(session)

	async def create(self, payload: TarefaCreate) -> Tarefa:
		"""Função para criar um novo registro."""
		tarefa = Tarefa(**payload.model_dump())
		tarefa = await self.repo.add(tarefa)
		await self.session.commit()
		return tarefa

	async def get(self, tarefa_id: int) -> Tarefa:
		"""Função para obter um registro pelo ID."""
		tarefa = await self.repo.get(tarefa_id)
		if not tarefa:
			raise NotFoundError(_ENTITY_TAREFA, tarefa_id)
		return tarefa

	async def list(self, offset: int, limit: int) -> list[Tarefa]:
		"""Função para listar registros."""
		return await self.repo.list_all(offset=offset, limit=limit)

	async def list_by_projeto(self, projeto_id: int) -> list[Tarefa]:
		"""Função para listar registros vinculados a um projeto."""
		return await self.repo.list_by_projeto(projeto_id)

	async def list_filtered(
		self,
		offset: int,
		limit: int,
		projeto_id: int | None = None,
		responsavel_id: int | None = None,
		status: TarefaStatus | None = None,
	) -> list[Tarefa]:
		"""Função para listar registros aplicando filtros e paginação."""
		return await self.repo.list_filtered(
			offset=offset,
			limit=limit,
			projeto_id=projeto_id,
			responsavel_id=responsavel_id,
			status=status,
		)

	async def list_visible(
		self,
		offset: int,
		limit: int,
		usuario_id: int,
		role: str,
		projeto_id: int | None = None,
		responsavel_id: int | None = None,
		status: TarefaStatus | None = None,
	) -> list[Tarefa]:
		"""Função para listar registros visíveis para o usuário autenticado."""
		if role == UserRole.ADMIN.value:
			return await self.list_filtered(
				offset=offset,
				limit=limit,
				projeto_id=projeto_id,
				responsavel_id=responsavel_id,
				status=status,
			)
		if role in {UserRole.CLIENTE.value, UserRole.FUNCIONARIO.value}:
			return await self.repo.list_visible(
				usuario_id=usuario_id,
				role=role,
				offset=offset,
				limit=limit,
				projeto_id=projeto_id,
				responsavel_id=responsavel_id,
				status=status,
			)
		raise HTTPException(
			status_code=status.HTTP_403_FORBIDDEN,
			detail='Acesso negado para tarefas',
		)

	async def get_visible(self, tarefa_id: int, usuario_id: int, role: str) -> Tarefa:
		"""Função para obter um registro respeitando as permissões do usuário."""
		tarefa = await self.get(tarefa_id)
		if role == UserRole.ADMIN.value or await self._can_access_tarefa(
			tarefa, usuario_id, role
		):
			return tarefa
		raise HTTPException(
			status_code=status.HTTP_403_FORBIDDEN,
			detail='Acesso negado para esta tarefa',
		)

	async def ensure_can_manage_tarefa(
		self, tarefa_id: int, usuario_id: int, role: str
	) -> Tarefa:
		"""Função para validar se o usuário pode gerenciar uma tarefa."""
		tarefa = await self.get(tarefa_id)
		if role == UserRole.ADMIN.value:
			return tarefa
		if role == UserRole.FUNCIONARIO.value and await self._funcionario_envolvido(
			tarefa, usuario_id
		):
			return tarefa
		raise HTTPException(
			status_code=status.HTTP_403_FORBIDDEN,
			detail='Apenas admin ou funcionário envolvido pode alterar esta tarefa',
		)

	async def _can_access_tarefa(
		self, tarefa: Tarefa, usuario_id: int, role: str
	) -> bool:
		"""Função interna para validar acesso a uma tarefa."""
		if role == UserRole.CLIENTE.value:
			projeto = await self.session.get(Projeto, tarefa.projeto_id)
			return bool(projeto and projeto.cliente_id == usuario_id)
		if role == UserRole.FUNCIONARIO.value:
			return await self._funcionario_envolvido(tarefa, usuario_id)
		return False

	async def _funcionario_envolvido(self, tarefa: Tarefa, funcionario_id: int) -> bool:
		"""Função interna para verificar vínculo do funcionário com a tarefa."""
		if tarefa.responsavel_id == funcionario_id:
			return True
		stmt = select(ProjetoFuncionario).where(
			ProjetoFuncionario.projeto_id == tarefa.projeto_id,
			ProjetoFuncionario.funcionario_id == funcionario_id,
		)
		result = await self.session.execute(stmt)
		return result.scalar_one_or_none() is not None

	async def update(self, tarefa_id: int, payload: TarefaUpdate) -> Tarefa:
		"""Função para atualizar um registro pelo ID."""
		data = payload.model_dump(exclude_none=True)
		if data.get('status') == TarefaStatus.CONCLUIDO:
			data['concluido_em'] = datetime.now(timezone.utc)
		tarefa = await self.repo.update(tarefa_id, data)
		if not tarefa:
			raise NotFoundError(_ENTITY_TAREFA, tarefa_id)
		await self.session.commit()
		return tarefa

	async def delete(self, tarefa_id: int) -> None:
		"""Função para excluir um registro pelo ID."""
		if not await self.repo.delete(tarefa_id):
			raise NotFoundError(_ENTITY_TAREFA, tarefa_id)
		await self.session.commit()

	async def add_comentario(
		self, payload: ComentarioCreate, autor_id: int
	) -> Comentario:
		"""Função para adicionar um comentário a uma tarefa."""
		await self.get(payload.tarefa_id)
		comentario = Comentario(
			tarefa_id=payload.tarefa_id,
			autor_id=autor_id,
			conteudo=payload.conteudo,
		)
		comentario = await self.comentarios.add(comentario)
		await self.session.commit()
		return comentario

	async def list_comentarios(self, tarefa_id: int) -> list[Comentario]:
		"""Função para listar comentários de uma tarefa."""
		await self.get(tarefa_id)
		return await self.comentarios.list_by_tarefa(tarefa_id)

	async def delete_comentario(self, comentario_id: int) -> None:
		"""Função para excluir um comentário pelo ID."""
		if not await self.comentarios.delete(comentario_id):
			raise NotFoundError(_ENTITY_COMENTARIO, comentario_id)
		await self.session.commit()

	async def add_anexo(self, payload: AnexoCreate) -> Anexo:
		"""Função para adicionar um anexo a uma tarefa."""
		await self.get(payload.tarefa_id)
		anexo = Anexo(**payload.model_dump())
		anexo = await self.anexos.add(anexo)
		await self.session.commit()
		return anexo

	async def list_anexos(self, tarefa_id: int) -> list[Anexo]:
		"""Função para listar anexos de uma tarefa."""
		await self.get(tarefa_id)
		return await self.anexos.list_by_tarefa(tarefa_id)

	async def delete_anexo(self, anexo_id: int) -> None:
		"""Função para excluir um anexo pelo ID."""
		if not await self.anexos.delete(anexo_id):
			raise NotFoundError(_ENTITY_ANEXO, anexo_id)
		await self.session.commit()
