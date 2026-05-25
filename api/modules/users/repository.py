from core.enums import UserRole, UserStatus
from db.base_repository import BaseRepository
from modules.users.model import Admin, Cliente, Funcionario, Usuario
from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession


class UsuarioRepository(BaseRepository[Usuario]):
	"""Classe responsável pelo acesso aos dados de usuário."""

	model = Usuario

	async def get_by_email(self, email: str) -> Usuario | None:
		"""Função para buscar um usuário pelo email."""
		stmt = select(Usuario).where(Usuario.email == email)
		result = await self.session.execute(stmt)
		return result.scalar_one_or_none()

	async def list_filtered(
		self,
		offset: int,
		limit: int,
		role: UserRole | None = None,
		status: UserStatus | None = None,
		search: str | None = None,
	) -> list[Usuario]:
		"""Função para listar registros aplicando filtros e paginação."""
		stmt = select(Usuario)
		if role is not None:
			stmt = stmt.where(Usuario.role == role)
		if status is not None:
			stmt = stmt.where(Usuario.status == status)
		if search:
			term = f'%{search}%'
			stmt = stmt.where(or_(Usuario.nome.ilike(term), Usuario.email.ilike(term)))
		stmt = stmt.order_by(Usuario.nome).offset(offset).limit(limit)
		result = await self.session.execute(stmt)
		return list(result.scalars().all())


class ClienteRepository(BaseRepository[Cliente]):
	"""Classe responsável pelo acesso aos dados de cliente."""

	model = Cliente

	def __init__(self, session: AsyncSession):
		"""Função para inicializar a instância com suas dependências."""
		super().__init__(session)

	async def get_by_documento(self, documento: str) -> Cliente | None:
		"""Função para buscar um cliente pelo documento."""
		stmt = select(Cliente).where(Cliente.cnpj_cpf == documento)
		result = await self.session.execute(stmt)
		return result.scalar_one_or_none()


class FuncionarioRepository(BaseRepository[Funcionario]):
	"""Classe responsável pelo acesso aos dados de funcionário."""

	model = Funcionario


class AdminRepository(BaseRepository[Admin]):
	"""Classe responsável pelo acesso aos dados de admin."""

	model = Admin
