from db.base_repository import BaseRepository
from modules.lgpd.model import ConsentimentoLgpd


class ConsentimentoLgpdRepository(BaseRepository[ConsentimentoLgpd]):
	model = ConsentimentoLgpd
