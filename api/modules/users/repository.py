from core.enums import PapelUsuario, SituacaoUsuario
from db.base_repository import RepositorioBase
from modules.users.model import Admin, Cliente, Funcionario, Usuario
from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession


class RepositorioUsuario(RepositorioBase[Usuario]):
	"""Classe responsável pelo acesso aos dados de usuário."""

	modelo = Usuario

	async def obter_por_email(self, email: str) -> Usuario | None:
		"""Função para buscar um usuário pelo email."""
		consulta = select(Usuario).where(Usuario.email == email)
		resultado = await self.sessao.execute(consulta)
		return resultado.scalar_one_or_none()

	async def listar_filtrados(
		self,
		offset: int,
		limit: int,
		papel: PapelUsuario | None = None,
		status: SituacaoUsuario | None = None,
		busca: str | None = None,
	) -> list[Usuario]:
		"""Função para listar registros aplicando filtros e paginação."""
		consulta = select(Usuario)
		if papel is not None:
			consulta = consulta.where(Usuario.role == papel)
		if status is not None:
			consulta = consulta.where(Usuario.status == status)
		if busca:
			termo = f'%{busca}%'
			consulta = consulta.where(or_(Usuario.nome.ilike(termo), Usuario.email.ilike(termo)))
		consulta = consulta.order_by(Usuario.nome).offset(offset).limit(limit)
		resultado = await self.sessao.execute(consulta)
		return list(resultado.scalars().all())


class RepositorioCliente(RepositorioBase[Cliente]):
	"""Classe responsável pelo acesso aos dados de cliente."""

	modelo = Cliente

	def __init__(self, sessao: AsyncSession):
		"""Função para inicializar a instância com suas dependências."""
		super().__init__(sessao)

	async def obter_por_documento(self, documento: str) -> Cliente | None:
		"""Função para buscar um cliente pelo documento."""
		consulta = select(Cliente).where(Cliente.cnpj_cpf == documento)
		resultado = await self.sessao.execute(consulta)
		return resultado.scalar_one_or_none()


class RepositorioFuncionario(RepositorioBase[Funcionario]):
	"""Classe responsável pelo acesso aos dados de funcionário."""

	modelo = Funcionario


class RepositorioAdmin(RepositorioBase[Admin]):
	"""Classe responsável pelo acesso aos dados de admin."""

	modelo = Admin
