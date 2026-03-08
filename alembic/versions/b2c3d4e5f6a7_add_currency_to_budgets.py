"""add currency to budgets

Revision ID: b2c3d4e5f6a7
Revises: aef448afaa15
Create Date: 2026-03-07 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b2c3d4e5f6a7'
down_revision: Union[str, None] = 'aef448afaa15'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('budgets', sa.Column('currency', sa.String(length=3), server_default='USD', nullable=False))

    # SQLite doesn't support dropping constraints directly, so we recreate the table
    # to update the unique constraint
    with op.batch_alter_table('budgets') as batch_op:
        batch_op.drop_constraint('uq_budget_category_period', type_='unique')
        batch_op.create_unique_constraint(
            'uq_budget_category_period_currency',
            ['category_id', 'year', 'month', 'currency']
        )


def downgrade() -> None:
    with op.batch_alter_table('budgets') as batch_op:
        batch_op.drop_constraint('uq_budget_category_period_currency', type_='unique')
        batch_op.create_unique_constraint(
            'uq_budget_category_period',
            ['category_id', 'year', 'month']
        )
    op.drop_column('budgets', 'currency')
