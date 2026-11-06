import os
import tempfile
import unittest
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from unittest.mock import patch

from alembic import command
from alembic.config import Config
from fastapi.testclient import TestClient
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.config import BACKEND_DIR, Settings
from app.main import create_app
from app.models import Category, Dish, Restaurant
from app.seed import seed_catalog
from app.import_menu import import_published_menu, SOURCE_FILE
import json

PREFIX = "/api/v1/restaurants/coconut-grove"


class CatalogTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.url = f"sqlite:///{Path(self.directory.name).as_posix()}/test.db"
        self.config = Config(str(BACKEND_DIR / "alembic.ini"))
        with patch.dict(os.environ, {"DATABASE_URL": self.url}):
            command.upgrade(self.config, "head")
        self.app = create_app(Settings(database_url=self.url, frontend_dir=Path(self.directory.name),
                                       cors_origins=("https://menu.example",)))
        with Session(self.app.state.engine) as session:
            seed_catalog(session)
        self.client = TestClient(self.app)
        self.client.__enter__()

    def tearDown(self):
        self.client.__exit__(None, None, None)
        self.directory.cleanup()

    def test_menu_contract_and_integer_money(self):
        response = self.client.get(PREFIX + "/menu")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["total"], 6)
        self.assertEqual(len(data["categories"]), 5)
        self.assertTrue(all(d["is_sample"] and d["ar_status"] == "planned" for d in data["dishes"]))
        self.assertEqual(data["dishes"][0]["portions"][1]["price_minor"], 295000)

    def test_combined_search_category_pagination_and_literal_wildcards(self):
        page = self.client.get(PREFIX + "/menu", params={"q": "basil", "category": "coconut-grove-pasta", "limit": 1, "offset": 1}).json()
        self.assertEqual(page["total"], 2)
        self.assertEqual([d["id"] for d in page["dishes"]], ["pasta-share"])
        self.assertEqual(self.client.get(PREFIX + "/menu", params={"q": "avocado"}).json()["total"], 2)
        self.assertEqual(self.client.get(PREFIX + "/menu", params={"q": "%"}).json()["total"], 0)

    def test_saved_ids_are_filtered_on_server(self):
        data = self.client.get(PREFIX + "/menu", params=[("dish_ids", "burger"), ("dish_ids", "salad")]).json()
        self.assertEqual(data["total"], 2)
        self.assertEqual({dish["id"] for dish in data["dishes"]}, {"burger", "salad"})

    def test_validation_and_missing_records(self):
        for params in ({"limit": 101}, {"offset": -1}, {"q": "x" * 101}, {"dish_ids": ["x"] * 101}):
            self.assertEqual(self.client.get(PREFIX + "/menu", params=params).status_code, 422)
        self.assertEqual(self.client.get(PREFIX + "/dishes/missing").status_code, 404)
        self.assertEqual(self.client.get("/api/v1/restaurants/missing/menu").status_code, 404)
        self.assertEqual(self.client.get("/api/unknown").json(), {"detail": "API endpoint not found"})

    def test_unpublished_and_other_restaurant_data_not_exposed(self):
        with Session(self.app.state.engine) as session:
            session.get(Dish, "burger").published = False
            session.add(Restaurant(id="other", name="Other", location="Other", instagram_url="https://example.com", currency="PKR"))
            session.flush()
            session.add(Category(id="other-mains", restaurant_id="other", name="Mains", position=0))
            session.flush()
            session.add(Dish(id="private-scope", restaurant_id="other", category_id="other-mains", name="Other dish",
                             description="Other", image_url="/assets/salad.webp", ingredients=[], example_allergens="Unknown",
                             preparation_min=1, preparation_max=2, spice_level=0, is_sample=True, published=True, position=0))
            session.commit()
        self.assertEqual(self.client.get(PREFIX + "/menu").json()["total"], 5)
        for dish_id in ("burger", "private-scope"):
            self.assertEqual(self.client.get(PREFIX + f"/dishes/{dish_id}").status_code, 404)

    def test_planned_capabilities_and_no_public_mutation(self):
        self.assertEqual(self.client.get(PREFIX + "/dishes/platter/ar").json()["model_urls"], [])
        self.assertEqual(self.client.get(PREFIX + "/dishes/platter/reviews").json()["status"], "planned")
        self.assertIn(self.client.post(PREFIX + "/dishes/platter/reviews", json={"rating": 5}).status_code, (404, 405))

    def test_health_cors_and_concurrent_guests(self):
        self.assertEqual(self.client.get("/api/health").status_code, 200)
        self.assertEqual(self.client.get("/api/ready").status_code, 200)
        allowed = self.client.get(PREFIX + "/menu", headers={"Origin": "https://menu.example"})
        denied = self.client.get(PREFIX + "/menu", headers={"Origin": "https://untrusted.example"})
        self.assertEqual(allowed.headers["access-control-allow-origin"], "https://menu.example")
        self.assertNotIn("access-control-allow-origin", denied.headers)
        with ThreadPoolExecutor(max_workers=8) as pool:
            results = list(pool.map(lambda _: self.client.get(PREFIX + "/menu").json()["total"], range(20)))
        self.assertEqual(results, [6] * 20)

    def test_seed_preserves_existing_edits_and_downgrade_roundtrip(self):
        with Session(self.app.state.engine) as session:
            session.get(Dish, "burger").name = "Edited by staff"
            session.commit()
            seed_catalog(session)
            self.assertEqual(session.get(Dish, "burger").name, "Edited by staff")
            self.assertEqual(session.scalar(select(func.count()).select_from(Dish)), 6)
        with patch.dict(os.environ, {"DATABASE_URL": self.url}):
            command.downgrade(self.config, "base")
            command.upgrade(self.config, "head")

    def test_unavailable_database_is_sanitized(self):
        broken = create_app(Settings(database_url=f"sqlite:///{Path(self.directory.name).as_posix()}/empty.db",
                                     frontend_dir=Path(self.directory.name)))
        with TestClient(broken) as client:
            response = client.get(PREFIX + "/menu")
            self.assertEqual(response.status_code, 503)
            self.assertEqual(response.json(), {"detail": "Menu temporarily unavailable"})

    def test_published_reference_provenance_unknowns_and_idempotence(self):
        expected = len(json.loads(SOURCE_FILE.read_text(encoding="utf-8"))["items"])
        with Session(self.app.state.engine) as session:
            import_published_menu(session)
        data = self.client.get(PREFIX + "/menu", params={"limit":100}).json()
        self.assertEqual(data["total"], expected)
        self.assertEqual(len(data["categories"]), 27)
        self.assertTrue(all(not d["is_sample"] and d["source_url"].startswith("https://www.menupak.com/") for d in data["dishes"]))
        self.assertTrue(all(d["preparation_minutes"] is None and d["spice_level"] is None and not d["ingredients"] for d in data["dishes"]))
        first = data["dishes"][0]["id"]
        with Session(self.app.state.engine) as session:
            session.get(Dish, first).name = "Staff approved name"
            session.commit()
            import_published_menu(session)
        self.assertEqual(self.client.get(PREFIX + f"/dishes/{first}").json()["name"], "Staff approved name")
        self.assertEqual(self.client.get(PREFIX + "/dishes/burger").status_code, 404)
        self.assertEqual(self.client.get(PREFIX + "/menu").json()["total"], expected)

    def test_direct_page_refresh_and_missing_asset(self):
        frontend = Path(self.directory.name) / "frontend"
        frontend.mkdir()
        (frontend / "index.html").write_text("<!doctype html><title>Grove</title>")
        app = create_app(Settings(database_url=self.url, frontend_dir=frontend))
        with TestClient(app) as client:
            for path in ("/", "/menu", "/preview?dish=example"):
                response = client.get(path)
                self.assertEqual(response.status_code, 200)
                self.assertIn("<title>Grove</title>", response.text)
            for path in ("/missing", "/assets/missing.js", "/api/missing"):
                self.assertEqual(client.get(path).status_code, 404)

    def test_migration_preserves_existing_catalog_and_constraints(self):
        from sqlalchemy import text
        from app.database import build_engine
        url = f"sqlite:///{Path(self.directory.name).as_posix()}/legacy.db"
        with patch.dict(os.environ, {"DATABASE_URL":url}):
            command.upgrade(self.config, "0001_catalog")
        engine = build_engine(url)
        with engine.begin() as connection:
            connection.execute(text("INSERT INTO restaurants VALUES ('legacy','Legacy','Karachi','https://example.com','PKR')"))
            connection.execute(text("INSERT INTO categories VALUES ('legacy-main','legacy','Mains',0)"))
            connection.execute(text("INSERT INTO dishes VALUES ('legacy-dish','legacy','legacy-main','Kept','Description','', '[]','Unknown',1,2,0,1,1,0)"))
            connection.execute(text("INSERT INTO portions VALUES ('legacy-portion','legacy-dish','Single','One',100,0)"))
        engine.dispose()
        with patch.dict(os.environ, {"DATABASE_URL":url}):
            command.upgrade(self.config, "head")
        engine = build_engine(url)
        try:
            with engine.connect() as connection:
                self.assertEqual(connection.scalar(text("SELECT name FROM dishes WHERE id='legacy-dish'")), "Kept")
                self.assertIsNone(connection.exec_driver_sql("PRAGMA foreign_key_check").fetchone())
                self.assertEqual(connection.exec_driver_sql("PRAGMA foreign_keys").scalar(), 1)
                from sqlalchemy.exc import IntegrityError
                with self.assertRaises(IntegrityError):
                    connection.execute(text("UPDATE portions SET price_minor=-1"))
        finally:
            engine.dispose()


if __name__ == "__main__":
    unittest.main()
