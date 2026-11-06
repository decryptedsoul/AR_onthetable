"""Explicit, idempotent demo seeding. Never overwrite edited catalog content."""
import json
from pathlib import Path

from sqlalchemy.orm import Session

from .config import Settings
from .database import build_engine
from .models import Category, Dish, Portion, Restaurant

SEED_FILE = Path(__file__).resolve().parent.parent / "data" / "menu.json"


def seed_catalog(session: Session):
    data = json.loads(SEED_FILE.read_text(encoding="utf-8"))
    if session.get(Restaurant, "coconut-grove") is None:
        session.add(Restaurant(id="coconut-grove", name="Coconut Grove", location="Tipu Sultan Road, Karachi",
                               instagram_url="https://www.instagram.com/cgpakistanofficial/", currency="PKR"))
        session.flush()
    for position, name in enumerate(["Starters", "Mains", "Burgers", "Pasta", "Greens"]):
        category_id = f"coconut-grove-{name.lower()}"
        if session.get(Category, category_id) is None:
            session.add(Category(id=category_id, restaurant_id="coconut-grove", name=name, position=position))
    session.flush()
    for position, item in enumerate(data):
        if session.get(Dish, item["id"]) is not None:
            continue
        portions = [Portion(id=f"{item['id']}-regular", label=item["portion"], quantity=item["quantity"],
                            price_minor=item["price"] * 100, position=0)]
        if item.get("variant"):
            portions.append(Portion(id=f"{item['id']}-sharing", label=item["variant"],
                                   quantity=item["variantQuantity"], price_minor=item["variantPrice"] * 100, position=1))
        session.add(Dish(
            id=item["id"], restaurant_id="coconut-grove", category_id=f"coconut-grove-{item['category'].lower()}",
            name=item["name"], description=item["description"], image_url=f"/assets/{item['photo']}.webp",
            ingredients=item["ingredients"], example_allergens=item["allergens"],
            preparation_min=item["minutes"][0], preparation_max=item["minutes"][1], spice_level=item["spice"],
            is_sample=True, published=True, position=position, portions=portions,
        ))
    session.commit()


if __name__ == "__main__":
    engine = build_engine(Settings.from_env().database_url)
    try:
        with Session(engine) as session:
            seed_catalog(session)
        print("Sample catalog seeded; existing records preserved.")
    finally:
        engine.dispose()
