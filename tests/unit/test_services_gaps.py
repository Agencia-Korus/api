from types import SimpleNamespace
from typing import Any
from unittest.mock import AsyncMock

import pytest
from core.enums import (
	Complexidade,
	ComunicadoAlvo,
	PapelUsuario,
	Prioridade,
	SituacaoIntegracao,
	SituacaoLead,
	SituacaoServico,
	SituacaoTarefa,
	SituacaoUsuario,
)
from fastapi import HTTPException
from modules.academy.schema import AcademiaAtualizar
from modules.agenda.schema import EventoAgendaAtualizar, SolicitacaoReuniaoAtualizar
from modules.comunicados.model import Comunicado
from modules.comunicados.schema import ComunicadoAtualizar
from modules.comunicados.service import ServicoComunicado
from modules.gamificacao.schema import ConquistaAtualizar, RegraXpAtualizar
from modules.gamificacao.service import ServicoGamificacao
from modules.integracoes.model import Integracao
from modules.integracoes.schema import IntegracaoAtualizar
from modules.integracoes.service import ServicoIntegracao
from modules.leads.schema import LeadAtualizar
from modules.projetos.model import Projeto, ProjetoFuncionario
from modules.projetos.schema import (
	ProjetoAtualizar,
	ProjetoCriar,
	ProjetoFuncionarioCriar,
)
from modules.projetos.service import ServicoProjeto
from modules.servicos.model import Entregavel, Servico
from modules.servicos.schema import (
	EntregavelAtualizar,
	EntregavelCriar,
	ServicoAtualizar,
)
from modules.servicos.service import ServicoServico
from modules.tarefas.model import Anexo, Comentario, Tarefa
from modules.tarefas.schema import (
	AnexoCriar,
	ComentarioCriar,
	TarefaAtualizar,
	TarefaCriar,
)
from modules.tarefas.service import ServicoTarefa
from modules.users.model import Admin, Usuario
from modules.users.schema import DadosCliente, UsuarioAtualizar, UsuarioCriar
from modules.users.service import ServicoUsuario

from tests.unit.test_services import (
	RepositorioFake,
	SessaoFake,
	servico_academia,
	servico_agenda,
	servico_lead,
	servico_portfolio,
)


class RepositorioAtualizacaoNula(RepositorioFake):
	"""Repository fake que encontra na leitura e falha na atualização."""

	async def atualizar(self, entidade_id: int, dados: dict[str, Any]):
		"""Função para simular atualização que não retorna entidade."""
		self.atualizacoes.append((entidade_id, dados))


@pytest.mark.asyncio
async def test_services_crud_basicos_cobrem_obter_listar_e_erros():
	"""Valida branches básicos de CRUD ainda não exercitados."""
	sessao = SessaoFake()
	academia = servico_academia(sessao)
	lead = servico_lead(sessao)
	portfolio = servico_portfolio(sessao)

	assert await academia.obter(1)
	assert await academia.listar(0, 10)
	assert await lead.obter(1)
	assert await lead.listar(0, 10)
	assert await portfolio.obter(1)
	assert await portfolio.listar(0, 10, destaques=True)
	assert await portfolio.listar_filtrados(0, 10, destaques=False, categoria='Case')

	with pytest.raises(HTTPException):
		await academia.obter(404)
	with pytest.raises(HTTPException):
		await lead.atualizar(404, LeadAtualizar(status=SituacaoLead.PERDIDO))
	with pytest.raises(HTTPException):
		await portfolio.deletar(404)
	with pytest.raises(HTTPException):
		await portfolio.obter(404)
	with pytest.raises(HTTPException):
		await academia.atualizar(404, AcademiaAtualizar(titulo='Novo'))


@pytest.mark.asyncio
async def test_servico_comunicado_cobre_listas_e_erros():
	"""Valida branches de leitura, filtro e erro de comunicado."""
	sessao = SessaoFake()
	servico = ServicoComunicado(sessao)
	comunicado = Comunicado(id=1, autor_id=7, titulo='Aviso', conteudo='Conteúdo')
	servico.repository = RepositorioFake({1: comunicado})
	servico.leituras = RepositorioFake()

	assert await servico.obter(1) is comunicado
	assert await servico.listar(0, 10) == [comunicado]
	assert await servico.listar_filtrados(0, 10, ComunicadoAlvo.TODOS) == [comunicado]
	await servico.atualizar(1, ComunicadoAtualizar(titulo='Novo'))
	await servico.deletar(1)

	with pytest.raises(HTTPException):
		await servico.obter(404)
	with pytest.raises(HTTPException):
		await servico.atualizar(404, ComunicadoAtualizar(titulo='Novo'))
	with pytest.raises(HTTPException):
		await servico.deletar(404)


