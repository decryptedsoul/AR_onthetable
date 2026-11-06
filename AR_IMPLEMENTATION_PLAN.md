# Restaurant AR Menu: Augmentation Implementation Plan

**Date:** 2026-11-06  
**Status:** Recommended prototype architecture; compatibility and performance require physical-device validation.  
**Product baseline:** [Project requirements](./PROJECT_REQUIREMENTS.md)

## 1. Recommendation

Use a standard mobile website for the menu and load a `<model-viewer>` component only when a guest requests 3D/AR. Prepare an optimized GLB and a separately validated USDZ for each AR-enabled portion. Route supported devices to WebXR, Android Scene Viewer, or Apple Quick Look, keeping photographs and the menu available when AR cannot run.

The component supports these AR modes and fixed-scale configuration. Platform paths still differ in interface and behavior; validate each path instead of assuming feature parity. See the [component AR examples](https://modelviewer.dev/examples/augmentedreality/index.html).

This keeps custom rendering work limited and lets the first prototype focus on the hard parts: food realism, correct physical size, table tracking, loading time, and returning to the menu.

## 2. What guests will experience

1. Scan a printed QR code that opens the restaurant menu. The QR code navigates to the website; it is not a spatial tracking marker.
2. Open a dish and see its photo, price, full ingredient list, reviews, preparation estimate, spice level, and portion information.
3. Select a portion, then request its 3D preview or tap “View on your table.” Fetch only that variant's required assets.
4. Start AR with a deliberate tap, follow the platform's camera permission and surface-scanning instructions, and point toward an unobstructed table.
5. Place the model on a detected horizontal surface, move around it, reposition it where supported, and inspect its approximate serving size.
6. Exit AR and return to the same dish/portion. Ingredients and reviews remain available on the detail page.

AR uses the live view of the guest's environment with an authored model placed in it. It does not identify the restaurant table or reproduce that day's food automatically. Guests must choose the intended surface; tracking can also detect the floor or another horizontal plane.

## 3. Platform routing and interface limits

| Environment | Proposed path | Experience and constraints |
|---|---|---|
| Android browser/device with tested immersive AR support | WebXR through the viewer | In-browser surface placement; custom information controls only when overlay capabilities are available and tested. |
| Compatible Android device with native AR services | Scene Viewer fallback | System viewer handles placement; the full website UI does not travel into it. Restore details on return. |
| Compatible iPhone/iPad browser | Quick Look using USDZ | System AR preview; provide full details before and after handoff. Validate launch behavior in the selected browser. |
| Desktop, unsupported phone, restricted browser, or denied access | Interactive 3D, then photo fallback | Full dish information stays usable. Never block browsing on AR support. |
| Embedded QR/social browser | Try supported behavior, otherwise guided browser switch | Preserve a copyable dish URL and offer concise “Open in Safari/Chrome” guidance after a failure; do not repeatedly request permissions. |

Apple documents USDZ viewing through Quick Look in built-in apps including Safari. Google documents Scene Viewer launching AR or 3D from web-hosted models. These are native system experiences reached from the website and generally require no restaurant-app installation, but device support and system components still matter. Sources: [Apple Quick Look](https://developer.apple.com/quick-look-gallery/), [Google Scene Viewer](https://developers.google.com/ar/develop/scene-viewer).

Do not promise an arbitrary HTML ingredients/reviews panel inside Quick Look or Scene Viewer. In WebXR, investigate a compact DOM overlay, with details outside AR if unavailable; the [WebXR DOM Overlays explainer](https://github.com/immersive-web/dom-overlays/blob/main/explainer.md) describes that capability. If full simultaneous UI is mandatory across iPhone and Android, run a separate feasibility comparison of browser tracking SDKs before accepting this baseline.

Perform runtime capability checks and handle launch failures; browser-name detection alone is insufficient. `isSessionSupported('immersive-ar')` is only an initial signal: session creation and required hit testing can still fail. WebXR is served in a secure context; follow the [WebXR specification](https://immersive-web.github.io/webxr/) and [hit-test specification](https://immersive-web.github.io/hit-test/) during implementation.

## 4. Alternatives and when to revisit

| Approach | Benefits | Costs / decision |
|---|---|---|
| Viewer component plus platform AR | Low custom rendering effort, standard asset pipeline, broad practical starting point | Recommended prototype; accept platform-specific UI and native handoff. |
| Custom WebXR renderer | Greater control of interactions and in-session information | More code, QA and rendering responsibility; still dependent on device/browser capabilities. Revisit for validated interaction needs. |
| Printed marker/image tracking | Known-size table target can supply a placement reference | Requires visible printed targets and a suitable tracking implementation; test tracking, payload, licensing and devices. Revisit if surface tracking fails frequently or cross-platform custom overlays are mandatory. |
| Commercial browser AR SDK | Potential alternative tracking and interface capabilities | Vendor-specific coverage, costs, terms, privacy and bundle size require a new evaluation. No vendor is selected. |
| Native app | Extensive platform integration | Installation and separate app delivery conflict with the current web-first goal. Outside baseline. |

A camera video with a fixed image pasted on top is not sufficient: it lacks stable surface placement and credible real-world scale.

## 5. 3D asset creation and publishing

### Capture and authoring

1. Plate a representative, approved serving. Record portion label, food quantities, plate diameter, and overall width/depth/height using real measurements.
2. Photograph the dish for immediate use in the menu. For 3D, trial photogrammetry with overlapping images around the dish under diffuse, consistent light; keep dish and lighting stable.
3. Clean reconstruction artifacts, remove captured table/background geometry, simplify the mesh, and bake textures. Use manual modeling or a hybrid workflow when capture fails.
4. Expect transparent glasses, glossy sauces, steam, thin leaves, and moving/melting food to be difficult. Prototype these early. Do not depend on runtime AI generation for faithful ingredients or size.
5. Author in physical units, with a consistent up axis and origin at the bottom of the plate so it sits on a table. Ensure the exported model bounds correspond to the measured serving.

### Optimization and format delivery

- Keep an editable master and export versioned GLB and USDZ artifacts from the same approved geometry, dimensions and materials.
- Apply the budgets in the [requirements document](./PROJECT_REQUIREMENTS.md#6-performance-and-delivery-budgets). They are project targets, not universal platform limits.
- Google recommends an ideal range of 30k–50k triangles for Scene Viewer and a 100k recommended limit. Keep the initial target conservative; see the [Scene Viewer asset guidance](https://developers.google.com/ar/develop/scene-viewer).
- Use simple baked physically based materials and restrained textures. Verify appearance and texture memory on devices, not only in an authoring tool.
- Compression support differs by viewer. Test geometry/texture extensions for every delivered path; keep a compatible export when necessary. Do not assume a GLB that works inline will work unchanged in a native viewer.
- Provide a prevalidated USDZ rather than relying on runtime conversion as the primary production path. Serve correct content types, public HTTPS access where required, and compatible cross-origin headers for browser rendering.
- Validate file structure, byte size, dimensions, texture/material compatibility, and availability before linking assets to published portions.

### Scale and appearance approval

Compare virtual and real plates on the same table from several viewpoints. Proposed pilot gate: perceived plate diameter within ±10% of the measured plate on each supported path under good tracking, using a documented measurement procedure. Confirm or revise this tolerance with the restaurant; it is not an AR accuracy guarantee.

Start at 1:1 scale and disable guest resizing where supported. If a viewer permits resizing anyway, explain that the appearance is representative and retain the numeric portion data on the page. Preview zoom in non-AR 3D is separate from physical AR scale.

Restaurant approval covers food appearance, portion dimensions and asset-to-variant mapping. Each recipe, plate, or portion change triggers a content/asset review. A dish can remain photo-only until its model is approved.

## 6. Logical architecture and viewer lifecycle

```text
QR / direct link
      |
Mobile menu web UI ---- Menu API / published content
      |                         |
Dish + portion selection   Staff editing / moderation
      |
On-demand viewer ---- CDN: posters, GLB, USDZ
      |
Capability / launch handling
      +-- WebXR
      +-- Scene Viewer
      +-- Quick Look
      +-- Inline 3D / photo fallback
```

Keep dish content, asset selection and capability handling separate. A small TypeScript web application is a reasonable implementation candidate; choosing React, Vue, another framework, or hosting infrastructure is deferred until prototype constraints are known. There is no need for a custom 3D engine or a persistent camera-streaming backend in the baseline.

Suggested viewer states: `idle → loading → ready → launching → AR active → returned`. Provide separate `unsupported`, `permission denied`, `asset failed`, and `tracking interrupted` paths with retry or fallback. Native viewers may expose only launch/return signals; do not invent an “AR active” or “placed” event without evidence.

Persist dish/portion ID and menu position before handoff. Handle page visibility, session exit, context loss and repeated entry. Stop rendering and release resources when the viewer closes; avoid multiple active WebGL contexts. Asset failure must not take down the dish page.

For a later custom WebXR path: request immersive AR and hit testing, show a placement indicator at a valid surface hit, place the model after confirmation, and handle tracking/session loss. Advanced anchors, depth occlusion and lighting estimation are optional enhancements requiring separate tests; they are not baseline guarantees.

## 7. Restaurant conditions and recovery

| Condition | Expected response |
|---|---|
| Dark, glossy, glass, or featureless table | Ask guest to scan slowly with sufficient light; offer reposition/retry and an immediate 3D/photo alternative. |
| Crowded table or wrong detected surface | Guide toward a clear patch of tabletop and allow re-placement; avoid claiming automatic table recognition. |
| Poor network or large model | Show useful loading progress, allow cancellation, retain the poster, and retry without losing details. |
| Camera denied or AR unavailable | Continue with inline 3D or photos; explain the alternative concisely. |
| Physical object intersects the dish | Permit repositioning; do not promise realistic occlusion on every device. |
| Tracking lost during use | Show platform-supported guidance; on WebXR, offer re-placement or exit. Never imply size remains exact after obvious drift. |
| Thermal slowdown or memory pressure | Reduce rendering work where controllable; close the viewer cleanly and preserve the menu. |

## 8. Prototype and validation plan

**Prototype assets:** One matte solid dish, one detailed/leafy dish, and one glossy or transparent case. Use actual measurements and matching GLB/USDZ exports.

**Provisional test coverage:** At least one older supported iPhone and one recent iPhone in Safari; two AR-capable Android phones across performance tiers in Chrome; an Android without usable AR services; and an embedded-browser QR launch. Choose exact devices/OS versions before declaring the support policy. Browser simulations alone cannot validate table tracking.

**Tests:**

- Scan QR, open deep-linked dish/portion, launch AR, place/reposition, exit, and verify restored selection and scroll.
- Compare appearance and scale in every format/path with a real serving and plate. Check models sit on, rather than float above or sink into, the surface.
- Try wood, patterned, glossy and glass tables in daylight and typical dim restaurant lighting.
- Exercise denied permissions, service/browser incompatibility, offline entry, slow downloads, asset 404s, tracking loss and interrupted sessions.
- Switch dishes repeatedly and run several-minute sessions to inspect memory, heat, battery and stability.
- Measure initial-menu and deferred-model budgets separately; test cold and warm caches. Capture device, browser, network, format and asset version with each result.
- Verify full dish details, review moderation, accessibility and photo fallback without any AR capability.
- Conduct a small observed guest pilot: can guests place the dish without staff help and understand that portion/appearance are approximate?

**Go/no-go gate:** Publish a tested support matrix, measured budget results, scale/visual approval, and per-dish asset effort. If table placement or iPhone handoff fails the agreed goals, reduce scope or compare marker/SDK alternatives before producing the full model catalog.

## 9. Main risks and decisions still open

The largest ongoing cost is likely asset creation and upkeep; measure it rather than estimating solely from application coding effort. Browser behavior, unsupported extensions, native handoffs, and difficult table surfaces require testing throughout delivery.

Before implementation, confirm whether full ingredients/reviews must remain simultaneously visible during AR on every target phone. Also choose the initial device list, launch dish count, asset owner, serving-scale tolerance, and acceptable capture turnaround. These decisions determine whether the recommended platform-viewer architecture is sufficient.

## 10. Primary references

Reviewed for this planning baseline on 2026-11-06. Recheck current documentation and actual devices before implementation.

- [Model-viewer AR examples](https://modelviewer.dev/examples/augmentedreality/index.html): supported viewer routes and example configuration.
- [Model-viewer documentation](https://modelviewer.dev/docs/): component API and loading/AR integration details.
- [Apple Quick Look gallery](https://developer.apple.com/quick-look-gallery/): platform USDZ preview support and sample assets.
- [WebKit: Viewing AR assets in Safari](https://webkit.org/blog/8421/viewing-augmented-reality-assets-in-safari-for-ios/): web-to-Quick-Look integration and MIME type.
- [Google Scene Viewer](https://developers.google.com/ar/develop/scene-viewer): Android launch behavior, fallbacks and model recommendations.
- [WebXR specification](https://immersive-web.github.io/webxr/): session and capability model.
- [WebXR Hit Test specification](https://immersive-web.github.io/hit-test/): surface hit-testing API.
- [WebXR DOM Overlays explainer](https://github.com/immersive-web/dom-overlays/blob/main/explainer.md): HTML controls during supported immersive sessions.

## Implemented demonstration — 6 November 2026

The separate Preview page now uses `@google/model-viewer` with a local 651 KB CC0 avocado GLB. Rotate/zoom/reset work in the browser. The viewer is loaded only on that route and offers AR when supported by the device/browser. This demonstrates the integration, not a Coconut Grove serving: dish models, plate dimensions, scale checks and physical iPhone/Android validation are still outstanding. Secure hosting is required for browser camera-based AR. See [current implementation boundaries](./coconut-grove/PAGE_UPDATE.md).
