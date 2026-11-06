from pathlib import Path

from sqlalchemy import create_engine, event
from sqlalchemy.engine import make_url
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.pool import NullPool


class Base(DeclarativeBase):
    pass


def build_engine(url: str, *, serverless: bool = False):
    parsed = make_url(url)
    # Neon supplies a standard PostgreSQL URI; preserve credentials and TLS
    # parameters while choosing the psycopg 3 driver installed by this app.
    if parsed.drivername in {"postgres", "postgresql"}:
        parsed = parsed.set(drivername="postgresql+psycopg")
    options = {"pool_pre_ping": True}
    if parsed.get_backend_name() == "postgresql":
        options["connect_args"] = {"connect_timeout": 10}
        if serverless:
            # Neon's pooled endpoint handles connection reuse. Do not leave
            # idle client connections in frozen serverless instances.
            options["poolclass"] = NullPool
    if parsed.get_backend_name() == "sqlite":
        if parsed.database and parsed.database != ":memory:":
            Path(parsed.database).parent.mkdir(parents=True, exist_ok=True)
        options["connect_args"] = {"check_same_thread": False}
    engine = create_engine(parsed, **options)
    if parsed.get_backend_name() == "sqlite":
        @event.listens_for(engine, "connect")
        def enable_foreign_keys(connection, _record):
            connection.execute("PRAGMA foreign_keys=ON")
    return engine
