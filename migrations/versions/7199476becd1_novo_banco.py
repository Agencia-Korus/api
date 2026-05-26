# ruff: noqa: E501
"""novo banco

Revision ID: 7199476becd1
Revises: 20260522_0002
Create Date: 2026-05-23 19:51:54.574874

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# Identificadores de revisão usados pelo Alembic.
revision: str = '7199476becd1'
down_revision: Union[str, Sequence[str], None] = '20260522_0002'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
	"""Aplica avanço do esquema."""
	# ### comandos gerados automaticamente pelo Alembic - ajuste se necessário! ###
	op.drop_index(op.f('idx_academy_publicado'), table_name='academy')
	op.drop_index(op.f('idx_anexo_tarefa'), table_name='anexo')
	op.drop_index(op.f('idx_comentario_tarefa'), table_name='comentario')
	op.drop_index(op.f('idx_comunicado_alvo'), table_name='comunicado')
	op.drop_index(op.f('idx_consentimento_usuario'), table_name='consentimento_lgpd')
	op.alter_column(
		'entregavel',
		'descricao',
		existing_type=sa.VARCHAR(length=255),
		type_=sa.String(length=500),
		existing_nullable=False,
	)
	op.drop_index(op.f('idx_entregavel_servico'), table_name='entregavel')
	op.drop_index(op.f('idx_historico_funcionario'), table_name='historico_xp')
	op.drop_index(op.f('idx_lead_servico'), table_name='lead')
	op.drop_index(op.f('idx_lead_status'), table_name='lead')
	op.drop_index(
		op.f('idx_portfolio_destaque'),
		table_name='portfolio',
		postgresql_where='(destaque = true)',
	)
	op.drop_index(op.f('idx_projeto_cliente'), table_name='projeto')
	op.drop_index(op.f('idx_projeto_status'), table_name='projeto')
	op.drop_index(op.f('idx_tarefa_projeto'), table_name='tarefa')
	op.drop_index(op.f('idx_tarefa_responsavel'), table_name='tarefa')
	op.drop_index(op.f('idx_tarefa_status'), table_name='tarefa')
	op.drop_index(op.f('idx_usuario_role'), table_name='usuario')
	# ### fim dos comandos do Alembic ###


def downgrade() -> None:
	"""Reverte avanço do esquema."""
	# ### comandos gerados automaticamente pelo Alembic - ajuste se necessário! ###
	op.create_index(op.f('idx_usuario_role'), 'usuario', ['role'], unique=False)
	op.create_index(op.f('idx_tarefa_status'), 'tarefa', ['status'], unique=False)
	op.create_index(
		op.f('idx_tarefa_responsavel'), 'tarefa', ['responsavel_id'], unique=False
	)
	op.create_index(op.f('idx_tarefa_projeto'), 'tarefa', ['projeto_id'], unique=False)
	op.create_index(op.f('idx_projeto_status'), 'projeto', ['status'], unique=False)
	op.create_index(
		op.f('idx_projeto_cliente'), 'projeto', ['cliente_id'], unique=False
	)
	op.create_index(
		op.f('idx_portfolio_destaque'),
		'portfolio',
		['destaque'],
		unique=False,
		postgresql_where='(destaque = true)',
	)
	op.create_index(op.f('idx_lead_status'), 'lead', ['status'], unique=False)
	op.create_index(op.f('idx_lead_servico'), 'lead', ['servico_id'], unique=False)
	op.create_index(
		op.f('idx_historico_funcionario'),
		'historico_xp',
		['funcionario_id', sa.literal_column('data DESC')],
		unique=False,
	)
	op.create_index(
		op.f('idx_entregavel_servico'), 'entregavel', ['servico_id'], unique=False
	)
	op.alter_column(
		'entregavel',
		'descricao',
		existing_type=sa.String(length=500),
		type_=sa.VARCHAR(length=255),
		existing_nullable=False,
	)
	op.create_index(
		op.f('idx_consentimento_usuario'),
		'consentimento_lgpd',
		['usuario_id'],
		unique=False,
	)
	op.create_index(op.f('idx_comunicado_alvo'), 'comunicado', ['alvo'], unique=False)
	op.create_index(
		op.f('idx_comentario_tarefa'), 'comentario', ['tarefa_id'], unique=False
	)
	op.create_index(op.f('idx_anexo_tarefa'), 'anexo', ['tarefa_id'], unique=False)
	op.create_index(
		op.f('idx_academy_publicado'), 'academy', ['publicado'], unique=False
	)
	# ### fim dos comandos do Alembic ###
