from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Annotated, Any

from core.config import obter_configuracoes
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt

configuracoes = obter_configuracoes()

esquema_bearer = HTTPBearer(auto_error=False)

EXCECAO_CREDENCIAIS = HTTPException(
	status_code=status.HTTP_401_UNAUTHORIZED,
	detail='Credenciais inválidas',
	headers={'WWW-Authenticate': 'Bearer'},
)


@dataclass(frozen=True)
class UsuarioAtual:
	"""Classe que representa o usuário autenticado extraído do token."""

	id: int
	papel: str


def criar_token_acesso(
	sujeito: str | int, dados_extras: dict[str, Any] | None = None
) -> str:
	"""Função para criar um token JWT de acesso."""
	expiracao = datetime.now(timezone.utc) + timedelta(
		minutes=configuracoes.jwt_access_token_expire_minutes
	)
	dados: dict[str, Any] = {'sub': str(sujeito), 'exp': expiracao, 'type': 'access'}
	if dados_extras:
		dados.update(dados_extras)
	return jwt.encode(
		dados, configuracoes.jwt_secret_key, algorithm=configuracoes.jwt_algorithm
	)


def criar_token_atualizacao(sujeito: str | int) -> str:
	"""Função para criar um token JWT de renovação."""
	expiracao = datetime.now(timezone.utc) + timedelta(
		days=configuracoes.jwt_refresh_token_expire_days
	)
	dados = {'sub': str(sujeito), 'exp': expiracao, 'type': 'refresh'}
	return jwt.encode(
		dados, configuracoes.jwt_secret_key, algorithm=configuracoes.jwt_algorithm
	)


def decodificar_token(token: str) -> dict[str, Any]:
	"""Função para decodificar e validar um token JWT."""
	try:
		return jwt.decode(
			token,
			configuracoes.jwt_secret_key,
			algorithms=[configuracoes.jwt_algorithm],
		)
	except JWTError as exc:
		raise EXCECAO_CREDENCIAIS from exc


def _extrair_token_bearer(credenciais: HTTPAuthorizationCredentials | None) -> str:
	"""Função interna para extrair o token Bearer recebido."""
	if not credenciais:
		raise EXCECAO_CREDENCIAIS
	return credenciais.credentials


def obter_usuario_atual_id(
	credenciais: Annotated[
		HTTPAuthorizationCredentials | None,
		Depends(esquema_bearer),
	],
) -> int:
	"""Função para obter o ID do usuário autenticado."""
	token = _extrair_token_bearer(credenciais)
	dados = decodificar_token(token)
	sujeito = dados.get('sub')
	if not sujeito:
		raise EXCECAO_CREDENCIAIS
	return int(sujeito)


def obter_usuario_atual(
	credenciais: Annotated[
		HTTPAuthorizationCredentials | None,
		Depends(esquema_bearer),
	],
) -> UsuarioAtual:
	"""Função para obter os dados do usuário autenticado."""
	token = _extrair_token_bearer(credenciais)
	dados = decodificar_token(token)
	sujeito = dados.get('sub')
	papel = dados.get('role')
	if not sujeito or not papel:
		raise EXCECAO_CREDENCIAIS
	return UsuarioAtual(id=int(sujeito), papel=str(papel))


def exigir_papel(*papeis_permitidos: str):
	"""Função para exigir perfis específicos de acesso."""

	def _verificar(
		credenciais: Annotated[
			HTTPAuthorizationCredentials | None,
			Depends(esquema_bearer),
		],
	) -> int:
		"""Função interna para validar o perfil do token recebido."""
		token = _extrair_token_bearer(credenciais)
		dados = decodificar_token(token)
		papel = dados.get('role')
		if papel not in papeis_permitidos:
			raise HTTPException(
				status_code=status.HTTP_403_FORBIDDEN,
				detail='Acesso negado para este recurso',
			)
		return int(dados['sub'])

	return _verificar
