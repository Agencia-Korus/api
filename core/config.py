from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict

from core.constants import (
	JWT_ACCESS_TOKEN_EXPIRE_MIN,
	JWT_DEFAULT_ALGORITHM,
	JWT_REFRESH_TOKEN_EXPIRE_DAYS,
)


class Settings(BaseSettings):
	database_url: str = 'postgres-url-development'
	debug: bool = False
	jwt_secret_key: str = 'secret-key-development'
	jwt_algorithm: str = JWT_DEFAULT_ALGORITHM
	jwt_access_token_expire_minutes: int = JWT_ACCESS_TOKEN_EXPIRE_MIN
	jwt_refresh_token_expire_days: int = JWT_REFRESH_TOKEN_EXPIRE_DAYS
	cors_allow_origins: str = '*'

	model_config = SettingsConfigDict(
		env_file='.env', env_file_encoding='utf-8', extra='ignore'
	)


@lru_cache
def get_settings() -> Settings:
	return Settings()
