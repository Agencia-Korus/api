from typing import Any


def exemplo_requisicao_json(exemplo: dict[str, Any]) -> dict[str, Any]:
	"""Função para documentar um exemplo JSON de requisição no Swagger."""
	return {
		'requestBody': {
			'content': {
				'application/json': {
					'example': exemplo,
				}
			}
		}
	}
