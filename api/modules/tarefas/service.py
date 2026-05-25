from __future__ import annotations

from datetime import datetime, timezone

from core.enums import TarefaStatus, UserRole
from core.exceptions import NotFoundError
from fastapi import HTTPException, status
from modules.projetos.model import Projeto, ProjetoFuncionario
from modules.tarefas.model import Anexo, Comentario, Tarefa
from modules.tarefas.repository import (
	RepositorioAnexo,
	RepositorioComentario,
	RepositorioTarefa,
)
from modules.tarefas.schema import (
	AnexoCriar,
	ComentarioCriar,
	TarefaCriar,
	TarefaAtualizar,
)
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

_ENTITY_TAREFA = 'Tarefa'
_ENTITY_COMENTARIO = 'Comentário'
_ENTITY_ANEXO = 'Anexo'


class ServicoTarefa:
	"""Classe responsável pelas regras de negócio de tarefa."""

	def __init__(self, session: AsyncSession):
		"""Função para inicializar a instância com suas dependências."""
		self.session = session
		self.repo = RepositorioTarefa(session)
		self.comentarios = RepositorioComentario(session)
		self.anexos = RepositorioAnexo(session)

	async def criar(self, payload: TarefaCriar) -> Tarefa:
		"""Função para criar um novo registro."""
		tarefa = Tarefa(**payload.model_dump())
		tarefa = await self.repo.adicionar(tarefa)
		await self.session.commit()
		return tarefa

	async def obter(self, tarefa_id: int) -> Tarefa:
		"""Função para obter um registro pelo ID."""
		tarefa = await self.repo.obter(tarefa_id)
		if not tarefa:
			raise NotFoundError(_ENTITY_TAREFA, tarefa_id)
		return tarefa

	async def listar(self, offset: int, limit: int) -> list[Tarefa]:
		"""Função para listar registros."""
		return await self.repo.listar_todos(offset=offset, limit=limit)

	async def listar_por_projeto(self, projeto_id: int) -> list[Tarefa]:
		"""Função para listar registros vinculados a um projeto."""
		return await self.repo.listar_por_projeto(projeto_id)

	async def listar_filtrados(
		self,
		offset: int,
		limit: int,
		projeto_id: int | None = None,
		responsavel_id: int | None = None,
		status: TarefaStatus | None = None,
	) -> list[Tarefa]:
		"""Função para listar registros aplicando filtros e paginação."""
		return await self.repo.listar_filtrados(
			offset=offset,
			limit=limit,
			projeto_id=projeto_id,
			responsavel_id=responsavel_id,
			status=status,
		)

	async def listar_visible(
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
			return await self.listar_filtrados(
				offset=offset,
				limit=limit,
				projeto_id=projeto_id,
				responsavel_id=responsavel_id,
				status=status,
			)
		if role in {UserRole.CLIENTE.value, UserRole.FUNCIONARIO.value}:
			return await self.repo.listar_visible(
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

	async def obter_visible(self, tarefa_id: int, usuario_id: int, role: str) -> Tarefa:
		"""Função para obter um registro respeitando as permissões do usuário."""
		tarefa = await self.obter(tarefa_id)
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
		tarefa = await self.obter(tarefa_id)
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
			projeto = await self.session.obter(Projeto, tarefa.projeto_id)
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

	async def atualizar(self, tarefa_id: int, payload: TarefaAtualizar) -> Tarefa:
		"""Função para atualizar um registro pelo ID."""
		data = payload.model_dump(exclude_none=True)
		if data.get('status') == TarefaStatus.CONCLUIDO:
			data['concluido_em'] = datetime.now(timezone.utc)
		tarefa = await self.repo.atualizar(tarefa_id, data)
		if not tarefa:
			raise NotFoundError(_ENTITY_TAREFA, tarefa_id)
		await self.session.commit()
		return tarefa

	async def deletar(self, tarefa_id: int) -> None:
		"""Função para excluir um registro pelo ID."""
		if not await self.repo.deletar(tarefa_id):
			raise NotFoundError(_ENTITY_TAREFA, tarefa_id)
		await self.session.commit()

	async def adicionar_comentario(
		self, payload: ComentarioCriar, autor_id: int
	) -> Comentario:
		"""Função para adicionar um comentário a uma tarefa."""
		await self.obter(payload.tarefa_id)
		comentario = Comentario(
			tarefa_id=payload.tarefa_id,
			autor_id=autor_id,
			conteudo=payload.conteudo,
		)
		comentario = await self.comentarios.adicionar(comentario)
		await self.session.commit()
		return comentario

	async def listar_comentarios(self, tarefa_id: int) -> list[Comentario]:
		"""Função para listar comentários de uma tarefa."""
		await self.obter(tarefa_id)
		return await self.comentarios.listar_por_tarefa(tarefa_id)

	async def deletar_comentario(self, comentario_id: int) -> None:
		"""Função para excluir um comentário pelo ID."""
		if not await self.comentarios.deletar(comentario_id):
			raise NotFoundError(_ENTITY_COMENTARIO, comentario_id)
		await self.session.commit()

	async def adicionar_anexo(self, payload: AnexoCriar) -> Anexo:
		"""Função para adicionar um anexo a uma tarefa."""
		await self.obter(payload.tarefa_id)
		anexo = Anexo(**payload.model_dump())
		anexo = await self.anexos.adicionar(anexo)
		await self.session.commit()
		return anexo

	async def listar_anexos(self, tarefa_id: int) -> list[Anexo]:
		"""Função para listar anexos de uma tarefa."""
		await self.obter(tarefa_id)
		return await self.anexos.listar_por_tarefa(tarefa_id)

	async def deletar_anexo(self, anexo_id: int) -> None:
		"""Função para excluir um anexo pelo ID."""
		if not await self.anexos.deletar(anexo_id):
			raise NotFoundError(_ENTITY_ANEXO, anexo_id)
		await self.session.commit()
