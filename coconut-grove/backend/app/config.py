import os
from dataclasses import dataclass
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parent.parent
PROJECT_DIR = BACKEND_DIR.parent


@dataclass(frozen=True)
class Settings:
    database_url: str = f"sqlite:///{(BACKEND_DIR / 'var' / 'menu.db').as_posix()}"
    frontend_dir: Path = PROJECT_DIR / "frontend" / "dist"
    cors_origins: tuple[str, ...] = ()

    @classmethod
    def from_env(cls) -> "Settings":
        defaults = cls()
        return cls(
            database_url=os.getenv("DATABASE_URL", defaults.database_url),
            frontend_dir=Path(os.getenv("FRONTEND_DIR", str(defaults.frontend_dir))).resolve(),
            cors_origins=tuple(x.strip() for x in os.getenv("CORS_ORIGINS", "").split(",") if x.strip()),
        )
