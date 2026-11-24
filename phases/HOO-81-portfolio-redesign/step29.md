# Step 29 — axe-prepare-page

- 목적: §6.3 step 29.
- 15분 / 선행 0~28 / 공통 §9 / gate GATE
- 허용(exact): `tests/helpers/axe-prepare.js`(신규: `PREPARE_PREFIX`, `prepareError`, `withPrepareCode`, `preparePage`만), `tests/specs/axe-prepare-page.spec.js`(신규)
- runtime: R0

## 작업
1. `SNAP 29`
2. spec(desktop-dark, desktop-light, mobile-dark): `revealChecked` > 0·모두 `.in`·scrollY 0·scrollSteps ≥ 1; `.in` 안 붙는 `.reveal` 1개 + `timeoutMs: 500` → `prepareForAxe: reveal-hidden:1`·code; `prepareError('x')` message·code; `withPrepareCode('fonts-not-ready', reject boom)` message·cause; `withPrepareCode('a', reject prepareError('b'))` 코드 b; data-theme·reduced-motion 불변.

## AC
- `T axe-prepare-page.spec.js && FULL && VS && GATE 29 tests/helpers/axe-prepare.js,tests/specs/axe-prepare-page.spec.js`
