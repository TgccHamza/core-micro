"""empty message

Revision ID: 7bd587b9bbe4
Revises: 75b3a1cfd8ef
Create Date: 2024-11-15 10:40:39.909954

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '7bd587b9bbe4'
down_revision: Union[str, None] = '75b3a1cfd8ef'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('projects', sa.Column('start_time', sa.DateTime(), nullable=True))
    op.add_column('projects', sa.Column('end_time', sa.DateTime(), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('projects', 'end_time')
    op.drop_column('projects', 'start_time')
    # ### end Alembic commands ###