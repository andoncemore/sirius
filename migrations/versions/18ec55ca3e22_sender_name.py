"""empty message

Revision ID: 18ec55ca3e22
Revises: 36ba0c7b9fbc
Create Date: 2018-01-10 16:50:07.468905

"""

# revision identifiers, used by Alembic.
revision = '18ec55ca3e22'
down_revision = '36ba0c7b9fbc'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.add_column('message', sa.Column('sender_name', sa.String(), nullable=True))
    op.drop_column('message', 'sender_id')


def downgrade():
    op.add_column('message', sa.Column('sender_id', sa.INTEGER(), autoincrement=False, nullable=True))
    op.drop_column('message', 'sender_name')
