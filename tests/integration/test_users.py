import uuid

import pytest
from httpx import AsyncClient

from tests.conftest import requires_db


def _payload_cliente():
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


def _payload_funcionario():
	suffix = uuid.uuid4().hex[:8]
	return {
		'nome': f'Funcionário {suffix}',
		'email': f'fn-{suffix}@example.com',
		'senha': 'senha-forte-123',
		'role': 'funcionario',
		'funcionario': {'cargo': 'Designer', 'especialidade': 'UI'},
	}


@pytest.mark.asyncio
@requires_db
@pytest.mark.parametrize('payload_builder', [_payload_cliente, _payload_funcionario])
async def test_admin_cria_usuarios_de_tipos_diversos(
	client: AsyncClient, admin_headers: dict[str, str], payload_builder
):
	dados = payload_builder()
	resp = await client.post('/api/v1/usuarios', json=dados, headers=admin_headers)
	assert resp.status_code == 201, resp.text
	criado = resp.json()
	assert criado['email'] == dados['email']
	assert criado['status'] == 'ativo'
	assert 'senha' not in criado


@pytest.mark.asyncio
@requires_db
async def test_criar_usuario_sem_token_retorna_401(client: AsyncClient):
	resp = await client.post('/api/v1/usuarios', json=_payload_cliente())
	assert resp.status_code == 401


@pytest.mark.asyncio
@requires_db
async def test_criar_usuario_com_role_nao_admin_retorna_403(
	client: AsyncClient, cliente_headers: dict[str, str]
):
	resp = await client.post(
		'/api/v1/usuarios', json=_payload_cliente(), headers=cliente_headers
	)
	assert resp.status_code == 403


@pytest.mark.asyncio
@requires_db
async def test_email_duplicado_retorna_409(
	client: AsyncClient, admin_headers: dict[str, str]
):
	dados = _payload_cliente()
	first = await client.post('/api/v1/usuarios', json=dados, headers=admin_headers)
	assert first.status_code == 201
	second = await client.post('/api/v1/usuarios', json=dados, headers=admin_headers)
	assert second.status_code == 409


@pytest.mark.asyncio
@requires_db
async def test_registro_publico_cria_usuario_pendente(client: AsyncClient):
	dados = _payload_cliente()
	resp = await client.post('/api/v1/usuarios/registro', json=dados)
	assert resp.status_code == 201, resp.text
	criado = resp.json()
	assert criado['status'] == 'pendente'


@pytest.mark.asyncio
@requires_db
async def test_registro_publico_nao_permite_admin(client: AsyncClient):
	dados = _payload_cliente()
	dados['role'] = 'admin'
	resp = await client.post('/api/v1/usuarios/registro', json=dados)
	assert resp.status_code == 400


@pytest.mark.asyncio
@requires_db
async def test_admin_aprova_cadastro_pendente(
	client: AsyncClient, admin_headers: dict[str, str]
):
	registro = await client.post(
		'/api/v1/usuarios/registro', json=_payload_funcionario()
	)
	assert registro.status_code == 201
	usuario_id = registro.json()['id']
	resp = await client.post(
		f'/api/v1/usuarios/{usuario_id}/aprovar', headers=admin_headers
	)
	assert resp.status_code == 200
	assert resp.json()['status'] == 'ativo'


@pytest.mark.asyncio
@requires_db
async def test_aprovar_sem_admin_retorna_403(
	client: AsyncClient, cliente_headers: dict[str, str]
):
	registro = await client.post(
		'/api/v1/usuarios/registro', json=_payload_funcionario()
	)
	usuario_id = registro.json()['id']
	resp = await client.post(
		f'/api/v1/usuarios/{usuario_id}/aprovar', headers=cliente_headers
	)
	assert resp.status_code == 403


@pytest.mark.asyncio
@requires_db
async def test_editar_usuario_requer_admin(
	client: AsyncClient,
	admin_headers: dict[str, str],
	cliente_headers: dict[str, str],
):
	criado = await client.post(
		'/api/v1/usuarios', json=_payload_cliente(), headers=admin_headers
	)
	usuario_id = criado.json()['id']
	sem_token = await client.patch(
		f'/api/v1/usuarios/{usuario_id}', json={'nome': 'Novo Nome'}
	)
	assert sem_token.status_code == 401
	com_cliente = await client.patch(
		f'/api/v1/usuarios/{usuario_id}',
		json={'nome': 'Novo Nome'},
		headers=cliente_headers,
	)
	assert com_cliente.status_code == 403
	ok = await client.patch(
		f'/api/v1/usuarios/{usuario_id}',
		json={'nome': 'Novo Nome'},
		headers=admin_headers,
	)
	assert ok.status_code == 200
	assert ok.json()['nome'] == 'Novo Nome'
