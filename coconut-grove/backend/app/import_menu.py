"""Explicit offline import of the checked-in public menu reference; no public write API."""
import json
import re
from pathlib import Path
from sqlalchemy.orm import Session
from .config import Settings
from .database import build_engine
from .models import Category, Dish, Portion
from .seed import seed_catalog

SOURCE_FILE = Path(__file__).resolve().parent.parent / "data" / "published-menu.json"
SAMPLE_IDS = ("platter", "burger", "pasta", "salad", "salmon", "pasta-share")


def import_published_menu(session: Session):
    seed_catalog(session)
    data = json.loads(SOURCE_FILE.read_text(encoding="utf-8"))
    for dish_id in SAMPLE_IDS:
        old = session.get(Dish, dish_id)
        if old is not None and old.restaurant_id == "coconut-grove" and old.is_sample:
            old.published = False
    categories = list(dict.fromkeys(item["category"] for item in data["items"]))
    for position, name in enumerate(categories):
        category_id = "coconut-grove-" + re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")
        category = session.get(Category, category_id)
        if category is None:
            session.add(Category(id=category_id, restaurant_id="coconut-grove", name=name, position=position))
            session.flush()
        for item_position, item in enumerate(x for x in data["items"] if x["category"] == name):
            if session.get(Dish, item["id"]) is not None:
                continue
            session.add(Dish(id=item["id"], restaurant_id="coconut-grove", category_id=category_id,
                name=item["name"], description="", image_url="", ingredients=[], example_allergens="Unconfirmed",
                preparation_min=None, preparation_max=None, spice_level=None, is_sample=False,
                source_url=data["source_url"], source_observed_on=data["observed_on"],
                published=True, position=position * 100 + item_position,
                portions=[Portion(id=item["id"]+"-listed", label="Listed serving", quantity="Measured portion pending", price_minor=item["price_minor"], position=0)]))
    session.commit()


if __name__ == "__main__":
    engine = build_engine(Settings.from_env().database_url)
    try:
        with Session(engine) as session:
            import_published_menu(session)
        print("Published reference imported; known sample dishes hidden; existing sourced edits preserved.")
    finally:
        engine.dispose()
