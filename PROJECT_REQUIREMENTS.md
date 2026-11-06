# Restaurant AR Menu: Project Goals and Requirements

**Version:** 0.1 — planning baseline  
**Date:** 2026-11-06  
**Status:** Proposed requirements; no application has been implemented or device-tested.  
**Related document:** [AR implementation plan](./AR_IMPLEMENTATION_PLAN.md)

## 1. Product goal

Help restaurant guests choose dishes confidently by showing their appearance and approximate serving size on the actual table, alongside complete restaurant-provided ingredients, reviews, preparation time, spice level, and portion information.

Deliver the experience through a lightweight, mobile-first website opened from a QR code or link. Guests must be able to browse without installing an app, signing in, or granting camera access. AR is an enhancement to a usable menu.

“Live preview” means rendering a prepared 3D representation over the live camera view. It does not mean a live feed of the kitchen or automatic reconstruction of the meal being prepared. Appearance and portion details are representative; actual plating can vary.

## 2. Planning assumptions

- Start with one restaurant and a small curated set of AR-enabled dishes; keep identifiers ready for additional restaurants and locations.
- All published dishes have useful photos and complete details. Initially, only selected dishes need 3D assets.
- The MVP supports one placed dish at a time. Multiple portion variants can have separate assets.
- Restaurant staff provide and approve recipes, ingredient and allergen information, serving sizes, and preparation estimates.
- Preparation time is initially a staff-maintained estimate or range, not a live kitchen queue prediction.
- The project is currently a planning exercise. Framework, hosting vendor, database, budget, launch date, and exact supported device versions remain undecided.
- Full dish information is available on the web detail page. Identical custom controls over the camera view on every phone are not an MVP promise; see the AR plan.

## 3. Intended users and primary journey

**Guests:** Scan a table QR code, browse categories, open a dish, inspect its details, optionally rotate its 3D preview, then tap “View on your table.” Place the dish, inspect it, exit AR, and return to the same dish and menu position.

**Restaurant staff:** Create and update dishes, preparation estimates, availability and prices; review ingredient information; publish approved photos and models; moderate submitted reviews.

**Content/3D operator:** Capture or model dishes, optimize assets, verify physical scale, and obtain restaurant approval before publication.

## 4. MVP functional requirements

| ID | Requirement | Acceptance criteria |
|---|---|---|
| MENU-01 | Open from QR code or direct URL | A restaurant-specific link opens its menu; table context is optional and contains no guest identity. |
| MENU-02 | Browse and find dishes | Guests can browse categories and search names. Unavailable dishes are clearly marked. |
| MENU-03 | Show essential menu data | Each dish displays name, description, price with currency, availability, photo, and the information below. |
| INFO-01 | Complete ingredients | Staff can list ingredients, including sauce, garnish, and compound-ingredient components where supplied. Missing information is explicitly marked; missing mandatory information blocks publication. |
| INFO-02 | Allergens and dietary information | Staff can record declared allergens and cross-contact notes separately from ingredients. Dietary claims require staff approval and cannot be inferred from an image or model. Unknown is distinct from absent. |
| INFO-03 | Preparation time | Display an estimated range in minutes, its scope (e.g. kitchen preparation excluding queue), and an update timestamp. Do not label it a guaranteed delivery time. |
| INFO-04 | Spice level | Show text and a consistent scale, proposed as 0–5 from no added heat to very hot. Available adjustments are separate options. |
| INFO-05 | Portion size | Show serving count and relevant quantity, such as pieces, weight, volume, or plate diameter. Distinguish food quantity from plate dimensions. |
| REV-01 | Read reviews | Show rating average, review count, and approved reviews with dates. Empty states say “No reviews yet”; sample content must never appear as real feedback. |
| REV-02 | Collect and moderate reviews | Provide a submission route with anti-abuse controls and moderation. Publish only approved reviews and compute aggregates from that same set. A verified-visit label requires an actual verification mechanism. |
| VIEW-01 | Preview in 3D | For approved assets, load an interactive model on request; allow rotation and provide a photo fallback if loading fails. |
| AR-01 | Place dish in the real environment | Supported devices offer a deliberate AR launch and horizontal-surface placement. Guests receive brief table-scanning guidance. |
| AR-02 | Represent portion scale | Start at the approved real-world scale, restrict resizing where supported, and explain any viewer limitation. Validate each portion asset against physical measurements. |
| AR-03 | Return and recover | Exiting AR preserves dish/portion selection and scroll position. Unsupported devices, denied permission, tracking loss, and load failures leave the menu usable. |
| STAFF-01 | Maintain menu | Authorized staff can edit content and availability, preview changes, and publish or unpublish a dish. Public guests cannot mutate menu records. |
| STAFF-02 | Control asset publication | AR assets remain unpublished until both format validation and restaurant approval pass. Photo-only dishes remain supported. |

