import importlib
from types import ModuleType

import pytest
from db.base import Base
from db.registro import TODOS_MODELOS

MODULOS_MODELO = (
	'modules.academy.model',
	'modules.agenda.model',
	'modules.comunicados.model',
	'modules.gamificacao.model',
	'modules.integracoes.model',
	'modules.leads.model',
	'modules.lgpd.model',
	'modules.portfolio.model',
	'modules.projetos.model',
	'modules.servicos.model',
	'modules.tarefas.model',
	'modules.users.model',
)

TABELAS_ESPERADAS = {
	'academy',
	'admin',
	'anexo',
	'cliente',
	'comentario',
	'comunicado',
	'comunicado_leitura',
	'conquista',
	'consentimento_lgpd',
	'entregavel',
	'evento_agenda',
	'funcionario',
	'funcionario_conquista',
	'historico_xp',
	'integracao',
	'lead',
	'portfolio',
	'projeto',
	'projeto_funcionario',
	'regra_xp',
	'servico',
	'solicitacao_reuniao',
	'tarefa',
	'usuario',
}


def test_registro_carrega_um_modulo_por_contexto_de_dominio():
	"""Valida que registro carrega um modulo por contexto de dominio."""
	assert len(TODOS_MODELOS) == len(MODULOS_MODELO)
	assert all(isinstance(modulo, ModuleType) for modulo in TODOS_MODELOS)


@pytest.mark.parametrize('nome_modulo', MODULOS_MODELO)
def test_modulos_de_modelo_registrados_sao_importaveis(nome_modulo: str):
	"""Valida que modulos de modelo registrados sao importaveis."""
	modulo = importlib.import_module(nome_modulo)

	assert modulo in TODOS_MODELOS


def test_registro_popula_metadata_usada_pelo_alembic():
	"""Valida que registro popula metadata usada pelo alembic."""
	assert TABELAS_ESPERADAS <= set(Base.metadata.tables)
