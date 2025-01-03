"""empty message

Revision ID: 7822fb59b476
Revises: acf872e2bcd8
Create Date: 2024-11-21 10:15:34.948263

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision: str = '7822fb59b476'
down_revision: Union[str, None] = '177e0e9b04ef'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('arena_session_players', 'email_status',
               existing_type=mysql.ENUM('PENDING', 'SENT', 'FAILED', 'DELIVERED'),
               nullable=True)
    op.alter_column('arena_sessions', 'period_type',
               existing_type=mysql.ENUM('FREE', 'RANGE'),
               nullable=True)
    op.alter_column('arena_sessions', 'start_time',
               existing_type=mysql.DATETIME(),
               nullable=True)
    op.alter_column('arena_sessions', 'access_status',
               existing_type=mysql.ENUM('AUTH', 'GUEST'),
               nullable=True)
    op.alter_column('arena_sessions', 'session_status',
               existing_type=mysql.ENUM('PENDING', 'PLAYING', 'ENDED'),
               nullable=True)
    op.alter_column('arena_sessions', 'view_access',
               existing_type=mysql.ENUM('ALL', 'GAME', 'SESSION', 'NONE'),
               nullable=True)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('arena_sessions', 'view_access',
               existing_type=mysql.ENUM('ALL', 'GAME', 'SESSION', 'NONE'),
               nullable=False)
    op.alter_column('arena_sessions', 'session_status',
               existing_type=mysql.ENUM('PENDING', 'PLAYING', 'ENDED'),
               nullable=False)
    op.alter_column('arena_sessions', 'access_status',
               existing_type=mysql.ENUM('AUTH', 'GUEST'),
               nullable=False)
    op.alter_column('arena_sessions', 'start_time',
               existing_type=mysql.DATETIME(),
               nullable=False)
    op.alter_column('arena_sessions', 'period_type',
               existing_type=mysql.ENUM('FREE', 'RANGE'),
               nullable=False)
    op.alter_column('arena_session_players', 'email_status',
               existing_type=mysql.ENUM('PENDING', 'SENT', 'FAILED', 'DELIVERED'),
               nullable=False)
    # ### end Alembic commands ###
