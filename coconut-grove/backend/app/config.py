import os
from dataclasses import dataclass
from pathlib import Path
from sqlalchemy.engine import make_url
from sqlalchemy.exc import ArgumentError

BACKEND_DIR = Path(__file__).resolve().parent.parent
PROJECT_DIR = BACKEND_DIR.parent


@dataclass(frozen=True)
class Settings:
    database_url: str = f"sqlite:///{(BACKEND_DIR / 'var' / 'menu.db').as_posix()}"
    frontend_dir: Path = PROJECT_DIR / "frontend" / "dist"
    cors_origins: tuple[str, ...] = ()
    serverless: bool = False

    @classmethod
    def from_env(cls) -> "Settings":
        defaults = cls()
        serverless = os.getenv("VERCEL") == "1"
        database_url = os.getenv("DATABASE_URL", "").strip()
        if serverless:
            try:
                postgres = make_url(database_url).get_backend_name() in {"postgres", "postgresql"}
            except (ArgumentError, ValueError):
                postgres = False
            if not postgres:
                raise RuntimeError("Vercel requires DATABASE_URL pointing to PostgreSQL. Set it on the backend project and redeploy.")
        return cls(
            database_url=database_url or defaults.database_url,
            frontend_dir=Path(os.getenv("FRONTEND_DIR", str(defaults.frontend_dir))).resolve(),
            cors_origins=tuple(x.strip() for x in os.getenv("CORS_ORIGINS", "").split(",") if x.strip()),
            serverless=serverless,
        )
