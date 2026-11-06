from sqlalchemy import Boolean, CheckConstraint, ForeignKey, Integer, JSON, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .database import Base


class Restaurant(Base):
    __tablename__ = "restaurants"
    id: Mapped[str] = mapped_column(String(80), primary_key=True)
    name: Mapped[str] = mapped_column(String(160))
    location: Mapped[str] = mapped_column(String(240))
    instagram_url: Mapped[str] = mapped_column(String(500))
    currency: Mapped[str] = mapped_column(String(3), default="PKR")


class Category(Base):
    __tablename__ = "categories"
    __table_args__ = (UniqueConstraint("restaurant_id", "name"),)
    id: Mapped[str] = mapped_column(String(100), primary_key=True)
    restaurant_id: Mapped[str] = mapped_column(ForeignKey("restaurants.id"), index=True)
    name: Mapped[str] = mapped_column(String(80))
    position: Mapped[int] = mapped_column(Integer)


class Dish(Base):
    __tablename__ = "dishes"
    __table_args__ = (
        CheckConstraint("spice_level >= 0 AND spice_level <= 5", name="ck_dishes_spice"),
        CheckConstraint("preparation_min >= 0 AND preparation_max >= preparation_min", name="ck_dishes_preparation"),
    )
    id: Mapped[str] = mapped_column(String(100), primary_key=True)
    restaurant_id: Mapped[str] = mapped_column(ForeignKey("restaurants.id"), index=True)
    category_id: Mapped[str] = mapped_column(ForeignKey("categories.id"), index=True)
    name: Mapped[str] = mapped_column(String(160))
    description: Mapped[str] = mapped_column(Text)
    image_url: Mapped[str] = mapped_column(String(500))
    ingredients: Mapped[list[str]] = mapped_column(JSON)
    example_allergens: Mapped[str] = mapped_column(String(300))
    preparation_min: Mapped[int | None] = mapped_column(Integer, nullable=True)
    preparation_max: Mapped[int | None] = mapped_column(Integer, nullable=True)
    spice_level: Mapped[int | None] = mapped_column(Integer, nullable=True)
    source_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    source_observed_on: Mapped[str | None] = mapped_column(String(10), nullable=True)
    is_sample: Mapped[bool] = mapped_column(Boolean, default=True)
    published: Mapped[bool] = mapped_column(Boolean, default=True)
    position: Mapped[int] = mapped_column(Integer)
    category: Mapped[Category] = relationship(lazy="raise")
    portions: Mapped[list["Portion"]] = relationship(
        back_populates="dish", order_by="Portion.position", cascade="all, delete-orphan", lazy="raise"
    )


class Portion(Base):
    __tablename__ = "portions"
    __table_args__ = (CheckConstraint("price_minor >= 0", name="ck_portions_price"),)
    id: Mapped[str] = mapped_column(String(120), primary_key=True)
    dish_id: Mapped[str] = mapped_column(ForeignKey("dishes.id"), index=True)
    label: Mapped[str] = mapped_column(String(80))
    quantity: Mapped[str] = mapped_column(String(240))
    price_minor: Mapped[int | None] = mapped_column(Integer, nullable=True)
    position: Mapped[int] = mapped_column(Integer)
    dish: Mapped[Dish] = relationship(back_populates="portions")
