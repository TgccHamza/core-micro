"""empty message

Revision ID: 8400f45fe46a
Revises: 98f3b3a9ec51
Create Date: 2024-11-07 08:38:49.655805

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '8400f45fe46a'
down_revision: Union[str, None] = '98f3b3a9ec51'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('arena_sessions', sa.Column('project_id', sa.String(length=36), nullable=True))
    op.add_column('arena_sessions', sa.Column('module_id', sa.String(length=36), nullable=True))
    op.add_column('project_modules', sa.Column('template_code', sa.String(length=255), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('project_modules', 'template_code')
    op.drop_column('arena_sessions', 'module_id')
    op.drop_column('arena_sessions', 'project_id')
    # ### end Alembic commands ###