# AR on the Table

A mobile-first restaurant website and table-preview foundation, using Coconut Grove, Karachi as the current brand concept.

The application uses React, TypeScript and Vite with a modular FastAPI/SQLAlchemy backend. Intro, Menu and Preview have independent URLs and a fixed top navbar. The menu includes a sourced public reference, search, categories and device-local favorites. Preview demonstrates interactive 3D with a small sample model and device-dependent AR.

## Run locally

Follow the [application setup guide](./coconut-grove/README.md). Build the frontend, migrate the database and run the published-menu importer before starting FastAPI. The local site opens at `http://127.0.0.1:8000`.

## Project documents

- [Goals and requirements](./PROJECT_REQUIREMENTS.md)
- [AR implementation plan](./AR_IMPLEMENTATION_PLAN.md)
- [Architecture and future scaling](./coconut-grove/ARCHITECTURE.md)
- [Current pages, content sources and preview boundaries](./coconut-grove/PAGE_UPDATE.md)
- [Brand palette](./COLOR_PALETTE.md)
- [Decision log](./DECISIONS.md)

## Current boundaries

Published menu prices are third-party references and need restaurant confirmation. Complete ingredients, preparation times, spice levels and measured portions remain pending. The 3D avocado is a labeled CC0 sample, not a restaurant dish. Actual dish AR requires approved models, measured servings and physical-device testing. Accounts, staff publishing, verified reviews and live kitchen integrations are planned.

Local environments, databases, generated builds and browser-review captures are excluded from version control. The setup guide includes production-build and backend-test commands. PostgreSQL/container execution and native phone AR remain unverified.
