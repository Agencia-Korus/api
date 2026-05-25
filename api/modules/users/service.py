from __future__ import annotations

from core.enums import UserRole, UserStatus
from core.exceptions import BadRequestError, ConflictError, NotFoundError
from core.password import hash_password
from modules.users.model import Admin, Cliente, Funcionario, Usuario
from modules.users.repository import (
	AdminRepository,
	ClienteRepository,
	FuncionarioRepository,
	UsuarioRepository,
)
from modules.users.schema import UsuarioCreate, UsuarioRegister, UsuarioUpdate
from sqlalchemy.ext.asyncio import AsyncSession

_ENTITY = 'Usuário'


class UsuarioService:
	"""Classe responsável pelas regras de negócio de usuário."""

	def __init__(self, session: AsyncSession):
		"""Função para inicializar a instância com suas dependências."""
		self.session = session
		self.usuarios = UsuarioRepository(session)
		self.clientes = ClienteRepository(session)
		self.funcionarios = FuncionarioRepository(session)
		self.admins = AdminRepository(session)

	async def create(self, payload: UsuarioCreate) -> Usuario:
		"""Função para criar um novo registro."""
		if await self.usuarios.get_by_email(payload.email):
			raise ConflictError('Email já cadastrado')

		usuario = Usuario(
			nome=payload.nome,
			email=payload.email,
			senha_hash=hash_password(payload.senha),
			role=payload.role,
			telefone=payload.telefone,
			avatar=payload.avatar,
			status=payload.status,
		)
		usuario = await self.usuarios.add(usuario)
		if payload.role == UserRole.CLIENTE:
			cliente_payload = payload.cliente
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
			await self.clientes.add(cliente)

		if payload.role == UserRole.FUNCIONARIO:
			funcionario_payload = payload.funcionario
			funcionario = Funcionario(
				id=usuario.id,
				cargo=funcionario_payload.cargo
				if funcionario_payload
				else 'Funcionário',
				especialidade=funcionario_payload.especialidade
				if funcionario_payload
				else None,
			)
			await self.funcionarios.add(funcionario)

		if payload.role == UserRole.ADMIN:
			admin = Admin(
				id=usuario.id,
				nivel_acesso=payload.admin.nivel_acesso if payload.admin else 1,
			)
			await self.admins.add(admin)

		await self.session.commit()
		await self.session.refresh(usuario)
		return usuario

	async def get(self, usuario_id: int) -> Usuario:
		"""Função para obter um registro pelo ID."""
		usuario = await self.usuarios.get(usuario_id)
		if not usuario:
			raise NotFoundError(_ENTITY, usuario_id)
		return usuario

	async def list(self, offset: int, limit: int) -> list[Usuario]:
		"""Função para listar registros."""
		return await self.usuarios.list_all(offset=offset, limit=limit)

	async def list_filtered(
		self,
		offset: int,
		limit: int,
		role: UserRole | None = None,
		status: UserStatus | None = None,
		search: str | None = None,
	) -> list[Usuario]:
		"""Função para listar registros aplicando filtros e paginação."""
		return await self.usuarios.list_filtered(
			offset=offset, limit=limit, role=role, status=status, search=search
		)

	async def update(self, usuario_id: int, payload: UsuarioUpdate) -> Usuario:
		"""Função para atualizar um registro pelo ID."""
		usuario = await self.usuarios.update(
			usuario_id, payload.model_dump(exclude_none=True)
		)
		if not usuario:
			raise NotFoundError(_ENTITY, usuario_id)
		await self.session.commit()
		return usuario

	async def delete(self, usuario_id: int) -> None:
		"""Função para excluir um registro pelo ID."""
		is_deleted = await self.usuarios.delete(usuario_id)
		if not is_deleted:
			raise NotFoundError(_ENTITY, usuario_id)
		await self.session.commit()

	async def register(self, payload: UsuarioRegister) -> Usuario:
		"""Função para registrar um novo usuário."""
		if payload.role == UserRole.ADMIN:
			raise BadRequestError(
				'Auto-cadastro como admin não é pertmitido. '
				'Apenas admins podem promover usuários'
			)
		create_payload = UsuarioCreate(
			nome=payload.nome,
			email=payload.email,
			senha=payload.senha,
			role=payload.role,
			telefone=payload.telefone,
			avatar=payload.avatar,
			status=UserStatus.PENDENTE,
			cliente=payload.cliente,
			funcionario=payload.funcionario,
		)
		return await self.create(create_payload)

	async def approve(self, usuario_id: int) -> Usuario:
		"""Função para aprovar o cadastro de um usuário."""
		usuario = await self.get(usuario_id)
		if usuario is None:
			raise NotFoundError(_ENTITY, usuario_id)
		if usuario.status == UserStatus.ATIVO:
			return usuario
		usuario_updated = await self.usuarios.update(
			usuario_id, {'status': UserStatus.ATIVO}
		)
		if usuario_updated is None:
			raise NotFoundError(_ENTITY, usuario_id)
		await self.session.commit()
		return usuario_updated
