from functools import lru_cache
from pathlib import Path

from core.constants import (
	ALGORITMO_PADRAO_JWT,
	DIAS_EXPIRACAO_TOKEN_ATUALIZACAO_JWT,
	MINUTOS_EXPIRACAO_TOKEN_ACESSO_JWT,
)
from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Configuracoes(BaseSettings):
	"""Classe que centraliza as configurações da aplicação."""

	database_url: str = 'database-url'
	debug: bool = False
	jwt_secret_key: str = 'change-me'
	jwt_algorithm: str = ALGORITMO_PADRAO_JWT
	jwt_access_token_expire_minutes: int = MINUTOS_EXPIRACAO_TOKEN_ACESSO_JWT
	jwt_refresh_token_expire_days: int = DIAS_EXPIRACAO_TOKEN_ATUALIZACAO_JWT
	cors_allow_origins: str = '*'
	google_calendar_enabled: bool = False
	google_calendar_id: str | None = None
	google_calendar_api_key: str | None = None
	google_calendar_service_account_file: str | None = None
	google_calendar_service_account_host_file: str | None = None
	google_calendar_service_account_json: str | None = None
	google_calendar_delegated_user: str | None = None
	google_calendar_timezone: str = 'America/Sao_Paulo'
	google_calendar_days_past: int = 7
	google_calendar_days_future: int = 60

	@field_validator('debug', mode='before')
	@classmethod
	def interpretar_debug(cls, valor: object) -> object:
		"""Função para converter o valor de debug recebido por configuração."""
		if isinstance(valor, str) and valor.strip().lower() in {
			'release',
			'production',
			'prod',
		}:
			return False
		return valor

	def caminho_conta_servico_google(self) -> Path | None:
		"""Função para localizar o arquivo de credenciais do Google Calendar."""
		candidatos = (
			self.google_calendar_service_account_host_file,
			self.google_calendar_service_account_file,
			'.env.google-calendar-service-account.json',
		)
		for caminho in candidatos:
			if not caminho:
				continue
			arquivo = Path(caminho)
			if arquivo.is_file():
				return arquivo.resolve()
		return None

	model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8', extra='ignore')


@lru_cache
def obter_configuracoes() -> Configuracoes:
	"""Função para obter as configurações carregadas do ambiente."""
	return Configuracoes()
