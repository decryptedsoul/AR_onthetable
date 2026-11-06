"""Deployment configuration checks without connecting to a cloud database."""
import json
import os
import unittest
from unittest.mock import patch

from sqlalchemy.pool import NullPool

from app.config import BACKEND_DIR, Settings
from app.database import build_engine


class DeploymentTests(unittest.TestCase):
    def test_vercel_requires_postgres_without_exposing_credentials(self):
        for value in ("", "sqlite:///local.db", "invalid-secret-value"):
            with self.subTest(value=value), patch.dict(os.environ, {"VERCEL":"1", "DATABASE_URL":value}):
                with self.assertRaisesRegex(RuntimeError, "Vercel requires DATABASE_URL") as result:
                    Settings.from_env()
                self.assertNotIn("invalid-secret-value", str(result.exception))

    def test_local_defaults_and_explicit_cloud_settings(self):
        with patch.dict(os.environ, {"VERCEL":"", "DATABASE_URL":""}):
            self.assertTrue(Settings.from_env().database_url.startswith("sqlite:///"))
            self.assertFalse(Settings.from_env().serverless)
        with patch.dict(os.environ, {"VERCEL":"1", "DATABASE_URL":"postgresql://role:password@localhost/db?sslmode=require", "CORS_ORIGINS":"https://web.example, https://staging.example"}):
            settings = Settings.from_env()
            self.assertTrue(settings.serverless)
            self.assertEqual(settings.cors_origins, ("https://web.example", "https://staging.example"))

    def test_postgres_driver_tls_and_serverless_pool(self):
        for scheme in ("postgres", "postgresql", "postgresql+psycopg"):
            engine = build_engine(f"{scheme}://role:p%40ss@localhost/db?sslmode=require&channel_binding=require", serverless=True)
            try:
                self.assertEqual(engine.url.drivername, "postgresql+psycopg")
                self.assertEqual(engine.url.password, "p@ss")
                self.assertEqual(engine.url.query["sslmode"], "require")
                self.assertEqual(engine.url.query["channel_binding"], "require")
                self.assertIsInstance(engine.pool, NullPool)
            finally:
                engine.dispose()

    def test_separate_vercel_roots_and_client_route_rewrites(self):
        backend = json.loads((BACKEND_DIR / "vercel.json").read_text())
        frontend_dir = BACKEND_DIR.parent / "frontend"
        frontend = json.loads((frontend_dir / "vercel.json").read_text())
        self.assertEqual(backend["framework"], "fastapi")
        self.assertTrue((BACKEND_DIR / next(iter(backend["functions"]))).is_file())
        self.assertEqual(frontend["outputDirectory"], "dist")
        self.assertEqual(frontend["rewrites"], [
            {"source":"/menu", "destination":"/index.html"},
            {"source":"/preview", "destination":"/index.html"},
        ])
        self.assertNotIn("env", frontend)


if __name__ == "__main__":
    unittest.main()
