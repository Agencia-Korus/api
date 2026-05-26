from typing import Any

import pytest
from db.base_repository import RepositorioBase
from modules.servicos.model import Servico
from sqlalchemy import select


class RepositorioServicoTeste(RepositorioBase[Servico]):
	modelo = Servico


class ResultadoRepositorioFake:
	def __init__(self, valores: list[Any] | None = None, escalar: Any = None):
		self.valores = valores or []
		self.escalar = escalar

	def scalars(self):
		return self

	def all(self):
		return self.valores

	def scalar_one_or_none(self):
		return self.escalar


class SessaoRepositorioFake:
	def __init__(self):
		self.adicionados: list[Any] = []
		self.flushes = 0
		self.refreshes: list[Any] = []
		self.execucoes: list[Any] = []
		self.resultado = ResultadoRepositorioFake()
		self.entidades: dict[tuple[type[Any], int], Any] = {}

	def add(self, entidade: Any):
		self.adicionados.append(entidade)

	async def flush(self):
		self.flushes += 1

	async def refresh(self, entidade: Any):
		self.refreshes.append(entidade)

	async def get(self, modelo: type[Any], entidade_id: int):
		return self.entidades.get((modelo, entidade_id))

	async def execute(self, instrucao: Any):
		self.execucoes.append(instrucao)
		return self.resultado


@pytest.mark.asyncio
async def test_repositorio_base_adiciona_e_atualiza_estado_da_sessao():
	"""Valida que repositorio base adiciona e atualiza estado da sessao."""
	sessao = SessaoRepositorioFake()
	repositorio = RepositorioServicoTeste(sessao)
	servico = Servico(id=1, nome='Site', slug='site')

	resposta = await repositorio.adicionar(servico)

	assert resposta is servico
	assert sessao.adicionados == [servico]
	assert sessao.flushes == 1
	assert sessao.refreshes == [servico]


@pytest.mark.asyncio
async def test_repositorio_base_obtem_por_id_usando_modelo_configurado():
	"""Valida que repositorio base obtem por id usando modelo configurado."""
	sessao = SessaoRepositorioFake()
	servico = Servico(id=1, nome='Site', slug='site')
	sessao.entidades[(Servico, 1)] = servico
	repositorio = RepositorioServicoTeste(sessao)

	assert await repositorio.obter(1) is servico


@pytest.mark.asyncio
async def test_repositorio_base_lista_com_paginacao_e_filtros_validos():
	"""Valida que repositorio base lista com paginacao e filtros validos."""
	servico = Servico(id=1, nome='Site', slug='site')
	sessao = SessaoRepositorioFake()
	sessao.resultado = ResultadoRepositorioFake(valores=[servico])
	repositorio = RepositorioServicoTeste(sessao)

	resposta = await repositorio.listar_todos(
		offset=5,
		limit=10,
		filtros={'status': None, 'slug': 'site', 'campo_inexistente': 'x'},
	)

	assert resposta == [servico]
	assert len(sessao.execucoes) == 1


@pytest.mark.asyncio
async def test_repositorio_base_atualiza_ignorando_valores_none():
	"""Valida que repositorio base atualiza ignorando valores none."""
	servico = Servico(id=1, nome='Site atualizado', slug='site')
	sessao = SessaoRepositorioFake()
	sessao.resultado = ResultadoRepositorioFake(escalar=servico)
	repositorio = RepositorioServicoTeste(sessao)

	resposta = await repositorio.atualizar(1, {'nome': 'Site atualizado', 'slug': None})

	assert resposta is servico
	assert sessao.flushes == 1
	assert len(sessao.execucoes) == 1


@pytest.mark.asyncio
async def test_repositorio_base_atualizacao_vazia_retorna_entidade_atual():
	"""Valida que repositorio base atualizacao vazia retorna entidade atual."""
	servico = Servico(id=1, nome='Site', slug='site')
	sessao = SessaoRepositorioFake()
	sessao.entidades[(Servico, 1)] = servico
	repositorio = RepositorioServicoTeste(sessao)

	resposta = await repositorio.atualizar(1, {'nome': None})

	assert resposta is servico
	assert sessao.execucoes == []


@pytest.mark.asyncio
@pytest.mark.parametrize(('escalar', 'esperado'), [(1, True), (None, False)])
async def test_repositorio_base_deleta_retornando_se_linha_existia(escalar, esperado):
	"""Valida que repositorio base deleta retornando se linha existia."""
	sessao = SessaoRepositorioFake()
	sessao.resultado = ResultadoRepositorioFake(escalar=escalar)
	repositorio = RepositorioServicoTeste(sessao)

	assert await repositorio.deletar(1) is esperado
	assert sessao.flushes == 1
	assert len(sessao.execucoes) == 1


def test_repositorio_base_remove_valores_vazios():
	"""Valida que repositorio base remove valores vazios."""
	assert RepositorioBase._remover_valores_vazios({'a': 1, 'b': None}) == {'a': 1}


def test_repositorio_base_aplicar_filtros_ignora_valores_nulos_e_campos_invalidos():
	"""Valida filtros nulos e campos invalidos no repositorio base."""
	repositorio = RepositorioServicoTeste(SessaoRepositorioFake())
	consulta = select(Servico)

	filtrada = repositorio._aplicar_filtros(
		consulta,
		{'slug': 'site', 'status': None, 'inexistente': 'x'},
	)

	assert filtrada is not consulta
	assert repositorio._aplicar_filtros(consulta, None) is consulta
