from __future__ import annotations

from core.enums import UserRole, UserStatus
from core.exceptions import BadRequestError, ConflictError, NotFoundError
from core.password import hash_password
from modules.users.model import Admin, Cliente, Funcionario, Usuario
from modules.users.repository import (
	RepositorioAdmin,
	RepositorioCliente,
	RepositorioFuncionario,
	RepositorioUsuario,
)
from modules.users.schema import UsuarioCriar, UsuarioRegistrar, UsuarioAtualizar
from sqlalchemy.ext.asyncio import AsyncSession

_ENTITY = 'Usuário'


class ServicoUsuario:
	"""Classe responsável pelas regras de negócio de usuário."""

	def __init__(self, session: AsyncSession):
		"""Função para inicializar a instância com suas dependências."""
		self.session = session
		self.usuarios = RepositorioUsuario(session)
		self.clientes = RepositorioCliente(session)
		self.funcionarios = RepositorioFuncionario(session)
		self.admins = RepositorioAdmin(session)

	async def criar(self, dados: UsuarioCriar) -> Usuario:
		"""Função para criar um novo registro."""
		if await self.usuarios.obter_por_email(dados.email):
			raise ConflictError('Email já cadastrado')

		usuario = Usuario(
			nome=dados.nome,
			email=dados.email,
			senha_hash=hash_password(dados.senha),
			role=dados.role,
			telefone=dados.telefone,
			avatar=dados.avatar,
			status=dados.status,
		)
		usuario = await self.usuarios.adicionar(usuario)
		if dados.role == UserRole.CLIENTE:
			cliente_payload = dados.cliente
			cliente = Cliente(
				id=usuario.id,
				razao_social=cliente_payload.razao_social
				if cliente_payload
				else usuario.nome,
				cnpj_cpf=cliente_payload.cnpj_cpf
				if cliente_payload
				else f'api-{usuario.id}',
				segmento=cliente_payload.segmento if cliente_payload else None,
			)
			await self.clientes.adicionar(cliente)

		if dados.role == UserRole.FUNCIONARIO:
			funcionario_payload = dados.funcionario
			funcionario = Funcionario(
				id=usuario.id,
				cargo=funcionario_payload.cargo
				if funcionario_payload
				else 'Funcionário',
				especialidade=funcionario_payload.especialidade
				if funcionario_payload
				else None,
			)
			await self.funcionarios.adicionar(funcionario)

		if dados.role == UserRole.ADMIN:
			admin = Admin(
				id=usuario.id,
				nivel_acesso=dados.admin.nivel_acesso if dados.admin else 1,
			)
			await self.admins.adicionar(admin)

		await self.session.commit()
		await self.session.refresh(usuario)
		return usuario

	async def obter(self, usuario_id: int) -> Usuario:
		"""Função para obter um registro pelo ID."""
		usuario = await self.usuarios.obter(usuario_id)
		if not usuario:
			raise NotFoundError(_ENTITY, usuario_id)
		return usuario

	async def listar(self, offset: int, limit: int) -> list[Usuario]:
		"""Função para listar registros."""
		return await self.usuarios.listar_todos(offset=offset, limit=limit)

	async def listar_filtrados(
		self,
		offset: int,
		limit: int,
		role: UserRole | None = None,
		status: UserStatus | None = None,
		search: str | None = None,
	) -> list[Usuario]:
		"""Função para listar registros aplicando filtros e paginação."""
		return await self.usuarios.listar_filtrados(
			offset=offset, limit=limit, role=role, status=status, search=search
		)

	async def atualizar(self, usuario_id: int, dados: UsuarioAtualizar) -> Usuario:
		"""Função para atualizar um registro pelo ID."""
		usuario = await self.usuarios.atualizar(
			usuario_id, dados.model_dump(exclude_none=True)
		)
		if not usuario:
			raise NotFoundError(_ENTITY, usuario_id)
		await self.session.commit()
		return usuario

	async def deletar(self, usuario_id: int) -> None:
		"""Função para excluir um registro pelo ID."""
		is_deleted = await self.usuarios.deletar(usuario_id)
		if not is_deleted:
			raise NotFoundError(_ENTITY, usuario_id)
		await self.session.commit()

	async def registrar(self, dados: UsuarioRegistrar) -> Usuario:
		"""Função para registrar um novo usuário."""
		if dados.role == UserRole.ADMIN:
			raise BadRequestError(
				'Auto-cadastro como admin não é pertmitido. '
				'Apenas admins podem promover usuários'
			)
		create_payload = UsuarioCriar(
			nome=dados.nome,
			email=dados.email,
			senha=dados.senha,
			role=dados.role,
			telefone=dados.telefone,
			avatar=dados.avatar,
			status=UserStatus.PENDENTE,
			cliente=dados.cliente,
			funcionario=dados.funcionario,
		)
		return await self.criar(create_payload)

	async def aprovar(self, usuario_id: int) -> Usuario:
		"""Função para aprovar o cadastro de um usuário."""
		usuario = await self.obter(usuario_id)
		if usuario is None:
			raise NotFoundError(_ENTITY, usuario_id)
		if usuario.status == UserStatus.ATIVO:
			return usuario
		usuario_updated = await self.usuarios.atualizar(
			usuario_id, {'status': UserStatus.ATIVO}
		)
		if usuario_updated is None:
			raise NotFoundError(_ENTITY, usuario_id)
		await self.session.commit()
		return usuario_updated
