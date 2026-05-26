from __future__ import annotations

from core.enums import PapelUsuario, SituacaoUsuario
from core.exceptions import ErroConflito, ErroNaoEncontrado, ErroRequisicaoInvalida
from core.password import gerar_hash_senha
from modules.users.model import Admin, Cliente, Funcionario, Usuario
from modules.users.repository import (
	RepositorioAdmin,
	RepositorioCliente,
	RepositorioFuncionario,
	RepositorioUsuario,
)
from modules.users.schema import UsuarioAtualizar, UsuarioCriar, UsuarioRegistrar
from sqlalchemy.ext.asyncio import AsyncSession

_ENTIDADE = 'Usuário'


class ServicoUsuario:
	"""Classe responsável pelas regras de negócio de usuário."""

	def __init__(self, sessao: AsyncSession):
		"""Função para inicializar a instância com suas dependências."""
		self.sessao = sessao
		self.usuarios = RepositorioUsuario(sessao)
		self.clientes = RepositorioCliente(sessao)
		self.funcionarios = RepositorioFuncionario(sessao)
		self.admins = RepositorioAdmin(sessao)

	async def criar(self, dados: UsuarioCriar) -> Usuario:
		"""Função para criar um novo registro."""
		if await self.usuarios.obter_por_email(dados.email):
			raise ErroConflito('Email já cadastrado')

		usuario = Usuario(
			nome=dados.nome,
			email=dados.email,
			senha_hash=gerar_hash_senha(dados.senha),
			role=dados.role,
			telefone=dados.telefone,
			avatar=dados.avatar,
			status=dados.status,
		)
		usuario = await self.usuarios.adicionar(usuario)
		if dados.role == PapelUsuario.CLIENTE:
			dados_cliente = dados.cliente
			cliente = Cliente(
				id=usuario.id,
				razao_social=dados_cliente.razao_social
				if dados_cliente
				else usuario.nome,
				cnpj_cpf=dados_cliente.cnpj_cpf
				if dados_cliente
				else f'api-{usuario.id}',
				segmento=dados_cliente.segmento if dados_cliente else None,
			)
			await self.clientes.adicionar(cliente)

		if dados.role == PapelUsuario.FUNCIONARIO:
			dados_funcionario = dados.funcionario
			funcionario = Funcionario(
				id=usuario.id,
				cargo=dados_funcionario.cargo if dados_funcionario else 'Funcionário',
				especialidade=dados_funcionario.especialidade
				if dados_funcionario
				else None,
			)
			await self.funcionarios.adicionar(funcionario)

		if dados.role == PapelUsuario.ADMIN:
			admin = Admin(
				id=usuario.id,
				nivel_acesso=dados.admin.nivel_acesso if dados.admin else 1,
			)
			await self.admins.adicionar(admin)

		await self.sessao.commit()
		await self.sessao.refresh(usuario)
		return usuario

	async def obter(self, usuario_id: int) -> Usuario:
		"""Função para obter um registro pelo ID."""
		usuario = await self.usuarios.obter(usuario_id)
		if not usuario:
			raise ErroNaoEncontrado(_ENTIDADE, usuario_id)
		return usuario

	async def listar(self, offset: int, limit: int) -> list[Usuario]:
		"""Função para listar registros."""
		return await self.usuarios.listar_todos(offset=offset, limit=limit)

	async def listar_filtrados(
		self,
		offset: int,
		limit: int,
		papel: PapelUsuario | None = None,
		status: SituacaoUsuario | None = None,
		busca: str | None = None,
	) -> list[Usuario]:
		"""Função para listar registros aplicando filtros e paginação."""
		return await self.usuarios.listar_filtrados(
			offset=offset, limit=limit, papel=papel, status=status, busca=busca
		)

	async def atualizar(self, usuario_id: int, dados: UsuarioAtualizar) -> Usuario:
		"""Função para atualizar um registro pelo ID."""
		usuario = await self.usuarios.atualizar(
			usuario_id, dados.model_dump(exclude_none=True)
		)
		if not usuario:
			raise ErroNaoEncontrado(_ENTIDADE, usuario_id)
		await self.sessao.commit()
		return usuario

	async def deletar(self, usuario_id: int) -> None:
		"""Função para excluir um registro pelo ID."""
		removido = await self.usuarios.deletar(usuario_id)
		if not removido:
			raise ErroNaoEncontrado(_ENTIDADE, usuario_id)
		await self.sessao.commit()

	async def registrar(self, dados: UsuarioRegistrar) -> Usuario:
		"""Função para registrar um novo usuário."""
		if dados.role == PapelUsuario.ADMIN:
			raise ErroRequisicaoInvalida(
				'Auto-cadastro como admin não é pertmitido. '
				'Apenas admins podem promover usuários'
			)
		dados_criacao = UsuarioCriar(
			nome=dados.nome,
			email=dados.email,
			senha=dados.senha,
			role=dados.role,
			telefone=dados.telefone,
			avatar=dados.avatar,
			status=SituacaoUsuario.PENDENTE,
			cliente=dados.cliente,
			funcionario=dados.funcionario,
		)
		return await self.criar(dados_criacao)

	async def aprovar(self, usuario_id: int) -> Usuario:
		"""Função para aprovar o cadastro de um usuário."""
		usuario = await self.obter(usuario_id)
		if usuario is None:
			raise ErroNaoEncontrado(_ENTIDADE, usuario_id)
		if usuario.status == SituacaoUsuario.ATIVO:
			return usuario
		usuario_atualizado = await self.usuarios.atualizar(
			usuario_id, {'status': SituacaoUsuario.ATIVO}
		)
		if usuario_atualizado is None:
			raise ErroNaoEncontrado(_ENTIDADE, usuario_id)
		await self.sessao.commit()
		return usuario_atualizado
