# Coconut Grove design review

**Date:** 2026-11-06  
**Scope:** Review and improve the existing React website, preserving its mobile-first menu, four-color palette and explicit sample/planned labels.

## Applied skill perspectives

- **gpt-taste:** editorial composition, a two-line hero, clear progression from introduction to menu to planned table preview to visit, and real GSAP motion.
- **minimalist-ui:** restrained controls, flat menu rows, readable charcoal text, consistent spacing and deliberate typographic contrast.
- **high-end-visual-design:** self-hosted typography, refined button feedback, stronger mobile composition and controlled motion easing.

These skills conflict on pills versus square buttons, light versus bold icon strokes, neutral versus colorful sections, and motion intensity. The project brief takes priority: retain the established green/gold/ivory/charcoal identity, keep the menu lightweight, and make planned features explicit. A new randomized marketing layout, fabricated testimonials, unrelated media, heavy glass effects and scroll pinning were not appropriate to this review.

## Findings and changes

| Finding | Improvement |
|---|---|
| Generic system typography and scattered style overrides weakened hierarchy. | Added locally served Geist and Instrument Serif. Replaced the old minified, repeatedly overridden stylesheet with one organized stylesheet. |
| Mobile navigation was entirely hidden. | Added a keyboard-operable mobile menu with expanded state, link navigation, Escape dismissal and focus restoration. Desktop navigation remains visible. |
| Favorites, categories and dish links had 32–40px touch targets. | Increased major controls to at least 44px. All tested targets meet that size at 390px. |
| Menu requests removed every row, briefly collapsing the page. | Added accessible decorative skeleton rows while requests are pending. In the throttled test, loading retained 1440px of a previously 1628px menu rather than collapsing to zero. |
| The phone introduction delayed access to the menu. | Reduced mobile hero spacing and omitted its duplicate location line on phones. Location remains in the visit section. |
| Category boxes and repeated diamond markers added visual clutter. | Simplified inactive categories, introduced consistent menu-row spacing/dividers, and retained clear text-only planned AR labels. |
| Hover and entry behavior lacked a consistent motion system. | Added custom easing and separately loaded GSAP/ScrollTrigger enhancements, scoped to subtle text and illustration entry. No scroll pinning or automatic video. |
| Motion could add unnecessary work for accessibility-sensitive users. | Reduced-motion preference disables CSS motion and skips the optional motion download on initial load. Optional-chunk failure is contained so the menu remains usable. |

## Validation

- Production TypeScript/Vite build passes.
- Existing 19 browser integration checks pass: API-backed menu, filters, ingredients, favorites, portions, dialogs, local review demo, offline recovery, responsive widths and development proxy.
- Additional 11 design/accessibility checks pass: mobile navigation, keyboard traversal, Escape and focus, navigation links, 44px major controls, stable loading, 320px overflow, reduced motion, font loading and runtime exceptions.
- Visual inspection completed at 1440, 768 and 390px. The hero stays at two lines, body text is 16px, both selected typefaces load, and the layout inspector reports no failures.
- Initial application JavaScript is approximately 76.3 KB gzip. Motion is a separate optional chunk of approximately 45.1 KB gzip, requested after the initial interface; it is skipped for initial reduced-motion preference. Fonts are served locally rather than requested from a third-party font service.

## Deliberate exceptions and remaining limits

The inspection tool still warns about the agreed warm ivory palette, multiple responsive type sizes, restrained motion, absent footage and a measured margin discrepancy. The CSS uses equal page gutters, verified visually; the tool's inferred content margins differ. These findings do not justify changing the established brand or adding unrelated video and stronger animation to a phone menu. Informative planned/sample labels and restrained row dividers are retained despite the newer inspector's generic label/divider rules.

This is not a complete accessibility audit or a performance benchmark on real restaurant phones. Production still needs approved restaurant food photography, menu/ingredient/allergen information, actual AR assets and device testing. No backend, authentication, review persistence or hosting behavior was changed by this design pass.
