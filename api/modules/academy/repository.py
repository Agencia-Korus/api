from db.base_repository import BaseRepository
from modules.academy.model import Academy


class AcademyRepository(BaseRepository[Academy]):
	"""Classe responsável pelo acesso aos dados de conteúdo da Academy."""

	model = Academy
