import uuid
from http import HTTPStatus

import httpx
from core.config import obter_configuracoes
from fastapi import HTTPException, UploadFile

TAMANHO_MAXIMO_BYTES = 5 * 1024 * 1024
PASTAS_PERMITIDAS = {'avatars', 'portfolio', 'academy'}
EXTENSAO_POR_TIPO = {
	'image/png': 'png',
	'image/jpeg': 'jpg',
	'image/jpg': 'jpg',
	'image/webp': 'webp',
	'image/gif': 'gif',
	'image/svg+xml': 'svg',
}


class ServicoUpload:
	"""Serviço para enviar imagens ao Supabase Storage usando a service role."""

	def __init__(self) -> None:
		"""Função para inicializar o serviço com as configurações atuais."""
		self._configuracoes = obter_configuracoes()

	def _credenciais(self) -> tuple[str, str, str]:
		"""Função para validar e obter as credenciais do storage."""
		url = (self._configuracoes.supabase_url or '').rstrip('/')
		chave = self._configuracoes.supabase_service_role_key
		bucket = self._configuracoes.supabase_bucket
		if not url or not chave:
			raise HTTPException(
				status_code=HTTPStatus.SERVICE_UNAVAILABLE,
				detail='Upload de imagens não configurado no servidor.',
			)
		return url, chave, bucket

	async def enviar_imagem(self, arquivo: UploadFile, pasta: str) -> str:
		"""Função para validar e enviar a imagem, retornando a URL pública."""
		url, chave, bucket = self._credenciais()

		if pasta not in PASTAS_PERMITIDAS:
			raise HTTPException(
				status_code=HTTPStatus.BAD_REQUEST,
				detail='Pasta de destino inválida.',
			)

		tipo = (arquivo.content_type or '').lower()
		if tipo not in EXTENSAO_POR_TIPO:
			raise HTTPException(
				status_code=HTTPStatus.BAD_REQUEST,
				detail='Envie uma imagem (png, jpg, webp, gif ou svg).',
			)

		conteudo = await arquivo.read()
		if len(conteudo) > TAMANHO_MAXIMO_BYTES:
			raise HTTPException(
				status_code=HTTPStatus.REQUEST_ENTITY_TOO_LARGE,
				detail='A imagem precisa ter até 5MB.',
			)

		caminho = f'{pasta}/{uuid.uuid4().hex}.{EXTENSAO_POR_TIPO[tipo]}'
		destino = f'{url}/storage/v1/object/{bucket}/{caminho}'

		async with httpx.AsyncClient(timeout=30) as cliente:
			resposta = await cliente.post(
				destino,
				content=conteudo,
				headers={
					'apikey': chave,
					'Authorization': f'Bearer {chave}',
					'Content-Type': tipo,
					'x-upsert': 'true',
				},
			)

		if resposta.status_code >= HTTPStatus.BAD_REQUEST:
			raise HTTPException(
				status_code=HTTPStatus.BAD_GATEWAY,
				detail='Não foi possível salvar a imagem no storage.',
			)

		return f'{url}/storage/v1/object/public/{bucket}/{caminho}'
