from db.base_repository import RepositorioBase
from modules.academy.model import Academy


class RepositorioAcademy(RepositorioBase[Academy]):
	"""Classe responsável pelo acesso aos dados de conteúdo da Academy."""

	model = Academy
