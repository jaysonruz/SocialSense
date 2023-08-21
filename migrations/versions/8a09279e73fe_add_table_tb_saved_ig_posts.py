"""add table tb_saved_ig_posts

Revision ID: 8a09279e73fe
Revises: 9aaed23990ab
Create Date: 2023-08-16 17:31:54.265653

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '8a09279e73fe'
down_revision = '9aaed23990ab'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('saved_ig_posts',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('caption', sa.String(length=1000), nullable=False),
    sa.Column('displayUrl_hosted', sa.String(length=255), nullable=False),
    sa.Column('correction_results', sa.String(length=1000), nullable=False),
    sa.Column('helpful', sa.Boolean(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('saved_ig_posts')
    # ### end Alembic commands ###