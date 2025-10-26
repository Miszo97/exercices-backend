"""
Remove unit column from duration_exercise_entry

Revision ID: 0001_remove_unit
Revises: 
Create Date: 2025-10-26 15:55:00.000000
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '0001_remove_unit'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Drop the 'unit' column from the duration_exercise_entry table
    with op.batch_alter_table('duration_exercise_entry') as batch_op:
        batch_op.drop_column('unit')


def downgrade() -> None:
    # Recreate the 'unit' column (will be NULL for existing rows)
    with op.batch_alter_table('duration_exercise_entry') as batch_op:
        batch_op.add_column(sa.Column('unit', sa.String(), nullable=True))