## 5. Mobile experience requirements

- Design first for portrait phones at widths of 360–430 CSS pixels; support 320 pixels without horizontal scrolling. Tablet and desktop layouts remain usable.
- Use large readable text, approximately 44×44 CSS-pixel primary touch targets, visible focus, accessible labels, sufficient contrast, and screen-reader-friendly dish information. Target WCAG 2.2 AA for the web interface.
- Keep essential facts near the dish photo: price, portion, spice, estimated time, and rating. Ingredients and reviews remain easy to expand.
- Provide a clear “View on your table” action only for an available asset/path; offer 3D or photos otherwise. Do not request camera access while browsing.
- Explain native-viewer handoff and how to return. Keep full ingredients/reviews on the detail page; optional compact WebXR controls must not hide placement or exit controls.
- Do not use color alone for spice, availability, or dietary labels. Respect reduced-motion preferences and avoid automatic 3D rotation by default.
- Ordinary vertical scrolling must remain usable around the embedded 3D viewer. Support safe areas and phone orientation changes.

## 6. Performance and delivery budgets

These are proposed engineering targets, not measured results or vendor limits. Confirm them during the prototype on named reference phones.

| Area | Proposed acceptance target |
|---|---|
| Initial menu transfer | At most 500 KB compressed for the first usable viewport, including HTML, CSS, initial JS, menu data, fonts and visible images; excludes deferred 3D. |
| Initial JavaScript | At most 150 KB compressed; do not include the AR/3D viewer in the initial menu bundle. |
| Menu responsiveness | Target p75 LCP ≤2.5 s, INP ≤200 ms, and CLS ≤0.1; evaluate by device/network cohort when field traffic exists. |
| 3D asset | Aim for 2–5 MB per delivered GLB or USDZ; set a 10 MB project publication ceiling pending device tests. Download only the selected format. |
| Geometry/textures | Start with 30k–50k triangles per dish including plate; normally 1K textures, up to 2K only when justified. Limit material count and avoid expensive effects. |
| Model loading | Target p75 model-ready within 8 s on a cold cache at a defined 10 Mbps/100 ms RTT test profile; record format and device. |
| Placement usability | Target at least 90% of pilot participants placing a dish within 20 s after the AR viewer is ready, under representative restaurant conditions. |
| Rendering | Target a stable 30 FPS or better on selected reference phones, measured where instrumentation is available; inspect native viewers separately for stutter and thermal issues. |

Use responsive images, immutable versioned asset URLs, CDN delivery, compression, and on-demand imports. Release inactive 3D resources. Do not preload every dish. Download size alone is insufficient: test decoded texture memory and repeated dish changes.

## 7. Data and content requirements

| Entity | Minimum information |
|---|---|
| Restaurant / location | Stable ID, name, currency, locale, categories, publication state; optional location and table links. |
| Dish | Stable ID, restaurant/category references, name, description, photo/alt text, price, availability, ordered ingredients, allergen/cross-contact notes, dietary labels, spice level, preparation range, review aggregate, timestamps. |
| Portion variant | Stable ID, dish reference, label, price override if needed, serving count, quantities/units, physical dimensions, matching image and asset reference. |
| AR asset | Variant reference, versioned GLB/USDZ URLs, poster, file sizes, dimensions in meters, triangle count, validation state, approved-by and approved-at. |
| Review | Dish/location reference, rating, text, submission date, optional display name, moderation state, optional visit-verification reference. |
| Staff access | Identity, restaurant scope, role, and audit metadata. |

