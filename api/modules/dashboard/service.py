from __future__ import annotations

from datetime import date, datetime, timezone
from typing import Any

from fastapi import HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from core.enums import ProjetoStatus, TarefaStatus, UserRole, UserStatus
from core.exceptions import NotFoundError
from modules.agenda.model import EventoAgenda
from modules.comunicados.model import Comunicado
from modules.gamificacao.model import Conquista, FuncionarioConquista, HistoricoXp
from modules.leads.model import Lead
from modules.projetos.model import Projeto, ProjetoFuncionario
from modules.tarefas.model import Tarefa
from modules.users.model import Cliente, Funcionario, Usuario


class DashboardService:
	def __init__(self, session: AsyncSession):
		self.session = session

	async def admin(self) -> dict[str, Any]:
		return {
			'cards': {
				'leads_no_mes': await self._count(Lead),
				'projetos_ativos': await self._count(
					Projeto,
					Projeto.status.in_([
						ProjetoStatus.PLANEJAMENTO,
						ProjetoStatus.EM_ANDAMENTO,
						ProjetoStatus.EM_REVISAO,
					]),
				),
				'tarefas_concluidas': await self._count(
					Tarefa, Tarefa.status == TarefaStatus.CONCLUIDO
				),
				'clientes_ativos': await self._count(
					Usuario,
					Usuario.role == UserRole.CLIENTE,
					Usuario.status == UserStatus.ATIVO,
				),
			},
			'leads_por_semana': await self._series_by_period(
				Lead.data, 'week', Lead.id
			),
			'tarefas_concluidas_por_dia': await self._series_by_period(
				Tarefa.concluido_em,
				'day',
				Tarefa.id,
				Tarefa.concluido_em.is_not(None),
			),
			'leads_recentes': await self._recent_leads(),
			'ranking_xp_semanal': await self._ranking(),
		}

	async def cliente(
		self, cliente_id: int, usuario_id: int | None = None, role: str | None = None
	) -> dict[str, Any]:
		await self._ensure_can_view_cliente(cliente_id, usuario_id, role)
		project_ids = select(Projeto.id).where(Projeto.cliente_id == cliente_id)
		return {
			'cards': {
				'projetos_ativos': await self._count(
					Projeto,
					Projeto.cliente_id == cliente_id,
					Projeto.status.in_([
						ProjetoStatus.PLANEJAMENTO,
						ProjetoStatus.EM_ANDAMENTO,
						ProjetoStatus.EM_REVISAO,
					]),
				),
				'tarefas_em_andamento': await self._count(
					Tarefa,
					Tarefa.projeto_id.in_(project_ids),
					Tarefa.status.in_([
						TarefaStatus.A_FAZER,
						TarefaStatus.EM_PROGRESSO,
					]),
				),
				'entregas_concluidas': await self._count(
					Tarefa,
					Tarefa.projeto_id.in_(project_ids),
					Tarefa.status == TarefaStatus.CONCLUIDO,
				),
			},
			'projetos': await self._projects_for_cliente(cliente_id),
			'proximas_entregas': await self._upcoming_tasks(project_ids),
			'comunicados_recentes': await self._recent_announcements(),
			'eventos': await self._events_for_user(cliente_id),
		}

	async def funcionario(
		self,
		funcionario_id: int,
		usuario_id: int | None = None,
		role: str | None = None,
	) -> dict[str, Any]:
		funcionario = await self._ensure_can_view_funcionario(
			funcionario_id, usuario_id, role
		)
		return {
			'perfil': {
				'id': funcionario.id,
				'cargo': funcionario.cargo,
				'xp_total': funcionario.xp_total,
				'nivel': funcionario.nivel,
			},
			'cards': {
				'tarefas_atribuidas': await self._count(
					Tarefa, Tarefa.responsavel_id == funcionario_id
				),
				'tarefas_concluidas': await self._count(
					Tarefa,
					Tarefa.responsavel_id == funcionario_id,
					Tarefa.status == TarefaStatus.CONCLUIDO,
				),
				'xp_no_mes': await self._xp_for_funcionario(funcionario_id),
			},
			'tarefas': await self._tasks_for_funcionario(funcionario_id),
			'historico_xp': await self._xp_history(funcionario_id),
			'conquistas': await self._achievements_for_funcionario(funcionario_id),
			'ranking_xp_semanal': await self._ranking(),
		}

	async def projeto_kanban(
		self, projeto_id: int, usuario_id: int | None = None, role: str | None = None
	) -> dict[str, Any]:
		projeto = await self.session.get(Projeto, projeto_id)
		if not projeto:
			raise NotFoundError('Projeto', projeto_id)
		await self._ensure_can_view_projeto(projeto, usuario_id, role)
		stmt = (
			select(Tarefa)
			.where(Tarefa.projeto_id == projeto_id)
			.order_by(Tarefa.status, Tarefa.ordem, Tarefa.prazo)
		)
		tarefas = list((await self.session.execute(stmt)).scalars().all())
		columns = {status.value: [] for status in TarefaStatus}
		for tarefa in tarefas:
			columns[tarefa.status.value].append(self._task_payload(tarefa))
		return {
			'projeto': {
				'id': projeto.id,
				'nome': projeto.nome,
				'status': projeto.status.value,
				'progresso': projeto.progresso,
				'data_fim': projeto.data_fim,
			},
			'colunas': columns,
			'columns': columns,
		}

	async def _count(self, model, *conditions) -> int:
		stmt = select(func.count()).select_from(model)
		for condition in conditions:
			stmt = stmt.where(condition)
		return int((await self.session.execute(stmt)).scalar_one())

	async def _series_by_period(
		self, date_column, period: str, id_column, *conditions
	) -> list[dict[str, Any]]:
		bucket = func.date_trunc(period, date_column).label('periodo')
		stmt = select(bucket, func.count(id_column)).where(date_column.is_not(None))
		for condition in conditions:
			stmt = stmt.where(condition)
		stmt = stmt.group_by(bucket).order_by(bucket)
		rows = (await self.session.execute(stmt)).all()
		return [{'periodo': row[0], 'total': int(row[1])} for row in rows]

	async def _recent_leads(self) -> list[dict[str, Any]]:
		stmt = select(Lead).order_by(Lead.data.desc()).limit(10)
		leads = list((await self.session.execute(stmt)).scalars().all())
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
		stmt = (
			select(Funcionario, Usuario)
			.join(Usuario, Usuario.id == Funcionario.id)
			.order_by(Funcionario.xp_total.desc(), Usuario.nome)
			.limit(10)
		)
		rows = (await self.session.execute(stmt)).all()
		return [
			{
				'funcionario_id': funcionario.id,
				'nome': usuario.nome,
				'cargo': funcionario.cargo,
				'nivel': funcionario.nivel,
				'xp_total': funcionario.xp_total,
			}
			for funcionario, usuario in rows
		]

	async def _ensure_cliente(self, cliente_id: int) -> Cliente:
		cliente = await self.session.get(Cliente, cliente_id)
		if not cliente:
			raise NotFoundError('Cliente', cliente_id)
		return cliente

	async def _ensure_funcionario(self, funcionario_id: int) -> Funcionario:
		funcionario = await self.session.get(Funcionario, funcionario_id)
		if not funcionario:
			raise NotFoundError('Funcionario', funcionario_id)
		return funcionario

	async def _ensure_can_view_cliente(
		self, cliente_id: int, usuario_id: int | None, role: str | None
	) -> Cliente:
		cliente = await self._ensure_cliente(cliente_id)
		if role is None:
			return cliente
		if role == UserRole.ADMIN.value:
			return cliente
		if role == UserRole.CLIENTE.value and usuario_id == cliente_id:
			return cliente
		raise HTTPException(
			status_code=status.HTTP_403_FORBIDDEN,
			detail='Acesso negado para este dashboard de cliente',
		)

	async def _ensure_can_view_funcionario(
		self, funcionario_id: int, usuario_id: int | None, role: str | None
	) -> Funcionario:
		funcionario = await self._ensure_funcionario(funcionario_id)
		if role is None:
			return funcionario
		if role == UserRole.ADMIN.value:
			return funcionario
		if role == UserRole.FUNCIONARIO.value and usuario_id == funcionario_id:
			return funcionario
		raise HTTPException(
			status_code=status.HTTP_403_FORBIDDEN,
			detail='Acesso negado para este dashboard de funcionário',
		)

	async def _ensure_can_view_projeto(
		self, projeto: Projeto, usuario_id: int | None, role: str | None
	) -> None:
		if role is None:
			return
		if role == UserRole.ADMIN.value:
			return
		if role == UserRole.CLIENTE.value and projeto.cliente_id == usuario_id:
			return
		if role == UserRole.FUNCIONARIO.value:
			stmt = select(func.count()).select_from(ProjetoFuncionario).where(
				ProjetoFuncionario.projeto_id == projeto.id,
				ProjetoFuncionario.funcionario_id == usuario_id,
			)
			if int((await self.session.execute(stmt)).scalar_one()) > 0:
				return
		raise HTTPException(
			status_code=status.HTTP_403_FORBIDDEN,
			detail='Acesso negado para este projeto',
		)

	async def _projects_for_cliente(self, cliente_id: int) -> list[dict[str, Any]]:
		stmt = (
			select(Projeto).where(Projeto.cliente_id == cliente_id).order_by(Projeto.id)
		)
		projetos = list((await self.session.execute(stmt)).scalars().all())
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

	async def _upcoming_tasks(self, project_ids) -> list[dict[str, Any]]:
		stmt = (
			select(Tarefa)
			.where(Tarefa.projeto_id.in_(project_ids), Tarefa.prazo >= date.today())
			.order_by(Tarefa.prazo)
			.limit(10)
		)
		tarefas = list((await self.session.execute(stmt)).scalars().all())
		return [self._task_payload(tarefa) for tarefa in tarefas]

	async def _recent_announcements(self) -> list[dict[str, Any]]:
		stmt = select(Comunicado).order_by(Comunicado.data.desc()).limit(10)
		comunicados = list((await self.session.execute(stmt)).scalars().all())
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

	async def _events_for_user(self, usuario_id: int) -> list[dict[str, Any]]:
		stmt = (
			select(EventoAgenda)
			.where(EventoAgenda.usuario_id == usuario_id)
			.order_by(EventoAgenda.data, EventoAgenda.hora)
			.limit(20)
		)
		eventos = list((await self.session.execute(stmt)).scalars().all())
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

	async def _xp_for_funcionario(self, funcionario_id: int) -> int:
		start = datetime.now(timezone.utc).replace(
			day=1, hour=0, minute=0, second=0, microsecond=0
		)
		stmt = select(func.coalesce(func.sum(HistoricoXp.xp), 0)).where(
			HistoricoXp.funcionario_id == funcionario_id,
			HistoricoXp.data >= start,
		)
		return int((await self.session.execute(stmt)).scalar_one())

	async def _tasks_for_funcionario(self, funcionario_id: int) -> list[dict[str, Any]]:
		stmt = (
			select(Tarefa)
			.where(Tarefa.responsavel_id == funcionario_id)
			.order_by(Tarefa.status, Tarefa.prazo)
			.limit(20)
		)
		tarefas = list((await self.session.execute(stmt)).scalars().all())
		return [self._task_payload(tarefa) for tarefa in tarefas]

	async def _xp_history(self, funcionario_id: int) -> list[dict[str, Any]]:
		stmt = (
			select(HistoricoXp)
			.where(HistoricoXp.funcionario_id == funcionario_id)
			.order_by(HistoricoXp.data.desc())
			.limit(20)
		)
		rows = list((await self.session.execute(stmt)).scalars().all())
		return [
			{
				'id': row.id,
				'acao': row.acao,
				'xp': row.xp,
				'tarefa_id': row.tarefa_id,
				'data': row.data,
			}
			for row in rows
		]

	async def _achievements_for_funcionario(
		self, funcionario_id: int
	) -> list[dict[str, Any]]:
		stmt = (
			select(Conquista, FuncionarioConquista.desbloqueado_em)
			.join(
				FuncionarioConquista,
				FuncionarioConquista.conquista_id == Conquista.id,
			)
			.where(FuncionarioConquista.funcionario_id == funcionario_id)
			.order_by(FuncionarioConquista.desbloqueado_em.desc())
		)
		rows = (await self.session.execute(stmt)).all()
		return [
			{
				'id': conquista.id,
				'nome': conquista.nome,
				'icone': conquista.icone,
				'descricao': conquista.descricao,
				'xp_bonus': conquista.xp_bonus,
				'desbloqueado_em': desbloqueado_em,
			}
			for conquista, desbloqueado_em in rows
		]

	@staticmethod
	def _task_payload(tarefa: Tarefa) -> dict[str, Any]:
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
