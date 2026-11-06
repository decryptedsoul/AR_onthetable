"""Published restaurant menu, categories and portion variants."""
from alembic import op
import sqlalchemy as sa

revision = "0001_catalog"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table("restaurants",
        sa.Column("id", sa.String(80), primary_key=True), sa.Column("name", sa.String(160), nullable=False),
        sa.Column("location", sa.String(240), nullable=False), sa.Column("instagram_url", sa.String(500), nullable=False),
        sa.Column("currency", sa.String(3), nullable=False))
    op.create_table("categories",
        sa.Column("id", sa.String(100), primary_key=True),
        sa.Column("restaurant_id", sa.String(80), sa.ForeignKey("restaurants.id"), nullable=False),
        sa.Column("name", sa.String(80), nullable=False), sa.Column("position", sa.Integer, nullable=False),
        sa.UniqueConstraint("restaurant_id", "name"))
    op.create_index("ix_categories_restaurant_id", "categories", ["restaurant_id"])
    op.create_table("dishes",
        sa.Column("id", sa.String(100), primary_key=True),
        sa.Column("restaurant_id", sa.String(80), sa.ForeignKey("restaurants.id"), nullable=False),
        sa.Column("category_id", sa.String(100), sa.ForeignKey("categories.id"), nullable=False),
        sa.Column("name", sa.String(160), nullable=False), sa.Column("description", sa.Text, nullable=False),
        sa.Column("image_url", sa.String(500), nullable=False), sa.Column("ingredients", sa.JSON, nullable=False),
        sa.Column("example_allergens", sa.String(300), nullable=False),
        sa.Column("preparation_min", sa.Integer, nullable=False), sa.Column("preparation_max", sa.Integer, nullable=False),
        sa.Column("spice_level", sa.Integer, nullable=False), sa.Column("is_sample", sa.Boolean, nullable=False),
        sa.Column("published", sa.Boolean, nullable=False), sa.Column("position", sa.Integer, nullable=False),
        sa.CheckConstraint("spice_level >= 0 AND spice_level <= 5"),
        sa.CheckConstraint("preparation_min >= 0 AND preparation_max >= preparation_min"))
    op.create_index("ix_dishes_restaurant_id", "dishes", ["restaurant_id"])
    op.create_index("ix_dishes_category_id", "dishes", ["category_id"])
    op.create_table("portions",
        sa.Column("id", sa.String(120), primary_key=True),
        sa.Column("dish_id", sa.String(100), sa.ForeignKey("dishes.id"), nullable=False),
        sa.Column("label", sa.String(80), nullable=False), sa.Column("quantity", sa.String(240), nullable=False),
        sa.Column("price_minor", sa.Integer, nullable=False), sa.Column("position", sa.Integer, nullable=False),
        sa.CheckConstraint("price_minor >= 0"))
    op.create_index("ix_portions_dish_id", "portions", ["dish_id"])


def downgrade():
    for table in ("portions", "dishes", "categories", "restaurants"):
        op.drop_table(table)
