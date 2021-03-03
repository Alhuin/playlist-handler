"""empty message

Revision ID: 635e91180d41
Revises: 2332f08e9430
Create Date: 2021-03-03 10:49:17.859153

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '635e91180d41'
down_revision = '2332f08e9430'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('soundcloud_tkn',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('token', sa.String(length=1000), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.drop_column('users', 'soundcloud_tkn')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('users', sa.Column('soundcloud_tkn', sa.VARCHAR(length=1000), autoincrement=False, nullable=True))
    op.drop_table('soundcloud_tkn')
    # ### end Alembic commands ###