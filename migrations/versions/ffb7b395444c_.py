"""empty message

Revision ID: ffb7b395444c
Revises: cb3efc15544c
Create Date: 2019-10-07 20:09:54.727720

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'ffb7b395444c'
down_revision = 'cb3efc15544c'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('user_account', sa.Column('user_name', sa.String(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('user_account', 'user_name')
    # ### end Alembic commands ###
