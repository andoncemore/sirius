"""empty message

Revision ID: 15dd8689e7fe
Revises: 18ec55ca3e22
Create Date: 2018-01-10 17:21:00.034598

"""

# revision identifiers, used by Alembic.
revision = '15dd8689e7fe'
down_revision = '18ec55ca3e22'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.create_table('print_key',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('secret', sa.String(), nullable=True),
    sa.Column('created', sa.DateTime(), nullable=True),
    sa.Column('printer_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['printer_id'], ['printer.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('secret')
    )


def downgrade():
    op.drop_table('print_key')
