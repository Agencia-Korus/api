"""Adiciona campos de sincronização com Google Calendar aos eventos da agenda.

Revision ID: 20260522_0002
Revises: 20260518_0001
Create Date: 2026-05-22
"""

from collections.abc import Sequence

from alembic import op

revision: str = '20260522_0002'
down_revision: str | Sequence[str] | None = '20260518_0001'
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
	op.execute(
		"""
		ALTER TABLE evento_agenda
		ADD COLUMN IF NOT EXISTS google_event_id VARCHAR(255),
		ADD COLUMN IF NOT EXISTS google_link VARCHAR(500);
		"""
	)
	op.execute(
		"""
		CREATE UNIQUE INDEX IF NOT EXISTS ux_evento_agenda_google_event_id
		ON evento_agenda(google_event_id)
		WHERE google_event_id IS NOT NULL;
		"""
	)


def downgrade() -> None:
	op.execute('DROP INDEX IF EXISTS ux_evento_agenda_google_event_id;')
	op.execute(
		"""
		ALTER TABLE evento_agenda
		DROP COLUMN IF EXISTS google_link,
		DROP COLUMN IF EXISTS google_event_id;
		"""
	)
