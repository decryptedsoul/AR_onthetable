# Coconut Grove — React + FastAPI

A mobile-first React/TypeScript menu backed by modular FastAPI and SQLAlchemy. Three separate pages (Intro, Menu and Preview) share a fixed top navbar. Search, categories, device-local favorites and explicit planned-feature labels remain available.

See [architecture and scaling](./ARCHITECTURE.md) for boundaries, concurrency and the future brand-platform roadmap.

See the [design review](./DESIGN_REVIEW.md) for the typography, mobile navigation, touch-target, loading-state and reduced-motion improvements, plus their validation and deliberate design tradeoffs.

## Requirements

Node.js 22.12+ (Node 24 tested), npm and Python 3.11+ (3.13 tested). SQLite supports local work; PostgreSQL is intended for production. On Windows use `npm.cmd` if PowerShell blocks `npm.ps1`; no execution-policy change is needed.

## Local setup

Run from this project directory:

```powershell
cd frontend
npm.cmd ci
npm.cmd run build
cd ../backend
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
.\.venv\Scripts\python.exe -m alembic upgrade head
.\.venv\Scripts\python.exe -m app.import_menu
.\.venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

Open **http://127.0.0.1:8000** for the built React site and **http://127.0.0.1:8000/docs** for API docs. The ignored local database is `backend/var/menu.db`. This version needs the API server; opening HTML directly through `file://` is no longer supported. On macOS/Linux use `npm` and `.venv/bin/python`.

## Frontend development

Keep FastAPI running and use another terminal:

```powershell
cd frontend
npm.cmd run dev
```

Open **http://127.0.0.1:5173**. Vite proxies `/api` to port 8000 and provides React hot reload. Add `--reload` to the backend command while editing Python. Rebuild the frontend to update the version served by FastAPI.

The [frontend environment example](./frontend/.env.example) documents an optional API origin and restaurant ID. Frontend environment values are public build-time configuration, never secrets. The [backend example](./backend/.env.example) documents process environment settings; Python does not automatically load those files.

## API

| Method | Endpoint | Behavior |
|---|---|---|
| GET | `/api/health` | Process liveness. |
| GET | `/api/ready` | Database schema connectivity. |
| GET | `/api/v1/restaurants/coconut-grove/menu` | Restaurant, categories and published dishes. |
| GET | `/api/v1/restaurants/coconut-grove/dishes/{id}` | Dish and portion details. |
| GET | `/api/v1/restaurants/coconut-grove/dishes/{id}/reviews` | Planned status and empty reviews. |
| GET | `/api/v1/restaurants/coconut-grove/dishes/{id}/ar` | Planned status, prerequisites and no model URLs. |

Menu parameters: `q` searches names/descriptions/ingredients; `category` is an API-returned category ID; `limit` is 1–100 (default 24); `offset` is nonnegative; repeated `dish_ids` filter up to 100 local favorites. Responses include total counts. Prices are integer minor units (paisa), with currency in the restaurant response.

Example: `/api/v1/restaurants/coconut-grove/menu?q=chicken&limit=24`. Unknown timing, spice and prices use JSON null; sourced dishes include source URL and observation date.

## PostgreSQL and containers

With Docker installed:

```powershell
Copy-Item .env.example .env
# Choose your own local POSTGRES_PASSWORD in .env before starting.
docker compose up --build -d
docker compose exec web python -m app.import_menu
```

Compose runs migrations in a separate service before starting the web service. Importing is explicit and does not overwrite edited catalog records. The example password is for local development only. Use a URL-safe generated password in Compose, or percent-encode special characters in a custom database URL.

For existing PostgreSQL hosting, set `DATABASE_URL=postgresql+psycopg://...` in the server environment, run `python -m alembic upgrade head` once per release, then start the application. Multiple workers/replicas can share PostgreSQL; provision connection budgets, TLS, backups and monitoring first.

Docker/PostgreSQL execution is unverified here because Docker is unavailable. No hosting upload or deployment was attempted. The retained Sites registration is only a static frontend target and cannot run the Python backend.

## Checks

```powershell
cd frontend
npm.cmd run build
cd ../backend
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
.\.venv\Scripts\python.exe -m alembic check
```

The build checks TypeScript and bundles React. API tests use temporary migrated databases and cover filters, pagination, validation, favorite lookup, unpublished content, restaurant scoping, concurrent guests, CORS, planned contracts, non-destructive seeding, downgrade/upgrade and sanitized database errors.

## Working and planned features

**Working:** independent `/`, `/menu` and `/preview` routes, fixed mobile navigation, database-backed published menu/search, categories, pagination, local favorites, dish dialogs, loading/error/retry states, local review-form demo, and an interactive 3D avocado sample. On compatible devices, the viewer offers native/WebXR AR; this remains unverified on physical phones.

**Planned:** approved restaurant dish models, measured serving scale, complete ingredients and allergens, preparation estimates, spice/portion metadata, accounts, staff publishing, review storage/moderation and live kitchen integration. The dedicated restaurant visit film is a labeled placeholder; a sourced visitor video opens externally.

[Published menu reference](./backend/data/published-menu.json) includes 166 entries from [MenuPak](https://www.menupak.com/m/coconut-grove-karachi), observed 6 November 2026. These are third-party reference prices, not confirmed current offers. An anomalous sub-Rs100 price is omitted. Full descriptions, dietary claims and speculative ingredients are not imported. `app.import_menu` hides only the six known sample IDs and preserves existing sourced edits. `app.seed` remains a legacy test fixture; use `app.import_menu` for this site.

The 651 KB sample model and its CC0 attribution live in [models](./frontend/public/models/). It loads only on Preview. The viewer chunk is approximately 292 KB gzip and the main app approximately 87 KB gzip. Actual serving dimensions and phone AR behavior are not validated. Hosting must route `/menu` and `/preview` to the frontend; FastAPI handles those explicitly while retaining real missing-asset/API 404 responses.

See [page update notes](./PAGE_UPDATE.md) for sources, boundaries and validation.

## Photography

Optimized files live in [public assets](./frontend/public/assets/), with credits also available from the footer.

- Restaurant reference: https://foodoplanet.com/listing/coconut-grove/ (production permission and approved original needed).
- Platter: https://images.unsplash.com/photo-1546833999-b9f581a1996d
- Burger: https://images.unsplash.com/photo-1568901346375-23c9450c58cd
- Pasta: https://images.unsplash.com/photo-1473093295043-cdd812d0e601
- Garden bowl: https://images.unsplash.com/photo-1512621776951-a57141f2eefd
- Salmon: https://images.unsplash.com/photo-1625944525533-473f1a3d54e7

The palm SVG is an original concept, not the official logo. Colors follow the parent [palette guide](../COLOR_PALETTE.md).
