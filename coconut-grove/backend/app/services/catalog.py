from fastapi import HTTPException

from ..models import Dish
from ..repositories.catalog import CatalogRepository
from ..schemas import DishRead, MenuRead, RestaurantRead


def serialize_dish(dish: Dish) -> DishRead:
    return DishRead(
        id=dish.id, name=dish.name, description=dish.description,
        category=dish.category.name, image_url=dish.image_url,
        ingredients=dish.ingredients, example_allergens=dish.example_allergens,
        preparation_minutes=(dish.preparation_min, dish.preparation_max) if dish.preparation_min is not None and dish.preparation_max is not None else None,
        source_url=dish.source_url, source_observed_on=dish.source_observed_on,
        spice_level=dish.spice_level, is_sample=dish.is_sample, portions=dish.portions,
    )


class CatalogService:
    def __init__(self, repository: CatalogRepository):
        self.repository = repository

    def menu(self, restaurant_id: str, query: str, category: str | None, limit: int, offset: int, dish_ids: list[str] | None = None):
        restaurant = self.repository.restaurant(restaurant_id)
        if restaurant is None:
            raise HTTPException(404, "Restaurant not found")
        dishes, total = self.repository.dishes(restaurant_id, query, category, limit, offset, dish_ids)
        return MenuRead(
            restaurant=RestaurantRead.model_validate(restaurant),
            categories=self.repository.categories(restaurant_id),
            dishes=[serialize_dish(dish) for dish in dishes], total=total, limit=limit, offset=offset,
        )

    def dish(self, restaurant_id: str, dish_id: str):
        dish = self.repository.dish(restaurant_id, dish_id)
        if dish is None:
            raise HTTPException(404, "Dish not found")
        return serialize_dish(dish)
