from __future__ import annotations

from core.enums import ProjetoStatus, UserRole
from core.exceptions import NotFoundError
from fastapi import HTTPException, status
from modules.projetos.model import Projeto, ProjetoFuncionario
from modules.projetos.repository import (
	ProjetoFuncionarioRepository,
	ProjetoRepository,
)
from modules.projetos.schema import (
	ProjetoCreate,
	ProjetoFuncionarioCreate,
	ProjetoUpdate,
)
from sqlalchemy.ext.asyncio import AsyncSession

_ENTITY = 'Projeto'


class ProjetoService:
	"""Classe responsável pelas regras de negócio de projeto."""

	def __init__(self, session: AsyncSession):
		"""Função para inicializar a instância com suas dependências."""
		self.session = session
		self.repo = ProjetoRepository(session)
		self.equipe = ProjetoFuncionarioRepository(session)

	async def create(self, payload: ProjetoCreate) -> Projeto:
		"""Função para criar um novo registro."""
		projeto = Projeto(**payload.model_dump())
		projeto = await self.repo.add(projeto)
		await self.session.commit()
		return projeto

	async def get(self, projeto_id: int) -> Projeto:
		"""Função para obter um registro pelo ID."""
		projeto = await self.repo.get(projeto_id)
		if not projeto:
			raise NotFoundError(_ENTITY, projeto_id)
		return projeto

	async def get_visible(self, projeto_id: int, usuario_id: int, role: str) -> Projeto:
		"""Função para obter um registro respeitando as permissões do usuário."""
		projeto = await self.get(projeto_id)
		if role == UserRole.ADMIN.value:
			return projeto
		if role == UserRole.CLIENTE.value and projeto.cliente_id == usuario_id:
			return projeto
		if role == UserRole.FUNCIONARIO.value and await self.equipe.has_member(
			projeto_id, usuario_id
		):
			return projeto
		raise HTTPException(
			status_code=status.HTTP_403_FORBIDDEN,
			detail='Acesso negado para este projeto',
		)

	async def list(self, offset: int, limit: int) -> list[Projeto]:
		"""Função para listar registros."""
		return await self.repo.list_all(offset=offset, limit=limit)

	async def list_filtered(
		self,
		offset: int,
		limit: int,
		cliente_id: int | None = None,
		status: ProjetoStatus | None = None,
	) -> list[Projeto]:
		"""Função para listar registros aplicando filtros e paginação."""
		return await self.repo.list_all(
			offset=offset,
			limit=limit,
			filters={'cliente_id': cliente_id, 'status': status},
		)

	async def list_visible(
		self,
		offset: int,
		limit: int,
		usuario_id: int,
		role: str,
		cliente_id: int | None = None,
		status: ProjetoStatus | None = None,
	) -> list[Projeto]:
		"""Função para listar registros visíveis para o usuário autenticado."""
		if role == UserRole.ADMIN.value:
			return await self.list_filtered(
				offset=offset, limit=limit, cliente_id=cliente_id, status=status
			)
		if role == UserRole.CLIENTE.value:
			return await self.list_filtered(
				offset=offset, limit=limit, cliente_id=usuario_id, status=status
			)
		if role == UserRole.FUNCIONARIO.value:
			return await self.repo.list_for_funcionario(
				funcionario_id=usuario_id,
				offset=offset,
				limit=limit,
				status=status,
			)
		raise HTTPException(
			status_code=status.HTTP_403_FORBIDDEN,
			detail='Acesso negado para projetos',
		)

	async def update(self, projeto_id: int, payload: ProjetoUpdate) -> Projeto:
		"""Função para atualizar um registro pelo ID."""
		projeto = await self.repo.update(
			projeto_id, payload.model_dump(exclude_none=True)
		)
		if not projeto:
			raise NotFoundError(_ENTITY, projeto_id)
		await self.session.commit()
		return projeto

	async def delete(self, projeto_id: int) -> None:
		"""Função para excluir um registro pelo ID."""
		if not await self.repo.delete(projeto_id):
			raise NotFoundError(_ENTITY, projeto_id)
		await self.session.commit()

	async def adicionar_membro(
		self, projeto_id: int, payload: ProjetoFuncionarioCreate
	) -> ProjetoFuncionario:
		"""Função para adicionar um funcionário à equipe do projeto."""
		await self.get(projeto_id)
		entry = ProjetoFuncionario(
			projeto_id=projeto_id,
			funcionario_id=payload.funcionario_id,
			papel=payload.papel,
		)
		entry = await self.equipe.add(entry)
		await self.session.commit()
		return entry

	async def listar_equipe(self, projeto_id: int) -> list[ProjetoFuncionario]:
		"""Função para listar a equipe de um projeto."""
		await self.get(projeto_id)
		return await self.equipe.list_by_projeto(projeto_id)

	async def remover_membro(self, projeto_id: int, funcionario_id: int) -> None:
		"""Função para remover um funcionário da equipe do projeto."""
		await self.get(projeto_id)
		if not await self.equipe.remove(projeto_id, funcionario_id):
			raise NotFoundError('Membro de projeto', funcionario_id)
		await self.session.commit()
