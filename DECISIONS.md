# Decision Log

This file records significant planning and implementation decisions and their tradeoffs. A React/FastAPI website prototype exists; actual AR and physical-device validation remain pending.

---

### Progressive enhancement for mobile table preview

**Date:** 2026-11-06  
**Status:** Accepted for planning; prototype validation pending  
**Files:** [Requirements](./PROJECT_REQUIREMENTS.md), [AR plan](./AR_IMPLEMENTATION_PLAN.md)

In the context of a lightweight, mobile-first restaurant web menu,
facing differing mobile browser AR capabilities,
we decided to plan on-demand model-viewer with WebXR and native viewer fallbacks instead of an initially custom renderer or mandatory native app,
to achieve accessible browsing and practical table preview,
accepting platform-specific interfaces and handoffs until the prototype verifies support.

### Keep complete dish information available outside AR

**Date:** 2026-11-06  
**Status:** Accepted for planning; cross-platform overlay requirement remains open  
**Files:** [Requirements](./PROJECT_REQUIREMENTS.md), [AR plan](./AR_IMPLEMENTATION_PLAN.md)

In the context of ingredients, reviews, preparation time, spice and portion information,
facing native viewers that do not carry the full web interface,
we decided to keep complete information on the dish page and treat in-AR overlays as optional,
to preserve usability across the planned device paths,
accepting that guests may need to exit AR to inspect details and that a mandatory universal overlay would require revisiting the architecture.

### Authored and measured assets per portion

**Date:** 2026-11-06  
**Status:** Accepted for planning; asset-production trial pending  
**Files:** [Requirements](./PROJECT_REQUIREMENTS.md), [AR plan](./AR_IMPLEMENTATION_PLAN.md)

In the context of credible food appearance and serving-size previews,
facing reconstruction quality, loading costs and format differences,
we decided to plan preprocessed, measured and approved GLB/USDZ assets per AR-enabled portion,
to support fast delivery and repeatable scale checks,
accepting manual production and maintenance costs and a photo-only fallback for dishes without approved models.

### Four-color Coconut Grove UI direction

**Date:** 2026-11-06  
**Status:** Proposed palette; user review pending  
**Files:** [Palette guide](./COLOR_PALETTE.md), [Swatches](./palette.svg)

In the context of a mobile menu for Coconut Grove,
facing the need to translate its green/gold visual references into readable interface colors,
we selected deep green, muted gold, warm ivory and charcoal as the proposed four-color palette,
to support recognizable branding and high-contrast menu information,
accepting that gold is restricted on ivory and that these values are UI proposals rather than official brand specifications.

### Buildless interactive website prototype

**Date:** 2026-11-06  
**Status:** Superseded by "React and modular FastAPI foundation"
**Files:** Historical implementation retired; see [current website setup](./coconut-grove/README.md).

In the context of the requested basic Coconut Grove website,
facing missing approved menu records, 3D models and backend services,
we implemented a buildless HTML/CSS/JavaScript menu with sample data, local favorites and explicit planned-feature dialogs,
to provide a lightweight, reviewable mobile experience now,
accepting that AR, live reviews, staff publishing and authoritative restaurant data require later implementation.

### React and modular FastAPI foundation

**Date:** 2026-11-06  
**Status:** Implemented and locally validated; production rollout pending  
**Supersedes:** Buildless interactive website prototype  
**Files:** [Frontend](./coconut-grove/frontend/src/App.tsx), [API](./coconut-grove/backend/app/main.py), [Architecture](./coconut-grove/ARCHITECTURE.md)

In the context of the requested React/FastAPI migration and a future brand platform serving multiple users,
facing the limits of a static prototype and process-local catalog data,
we implemented typed React components and a versioned FastAPI API separated into routes, services and repositories,
with SQLAlchemy, explicit Alembic migrations, SQLite for development and PostgreSQL configuration for production,
to support concurrent guest reads and future identity/publishing modules,
accepting a build/server setup and deferring authentication, moderation and production capacity claims until implemented and tested.

### Editorial refinement with mobile usability first

**Date:** 2026-11-06  
**Status:** Implemented and browser-validated  
**Files:** [Styles](./coconut-grove/frontend/src/design.css), [Navigation](./coconut-grove/frontend/src/Layout.tsx), [Review](./coconut-grove/DESIGN_REVIEW.md)

In the context of the requested three-skill design review,
facing conflicting visual prescriptions and small mobile controls,
we kept the established palette and editorial split while adding self-hosted type, 44px controls, mobile navigation and loading skeletons,
to improve the existing restaurant menu without replacing its identity,
accepting a small font payload and a deferred optional GSAP chunk that is skipped on initial reduced-motion preference.

### Independent pages, sourced catalog and isolated preview

**Date:** 2026-11-06  
**Status:** Implemented; native phone AR validation pending  
**Supersedes:** Single scrolling-page composition and sample-only public catalog; optional GSAP enhancement  
**Files:** [Routes](./coconut-grove/frontend/src/App.tsx), [Reference importer](./coconut-grove/backend/app/import_menu.py), [Page notes](./coconut-grove/PAGE_UPDATE.md)

In the context of the requested Intro, Menu and Preview pages with fixed navigation,
facing a long scrolling composition, unavailable restaurant dish assets and unconfirmed menu metadata,
we chose independent React Router URLs with explicit FastAPI entry points, a provenance-tracked public menu reference, nullable unknown facts, and a lazy-loaded model-viewer sample,
to provide distinct mobile browsing tasks and a working preview without fabricating restaurant servings,
accepting third-party reference prices, a deferred 3D payload, a labeled visit-film placeholder, and the need for approved dish models and physical-device AR testing.
The fixed navbar is explicitly requested by the user; page sections are no longer cross-page scroll targets. Unused scroll animations were removed. Existing sourced catalog edits are preserved by the explicit importer.

### Vercel frontend/API projects with Neon PostgreSQL

**Date:** 2026-11-07  
**Status:** Prepared and locally tested; cloud deployment pending  
**Files:** [Deployment guide](./coconut-grove/DEPLOYMENT_VERCEL_NEON.md), [Database engine](./coconut-grove/backend/app/database.py), [Settings](./coconut-grove/backend/app/config.py)

In the context of the user's Vercel and Neon prototype deployment,
facing separate React/Python runtimes and serverless filesystem and connection-lifecycle constraints,
we chose two Vercel project roots with explicit route configuration, PostgreSQL-required settings on Vercel, psycopg 3 URL normalization, and NullPool against Neon's pooled endpoint,
to retain the existing application architecture while releasing database client connections after requests,
accepting separate environment/CORS setup and explicit migration/import steps before deployment.
Local SQLite and traditional server pooling remain available. Sixteen backend tests, the frontend production build and Alembic schema check pass; no actual Neon connection or Vercel deployment is claimed.
