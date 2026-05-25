from functools import lru_cache
from pathlib import Path

from core.constants import (
	JWT_ACCESS_TOKEN_EXPIRE_MIN,
	JWT_DEFAULT_ALGORITHM,
	JWT_REFRESH_TOKEN_EXPIRE_DAYS,
)
from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
	"""Classe que centraliza as configurações da aplicação."""

	database_url: str = 'database-url'
	debug: bool = False
	jwt_secret_key: str = 'change-me'
	jwt_algorithm: str = JWT_DEFAULT_ALGORITHM
	jwt_access_token_expire_minutes: int = JWT_ACCESS_TOKEN_EXPIRE_MIN
	jwt_refresh_token_expire_days: int = JWT_REFRESH_TOKEN_EXPIRE_DAYS
	cors_allow_origins: str = '*'
	auth_token_url: str = 'http://127.0.0.1:8001/auth/login'
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
	def parse_debug(cls, value: object) -> object:
		"""Função para converter o valor de debug recebido por configuração."""
		if isinstance(value, str) and value.strip().lower() in {
			'release',
			'production',
			'prod',
		}:
			return False
		return value

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

	model_config = SettingsConfigDict(
		env_file='.env', env_file_encoding='utf-8', extra='ignore'
	)


@lru_cache
def get_settings() -> Settings:
	"""Função para obter as configurações carregadas do ambiente."""
	return Settings()
