from __future__ import annotations

from core.enums import ProjetoStatus, UserRole
from core.exceptions import NotFoundError
from fastapi import HTTPException, status
from modules.projetos.model import Projeto, ProjetoFuncionario
from modules.projetos.repository import (
	RepositorioProjetoFuncionario,
	RepositorioProjeto,
)
from modules.projetos.schema import (
	ProjetoCriar,
	ProjetoFuncionarioCriar,
	ProjetoAtualizar,
)
from sqlalchemy.ext.asyncio import AsyncSession

_ENTITY = 'Projeto'


class ServicoProjeto:
	"""Classe responsável pelas regras de negócio de projeto."""

	def __init__(self, session: AsyncSession):
		"""Função para inicializar a instância com suas dependências."""
		self.session = session
		self.repo = RepositorioProjeto(session)
		self.equipe = RepositorioProjetoFuncionario(session)

	async def criar(self, dados: ProjetoCriar) -> Projeto:
		"""Função para criar um novo registro."""
		projeto = Projeto(**dados.model_dump())
		projeto = await self.repo.adicionar(projeto)
		await self.session.commit()
		return projeto

	async def obter(self, projeto_id: int) -> Projeto:
		"""Função para obter um registro pelo ID."""
		projeto = await self.repo.obter(projeto_id)
		if not projeto:
			raise NotFoundError(_ENTITY, projeto_id)
		return projeto

	async def obter_visible(self, projeto_id: int, usuario_id: int, role: str) -> Projeto:
		"""Função para obter um registro respeitando as permissões do usuário."""
		projeto = await self.obter(projeto_id)
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

	async def listar(self, offset: int, limit: int) -> list[Projeto]:
		"""Função para listar registros."""
		return await self.repo.listar_todos(offset=offset, limit=limit)

	async def listar_filtrados(
		self,
		offset: int,
		limit: int,
		cliente_id: int | None = None,
		status: ProjetoStatus | None = None,
	) -> list[Projeto]:
		"""Função para listar registros aplicando filtros e paginação."""
		return await self.repo.listar_todos(
			offset=offset,
			limit=limit,
			filters={'cliente_id': cliente_id, 'status': status},
		)

	async def listar_visible(
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
			return await self.listar_filtrados(
				offset=offset, limit=limit, cliente_id=cliente_id, status=status
			)
		if role == UserRole.CLIENTE.value:
			return await self.listar_filtrados(
				offset=offset, limit=limit, cliente_id=usuario_id, status=status
			)
		if role == UserRole.FUNCIONARIO.value:
			return await self.repo.listar_for_funcionario(
				funcionario_id=usuario_id,
				offset=offset,
				limit=limit,
				status=status,
			)
		raise HTTPException(
			status_code=status.HTTP_403_FORBIDDEN,
			detail='Acesso negado para projetos',
		)

	async def atualizar(self, projeto_id: int, dados: ProjetoAtualizar) -> Projeto:
		"""Função para atualizar um registro pelo ID."""
		projeto = await self.repo.atualizar(
			projeto_id, dados.model_dump(exclude_none=True)
		)
		if not projeto:
			raise NotFoundError(_ENTITY, projeto_id)
		await self.session.commit()
		return projeto

	async def deletar(self, projeto_id: int) -> None:
		"""Função para excluir um registro pelo ID."""
		if not await self.repo.deletar(projeto_id):
			raise NotFoundError(_ENTITY, projeto_id)
		await self.session.commit()

	async def adicionar_membro(
		self, projeto_id: int, dados: ProjetoFuncionarioCriar
	) -> ProjetoFuncionario:
		"""Função para adicionar um funcionário à equipe do projeto."""
		await self.obter(projeto_id)
		entry = ProjetoFuncionario(
			projeto_id=projeto_id,
			funcionario_id=dados.funcionario_id,
			papel=dados.papel,
		)
		entry = await self.equipe.adicionar(entry)
		await self.session.commit()
		return entry

	async def listar_equipe(self, projeto_id: int) -> list[ProjetoFuncionario]:
		"""Função para listar a equipe de um projeto."""
		await self.obter(projeto_id)
		return await self.equipe.listar_por_projeto(projeto_id)

	async def remover_membro(self, projeto_id: int, funcionario_id: int) -> None:
		"""Função para remover um funcionário da equipe do projeto."""
		await self.obter(projeto_id)
		if not await self.equipe.remove(projeto_id, funcionario_id):
			raise NotFoundError('Membro de projeto', funcionario_id)
		await self.session.commit()
