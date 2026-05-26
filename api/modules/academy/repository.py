from db.base_repository import RepositorioBase
from modules.academy.model import Academia


class RepositorioAcademia(RepositorioBase[Academia]):
	"""Classe responsável pelo acesso aos dados de conteúdo da Academia."""

	modelo = Academia
