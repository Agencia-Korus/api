from __future__ import annotations

from core.enums import PapelUsuario, SituacaoProjeto
from core.exceptions import ErroNaoEncontrado
from fastapi import HTTPException
from fastapi import status as http_status
from modules.projetos.model import Projeto, ProjetoFuncionario
from modules.projetos.repository import (
	RepositorioProjeto,
	RepositorioProjetoFuncionario,
)
from modules.projetos.schema import (
	ProjetoAtualizar,
	ProjetoCriar,
	ProjetoFuncionarioCriar,
)
from sqlalchemy.ext.asyncio import AsyncSession

_ENTIDADE = 'Projeto'


class ServicoProjeto:
	"""Classe responsável pelas regras de negócio de projeto."""

	def __init__(self, sessao: AsyncSession):
		"""Função para inicializar a instância com suas dependências."""
		self.sessao = sessao
		self.repository = RepositorioProjeto(sessao)
		self.equipe = RepositorioProjetoFuncionario(sessao)

	async def criar(self, dados: ProjetoCriar) -> Projeto:
		"""Função para criar um novo registro."""
		projeto = Projeto(**dados.model_dump())
		projeto = await self.repository.adicionar(projeto)
		await self.sessao.commit()
		return projeto

	async def obter(self, projeto_id: int) -> Projeto:
		"""Função para obter um registro pelo ID."""
		projeto = await self.repository.obter(projeto_id)
		if not projeto:
			raise ErroNaoEncontrado(_ENTIDADE, projeto_id)
		return projeto

	async def obter_visivel(self, projeto_id: int, usuario_id: int, papel: str) -> Projeto:
		"""Função para obter um registro respeitando as permissões do usuário."""
		projeto = await self.obter(projeto_id)
		if papel == PapelUsuario.ADMIN.value:
			return projeto
		if papel == PapelUsuario.CLIENTE.value and projeto.cliente_id == usuario_id:
			return projeto
		if papel == PapelUsuario.FUNCIONARIO.value and await self.equipe.contem_membro(
			projeto_id, usuario_id
		):
			return projeto
		raise HTTPException(
			status_code=http_status.HTTP_403_FORBIDDEN,
			detail='Acesso negado para este projeto',
		)

	async def listar(self, offset: int, limit: int) -> list[Projeto]:
		"""Função para listar registros."""
		return await self.repository.listar_todos(offset=offset, limit=limit)

	async def listar_filtrados(
		self,
		offset: int,
		limit: int,
		cliente_id: int | None = None,
		status: SituacaoProjeto | None = None,
	) -> list[Projeto]:
		"""Função para listar registros aplicando filtros e paginação."""
		return await self.repository.listar_todos(
			offset=offset,
			limit=limit,
			filtros={'cliente_id': cliente_id, 'status': status},
		)

	async def listar_visiveis(
		self,
		offset: int,
		limit: int,
		usuario_id: int,
		papel: str,
		cliente_id: int | None = None,
		status: SituacaoProjeto | None = None,
	) -> list[Projeto]:
		"""Função para listar registros visíveis para o usuário autenticado."""
		if papel == PapelUsuario.ADMIN.value:
			return await self.listar_filtrados(
				offset=offset, limit=limit, cliente_id=cliente_id, status=status
			)
		if papel == PapelUsuario.CLIENTE.value:
			return await self.listar_filtrados(
				offset=offset, limit=limit, cliente_id=usuario_id, status=status
			)
		if papel == PapelUsuario.FUNCIONARIO.value:
			return await self.repository.listar_para_funcionario(
				funcionario_id=usuario_id,
				offset=offset,
				limit=limit,
				status=status,
			)
		raise HTTPException(
			status_code=http_status.HTTP_403_FORBIDDEN,
			detail='Acesso negado para projetos',
		)

	async def atualizar(self, projeto_id: int, dados: ProjetoAtualizar) -> Projeto:
		"""Função para atualizar um registro pelo ID."""
		projeto = await self.repository.atualizar(projeto_id, dados.model_dump(exclude_none=True))
		if not projeto:
			raise ErroNaoEncontrado(_ENTIDADE, projeto_id)
		await self.sessao.commit()
		return projeto

	async def deletar(self, projeto_id: int) -> None:
		"""Função para excluir um registro pelo ID."""
		if not await self.repository.deletar(projeto_id):
			raise ErroNaoEncontrado(_ENTIDADE, projeto_id)
		await self.sessao.commit()

	async def adicionar_membro(
		self, projeto_id: int, dados: ProjetoFuncionarioCriar
	) -> ProjetoFuncionario:
		"""Função para adicionar um funcionário à equipe do projeto."""
		await self.obter(projeto_id)
		registro = ProjetoFuncionario(
			projeto_id=projeto_id,
			funcionario_id=dados.funcionario_id,
			papel=dados.papel,
		)
		registro = await self.equipe.adicionar(registro)
		await self.sessao.commit()
		return registro

	async def listar_equipe(self, projeto_id: int) -> list[ProjetoFuncionario]:
		"""Função para listar a equipe de um projeto."""
		await self.obter(projeto_id)
		return await self.equipe.listar_por_projeto(projeto_id)

	async def remover_membro(self, projeto_id: int, funcionario_id: int) -> None:
		"""Função para remover um funcionário da equipe do projeto."""
		await self.obter(projeto_id)
		if not await self.equipe.remover(projeto_id, funcionario_id):
			raise ErroNaoEncontrado('Membro de projeto', funcionario_id)
		await self.sessao.commit()
