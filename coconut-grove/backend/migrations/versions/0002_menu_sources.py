"""Allow unknown menu facts and retain source provenance."""
from alembic import op
import sqlalchemy as sa

revision = "0002_menu_sources"
down_revision = "0001_catalog"
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table("dishes", table_args=(
        sa.CheckConstraint("spice_level >= 0 AND spice_level <= 5", name="ck_dishes_spice"),
        sa.CheckConstraint("preparation_min >= 0 AND preparation_max >= preparation_min", name="ck_dishes_preparation"),
    )) as batch:
        for name in ("preparation_min", "preparation_max", "spice_level"):
            batch.alter_column(name, existing_type=sa.Integer(), nullable=True)
        batch.add_column(sa.Column("source_url", sa.String(500), nullable=True))
        batch.add_column(sa.Column("source_observed_on", sa.String(10), nullable=True))
    with op.batch_alter_table("portions", table_args=(sa.CheckConstraint("price_minor >= 0", name="ck_portions_price"),)) as batch:
        batch.alter_column("price_minor", existing_type=sa.Integer(), nullable=True)


def downgrade():
    # Unknown values cannot safely become fabricated estimates on downgrade.
    connection = op.get_bind()
    unknown = connection.scalar(sa.text("SELECT COUNT(*) FROM dishes WHERE preparation_min IS NULL OR preparation_max IS NULL OR spice_level IS NULL"))
    unknown += connection.scalar(sa.text("SELECT COUNT(*) FROM portions WHERE price_minor IS NULL"))
    if unknown:
        raise RuntimeError("Export/remove sourced rows with unknown facts before downgrading.")
    with op.batch_alter_table("portions") as batch:
        batch.alter_column("price_minor", existing_type=sa.Integer(), nullable=False)
    with op.batch_alter_table("dishes") as batch:
        batch.drop_column("source_observed_on")
        batch.drop_column("source_url")
        for name in ("preparation_min", "preparation_max", "spice_level"):
            batch.alter_column(name, existing_type=sa.Integer(), nullable=False)
