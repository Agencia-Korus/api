from __future__ import annotations

import asyncio
import os
import sys
from datetime import date, datetime, time, timezone
from decimal import Decimal
from pathlib import Path
from typing import Any

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncConnection, create_async_engine

sys.path.append(str(Path(__file__).resolve().parents[1]))

from core.password import hash_password

PASSWORD_HASH = hash_password('senha-forte-123')


async def scalar(conn: AsyncConnection, sql: str, **params: Any) -> Any:
	return (await conn.execute(text(sql), params)).scalar_one()


async def maybe_scalar(conn: AsyncConnection, sql: str, **params: Any) -> Any:
	return (await conn.execute(text(sql), params)).scalar_one_or_none()


async def upsert_user(
	conn: AsyncConnection,
	nome: str,
	email: str,
	role: str,
	telefone: str = '(61) 99999-0000',
	avatar: str | None = None,
) -> int:
	return await scalar(
		conn,
		"""
		INSERT INTO usuario (nome, email, senha_hash, role, telefone, avatar, status)
		VALUES (:nome, :email, :senha_hash, :role, :telefone, :avatar, 'ativo')
		ON CONFLICT (email) DO UPDATE SET
			nome = EXCLUDED.nome,
			role = EXCLUDED.role,
			telefone = EXCLUDED.telefone,
			avatar = COALESCE(EXCLUDED.avatar, usuario.avatar),
			status = 'ativo'
		RETURNING id
		""",
		nome=nome,
		email=email,
		senha_hash=PASSWORD_HASH,
		role=role,
		telefone=telefone,
		avatar=avatar,
	)


async def upsert_project(
	conn: AsyncConnection,
	nome: str,
	cliente_id: int,
	servico_id: int,
	status: str,
	progresso: int,
	inicio: date,
	fim: date,
) -> int:
	projeto_id = await maybe_scalar(
		conn,
		'SELECT id FROM projeto WHERE nome=:nome AND cliente_id=:cliente_id',
		nome=nome,
		cliente_id=cliente_id,
	)
	if projeto_id:
		await conn.execute(
			text(
				"""
				UPDATE projeto
				SET servico_id=:servico_id,
					status=:status,
					progresso=:progresso,
					data_inicio=:inicio,
					data_fim=:fim,
					descricao=:descricao
				WHERE id=:id
				"""
			),
			{
				'id': projeto_id,
				'servico_id': servico_id,
				'status': status,
				'progresso': progresso,
				'inicio': inicio,
				'fim': fim,
				'descricao': f'Projeto {nome}',
			},
		)
		return projeto_id
	return await scalar(
		conn,
		"""
		INSERT INTO projeto (
			cliente_id, servico_id, nome, descricao, status, progresso,
			data_inicio, data_fim
		)
		VALUES (
			:cliente_id, :servico_id, :nome, :descricao, :status, :progresso,
			:inicio, :fim
		)
		RETURNING id
		""",
		cliente_id=cliente_id,
		servico_id=servico_id,
		nome=nome,
		descricao=f'Projeto {nome}',
		status=status,
		progresso=progresso,
		inicio=inicio,
		fim=fim,
	)


async def upsert_task(
	conn: AsyncConnection,
	projeto_id: int,
	responsavel_id: int,
	titulo: str,
	descricao: str,
	status: str,
	complexidade: str,
	categoria: str,
	prazo: date,
	ordem: int,
) -> int:
	prioridade = complexidade if complexidade in {'baixa', 'media', 'alta'} else 'alta'
	concluido_em = (
		datetime(2026, 4, 15, 12, 0, tzinfo=timezone.utc)
		if status == 'concluido'
		else None
	)
	tarefa_id = await maybe_scalar(
		conn,
		'SELECT id FROM tarefa WHERE projeto_id=:projeto_id AND titulo=:titulo',
		projeto_id=projeto_id,
		titulo=titulo,
	)
	params = {
		'projeto_id': projeto_id,
		'responsavel_id': responsavel_id,
		'titulo': titulo,
		'descricao': descricao,
		'status': status,
		'complexidade': complexidade,
		'prioridade': prioridade,
		'categoria': categoria,
		'prazo': prazo,
		'ordem': ordem,
		'concluido_em': concluido_em,
	}
	if tarefa_id:
		await conn.execute(
			text(
				"""
				UPDATE tarefa
				SET responsavel_id=:responsavel_id,
					descricao=:descricao,
					status=:status,
					complexidade=:complexidade,
					prioridade=:prioridade,
					categoria=:categoria,
					prazo=:prazo,
					ordem=:ordem,
					concluido_em=COALESCE(:concluido_em, concluido_em)
				WHERE id=:id
				"""
			),
			{**params, 'id': tarefa_id},
		)
		return tarefa_id
	return await scalar(
		conn,
		"""
		INSERT INTO tarefa (
			projeto_id, responsavel_id, titulo, descricao, status, complexidade,
			prioridade, categoria, prazo, ordem, concluido_em
		)
		VALUES (
			:projeto_id, :responsavel_id, :titulo, :descricao, :status,
			:complexidade, :prioridade, :categoria, :prazo, :ordem, :concluido_em
		)
		RETURNING id
		""",
		**params,
	)


