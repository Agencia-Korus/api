import uuid

import pytest
from httpx import AsyncClient

from tests.conftest import exige_banco


def _dados_cliente():
	suffix = uuid.uuid4().hex[:8]
	return {
		'nome': f'Cliente {suffix}',
		'email': f'cli-{suffix}@example.com',
		'senha': 'senha-forte-123',
		'role': 'cliente',
		'cliente': {
			'razao_social': 'Acme LTDA',
			'cnpj_cpf': f'00.000.000/0001-{int(suffix[:2], 16) % 100:02d}',
			'segmento': 'Tech',
		},
	}


def _dados_funcionario():
	suffix = uuid.uuid4().hex[:8]
	return {
		'nome': f'Funcionário {suffix}',
		'email': f'fn-{suffix}@example.com',
		'senha': 'senha-forte-123',
		'role': 'funcionario',
		'funcionario': {'cargo': 'Designer', 'especialidade': 'UI'},
	}


@pytest.mark.asyncio
@exige_banco
@pytest.mark.parametrize('construtor_dados', [_dados_cliente, _dados_funcionario])
async def test_admin_cria_usuarios_de_tipos_diversos(
	cliente_http: AsyncClient, cabecalhos_admin: dict[str, str], construtor_dados
):
	"""Valida que admin cria usuarios de tipos diversos."""
	dados = construtor_dados()
	resposta = await cliente_http.post(
		'/api/v1/usuarios', json=dados, headers=cabecalhos_admin
	)
	assert resposta.status_code == 201, resposta.text
	criado = resposta.json()
	assert criado['email'] == dados['email']
	assert criado['status'] == 'ativo'
	assert 'senha' not in criado


@pytest.mark.asyncio
@exige_banco
async def test_criar_usuario_sem_token_retorna_401(cliente_http: AsyncClient):
	"""Valida que criar usuario sem token retorna 401."""
	resposta = await cliente_http.post('/api/v1/usuarios', json=_dados_cliente())
	assert resposta.status_code == 401


@pytest.mark.asyncio
@exige_banco
async def test_criar_usuario_com_role_nao_admin_retorna_403(
	cliente_http: AsyncClient, cabecalhos_cliente: dict[str, str]
):
	"""Valida que criar usuario com role nao admin retorna 403."""
	resposta = await cliente_http.post(
		'/api/v1/usuarios', json=_dados_cliente(), headers=cabecalhos_cliente
	)
	assert resposta.status_code == 403


@pytest.mark.asyncio
@exige_banco
async def test_email_duplicado_retorna_409(
	cliente_http: AsyncClient, cabecalhos_admin: dict[str, str]
):
	"""Valida que email duplicado retorna 409."""
	dados = _dados_cliente()
	primeira_resposta = await cliente_http.post(
		'/api/v1/usuarios', json=dados, headers=cabecalhos_admin
	)
	assert primeira_resposta.status_code == 201
	segunda_resposta = await cliente_http.post(
		'/api/v1/usuarios', json=dados, headers=cabecalhos_admin
	)
	assert segunda_resposta.status_code == 409


@pytest.mark.asyncio
@exige_banco
async def test_registro_publico_cria_usuario_pendente(cliente_http: AsyncClient):
	"""Valida que registro publico cria usuario pendente."""
	dados = _dados_cliente()
	resposta = await cliente_http.post('/api/v1/usuarios/registro', json=dados)
	assert resposta.status_code == 201, resposta.text
	criado = resposta.json()
	assert criado['status'] == 'pendente'


@pytest.mark.asyncio
@exige_banco
async def test_registro_publico_nao_permite_admin(cliente_http: AsyncClient):
	"""Valida que registro publico nao permite admin."""
	dados = _dados_cliente()
	dados['role'] = 'admin'
	resposta = await cliente_http.post('/api/v1/usuarios/registro', json=dados)
	assert resposta.status_code == 400


@pytest.mark.asyncio
@exige_banco
async def test_admin_aprova_cadastro_pendente(
	cliente_http: AsyncClient, cabecalhos_admin: dict[str, str]
):
	"""Valida que admin aprova cadastro pendente."""
	registro = await cliente_http.post(
		'/api/v1/usuarios/registro', json=_dados_funcionario()
	)
	assert registro.status_code == 201
	usuario_id = registro.json()['id']
	resposta = await cliente_http.post(
		f'/api/v1/usuarios/{usuario_id}/aprovar', headers=cabecalhos_admin
	)
	assert resposta.status_code == 200
	assert resposta.json()['status'] == 'ativo'


@pytest.mark.asyncio
@exige_banco
async def test_aprovar_sem_admin_retorna_403(
	cliente_http: AsyncClient, cabecalhos_cliente: dict[str, str]
):
	"""Valida que aprovar sem admin retorna 403."""
	registro = await cliente_http.post(
		'/api/v1/usuarios/registro', json=_dados_funcionario()
	)
	usuario_id = registro.json()['id']
	resposta = await cliente_http.post(
		f'/api/v1/usuarios/{usuario_id}/aprovar', headers=cabecalhos_cliente
	)
	assert resposta.status_code == 403


@pytest.mark.asyncio
@exige_banco
async def test_editar_usuario_requer_admin(
	cliente_http: AsyncClient,
	cabecalhos_admin: dict[str, str],
	cabecalhos_cliente: dict[str, str],
):
	"""Valida que editar usuario requer admin."""
	criado = await cliente_http.post(
		'/api/v1/usuarios', json=_dados_cliente(), headers=cabecalhos_admin
	)
	usuario_id = criado.json()['id']
	sem_token = await cliente_http.patch(
		f'/api/v1/usuarios/{usuario_id}', json={'nome': 'Novo Nome'}
	)
	assert sem_token.status_code == 401
	com_cliente = await cliente_http.patch(
		f'/api/v1/usuarios/{usuario_id}',
		json={'nome': 'Novo Nome'},
		headers=cabecalhos_cliente,
	)
	assert com_cliente.status_code == 403
	ok = await cliente_http.patch(
		f'/api/v1/usuarios/{usuario_id}',
		json={'nome': 'Novo Nome'},
		headers=cabecalhos_admin,
	)
	assert ok.status_code == 200
	assert ok.json()['nome'] == 'Novo Nome'
