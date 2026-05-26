from __future__ import annotations

from datetime import date, datetime, timezone
from typing import Any

from core.enums import (
	PapelUsuario,
	SituacaoProjeto,
	SituacaoTarefa,
	SituacaoUsuario,
)
from core.exceptions import ErroNaoEncontrado
from fastapi import HTTPException, status
from modules.agenda.model import EventoAgenda
from modules.comunicados.model import Comunicado
from modules.gamificacao.model import Conquista, FuncionarioConquista, HistoricoXp
from modules.leads.model import Lead
from modules.projetos.model import Projeto, ProjetoFuncionario
from modules.tarefas.model import Tarefa
from modules.users.model import Cliente, Funcionario, Usuario
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession


class ServicoPainel:
	"""Classe responsável pelas regras de negócio do painel."""

	def __init__(self, sessao: AsyncSession):
		"""Função para inicializar a instância com suas dependências."""
		self.sessao = sessao

	async def admin(self) -> dict[str, Any]:
		"""Função para montar os indicadores do painel administrativo."""
		return {
			'cards': {
				'leads_no_mes': await self._contar(Lead),
				'projetos_ativos': await self._contar(
					Projeto,
					Projeto.status.in_([
						SituacaoProjeto.PLANEJAMENTO,
						SituacaoProjeto.EM_ANDAMENTO,
						SituacaoProjeto.EM_REVISAO,
					]),
				),
				'tarefas_concluidas': await self._contar(
					Tarefa, Tarefa.status == SituacaoTarefa.CONCLUIDO
				),
				'clientes_ativos': await self._contar(
					Usuario,
					Usuario.role == PapelUsuario.CLIENTE,
					Usuario.status == SituacaoUsuario.ATIVO,
				),
			},
			'leads_por_semana': await self._series_por_periodo(
				Lead.data, 'week', Lead.id
			),
			'tarefas_concluidas_por_dia': await self._series_por_periodo(
				Tarefa.concluido_em,
				'day',
				Tarefa.id,
				Tarefa.concluido_em.is_not(None),
			),
			'leads_recentes': await self._leads_recentes(),
			'ranking_xp_semanal': await self._ranking(),
		}

	async def cliente(
		self, cliente_id: int, usuario_id: int | None = None, papel: str | None = None
	) -> dict[str, Any]:
		"""Função para montar os indicadores do painel do cliente."""
		await self._garantir_acesso_cliente(cliente_id, usuario_id, papel)
		ids_projetos = select(Projeto.id).where(Projeto.cliente_id == cliente_id)
		return {
			'cards': {
				'projetos_ativos': await self._contar(
					Projeto,
					Projeto.cliente_id == cliente_id,
					Projeto.status.in_([
						SituacaoProjeto.PLANEJAMENTO,
						SituacaoProjeto.EM_ANDAMENTO,
						SituacaoProjeto.EM_REVISAO,
					]),
				),
				'tarefas_em_andamento': await self._contar(
					Tarefa,
					Tarefa.projeto_id.in_(ids_projetos),
					Tarefa.status.in_([
						SituacaoTarefa.A_FAZER,
						SituacaoTarefa.EM_PROGRESSO,
					]),
				),
				'entregas_concluidas': await self._contar(
					Tarefa,
					Tarefa.projeto_id.in_(ids_projetos),
					Tarefa.status == SituacaoTarefa.CONCLUIDO,
				),
			},
			'projetos': await self._projetos_do_cliente(cliente_id),
			'proximas_entregas': await self._tarefas_proximas(ids_projetos),
			'comunicados_recentes': await self._comunicados_recentes(),
			'eventos': await self._eventos_do_usuario(cliente_id),
		}

	async def funcionario(
		self,
		funcionario_id: int,
		usuario_id: int | None = None,
		papel: str | None = None,
	) -> dict[str, Any]:
		"""Função para montar os indicadores do painel do funcionário."""
		funcionario = await self._garantir_acesso_funcionario(
			funcionario_id, usuario_id, papel
		)
		return {
			'perfil': {
				'id': funcionario.id,
				'cargo': funcionario.cargo,
				'xp_total': funcionario.xp_total,
				'nivel': funcionario.nivel,
			},
			'cards': {
				'tarefas_atribuidas': await self._contar(
					Tarefa, Tarefa.responsavel_id == funcionario_id
				),
				'tarefas_concluidas': await self._contar(
					Tarefa,
					Tarefa.responsavel_id == funcionario_id,
					Tarefa.status == SituacaoTarefa.CONCLUIDO,
				),
				'xp_no_mes': await self._xp_do_funcionario(funcionario_id),
			},
			'tarefas': await self._tarefas_do_funcionario(funcionario_id),
			'historico_xp': await self._historico_xp(funcionario_id),
			'conquistas': await self._conquistas_do_funcionario(funcionario_id),
			'ranking_xp_semanal': await self._ranking(),
		}

	async def projeto_kanban(
		self, projeto_id: int, usuario_id: int | None = None, papel: str | None = None
	) -> dict[str, Any]:
		"""Função para montar os dados do quadro Kanban de um projeto."""
		projeto = await self.sessao.obter(Projeto, projeto_id)
		if not projeto:
			raise ErroNaoEncontrado('Projeto', projeto_id)
		await self._garantir_acesso_projeto(projeto, usuario_id, papel)
		consulta = (
			select(Tarefa)
			.where(Tarefa.projeto_id == projeto_id)
			.order_by(Tarefa.status, Tarefa.ordem, Tarefa.prazo)
		)
		tarefas = list((await self.sessao.execute(consulta)).scalars().all())
		colunas = {situacao.value: [] for situacao in SituacaoTarefa}
		for tarefa in tarefas:
			colunas[tarefa.status.value].append(self._dados_tarefa(tarefa))
		return {
			'projeto': {
				'id': projeto.id,
				'nome': projeto.nome,
				'status': projeto.status.value,
				'progresso': projeto.progresso,
				'data_fim': projeto.data_fim,
			},
			'colunas': colunas,
			'columns': colunas,
		}

	async def _contar(self, modelo, *condicoes) -> int:
		"""Função interna para contar registros com filtros opcionais."""
		consulta = select(func.count()).select_from(modelo)
		for condicao in condicoes:
			consulta = consulta.where(condicao)
		return int((await self.sessao.execute(consulta)).scalar_one())

	async def _series_por_periodo(
		self, coluna_data, periodo: str, coluna_id, *condicoes
	) -> list[dict[str, Any]]:
		"""Função interna para agrupar registros por período."""
		faixa = func.date_trunc(periodo, coluna_data).label('periodo')
		consulta = select(faixa, func.count(coluna_id)).where(coluna_data.is_not(None))
		for condicao in condicoes:
			consulta = consulta.where(condicao)
		consulta = consulta.group_by(faixa).order_by(faixa)
		linhas = (await self.sessao.execute(consulta)).all()
		return [{'periodo': linha[0], 'total': int(linha[1])} for linha in linhas]

	async def _leads_recentes(self) -> list[dict[str, Any]]:
		"""Função interna para listar leads recentes."""
		consulta = select(Lead).order_by(Lead.data.desc()).limit(10)
		leads = list((await self.sessao.execute(consulta)).scalars().all())
		return [
			{
				'id': lead.id,
				'nome': lead.nome,
				'email': lead.email,
				'empresa': lead.empresa,
				'status': lead.status.value,
				'prioridade': lead.prioridade.value,
				'data': lead.data,
			}
			for lead in leads
		]

	async def _ranking(self) -> list[dict[str, Any]]:
		"""Função interna para montar o ranking de funcionários."""
		consulta = (
			select(Funcionario, Usuario)
			.join(Usuario, Usuario.id == Funcionario.id)
			.order_by(Funcionario.xp_total.desc(), Usuario.nome)
			.limit(10)
		)
		linhas = (await self.sessao.execute(consulta)).all()
		return [
			{
				'funcionario_id': funcionario.id,
				'nome': usuario.nome,
				'cargo': funcionario.cargo,
				'nivel': funcionario.nivel,
				'xp_total': funcionario.xp_total,
			}
			for funcionario, usuario in linhas
		]

	async def _garantir_cliente(self, cliente_id: int) -> Cliente:
		"""Função interna para garantir que o cliente existe."""
		cliente = await self.sessao.obter(Cliente, cliente_id)
		if not cliente:
			raise ErroNaoEncontrado('Cliente', cliente_id)
		return cliente

	async def _garantir_funcionario(self, funcionario_id: int) -> Funcionario:
		"""Função interna para garantir que o funcionário existe."""
		funcionario = await self.sessao.obter(Funcionario, funcionario_id)
		if not funcionario:
			raise ErroNaoEncontrado('Funcionario', funcionario_id)
		return funcionario

	async def _garantir_acesso_cliente(
		self, cliente_id: int, usuario_id: int | None, papel: str | None
	) -> Cliente:
		"""Função interna para validar acesso aos dados de um cliente."""
		cliente = await self._garantir_cliente(cliente_id)
		if papel is None:
			return cliente
		if papel == PapelUsuario.ADMIN.value:
			return cliente
		if papel == PapelUsuario.CLIENTE.value and usuario_id == cliente_id:
			return cliente
		raise HTTPException(
			status_code=status.HTTP_403_FORBIDDEN,
			detail='Acesso negado para este painel de cliente',
		)

	async def _garantir_acesso_funcionario(
		self, funcionario_id: int, usuario_id: int | None, papel: str | None
	) -> Funcionario:
		"""Função interna para validar acesso aos dados de um funcionário."""
		funcionario = await self._garantir_funcionario(funcionario_id)
		if papel is None:
			return funcionario
		if papel == PapelUsuario.ADMIN.value:
			return funcionario
		if papel == PapelUsuario.FUNCIONARIO.value and usuario_id == funcionario_id:
			return funcionario
		raise HTTPException(
			status_code=status.HTTP_403_FORBIDDEN,
			detail='Acesso negado para este painel de funcionário',
		)

	async def _garantir_acesso_projeto(
		self, projeto: Projeto, usuario_id: int | None, papel: str | None
	) -> None:
		"""Função interna para validar acesso aos dados de um projeto."""
		if papel is None:
			return
		if papel == PapelUsuario.ADMIN.value:
			return
		if papel == PapelUsuario.CLIENTE.value and projeto.cliente_id == usuario_id:
			return
		if papel == PapelUsuario.FUNCIONARIO.value:
			consulta = (
				select(func.count())
				.select_from(ProjetoFuncionario)
				.where(
					ProjetoFuncionario.projeto_id == projeto.id,
					ProjetoFuncionario.funcionario_id == usuario_id,
				)
			)
			if int((await self.sessao.execute(consulta)).scalar_one()) > 0:
				return
		raise HTTPException(
			status_code=status.HTTP_403_FORBIDDEN,
			detail='Acesso negado para este projeto',
		)

	async def _projetos_do_cliente(self, cliente_id: int) -> list[dict[str, Any]]:
		"""Função interna para listar projetos de um cliente."""
		consulta = (
			select(Projeto).where(Projeto.cliente_id == cliente_id).order_by(Projeto.id)
		)
		projetos = list((await self.sessao.execute(consulta)).scalars().all())
		return [
			{
				'id': projeto.id,
				'nome': projeto.nome,
				'status': projeto.status.value,
				'progresso': projeto.progresso,
				'data_fim': projeto.data_fim,
			}
			for projeto in projetos
		]

	async def _tarefas_proximas(self, ids_projetos) -> list[dict[str, Any]]:
		"""Função interna para listar próximas tarefas."""
		consulta = (
			select(Tarefa)
			.where(Tarefa.projeto_id.in_(ids_projetos), Tarefa.prazo >= date.today())
			.order_by(Tarefa.prazo)
			.limit(10)
		)
		tarefas = list((await self.sessao.execute(consulta)).scalars().all())
		return [self._dados_tarefa(tarefa) for tarefa in tarefas]

	async def _comunicados_recentes(self) -> list[dict[str, Any]]:
		"""Função interna para listar comunicados recentes."""
		consulta = select(Comunicado).order_by(Comunicado.data.desc()).limit(10)
		comunicados = list((await self.sessao.execute(consulta)).scalars().all())
		return [
			{
				'id': comunicado.id,
				'titulo': comunicado.titulo,
				'conteudo': comunicado.conteudo,
				'alvo': comunicado.alvo.value,
				'data': comunicado.data,
			}
			for comunicado in comunicados
		]

	async def _eventos_do_usuario(self, usuario_id: int) -> list[dict[str, Any]]:
		"""Função interna para listar eventos de um usuário."""
		consulta = (
			select(EventoAgenda)
			.where(EventoAgenda.usuario_id == usuario_id)
			.order_by(EventoAgenda.data, EventoAgenda.hora)
			.limit(20)
		)
		eventos = list((await self.sessao.execute(consulta)).scalars().all())
		return [
			{
				'id': evento.id,
				'titulo': evento.titulo,
				'tipo': evento.tipo.value,
				'data': evento.data,
				'hora': evento.hora,
			}
			for evento in eventos
		]

	async def _xp_do_funcionario(self, funcionario_id: int) -> int:
		"""Função interna para calcular o XP de um funcionário."""
		inicio = datetime.now(timezone.utc).replace(
			day=1, hour=0, minute=0, second=0, microsecond=0
		)
		consulta = select(func.coalesce(func.sum(HistoricoXp.xp), 0)).where(
			HistoricoXp.funcionario_id == funcionario_id,
			HistoricoXp.data >= inicio,
		)
		return int((await self.sessao.execute(consulta)).scalar_one())

	async def _tarefas_do_funcionario(
		self, funcionario_id: int
	) -> list[dict[str, Any]]:
		"""Função interna para listar tarefas de um funcionário."""
		consulta = (
			select(Tarefa)
			.where(Tarefa.responsavel_id == funcionario_id)
			.order_by(Tarefa.status, Tarefa.prazo)
			.limit(20)
		)
		tarefas = list((await self.sessao.execute(consulta)).scalars().all())
		return [self._dados_tarefa(tarefa) for tarefa in tarefas]

	async def _historico_xp(self, funcionario_id: int) -> list[dict[str, Any]]:
		"""Função interna para listar o histórico de XP."""
		consulta = (
			select(HistoricoXp)
			.where(HistoricoXp.funcionario_id == funcionario_id)
			.order_by(HistoricoXp.data.desc())
			.limit(20)
		)
		linhas = list((await self.sessao.execute(consulta)).scalars().all())
		return [
			{
				'id': linha.id,
				'acao': linha.acao,
				'xp': linha.xp,
				'tarefa_id': linha.tarefa_id,
				'data': linha.data,
			}
			for linha in linhas
		]

	async def _conquistas_do_funcionario(
		self, funcionario_id: int
	) -> list[dict[str, Any]]:
		"""Função interna para listar conquistas de um funcionário."""
		consulta = (
			select(Conquista, FuncionarioConquista.desbloqueado_em)
			.join(
				FuncionarioConquista,
				FuncionarioConquista.conquista_id == Conquista.id,
			)
			.where(FuncionarioConquista.funcionario_id == funcionario_id)
			.order_by(FuncionarioConquista.desbloqueado_em.desc())
		)
		linhas = (await self.sessao.execute(consulta)).all()
		return [
			{
				'id': conquista.id,
				'nome': conquista.nome,
				'icone': conquista.icone,
				'descricao': conquista.descricao,
				'xp_bonus': conquista.xp_bonus,
				'desbloqueado_em': desbloqueado_em,
			}
			for conquista, desbloqueado_em in linhas
		]

	@staticmethod
	def _dados_tarefa(tarefa: Tarefa) -> dict[str, Any]:
		"""Função interna para montar o dados de uma tarefa."""
		return {
			'id': tarefa.id,
			'projeto_id': tarefa.projeto_id,
			'responsavel_id': tarefa.responsavel_id,
			'titulo': tarefa.titulo,
			'descricao': tarefa.descricao,
			'status': tarefa.status.value,
			'complexidade': tarefa.complexidade.value,
			'prioridade': tarefa.prioridade.value,
			'categoria': tarefa.categoria,
			'prazo': tarefa.prazo,
			'ordem': tarefa.ordem,
		}