async def main() -> None:  # noqa: PLR0912, PLR0914, PLR0915
	engine = create_async_engine(os.environ['DATABASE_URL'], pool_pre_ping=True)
	async with engine.begin() as conn:
		carlos = await upsert_user(
			conn,
			'Carlos Mendes',
			'carlos@korusagencia.com.br',
			'admin',
			avatar='https://images.unsplash.com/photo-1506794778202-cad84cf45f1d',
		)
		ana = await upsert_user(
			conn,
			'Ana Lima',
			'ana@korusagencia.com.br',
			'funcionario',
			avatar='https://images.unsplash.com/photo-1494790108377-be9c29b29330',
		)
		pedro = await upsert_user(
			conn,
			'Pedro Souza',
			'pedro@korusagencia.com.br',
			'funcionario',
			avatar='https://images.unsplash.com/photo-1500648767791-00dcc994a43e',
		)
		julia = await upsert_user(
			conn,
			'Julia Ramos',
			'julia@korusagencia.com.br',
			'funcionario',
			avatar='https://images.unsplash.com/photo-1438761681033-6461ffad8d80',
		)
		tech = await upsert_user(
			conn, 'Tech Solutions Ltda.', 'contato@techsol.com.br', 'cliente'
		)
		sabor = await upsert_user(
			conn, 'Restaurante Sabor & Arte', 'contato@saborarte.com', 'cliente'
		)
		rv = await upsert_user(
			conn, 'Consultoria RV', 'rv@consultoriasrv.com', 'cliente'
		)

		await conn.execute(
			text(
				"""
				INSERT INTO admin (id, nivel_acesso)
				VALUES (:id, 5)
				ON CONFLICT (id) DO UPDATE SET nivel_acesso=EXCLUDED.nivel_acesso
				"""
			),
			{'id': carlos},
		)
		await conn.execute(
			text(
				"""
				INSERT INTO admin (id, nivel_acesso)
				SELECT id, 1 FROM usuario WHERE role='admin'
				ON CONFLICT (id) DO NOTHING
				"""
			)
		)
		for funcionario_id, cargo, especialidade, xp, nivel in [
			(ana, 'Designer', 'Identidade Visual', 1240, 4),
			(pedro, 'Desenvolvedor', 'Web', 980, 3),
			(julia, 'Marketing', 'Social Media', 2100, 6),
		]:
			await conn.execute(
				text(
					"""
					INSERT INTO funcionario (
						id, cargo, especialidade, xp_total, nivel
					)
					VALUES (:id, :cargo, :especialidade, :xp, :nivel)
					ON CONFLICT (id) DO UPDATE SET
						cargo=:cargo,
						especialidade=:especialidade,
						xp_total=:xp,
						nivel=:nivel
					"""
				),
				{
					'id': funcionario_id,
					'cargo': cargo,
					'especialidade': especialidade,
					'xp': xp,
					'nivel': nivel,
				},
			)
		for cliente_id, razao, doc, segmento in [
			(tech, 'Tech Solutions Ltda.', 'techsol-demo', 'Tecnologia'),
			(sabor, 'Restaurante Sabor & Arte', 'sabor-demo', 'Gastronomia'),
			(rv, 'Consultoria RV', 'rv-demo', 'Consultoria'),
		]:
			await conn.execute(
				text(
					"""
					INSERT INTO cliente (id, razao_social, cnpj_cpf, segmento)
					VALUES (:id, :razao, :doc, :segmento)
					ON CONFLICT (id) DO UPDATE SET
						razao_social=:razao,
						cnpj_cpf=:doc,
						segmento=:segmento
					"""
				),
				{
					'id': cliente_id,
					'razao': razao,
					'doc': doc,
					'segmento': segmento,
				},
			)

		services = [
			(
				'Identidade Visual',
				'identidade-visual',
				'Criamos a identidade visual completa da sua marca.',
				'palette',
			),
			(
				'Gestao de Redes Sociais',
				'gestao-redes-sociais',
				'Gerenciamos suas redes sociais com estrategia e conteudo.',
				'share',
			),
			(
				'Desenvolvimento Web',
				'desenvolvimento-web',
				'Sites modernos, responsivos e otimizados.',
				'globe',
			),
			(
				'Marketing de Conteudo',
				'marketing-conteudo',
				'Conteudo estrategico para atrair e converter.',
				'file-text',
			),
			(
				'Trafego Pago',
				'trafego-pago',
				'Campanhas Meta e Google Ads.',
				'megaphone',
			),
			(
				'Fotografia e Video',
				'fotografia-video',
				'Producao audiovisual profissional.',
				'camera',
			),
		]
		service_ids = {}
		for nome, slug, descricao, icone in services:
			service_ids[slug] = await scalar(
				conn,
				"""
				INSERT INTO servico (nome, slug, descricao, icone, status)
				VALUES (:nome, :slug, :descricao, :icone, 'ativo')
				ON CONFLICT (slug) DO UPDATE SET
					nome=:nome,
					descricao=:descricao,
					icone=:icone,
					status='ativo'
				RETURNING id
				""",
				nome=nome,
				slug=slug,
				descricao=descricao,
				icone=icone,
			)

		deliverables = {
			'identidade-visual': [
				'Logotipo',
				'Paleta de cores',
				'Tipografia',
				'Manual da marca',
				'Papelaria',
			],
			'gestao-redes-sociais': [
				'Planejamento editorial',
				'Criacao de posts',
				'Gestao de comunidade',
				'Relatorios mensais',
			],
			'desenvolvimento-web': [
				'Wireframes',
				'Design UI/UX',
				'Desenvolvimento responsivo',
				'SEO tecnico',
			],
			'marketing-conteudo': [
				'Estrategia de conteudo',
				'Blog posts',
				'Calendario editorial',
				'Copywriting',
			],
		}
		for slug, items in deliverables.items():
			await conn.execute(
				text('DELETE FROM entregavel WHERE servico_id=:servico_id'),
				{'servico_id': service_ids[slug]},
			)
			for ordem, descricao in enumerate(items, start=1):
				await conn.execute(
					text(
						"""
						INSERT INTO entregavel (servico_id, descricao, ordem)
						VALUES (:servico_id, :descricao, :ordem)
						"""
					),
					{
						'servico_id': service_ids[slug],
						'descricao': descricao,
						'ordem': ordem,
					},
				)

		p_tech = await upsert_project(
			conn,
			'Identidade Visual Tech Solutions',
			tech,
			service_ids['identidade-visual'],
			'em_andamento',
			65,
			date(2026, 2, 1),
			date(2026, 5, 30),
		)
		p_sabor = await upsert_project(
			conn,
			'Site Institucional Sabor & Arte',
			sabor,
			service_ids['desenvolvimento-web'],
			'em_revisao',
			90,
			date(2026, 2, 20),
			date(2026, 4, 30),
		)
		p_rv = await upsert_project(
			conn,
			'Gestao de Redes RV',
			rv,
			service_ids['gestao-redes-sociais'],
			'planejamento',
			10,
			date(2026, 4, 1),
			date(2026, 6, 30),
		)
		for projeto_id, funcionario_id, papel in [
			(p_tech, ana, 'Design'),
			(p_tech, julia, 'Marketing'),
			(p_sabor, pedro, 'Desenvolvimento'),
			(p_rv, julia, 'Social Media'),
		]:
			await conn.execute(
				text(
					"""
					INSERT INTO projeto_funcionario (
						projeto_id, funcionario_id, papel
					)
					VALUES (:projeto_id, :funcionario_id, :papel)
					ON CONFLICT (projeto_id, funcionario_id)
					DO UPDATE SET papel=:papel
					"""
				),
				{
					'projeto_id': projeto_id,
					'funcionario_id': funcionario_id,
					'papel': papel,
				},
			)

		task_ids = {}
		for task in [
			(
				p_tech,
				ana,
				'Criar logotipo',
				'Desenvolver o logo principal',
				'a_fazer',
				'alta',
				'design',
				date(2026, 3, 15),
				1,
			),
			(
				p_tech,
				ana,
				'Manual da marca',
				'Documentar guidelines',
				'a_fazer',
				'media',
				'marketing',
				date(2026, 4, 1),
				2,
			),
			(
				p_tech,
				ana,
				'Definir paleta de cores',
				'Selecionar cores institucionais',
				'em_progresso',
				'media',
				'design',
				date(2026, 3, 1),
				1,
			),
			(
				p_tech,
				ana,
				'Criar moodboard',
				'Referencias visuais aprovadas',
				'concluido',
				'media',
				'design',
				date(2026, 2, 15),
				1,
			),
			(
				p_sabor,
				pedro,
				'Publicar homepage',
				'Subir versao de revisao',
				'em_revisao',
				'alta',
				'web',
				date(2026, 4, 20),
				1,
			),
			(
				p_rv,
				julia,
				'Planejamento editorial',
				'Calendario inicial',
				'a_fazer',
				'media',
				'social',
				date(2026, 5, 10),
				1,
			),
		]:
			task_ids[task[2]] = await upsert_task(conn, *task)

		await conn.execute(
			text(
				"""
				DELETE FROM comentario
				WHERE tarefa_id=:tarefa_id
					AND conteudo='Iniciando o trabalho nesta tarefa.'
				"""
			),
			{'tarefa_id': task_ids['Criar logotipo']},
		)
		await conn.execute(
			text(
				"""
				INSERT INTO comentario (tarefa_id, autor_id, conteudo, criado_em)
				VALUES (:tarefa_id, :autor_id, :conteudo, :criado_em)
				"""
			),
			{
				'tarefa_id': task_ids['Criar logotipo'],
				'autor_id': carlos,
				'conteudo': 'Iniciando o trabalho nesta tarefa.',
				'criado_em': datetime(2026, 4, 14, 10, 30, tzinfo=timezone.utc),
			},
		)

		for nome, cliente, categoria, descricao, imagem, ano, destaque, tags in [
			(
				'Rebranding Tech Solutions',
				'Tech Solutions',
				'Identidade Visual',
				'Projeto desenvolvido pela Korus Agency com foco em resultados.',
				'https://images.unsplash.com/photo-1528459801416-a9e53bbf4e17',
				2025,
				True,
				['branding', 'design'],
			),
			(
				'Campanha Digital RV',
				'Consultoria RV',
				'Social Media',
				'Campanha para ampliar presenca digital.',
				'https://images.unsplash.com/photo-1516321318423-f06f85e504b3',
				2025,
				True,
				['social', 'performance'],
			),
			(
				'Cobertura Evento Tech Summit',
				'Tech Solutions',
				'Fotografia',
				'Cobertura fotografica para evento corporativo.',
				'https://images.unsplash.com/photo-1516035069371-29a1b244cc32',
				2025,
				False,
				['foto', 'evento'],
			),
			(
				'Estrategia de Conteudo StartUp X',
				'StartUp X',
				'Social Media',
				'Planejamento de conteudo para lancamento.',
				'https://images.unsplash.com/photo-1551288049-bebda4e38f71',
				2025,
				False,
				['conteudo'],
			),
		]:
			exists = await maybe_scalar(
				conn, 'SELECT id FROM portfolio WHERE nome=:nome', nome=nome
			)
			if not exists:
				await conn.execute(
					text(
						"""
						INSERT INTO portfolio (
							nome, cliente, categoria, descricao, imagem, ano,
							destaque, tags
						)
						VALUES (
							:nome, :cliente, :categoria, :descricao, :imagem,
							:ano, :destaque, :tags
						)
						"""
					),
					{
						'nome': nome,
						'cliente': cliente,
						'categoria': categoria,
						'descricao': descricao,
						'imagem': imagem,
						'ano': ano,
						'destaque': destaque,
						'tags': tags,
					},
				)

		for titulo, tipo, descricao, preco, imagem, url in [
			(
				'Guia Completo de Branding',
				'ebook',
				'Tudo que voce precisa saber para construir uma marca forte.',
				Decimal('0'),
				'https://images.unsplash.com/photo-1542291026-7eec264c27ff',
				'https://korus.local/branding',
			),
			(
				'Marketing Digital do Zero',
				'curso',
				'Aprenda as bases do marketing digital com a Korus.',
				Decimal('197.00'),
				'https://images.unsplash.com/photo-1460925895917-afdab827c52f',
				'https://korus.local/marketing',
			),
			(
				'Social Media para Negocios',
				'ebook',
				'Como usar redes sociais para alavancar seu negocio.',
				Decimal('29.90'),
				'https://images.unsplash.com/photo-1516321497487-e288fb19713f',
				'https://korus.local/social',
			),
			(
				'Fotografia para Redes Sociais',
				'curso',
				'Tecnicas de fotografia para criar conteudo profissional.',
				Decimal('147.00'),
				'https://images.unsplash.com/photo-1520390138845-fd2d229dd553',
				'https://korus.local/foto',
			),
		]:
			exists = await maybe_scalar(
				conn, 'SELECT id FROM academy WHERE titulo=:titulo', titulo=titulo
			)
			if not exists:
				await conn.execute(
					text(
						"""
						INSERT INTO academy (
							titulo, tipo, descricao, preco, imagem,
							url_externa, publicado
						)
						VALUES (
							:titulo, :tipo, :descricao, :preco, :imagem,
							:url, true
						)
						"""
					),
					{
						'titulo': titulo,
						'tipo': tipo,
						'descricao': descricao,
						'preco': preco,
						'imagem': imagem,
						'url': url,
					},
				)

		for titulo, conteudo, alvo, data in [
			(
				'Novo projeto aprovado!',
				'O projeto de identidade visual para a Tech Solutions foi aprovado.',
				'funcionarios',
				datetime(2026, 4, 15, 9, 0, tzinfo=timezone.utc),
			),
			(
				'Atualizacao de processos',
				'Todos os projetos deverao seguir o novo fluxo de aprovacao.',
				'todos',
				datetime(2026, 4, 14, 9, 0, tzinfo=timezone.utc),
			),
			(
				'Entrega parcial disponivel',
				'As primeiras versoes estao prontas para revisao.',
				'clientes',
				datetime(2026, 4, 13, 9, 0, tzinfo=timezone.utc),
			),
		]:
			exists = await maybe_scalar(
				conn, 'SELECT id FROM comunicado WHERE titulo=:titulo', titulo=titulo
			)
			if not exists:
				await conn.execute(
					text(
						"""
						INSERT INTO comunicado (
							autor_id, titulo, conteudo, alvo, data
						)
						VALUES (:autor_id, :titulo, :conteudo, :alvo, :data)
						"""
					),
					{
						'autor_id': carlos,
						'titulo': titulo,
						'conteudo': conteudo,
						'alvo': alvo,
						'data': data,
					},
				)

		for usuario_id, titulo, tipo, data, hora in [
			(
				tech,
				'Apresentacao da identidade',
				'reuniao',
				date(2026, 4, 30),
				time(16, 0),
			),
			(ana, 'Reuniao kickoff', 'reuniao', date(2026, 4, 22), time(10, 0)),
			(
				ana,
				'Revisao de moodboard',
				'entrega',
				date(2026, 4, 28),
				time(15, 0),
			),
			(carlos, 'Sprint Planning', 'reuniao', date(2026, 4, 28), time(9, 0)),
		]:
			exists = await maybe_scalar(
				conn,
				"""
				SELECT id FROM evento_agenda
				WHERE usuario_id=:usuario_id AND titulo=:titulo AND data=:data
				""",
				usuario_id=usuario_id,
				titulo=titulo,
				data=data,
			)
			if not exists:
				await conn.execute(
					text(
						"""
						INSERT INTO evento_agenda (
							usuario_id, titulo, tipo, data, hora, duracao_min
						)
						VALUES (:usuario_id, :titulo, :tipo, :data, :hora, 60)
						"""
					),
					{
						'usuario_id': usuario_id,
						'titulo': titulo,
						'tipo': tipo,
						'data': data,
						'hora': hora,
					},
				)

		conquista_ids = []
		for nome, icone, descricao, bonus in [
			('Primeira Tarefa', 'star', 'Concluiu a primeira tarefa.', 25),
			('5 Projetos', 'trophy', 'Participou de 5 projetos.', 100),
			('Mes Perfeito', 'calendar', 'Entregou todas as tarefas do mes.', 150),
			('Top da Semana', 'award', 'Ficou no ranking semanal.', 50),
		]:
			conquista_id = await maybe_scalar(
				conn, 'SELECT id FROM conquista WHERE nome=:nome', nome=nome
			)
			if not conquista_id:
				conquista_id = await scalar(
					conn,
					"""
					INSERT INTO conquista (nome, icone, descricao, xp_bonus)
					VALUES (:nome, :icone, :descricao, :bonus)
					RETURNING id
					""",
					nome=nome,
					icone=icone,
					descricao=descricao,
					bonus=bonus,
				)
			conquista_ids.append(conquista_id)
		for funcionario_id, conquista_id in [
			(ana, conquista_ids[0]),
			(ana, conquista_ids[3]),
			(julia, conquista_ids[1]),
			(julia, conquista_ids[2]),
		]:
			await conn.execute(
				text(
					"""
					INSERT INTO funcionario_conquista (
						funcionario_id, conquista_id
					)
					VALUES (:funcionario_id, :conquista_id)
					ON CONFLICT DO NOTHING
					"""
				),
				{
					'funcionario_id': funcionario_id,
					'conquista_id': conquista_id,
				},
			)

		for funcionario_id, tarefa_id, acao, xp, data in [
			(
				ana,
				task_ids['Criar moodboard'],
				'Concluiu tarefa: Criar moodboard',
				25,
				datetime(2026, 4, 15, 12, 0, tzinfo=timezone.utc),
			),
			(
				ana,
				task_ids['Definir paleta de cores'],
				'Iniciou tarefa: Definir paleta de cores',
				10,
				datetime(2026, 4, 14, 12, 0, tzinfo=timezone.utc),
			),
			(
				julia,
				None,
				'Concluiu campanha integrada',
				100,
				datetime(2026, 4, 15, 11, 0, tzinfo=timezone.utc),
			),
			(
				pedro,
				None,
				'Publicou entrega parcial',
				50,
				datetime(2026, 4, 13, 11, 0, tzinfo=timezone.utc),
			),
		]:
			exists = await maybe_scalar(
				conn,
				"""
				SELECT id FROM historico_xp
				WHERE funcionario_id=:funcionario_id AND acao=:acao AND data=:data
				""",
				funcionario_id=funcionario_id,
				acao=acao,
				data=data,
			)
			if not exists:
				await conn.execute(
					text(
						"""
						INSERT INTO historico_xp (
							funcionario_id, tarefa_id, acao, xp, data
						)
						VALUES (
							:funcionario_id, :tarefa_id, :acao, :xp, :data
						)
						"""
					),
					{
						'funcionario_id': funcionario_id,
						'tarefa_id': tarefa_id,
						'acao': acao,
						'xp': xp,
						'data': data,
					},
				)

		for nome, email, empresa, slug, orcamento, status, prioridade, prazo in [
			(
				'Marcos Silva',
				'marcos@email.com',
				'Marcos Studio',
				'identidade-visual',
				'R$ 3.000 - R$ 5.000',
				'novo',
				'alta',
				date(2026, 5, 30),
			),
			(
				'Fernanda Costa',
				'fernanda@email.com',
				'FC Moda',
				'gestao-redes-sociais',
				'R$ 2.000 - R$ 3.000',
				'em_contato',
				'media',
				date(2026, 6, 10),
			),
			(
				'Roberto Alves',
				'roberto@email.com',
				'Alves Tech',
				'desenvolvimento-web',
				'R$ 10.000 - R$ 20.000',
				'qualificado',
				'alta',
				date(2026, 7, 1),
			),
			(
				'Camila Santos',
				'camila@email.com',
				'Santos Consultoria',
				'marketing-conteudo',
				'R$ 1.500 - R$ 3.000',
				'convertido',
				'media',
				date(2026, 5, 25),
			),
		]:
			exists = await maybe_scalar(
				conn,
				'SELECT id FROM lead WHERE email=:email AND nome=:nome',
				email=email,
				nome=nome,
			)
			if not exists:
				await conn.execute(
					text(
						"""
						INSERT INTO lead (
							nome, email, whatsapp, empresa, servico_id,
							orcamento, prazo_desejado, mensagem, status,
							prioridade, termos_aceitos
						)
						VALUES (
							:nome, :email, '(61) 99999-0000', :empresa,
							:servico_id, :orcamento, :prazo, :mensagem,
							:status, :prioridade, true
						)
						"""
					),
					{
						'nome': nome,
						'email': email,
						'empresa': empresa,
						'servico_id': service_ids[slug],
						'orcamento': orcamento,
						'prazo': prazo,
						'mensagem': 'Solicitacao criada pelo formulario do site.',
						'status': status,
						'prioridade': prioridade,
					},
				)

	await engine.dispose()
	print({'seed': 'ok'})


if __name__ == '__main__':
	asyncio.run(main())