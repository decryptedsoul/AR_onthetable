import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from .api.routes import router
from .config import Settings
from .database import build_engine

logger = logging.getLogger(__name__)


def create_app(settings: Settings | None = None) -> FastAPI:
    settings = settings or Settings.from_env()
    engine = build_engine(settings.database_url, serverless=settings.serverless)

    @asynccontextmanager
    async def lifespan(_app):
        yield
        engine.dispose()

    app = FastAPI(title="Coconut Grove API", version="0.2.0", lifespan=lifespan)
    app.state.engine = engine
    app.add_middleware(GZipMiddleware, minimum_size=1000)
    if settings.cors_origins:
        app.add_middleware(
            CORSMiddleware, allow_origins=list(settings.cors_origins),
            allow_methods=["GET"], allow_headers=["Accept", "Content-Type"],
        )

    @app.exception_handler(SQLAlchemyError)
    async def database_error(_request: Request, error: SQLAlchemyError):
        logger.error("Database operation failed: %s", type(error).__name__)
        return JSONResponse(status_code=503, content={"detail": "Menu temporarily unavailable"})

    @app.get("/api/health", tags=["Health"])
    def health():
        return {"status": "ok"}

    @app.get("/api/ready", tags=["Health"])
    def ready():
        with engine.connect() as connection:
            connection.execute(text("SELECT id FROM restaurants LIMIT 1"))
        return {"status": "ready"}

    app.include_router(router)

    # Reserve the API namespace so unknown endpoints never return frontend HTML.
    @app.api_route("/api/{path:path}", methods=["GET", "POST", "PUT", "PATCH", "DELETE"])
    def missing_api(path: str):
        return JSONResponse(status_code=404, content={"detail": "API endpoint not found"})

    # One origin in production; Vite proxies /api during frontend development.
    if (settings.frontend_dir / "index.html").is_file():
        @app.get("/", include_in_schema=False)
        @app.get("/menu", include_in_schema=False)
        @app.get("/preview", include_in_schema=False)
        def frontend_page():
            return FileResponse(settings.frontend_dir / "index.html", headers={"Cache-Control": "no-cache"})

        app.mount("/", StaticFiles(directory=settings.frontend_dir, html=True), name="frontend")
    return app


app = create_app()
