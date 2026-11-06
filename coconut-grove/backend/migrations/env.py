from alembic import context

from app import models  # Register model metadata.
from app.config import Settings
from app.database import Base, build_engine

if context.is_offline_mode():
    context.configure(url=Settings.from_env().database_url, target_metadata=Base.metadata, literal_binds=True)
    with context.begin_transaction():
        context.run_migrations()
else:
    engine = build_engine(Settings.from_env().database_url)
    with engine.connect() as connection:
        sqlite = engine.dialect.name == "sqlite"
        # Batch table replacement requires FK checks off on this migration
        # connection only; application connections always enforce them.
        if sqlite:
            connection.exec_driver_sql("PRAGMA foreign_keys=OFF")
            connection.commit()
        context.configure(connection=connection, target_metadata=Base.metadata, render_as_batch=engine.dialect.name == "sqlite")
        with context.begin_transaction():
            context.run_migrations()
            if sqlite and connection.exec_driver_sql("PRAGMA foreign_key_check").fetchone():
                raise RuntimeError("Migration produced invalid foreign keys")
        if sqlite:
            connection.exec_driver_sql("PRAGMA foreign_keys=ON")
            connection.commit()
    engine.dispose()
