from pathlib import Path

import pytest
from core.config import Configuracoes


@pytest.mark.parametrize('valor_debug', ['release', 'production', 'prod'])
def test_configuracoes_interpreta_ambientes_de_release_como_debug_falso(
	valor_debug: str,
):
	"""Valida que configuracoes interpreta ambientes de release como debug falso."""
	configuracoes = Configuracoes(debug=valor_debug)

	assert configuracoes.debug is False


@pytest.mark.parametrize('valor_debug', ['true', '1', True])
def test_configuracoes_mantem_valores_verdadeiros_de_debug(valor_debug: str | bool):
	"""Valida que configuracoes mantem valores verdadeiros de debug."""
	configuracoes = Configuracoes(debug=valor_debug)

	assert configuracoes.debug is True


def test_caminho_conta_servico_google_prioriza_arquivo_do_host(tmp_path: Path):
	"""Valida que caminho conta servico google prioriza arquivo do host."""
	arquivo_container = tmp_path / 'container.json'
	arquivo_host = tmp_path / 'host.json'
	arquivo_container.write_text('{}')
	arquivo_host.write_text('{}')
	configuracoes = Configuracoes(
		google_calendar_service_account_file=str(arquivo_container),
		google_calendar_service_account_host_file=str(arquivo_host),
	)

	assert configuracoes.caminho_conta_servico_google() == arquivo_host.resolve()


def test_caminho_conta_servico_google_retorna_none_sem_arquivo_existente(
	tmp_path: Path, monkeypatch: pytest.MonkeyPatch
):
	"""Valida que caminho conta servico google retorna none sem arquivo existente."""
	monkeypatch.chdir(tmp_path)
	configuracoes = Configuracoes(
		google_calendar_service_account_file='arquivo-inexistente.json',
		google_calendar_service_account_host_file='outro-inexistente.json',
	)

	assert configuracoes.caminho_conta_servico_google() is None
