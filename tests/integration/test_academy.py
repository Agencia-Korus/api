import uuid

import pytest
from httpx import AsyncClient

from tests.conftest import exige_banco


def _dados(tipo: str) -> dict[str, object]:
	sufixo = uuid.uuid4().hex[:8]
	return {
		'titulo': f'Conteudo teste {sufixo}',
		'tipo': tipo,
		'descricao': 'Conteudo criado para testar filtros JSON.',
		'preco': '0.00',
		'url_externa': f'https://example.com/{sufixo}',
		'publicado': True,
	}


@pytest.mark.asyncio
@exige_banco
async def test_listar_academia_filtra_body_json(
	cliente_admin: AsyncClient, cliente_http: AsyncClient
):
	ebook = (await cliente_admin.post('/api/v1/academy', json=_dados('ebook'))).json()
	await cliente_admin.post('/api/v1/academy', json=_dados('curso'))

	resposta = await cliente_http.request(
		'GET',
		'/api/v1/academy',
		json={'offset': 0, 'limit': 100, 'tipo': 'ebook', 'publicado': True},
	)

	assert resposta.status_code == 200
	conteudos = resposta.json()
	assert ebook['id'] in {conteudo['id'] for conteudo in conteudos}
	assert all(conteudo['tipo'] == 'ebook' for conteudo in conteudos)
	assert all(conteudo['publicado'] is True for conteudo in conteudos)
