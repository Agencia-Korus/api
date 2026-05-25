from db.base_repository import RepositorioBase
from modules.lgpd.model import ConsentimentoLgpd


class RepositorioConsentimentoLgpd(RepositorioBase[ConsentimentoLgpd]):
	"""Classe responsável pelo acesso aos dados de consentimento LGPD."""

	model = ConsentimentoLgpd