@pytest.mark.asyncio
async def test_servico_agenda_cobre_obtencoes_e_erros():
	"""Valida branches de agenda para eventos e solicitações inexistentes."""
	servico = servico_agenda(SessaoFake())

	assert await servico.obter_evento(1)
	assert await servico.listar_eventos(1)
	assert await servico.listar_eventos_calendario_google() == []
	await servico.atualizar_evento(2, EventoAgendaAtualizar(titulo='Atualizado'))
	assert await servico.obter_solicitacao(1)

	with pytest.raises(HTTPException):
		await servico.obter_evento(404)
	with pytest.raises(HTTPException):
		await servico.deletar_evento(404)
	with pytest.raises(HTTPException):
		await servico.atualizar_evento(404, EventoAgendaAtualizar(titulo='Ausente'))
	with pytest.raises(HTTPException):
		await servico.obter_solicitacao(404)
	with pytest.raises(HTTPException):
		await servico.atualizar_solicitacao(404, SolicitacaoReuniaoAtualizar(status='aceita'))
	with pytest.raises(HTTPException):
		await servico.deletar_solicitacao(404)


@pytest.mark.asyncio
async def test_servico_integracao_cobre_nao_encontrado_e_atualizacao_nula():
	"""Valida branches de integração não encontrada e atualização nula."""
	sessao = SessaoFake()
	servico = ServicoIntegracao(sessao)
	integracao = Integracao(id=1, nome='google_calendar')
	servico.repository = RepositorioFake({1: integracao})

	with pytest.raises(HTTPException):
		await servico.obter(404)

	servico.repository = RepositorioAtualizacaoNula({1: integracao})
	with pytest.raises(HTTPException):
		await servico.atualizar(1, IntegracaoAtualizar(status=SituacaoIntegracao.CONECTADO))


@pytest.mark.asyncio
async def test_servico_gamificacao_cobre_erros_de_atualizacao_e_delecao():
	"""Valida erros de regras e conquistas inexistentes."""
	servico = ServicoGamificacao(SessaoFake())
	servico.regras = RepositorioFake()
	servico.historicos = RepositorioFake()
	servico.conquistas = RepositorioFake()
	servico.fc = RepositorioFake()

	assert await servico.listar_regras(0, 10) == []
	assert await servico.listar_conquistas(0, 10) == []
	with pytest.raises(HTTPException):
		await servico.atualizar_regra(404, RegraXpAtualizar(xp=10))
	with pytest.raises(HTTPException):
		await servico.deletar_regra(404)
	with pytest.raises(HTTPException):
		await servico.atualizar_conquista(404, ConquistaAtualizar(nome='Nova'))
	with pytest.raises(HTTPException):
		await servico.deletar_conquista(404)
	servico.regras = RepositorioFake({1: SimpleNamespace(id=1)})
	servico.conquistas = RepositorioFake({1: SimpleNamespace(id=1)})
	await servico.deletar_regra(1)
	await servico.deletar_conquista(1)
	assert await servico.listar_historico(7) == []
	assert await servico.listar_conquistas_funcionario(7) == []


@pytest.mark.asyncio
async def test_servico_projeto_cobre_crud_visibilidade_e_equipe():
	"""Valida branches de projeto, visibilidade e equipe."""
	sessao = SessaoFake()
	servico = ServicoProjeto(sessao)
	projeto = Projeto(id=1, cliente_id=7, nome='Projeto')
	servico.repository = RepositorioFake({1: projeto})
	servico.equipe = RepositorioFake({
		1: ProjetoFuncionario(projeto_id=1, funcionario_id=8, papel='Dev')
	})

	criado = await servico.criar(ProjetoCriar(nome='Novo', cliente_id=7))
	assert criado.nome == 'Novo'
	assert await servico.obter(1) is projeto
	assert await servico.obter_visivel(1, 7, PapelUsuario.CLIENTE.value) is projeto
	assert await servico.obter_visivel(1, 8, PapelUsuario.FUNCIONARIO.value) is projeto
	assert await servico.listar(0, 10)
	assert await servico.listar_filtrados(0, 10, cliente_id=7)
	assert await servico.listar_visiveis(0, 10, 1, PapelUsuario.ADMIN.value)
	assert await servico.listar_visiveis(0, 10, 7, PapelUsuario.CLIENTE.value)
	assert await servico.listar_visiveis(0, 10, 8, PapelUsuario.FUNCIONARIO.value)
	await servico.atualizar(1, ProjetoAtualizar(nome='Atualizado'))
	await servico.deletar(1)
	servico.repository = RepositorioFake({1: projeto})
	await servico.adicionar_membro(1, ProjetoFuncionarioCriar(funcionario_id=9, papel='QA'))
	assert await servico.listar_equipe(1)
	await servico.remover_membro(1, 8)

	with pytest.raises(HTTPException):
		await servico.obter(404)
	with pytest.raises(HTTPException):
		await servico.obter_visivel(1, 99, PapelUsuario.CLIENTE.value)
	with pytest.raises(HTTPException):
		await servico.listar_visiveis(0, 10, 1, 'visitante')
	with pytest.raises(HTTPException):
		await servico.atualizar(404, ProjetoAtualizar(nome='X'))
	with pytest.raises(HTTPException):
		await servico.deletar(404)
	with pytest.raises(HTTPException):
		await servico.remover_membro(1, 999)


