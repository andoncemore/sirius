"""empty message

Revision ID: 36ba0c7b9fbc
Revises: 5ac2a9d2e622
Create Date: 2017-05-01 15:11:19.337843

"""

# revision identifiers, used by Alembic.
revision = '36ba0c7b9fbc'
down_revision = '5ac2a9d2e622'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.add_column('user',
      sa.Column('api_key', sa.String())
    )


def downgrade():
    op.drop_column('user', 'api_key')
