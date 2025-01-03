"""empty message

Revision ID: 8f1b52798280
Revises: 60de946d2e25
Create Date: 2024-11-19 01:23:58.373447

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '8f1b52798280'
down_revision: Union[str, None] = '60de946d2e25'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('projects', sa.Column('game_type', sa.Enum('DIGITAL', 'PHYGITAL', 'PHYSICAL', name='gametype'), nullable=True))
    op.add_column('projects', sa.Column('playing_type', sa.Enum('SOLO', 'TEAM', name='playingtype'), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('projects', 'playing_type')
    op.drop_column('projects', 'game_type')
    # ### end Alembic commands ###