Use explicit null/unknown states. Validate numeric ranges and units. Do not treat unpublished content as public API data. Publish related dish, variant, and asset changes consistently to avoid showing the wrong portion.

## 8. Security, privacy, and reliability

- Serve the application and assets over HTTPS. Public asset URLs may be needed by platform viewers; keep private upload originals and staff data separate.
- Request camera/sensor access only as required by the chosen AR path after a guest action. The application must not upload, store, or analyze camera frames.
- Use authenticated, restaurant-scoped staff writes; sanitize user text and validate uploads and asset URLs. Rate-limit review submissions and administrative endpoints appropriately.
- Avoid guest accounts for browsing. Review submissions should collect minimal personal data, with retention and deletion rules defined before launch.
- Cache versioned models aggressively; refresh menu availability and preparation estimates. If showing cached menu data offline, display when it was last updated.
- Log actionable model/API failures without camera data or unnecessary personal identifiers. Record web launch requests separately from confirmed placements; native handoffs cannot always report completion.

## 9. Scope boundaries

**MVP:** Mobile menu, dish details, review reading/submission/moderation, basic staff publishing, selected-dish 3D/AR, measured scale, resilient fallbacks, and essential analytics.

**Later options:** More dishes and locations, localization, supported WebXR ingredient hotspots, multiple dishes on one table, favorites, kitchen-system integration for updated estimates, and ordering/payment integrations.

**Outside the baseline:** Native app development, automatic model generation at runtime, exact visual matching to each cooked serving, guaranteed allergen detection, persistent shared room maps, and universally identical AR interfaces.

## 10. Delivery stages and release gates

1. **Feasibility prototype:** Use three representative dishes, including one difficult surface/material. Test GLB and USDZ, physical scale, handoff/return, and real restaurant tables. Record supported device/browser combinations and asset-production effort.
2. **Menu foundation:** Implement mobile browsing, the data model, approved dish content, review flow, and basic staff publication. Verify the menu without AR or camera permission.
3. **AR integration:** Add lazy-loaded 3D and platform routing, approved portion assets, graceful failure states, and performance instrumentation.
4. **Restaurant pilot:** Test QR entry, guest comprehension, table placement, accessibility, low connectivity, and repeated use. Correct content and device problems before expansion.
5. **Release:** Meet the budgets on the agreed reference devices, approve content/assets, document unsupported paths, verify staff permissions, and confirm rollback/unpublish procedures.

Do not commit to a full-menu asset-production schedule until the prototype measures cost and turnaround per dish.

## 11. Success measures and unresolved choices

Measure menu-to-detail engagement, 3D usage, AR launch requests by device/path, observable placement success in WebXR, pilot-observed native placement success, fallback/error rates, and guest understanding of portion/spice/preparation information. Establish baselines during the pilot; avoid claiming revenue impact without ordering data and a suitable comparison.

Decisions still needed: restaurant/menu size, pilot phones and supported OS versions, number of launch models, capture budget and content owner, recipe/allergen approval process, portion tolerances, review identity/moderation policy, language needs, and whether simultaneous detailed information over AR is mandatory across all target devices. The last choice can materially change the AR approach and cost.

## 12. Technical references

Browser support and viewer behavior must be rechecked at implementation time. The supporting platform documentation and research notes are in the [AR implementation plan](./AR_IMPLEMENTATION_PLAN.md#10-primary-references).

## Current website implementation — 6 November 2026

The website now has independent Intro (`/`), Menu (`/menu`) and Preview (`/preview`) pages, reached through a fixed top navbar. Scrolling stays within the current page. Intro includes sourced visitor accounts, a linked visitor video and a clearly labeled slot for restaurant-owned footage. Menu uses 166 public-listing entries across 27 categories with provenance and reference-price labels. Unknown full ingredients/allergens, preparation, spice and measured portions remain pending. Preview runs an optimized sample object with working 3D controls and device-dependent AR; restaurant dish models, true serving scale and physical-device testing remain required. See [implementation notes](./coconut-grove/PAGE_UPDATE.md).
