from sqlalchemy import String, cast, func, or_, select
from sqlalchemy.orm import Session, joinedload, selectinload

from ..models import Category, Dish, Restaurant


class CatalogRepository:
    def __init__(self, session: Session):
        self.session = session

    def restaurant(self, restaurant_id: str):
        return self.session.get(Restaurant, restaurant_id)

    def categories(self, restaurant_id: str):
        return self.session.scalars(
            select(Category).where(Category.restaurant_id == restaurant_id,
                Category.id.in_(select(Dish.category_id).where(Dish.restaurant_id == restaurant_id, Dish.published.is_(True))))
            .order_by(Category.position, Category.id)
        ).all()

    def dishes(self, restaurant_id: str, query: str, category: str | None, limit: int, offset: int, dish_ids: list[str] | None = None):
        filters = [Dish.restaurant_id == restaurant_id, Dish.published.is_(True)]
        if category:
            filters.append(Dish.category_id == category)
        if dish_ids is not None:
            filters.append(Dish.id.in_(dish_ids))
        if query:
            value = query.strip().lower()
            filters.append(or_(
                func.lower(Dish.name).contains(value, autoescape=True),
                func.lower(Dish.description).contains(value, autoescape=True),
                func.lower(cast(Dish.ingredients, String)).contains(value, autoescape=True),
            ))
        total = self.session.scalar(select(func.count()).select_from(Dish).where(*filters))
        statement = select(Dish).where(*filters).options(
            joinedload(Dish.category), selectinload(Dish.portions)
        ).order_by(Dish.position, Dish.id).offset(offset).limit(limit)
        return self.session.scalars(statement).all(), total

    def dish(self, restaurant_id: str, dish_id: str):
        return self.session.scalar(select(Dish).where(
            Dish.id == dish_id, Dish.restaurant_id == restaurant_id, Dish.published.is_(True)
        ).options(joinedload(Dish.category), selectinload(Dish.portions)))
