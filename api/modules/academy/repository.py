from db.base_repository import BaseRepository
from modules.academy.model import Academy


class AcademyRepository(BaseRepository[Academy]):
	model = Academy
