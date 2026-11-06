# Separate pages and published menu reference

Implemented 6 November 2026.

## Navigation

- `/`: restaurant introduction, sourced visitor stories, visit-film placeholder, external visitor video and official Instagram link.
- `/menu`: 166 public-listing entries across 27 categories, search, filtering, pagination, local favorites and dish details.
- `/preview`: lazy-loaded interactive 3D sample with rotation, zoom and reset; AR is offered when the browser reports support.

Each route mounts its own page. Scrolling does not navigate between pages. The fixed top navbar exposes all three links on phones and desktops. Legacy `#menu` and `#preview` links redirect to their page URLs. FastAPI serves the explicit entry points, including refresh, without swallowing missing assets or API routes.

## Content sources

The [reference catalog](./backend/data/published-menu.json) imports factual item names, category membership and listed prices from [MenuPak’s Coconut Grove Karachi listing](https://www.menupak.com/m/coconut-grove-karachi), observed 6 November 2026. This is a third-party reference, not an authenticated restaurant feed. Prices and availability need confirmation; anomalous prices below Rs100 remain unknown. Capitalization is normalized; source stars are not interpreted as spice levels. The source’s long platter composition is displayed as “Barbeque Platter.” Descriptions and dietary claims are not imported.

Timing, spice, complete ingredients, allergens, measured portions and dish models are unknown and displayed as pending. No substitute photographs are presented as original restaurant dishes.

Intro stories are linked paraphrases of [Jadirah Sarmad’s review](https://jadirahsarmad.com/coconut-grove-karachi-restaurant-review/) and [Amar Makhdoom’s dinner post](https://www.linkedin.com/posts/amar-makhdoom_about-last-night-dinner-hosted-by-cxo-club-activity-7264116603556970496-embr), not invented testimonials or verified in-app reviews. The visitor video links to [@seheri_hanul on Snapchat](https://www.snapchat.com/%40seheri_hanul/spotlight/W7_EDlXWTBiXAEEniNoMPwAAYa2x3dHJoaHBrAZ7ZRv5hAZ7ZRvEwAAAAAQ). Restaurant-owned footage is needed for the dedicated film slot. Review content and image permissions before production.

## Preview and assets

The [Avocado model](./frontend/public/models/README.md) is a Microsoft CC0 sample via Khronos. Resizing textures to 512px reduced the GLB from 8.11 MB to 651 KB. It is not a restaurant dish or a verified serving-size demonstration. The roughly 292 KB gzip viewer chunk and model load only on Preview; the main application is roughly 87 KB gzip.

`@google/model-viewer` supplies WebGL controls and device-dependent WebXR, Android Scene Viewer or iOS Quick Look integration. Guests initiate AR; compatible secure contexts are required. A local LAN HTTP address is insufficient for browser AR. No camera frames are sent to FastAPI. Physical iPhone/Android placement, permissions and real-world scale remain unverified. Actual dish previews require approved models and measured dimensions.

## Setup and boundaries

Run migrations, then `python -m app.import_menu`. This offline importer preserves existing sourced edits and unpublishes only the six known sample IDs. The old sample seed remains for regression fixtures. Source URL/date are stored per dish; unknown preparation, spice and prices are nullable. Restaurant-scoped read APIs and bounded pagination remain; no public mutation endpoint is added.

Migration 0002 supports SQLite batch replacement with foreign-key verification and retains data constraints. Downgrade refuses to fabricate values when sourced rows contain nulls: export/remove those rows before a deliberate downgrade. PostgreSQL/container execution and physical phone AR remain unverified.

## Validation

TypeScript and production build pass. Backend checks cover provenance, unknown data, repeat importing, preserved edits, populated legacy migration, direct-page refresh, asset/API 404s, restaurant scoping, validation, concurrent readers and sanitized errors. Browser checks cover mobile/desktop layout, page separation, fixed navigation, model loading/controls, favorites and dish-to-preview navigation.