@pytest.mark.asyncio
async def test_servico_servicos_cobre_listas_e_erros_de_servico_e_entregavel():
	"""Valida branches de serviço e entregáveis inexistentes."""
	sessao = SessaoFake()
	servico = ServicoServico(sessao)
	item = Servico(id=1, nome='Site', slug='site')
	entregavel = Entregavel(id=1, servico_id=1, descricao='Entrega')
	servico.repository = RepositorioFake({1: item})
	servico.entregaveis = RepositorioFake({1: entregavel})

	assert await servico.listar(0, 10) == [item]
	assert await servico.listar_filtrados(0, 10, SituacaoServico.ATIVO) == [item]
	await servico.atualizar(1, ServicoAtualizar(nome='Novo'))
	await servico.deletar(1)
	servico.repository = RepositorioFake({1: item})
	assert await servico.criar_entregavel(EntregavelCriar(servico_id=1, descricao='Entrega'))
	assert await servico.listar_entregaveis(1)

	with pytest.raises(HTTPException):
		await servico.obter(404)
	with pytest.raises(HTTPException):
		await servico.atualizar(404, ServicoAtualizar(nome='Novo'))
	with pytest.raises(HTTPException):
		await servico.deletar(404)
	with pytest.raises(HTTPException):
		await servico.atualizar_entregavel(404, EntregavelAtualizar(descricao='Nova'))
	with pytest.raises(HTTPException):
		await servico.deletar_entregavel(404)


@pytest.mark.asyncio
async def test_servico_tarefa_cobre_crud_permissoes_e_auxiliares():
	"""Valida branches de tarefa, permissões, comentários e anexos."""
	sessao = SessaoFake()
	projeto = Projeto(id=1, cliente_id=7, nome='Projeto')
	sessao.entidades[(Projeto, 1)] = projeto
	sessao.execute_result = ProjetoFuncionario(projeto_id=1, funcionario_id=8)
	servico = ServicoTarefa(sessao)
	tarefa = Tarefa(
		id=1,
		projeto_id=1,
		responsavel_id=8,
		titulo='Tarefa',
		status=SituacaoTarefa.A_FAZER,
		complexidade=Complexidade.MEDIA,
		prioridade=Prioridade.MEDIA,
	)
	servico.repository = RepositorioFake({1: tarefa})
	servico.comentarios = RepositorioFake({
		1: Comentario(id=1, tarefa_id=1, autor_id=7, conteudo='ok')
	})
	servico.anexos = RepositorioFake({
		1: Anexo(id=1, tarefa_id=1, nome='arquivo', url='https://example.test')
	})

	assert await servico.criar(TarefaCriar(projeto_id=1, titulo='Nova'))
	assert await servico.obter(1) is tarefa
	assert await servico.listar(0, 10)
	assert await servico.listar_por_projeto(1)
	assert await servico.listar_visiveis(0, 10, 1, PapelUsuario.ADMIN.value)
	assert await servico.listar_visiveis(0, 10, 7, PapelUsuario.CLIENTE.value)
	assert await servico.obter_visivel(1, 7, PapelUsuario.CLIENTE.value)
	assert await servico.garantir_permissao_gerenciar_tarefa(1, 8, PapelUsuario.FUNCIONARIO.value)
	assert await servico.garantir_permissao_gerenciar_tarefa(1, 99, PapelUsuario.ADMIN.value)
	assert await servico._pode_acessar_tarefa(tarefa, 8, PapelUsuario.FUNCIONARIO.value)
	assert await servico._pode_acessar_tarefa(tarefa, 8, 'visitante') is False
	assert await servico._funcionario_envolvido(tarefa, 99) is True
	await servico.atualizar(1, TarefaAtualizar(status=SituacaoTarefa.EM_PROGRESSO))
	await servico.deletar(1)
	servico.repository = RepositorioFake({1: tarefa})
	assert await servico.adicionar_comentario(ComentarioCriar(tarefa_id=1, conteudo='ok'), 7)
	assert await servico.listar_comentarios(1)
	await servico.deletar_comentario(1)
	assert await servico.adicionar_anexo(
		AnexoCriar(tarefa_id=1, nome='arquivo', url='https://example.test')
	)
	assert await servico.listar_anexos(1)
	await servico.deletar_anexo(1)

	with pytest.raises(HTTPException):
		await servico.obter(404)
	with pytest.raises(HTTPException):
		await servico.listar_visiveis(0, 10, 1, 'visitante')
	with pytest.raises(HTTPException):
		await servico.obter_visivel(1, 99, PapelUsuario.CLIENTE.value)
	with pytest.raises(HTTPException):
		await servico.garantir_permissao_gerenciar_tarefa(1, 7, PapelUsuario.CLIENTE.value)
	with pytest.raises(HTTPException):
		await servico.atualizar(404, TarefaAtualizar(titulo='x'))
	with pytest.raises(HTTPException):
		await servico.deletar(404)
	with pytest.raises(HTTPException):
		await servico.deletar_comentario(404)
	with pytest.raises(HTTPException):
		await servico.deletar_anexo(404)


