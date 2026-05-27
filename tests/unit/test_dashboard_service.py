from datetime import date
from typing import Any
from unittest.mock import AsyncMock

import pytest
from core.enums import (
	Complexidade,
	PapelUsuario,
	Prioridade,
	SituacaoProjeto,
	SituacaoTarefa,
)
from fastapi import HTTPException
from modules.dashboard.service import ServicoPainel
from modules.projetos.model import Projeto
from modules.tarefas.model import Tarefa
from modules.users.model import Cliente, Funcionario


class ResultadoEscalarFake:
	def __init__(self, valores: list[Any]):
		self.valores = valores

	def scalars(self):
		return self

	def all(self):
		return self.valores


class SessaoPainelFake:
	def __init__(self):
		self.entidades: dict[tuple[type[Any], int], Any] = {}
		self.resultado_execute: Any = ResultadoEscalarFake([])

	async def get(self, modelo: type[Any], entidade_id: int):
		return self.entidades.get((modelo, entidade_id))

	async def execute(self, _consulta: Any):
		return self.resultado_execute


@pytest.mark.asyncio
async def test_painel_admin_monta_indicadores_principais():
	"""Valida que painel admin monta indicadores principais."""
	servico = ServicoPainel(SessaoPainelFake())
	servico._contar = AsyncMock(side_effect=[3, 2, 7, 5])
	servico._series_por_periodo = AsyncMock(
		side_effect=[
			[{'periodo': 'semana', 'total': 3}],
			[{'periodo': 'dia', 'total': 7}],
		]
	)
	servico._leads_recentes = AsyncMock(return_value=[{'id': 1}])
	servico._ranking = AsyncMock(return_value=[{'funcionario_id': 2}])

	resposta = await servico.admin()

	assert resposta['cards'] == {
		'leads_no_mes': 3,
		'projetos_ativos': 2,
		'tarefas_concluidas': 7,
		'clientes_ativos': 5,
	}
	assert resposta['leads_por_semana'] == [{'periodo': 'semana', 'total': 3}]
	assert resposta['ranking_xp_semanal'] == [{'funcionario_id': 2}]


@pytest.mark.asyncio
async def test_painel_cliente_monta_dados_do_cliente_autorizado():
	"""Valida que painel cliente monta dados do cliente autorizado."""
	servico = ServicoPainel(SessaoPainelFake())
	servico._garantir_acesso_cliente = AsyncMock(return_value=Cliente(id=10))
	servico._contar = AsyncMock(side_effect=[2, 4, 1])
	servico._projetos_do_cliente = AsyncMock(return_value=[{'id': 1}])
	servico._tarefas_proximas = AsyncMock(return_value=[{'id': 2}])
	servico._comunicados_recentes = AsyncMock(return_value=[{'id': 3}])
	servico._eventos_do_usuario = AsyncMock(return_value=[{'id': 4}])

	resposta = await servico.cliente(
		cliente_id=10,
		usuario_id=10,
		papel=PapelUsuario.CLIENTE.value,
	)

	assert resposta['cards']['projetos_ativos'] == 2
	assert resposta['cards']['tarefas_em_andamento'] == 4
	assert resposta['proximas_entregas'] == [{'id': 2}]
	assert resposta['eventos'] == [{'id': 4}]


@pytest.mark.asyncio
async def test_painel_funcionario_monta_perfil_cards_e_listas():
	"""Valida que painel funcionario monta perfil cards e listas."""
	funcionario = Funcionario(id=20, cargo='Dev', xp_total=750, nivel=2)
	servico = ServicoPainel(SessaoPainelFake())
	servico._garantir_acesso_funcionario = AsyncMock(return_value=funcionario)
	servico._contar = AsyncMock(side_effect=[8, 6])
	servico._xp_do_funcionario = AsyncMock(return_value=150)
	servico._tarefas_do_funcionario = AsyncMock(return_value=[{'id': 1}])
	servico._historico_xp = AsyncMock(return_value=[{'id': 2}])
	servico._conquistas_do_funcionario = AsyncMock(return_value=[{'id': 3}])
	servico._ranking = AsyncMock(return_value=[{'funcionario_id': 20}])

	resposta = await servico.funcionario(
		funcionario_id=20,
		usuario_id=20,
		papel=PapelUsuario.FUNCIONARIO.value,
	)

	assert resposta['perfil'] == {
		'id': 20,
		'cargo': 'Dev',
		'xp_total': 750,
		'nivel': 2,
	}
	assert resposta['cards']['xp_no_mes'] == 150
	assert resposta['conquistas'] == [{'id': 3}]


@pytest.mark.asyncio
async def test_painel_projeto_kanban_agrupa_tarefas_por_status():
	"""Valida que painel projeto kanban agrupa tarefas por status."""
	sessao = SessaoPainelFake()
	projeto = Projeto(
		id=1,
		cliente_id=10,
		nome='Site',
		status=SituacaoProjeto.EM_ANDAMENTO,
		progresso=40,
		data_fim=date(2026, 6, 30),
	)
	tarefa = Tarefa(
		id=1,
		projeto_id=1,
		responsavel_id=20,
		titulo='Layout',
		descricao='Criar layout',
		status=SituacaoTarefa.EM_PROGRESSO,
		complexidade=Complexidade.MEDIA,
		prioridade=Prioridade.ALTA,
		categoria='design',
		prazo=date(2026, 6, 1),
		ordem=2,
	)
	sessao.entidades[(Projeto, 1)] = projeto
	sessao.resultado_execute = ResultadoEscalarFake([tarefa])
	servico = ServicoPainel(sessao)

	resposta = await servico.projeto_kanban(
		projeto_id=1,
		usuario_id=99,
		papel=PapelUsuario.ADMIN.value,
	)

	assert resposta['projeto']['nome'] == 'Site'
	assert resposta['colunas']['em_progresso'][0]['titulo'] == 'Layout'
	assert resposta['columns'] is resposta['colunas']


@pytest.mark.asyncio
async def test_painel_bloqueia_cliente_e_funcionario_sem_permissao():
	"""Valida que painel bloqueia cliente e funcionario sem permissao."""
	sessao = SessaoPainelFake()
	sessao.entidades[(Cliente, 10)] = Cliente(id=10)
	sessao.entidades[(Funcionario, 20)] = Funcionario(id=20, cargo='Dev')
	servico = ServicoPainel(sessao)

	with pytest.raises(HTTPException) as cliente:
		await servico._garantir_acesso_cliente(
			10,
			usuario_id=99,
			papel=PapelUsuario.CLIENTE.value,
		)
	with pytest.raises(HTTPException) as funcionario:
		await servico._garantir_acesso_funcionario(
			20,
			usuario_id=99,
			papel=PapelUsuario.FUNCIONARIO.value,
		)

	assert cliente.value.status_code == 403
	assert funcionario.value.status_code == 403


@pytest.mark.asyncio
async def test_painel_retorna_404_para_entidades_inexistentes():
	"""Valida que painel retorna 404 para entidades inexistentes."""
	servico = ServicoPainel(SessaoPainelFake())

	with pytest.raises(HTTPException) as cliente:
		await servico._garantir_cliente(404)
	with pytest.raises(HTTPException) as funcionario:
		await servico._garantir_funcionario(404)
	with pytest.raises(HTTPException) as projeto:
		await servico.projeto_kanban(404)

	assert cliente.value.status_code == 404
	assert funcionario.value.status_code == 404
	assert projeto.value.status_code == 404
