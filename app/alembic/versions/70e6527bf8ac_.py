"""empty message

Revision ID: 70e6527bf8ac
Revises: 75b3a1cfd8ef
Create Date: 2024-11-15 10:14:23.137405

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '70e6527bf8ac'
down_revision: Union[str, None] = '7bd587b9bbe4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('project_favorites',
    sa.Column('id', sa.String(length=36), nullable=False),
    sa.Column('project_id', sa.String(length=36), nullable=True),
    sa.Column('user_id', sa.String(length=36), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_project_favorites_project_id'), 'project_favorites', ['project_id'], unique=False)
    op.create_index(op.f('ix_project_favorites_user_id'), 'project_favorites', ['user_id'], unique=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_project_favorites_user_id'), table_name='project_favorites')
    op.drop_index(op.f('ix_project_favorites_project_id'), table_name='project_favorites')
    op.drop_table('project_favorites')
    # ### end Alembic commands ###