@pytest.mark.asyncio
async def test_servico_usuario_cobre_admin_defaults_listas_e_erros():
	"""Valida branches de usuário admin, listagem e erros."""
	sessao = SessaoFake()
	servico = ServicoUsuario(sessao)
	servico.usuarios = RepositorioFake({
		1: Usuario(
			id=1,
			nome='Admin',
			email='admin@example.com',
			senha_hash='hash',
			role=PapelUsuario.ADMIN,
			status=SituacaoUsuario.PENDENTE,
		)
	})
	servico.clientes = RepositorioFake()
	servico.funcionarios = RepositorioFake()
	servico.admins = RepositorioFake()

	admin = await servico.criar(
		UsuarioCriar(
			nome='Novo Admin',
			email='novo-admin@example.com',
			senha='senha-forte',
			role=PapelUsuario.ADMIN,
		)
	)
	assert admin.role == PapelUsuario.ADMIN
	assert isinstance(servico.admins.adicionados[-1], Admin)
	assert await servico.listar(0, 10)
	assert await servico.listar_filtrados(0, 10, PapelUsuario.ADMIN)
	await servico.atualizar(1, UsuarioAtualizar(nome='Atualizado'))
	await servico.deletar(1)

	servico.usuarios = RepositorioFake()
	with pytest.raises(HTTPException):
		await servico.obter(404)
	with pytest.raises(HTTPException):
		await servico.atualizar(404, UsuarioAtualizar(nome='x'))
	with pytest.raises(HTTPException):
		await servico.deletar(404)

	servico.usuarios = RepositorioAtualizacaoNula({
		2: Usuario(
			id=2,
			nome='Pendente',
			email='pendente@example.com',
			senha_hash='hash',
			role=PapelUsuario.CLIENTE,
			status=SituacaoUsuario.PENDENTE,
		)
	})
	with pytest.raises(HTTPException):
		await servico.aprovar(2)

	servico.obter = AsyncMock(return_value=None)  # type: ignore[method-assign]
	with pytest.raises(HTTPException):
		await servico.aprovar(3)
	servico.obter = AsyncMock(
		return_value=Usuario(  # type: ignore[method-assign]
			id=4,
			nome='Ativo',
			email='ativo@example.com',
			senha_hash='hash',
			role=PapelUsuario.CLIENTE,
			status=SituacaoUsuario.ATIVO,
		)
	)
	assert (await servico.aprovar(4)).status == SituacaoUsuario.ATIVO


@pytest.mark.asyncio
async def test_servico_usuario_cria_cliente_com_dados_padrao():
	"""Valida criação de cliente com dados padrão quando perfil não vem completo."""
	sessao = SessaoFake()
	servico = ServicoUsuario(sessao)
	servico.usuarios = RepositorioFake()
	servico.clientes = RepositorioFake()
	servico.funcionarios = RepositorioFake()
	servico.admins = RepositorioFake()

	usuario = await servico.criar(
		UsuarioCriar(
			nome='Cliente Sem Dados',
			email='cliente-sem-dados@example.com',
			senha='senha-forte',
			role=PapelUsuario.CLIENTE,
			cliente=DadosCliente(razao_social='Cliente', cnpj_cpf='123'),
		)
	)

	assert usuario.id is not None
	assert servico.clientes.adicionados[-1].cnpj_cpf == '123'
