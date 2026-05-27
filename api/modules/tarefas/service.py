from __future__ import annotations

from datetime import datetime, timezone

from core.enums import PapelUsuario, SituacaoTarefa
from core.exceptions import ErroNaoEncontrado
from fastapi import HTTPException
from fastapi import status as http_status
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
	TarefaAtualizar,
	TarefaCriar,
)
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

_ENTIDADE_TAREFA = 'Tarefa'
_ENTIDADE_COMENTARIO = 'Comentário'
_ENTIDADE_ANEXO = 'Anexo'


class ServicoTarefa:
	"""Classe responsável pelas regras de negócio de tarefa."""

	def __init__(self, sessao: AsyncSession):
		"""Função para inicializar a instância com suas dependências."""
		self.sessao = sessao
		self.repository = RepositorioTarefa(sessao)
		self.comentarios = RepositorioComentario(sessao)
		self.anexos = RepositorioAnexo(sessao)

	async def criar(self, dados: TarefaCriar) -> Tarefa:
		"""Função para criar um novo registro."""
		tarefa = Tarefa(**dados.model_dump())
		tarefa = await self.repository.adicionar(tarefa)
		await self.sessao.commit()
		return tarefa

	async def obter(self, tarefa_id: int) -> Tarefa:
		"""Função para obter um registro pelo ID."""
		tarefa = await self.repository.obter(tarefa_id)
		if not tarefa:
			raise ErroNaoEncontrado(_ENTIDADE_TAREFA, tarefa_id)
		return tarefa

	async def listar(self, offset: int, limit: int) -> list[Tarefa]:
		"""Função para listar registros."""
		return await self.repository.listar_todos(offset=offset, limit=limit)

	async def listar_por_projeto(self, projeto_id: int) -> list[Tarefa]:
		"""Função para listar registros vinculados a um projeto."""
		return await self.repository.listar_por_projeto(projeto_id)

	async def listar_filtrados(
		self,
		offset: int,
		limit: int,
		projeto_id: int | None = None,
		responsavel_id: int | None = None,
		status: SituacaoTarefa | None = None,
	) -> list[Tarefa]:
		"""Função para listar registros aplicando filtros e paginação."""
		return await self.repository.listar_filtrados(
			offset=offset,
			limit=limit,
			projeto_id=projeto_id,
			responsavel_id=responsavel_id,
			status=status,
		)

	async def listar_visiveis(
		self,
		offset: int,
		limit: int,
		usuario_id: int,
		papel: str,
		projeto_id: int | None = None,
		responsavel_id: int | None = None,
		status: SituacaoTarefa | None = None,
	) -> list[Tarefa]:
		"""Função para listar registros visíveis para o usuário autenticado."""
		if papel == PapelUsuario.ADMIN.value:
			return await self.listar_filtrados(
				offset=offset,
				limit=limit,
				projeto_id=projeto_id,
				responsavel_id=responsavel_id,
				status=status,
			)
		if papel in {PapelUsuario.CLIENTE.value, PapelUsuario.FUNCIONARIO.value}:
			return await self.repository.listar_visiveis(
				usuario_id=usuario_id,
				papel=papel,
				offset=offset,
				limit=limit,
				projeto_id=projeto_id,
				responsavel_id=responsavel_id,
				status=status,
			)
		raise HTTPException(
			status_code=http_status.HTTP_403_FORBIDDEN,
			detail='Acesso negado para tarefas',
		)

	async def obter_visivel(self, tarefa_id: int, usuario_id: int, papel: str) -> Tarefa:
		"""Função para obter um registro respeitando as permissões do usuário."""
		tarefa = await self.obter(tarefa_id)
		if papel == PapelUsuario.ADMIN.value or await self._pode_acessar_tarefa(
			tarefa, usuario_id, papel
		):
			return tarefa
		raise HTTPException(
			status_code=http_status.HTTP_403_FORBIDDEN,
			detail='Acesso negado para esta tarefa',
		)

	async def garantir_permissao_gerenciar_tarefa(
		self, tarefa_id: int, usuario_id: int, papel: str
	) -> Tarefa:
		"""Função para validar se o usuário pode gerenciar uma tarefa."""
		tarefa = await self.obter(tarefa_id)
		if papel == PapelUsuario.ADMIN.value:
			return tarefa
		if papel == PapelUsuario.FUNCIONARIO.value and await self._funcionario_envolvido(
			tarefa, usuario_id
		):
			return tarefa
		raise HTTPException(
			status_code=http_status.HTTP_403_FORBIDDEN,
			detail='Apenas admin ou funcionário envolvido pode alterar esta tarefa',
		)

	async def _pode_acessar_tarefa(self, tarefa: Tarefa, usuario_id: int, papel: str) -> bool:
		"""Função interna para validar acesso a uma tarefa."""
		if papel == PapelUsuario.CLIENTE.value:
			projeto = await self.sessao.get(Projeto, tarefa.projeto_id)
			return bool(projeto and projeto.cliente_id == usuario_id)
		if papel == PapelUsuario.FUNCIONARIO.value:
			return await self._funcionario_envolvido(tarefa, usuario_id)
		return False

	async def _funcionario_envolvido(self, tarefa: Tarefa, funcionario_id: int) -> bool:
		"""Função interna para verificar vínculo do funcionário com a tarefa."""
		if tarefa.responsavel_id == funcionario_id:
			return True
		consulta = select(ProjetoFuncionario).where(
			ProjetoFuncionario.projeto_id == tarefa.projeto_id,
			ProjetoFuncionario.funcionario_id == funcionario_id,
		)
		resultado = await self.sessao.execute(consulta)
		return resultado.scalar_one_or_none() is not None

	async def atualizar(self, tarefa_id: int, dados: TarefaAtualizar) -> Tarefa:
		"""Função para atualizar um registro pelo ID."""
		dados_atualizacao = dados.model_dump(exclude_none=True)
		if dados_atualizacao.get('status') == SituacaoTarefa.CONCLUIDO:
			dados_atualizacao['concluido_em'] = datetime.now(timezone.utc)
		tarefa = await self.repository.atualizar(tarefa_id, dados_atualizacao)
		if not tarefa:
			raise ErroNaoEncontrado(_ENTIDADE_TAREFA, tarefa_id)
		await self.sessao.commit()
		return tarefa

	async def deletar(self, tarefa_id: int) -> None:
		"""Função para excluir um registro pelo ID."""
		if not await self.repository.deletar(tarefa_id):
			raise ErroNaoEncontrado(_ENTIDADE_TAREFA, tarefa_id)
		await self.sessao.commit()

	async def adicionar_comentario(self, dados: ComentarioCriar, autor_id: int) -> Comentario:
		"""Função para adicionar um comentário a uma tarefa."""
		await self.obter(dados.tarefa_id)
		comentario = Comentario(
			tarefa_id=dados.tarefa_id,
			autor_id=autor_id,
			conteudo=dados.conteudo,
		)
		comentario = await self.comentarios.adicionar(comentario)
		await self.sessao.commit()
		return comentario

	async def listar_comentarios(self, tarefa_id: int) -> list[Comentario]:
		"""Função para listar comentários de uma tarefa."""
		await self.obter(tarefa_id)
		return await self.comentarios.listar_por_tarefa(tarefa_id)

	async def deletar_comentario(self, comentario_id: int) -> None:
		"""Função para excluir um comentário pelo ID."""
		if not await self.comentarios.deletar(comentario_id):
			raise ErroNaoEncontrado(_ENTIDADE_COMENTARIO, comentario_id)
		await self.sessao.commit()

	async def adicionar_anexo(self, dados: AnexoCriar) -> Anexo:
		"""Função para adicionar um anexo a uma tarefa."""
		await self.obter(dados.tarefa_id)
		anexo = Anexo(**dados.model_dump())
		anexo = await self.anexos.adicionar(anexo)
		await self.sessao.commit()
		return anexo

	async def listar_anexos(self, tarefa_id: int) -> list[Anexo]:
		"""Função para listar anexos de uma tarefa."""
		await self.obter(tarefa_id)
		return await self.anexos.listar_por_tarefa(tarefa_id)

	async def deletar_anexo(self, anexo_id: int) -> None:
		"""Função para excluir um anexo pelo ID."""
		if not await self.anexos.deletar(anexo_id):
			raise ErroNaoEncontrado(_ENTIDADE_ANEXO, anexo_id)
		await self.sessao.commit()
