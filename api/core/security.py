from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Annotated, Any

from core.config import get_settings
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt

settings = get_settings()

oauth2_scheme = OAuth2PasswordBearer(
	tokenUrl='/api/v1/auth/login',
	auto_error=False,
)

CREDENTIALS_EXCEPTION = HTTPException(
	status_code=status.HTTP_401_UNAUTHORIZED,
	detail='Credenciais inválidas',
	headers={'WWW-Authenticate': 'Bearer'},
)


@dataclass(frozen=True)
class CurrentUser:
	"""Classe que representa o usuário autenticado extraído do token."""

	id: int
	role: str


def create_access_token(subject: str | int, extra: dict[str, Any] | None = None) -> str:
	"""Função para criar um token JWT de acesso."""
	expire = datetime.now(timezone.utc) + timedelta(
		minutes=settings.jwt_access_token_expire_minutes
	)
	payload: dict[str, Any] = {'sub': str(subject), 'exp': expire, 'type': 'access'}
	if extra:
		payload.update(extra)
	return jwt.encode(
		payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm
	)


def create_refresh_token(subject: str | int) -> str:
	"""Função para criar um token JWT de renovação."""
	expire = datetime.now(timezone.utc) + timedelta(
		days=settings.jwt_refresh_token_expire_days
	)
	payload = {'sub': str(subject), 'exp': expire, 'type': 'refresh'}
	return jwt.encode(
		payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm
	)


def decode_token(token: str) -> dict[str, Any]:
	"""Função para decodificar e validar um token JWT."""
	try:
		return jwt.decode(
			token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm]
		)
	except JWTError as exc:
		raise CREDENTIALS_EXCEPTION from exc


def get_current_user_id(token: Annotated[str | None, Depends(oauth2_scheme)]) -> int:
	"""Função para obter o ID do usuário autenticado."""
	if not token:
		raise CREDENTIALS_EXCEPTION
	payload = decode_token(token)
	subject = payload.get('sub')
	if not subject:
		raise CREDENTIALS_EXCEPTION
	return int(subject)


def get_current_user(
	token: Annotated[str | None, Depends(oauth2_scheme)],
) -> CurrentUser:
	"""Função para obter os dados do usuário autenticado."""
	if not token:
		raise CREDENTIALS_EXCEPTION
	payload = decode_token(token)
	subject = payload.get('sub')
	role = payload.get('role')
	if not subject or not role:
		raise CREDENTIALS_EXCEPTION
	return CurrentUser(id=int(subject), role=str(role))


def require_role(*allowed_roles: str):
	"""Função para exigir perfis específicos de acesso."""

	def _checker(token: Annotated[str | None, Depends(oauth2_scheme)]) -> int:
		"""Função interna para validar o perfil do token recebido."""
		if not token:
			raise CREDENTIALS_EXCEPTION
		payload = decode_token(token)
		role = payload.get('role')
		if role not in allowed_roles:
			raise HTTPException(
				status_code=status.HTTP_403_FORBIDDEN,
				detail='Acesso negado para este recurso',
			)
		return int(payload['sub'])

	return _checker
