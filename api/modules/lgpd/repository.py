from db.base_repository import BaseRepository
from modules.lgpd.model import ConsentimentoLgpd


class ConsentimentoLgpdRepository(BaseRepository[ConsentimentoLgpd]):
	"""Classe responsável pelo acesso aos dados de consentimento LGPD."""

	model = ConsentimentoLgpd
