from core.enums import UserRole, UserStatus
from db.base_repository import BaseRepository
from modules.users.model import Admin, Cliente, Funcionario, Usuario
from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession


class UsuarioRepository(BaseRepository[Usuario]):
	model = Usuario

	async def get_by_email(self, email: str) -> Usuario | None:
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
	model = Cliente

	def __init__(self, session: AsyncSession):
		super().__init__(session)

	async def get_by_documento(self, documento: str) -> Cliente | None:
		stmt = select(Cliente).where(Cliente.cnpj_cpf == documento)
		result = await self.session.execute(stmt)
		return result.scalar_one_or_none()


class FuncionarioRepository(BaseRepository[Funcionario]):
	model = Funcionario


class AdminRepository(BaseRepository[Admin]):
	model = Admin
