"""add table tb_sapling_api_responses

Revision ID: 0d104ff39900
Revises: 84b9c79ee8fe
Create Date: 2023-09-11 15:47:13.009842

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0d104ff39900'
down_revision = '84b9c79ee8fe'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('sapling_api_responses',
    sa.Column('post_id', sa.String(length=255), nullable=False),
    sa.Column('text', sa.String(length=1000), nullable=False),
    sa.Column('result', sa.String(length=1000), nullable=False),
    sa.Column('corrections', sa.JSON(), nullable=True),
    sa.PrimaryKeyConstraint('post_id'),
    sa.UniqueConstraint('post_id')
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('sapling_api_responses')
    # ### end Alembic commands ###
