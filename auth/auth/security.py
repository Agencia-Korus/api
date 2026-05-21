from datetime import datetime, timedelta, timezone
from typing import Any

from fastapi import HTTPException, status
from jose import JWTError, jwt
from passlib.context import CryptContext

from auth.config import get_settings

_pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')
_settings = get_settings()


CREDENTIALS_EXCEPTION = HTTPException(
	status_code=status.HTTP_401_UNAUTHORIZED,
	detail='Credenciais inválidas',
	headers={'WWW-Authenticate': 'Bearer'},
)

TOKEN_TYPE_ACCESS = 'access'
TOKEN_TYPE_REFRESH = 'refresh'


def hash_password(plain: str) -> str:
	return _pwd_context.hash(plain)


def verify_password(plain: str, hashed: str) -> bool:
	return _pwd_context.verify(plain, hashed)


def _create_token(
	subject: int,
	token_type: str,
	expires_delta: timedelta,
	**extra: Any,
) -> str:
	expire = datetime.now(timezone.utc) + expires_delta
	payload: dict[str, Any] = {
		'sub': str(subject),
		'exp': expire,
		'type': token_type,
		**extra,
	}
	return jwt.encode(
		payload, _settings.jwt_secret_key, algorithm=_settings.jwt_algorithm
	)


def create_access_token(subject: int, role: str) -> str:
	return _create_token(
		subject,
		TOKEN_TYPE_ACCESS,
		timedelta(minutes=_settings.jwt_access_token_expire_minutes),
		role=role,
	)


def create_refresh_token(subject: int) -> str:
	return _create_token(
		subject,
		TOKEN_TYPE_REFRESH,
		timedelta(days=_settings.jwt_refresh_token_expire_days),
	)


def decode_token(token: str, expected_type: str) -> dict[str, Any]:
	try:
		payload = jwt.decode(
			token,
			_settings.jwt_secret_key,
			algorithms=[_settings.jwt_algorithm],
		)
	except JWTError as exc:
		raise CREDENTIALS_EXCEPTION from exc
	if payload.get('type') != expected_type:
		raise CREDENTIALS_EXCEPTION
	return payload
