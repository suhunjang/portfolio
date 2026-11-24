# Step 25 — axe-prepare-page

- 목적: 준비 helper 공통 오류 계약과 page 준비.
- 예상 15분 / 선행 0~24 / 공통 절차 설계 §15 / 종료 gate: CLI
- read-first: 설계 §3(reveal), §8.4(step 25)
- tracked 허용(exact): `tests/helpers/axe-prepare.js`(신규: `PREPARE_PREFIX`, `prepareError`, `withPrepareCode`, `preparePage`만), `tests/specs/axe-prepare-page.spec.js`(신규)
- runtime: R0
- 금지: §15.7

## 작업

1. 시작 snapshot: `python3 -I tests/scripts/start-snapshot.py step25`
2. 설계 §8.4 step 25 계약.
3. spec(desktop-dark, desktop-light, mobile-dark): 실제 사이트 `revealChecked` > 0·모두 `.in`·반환 후 scrollY 0·scrollSteps ≥ 1; `.in`이 안 붙는 `.reveal` 1개 + `timeoutMs: 500` → `prepareForAxe: reveal-hidden:1`·code 일치; `prepareError('x')` message·code; `withPrepareCode('fonts-not-ready', reject boom)` message·cause; `withPrepareCode('a', reject prepareError('b'))` 코드 b; data-theme·reduced-motion 불변.

## AC

- `sh tests/scripts/with-env.sh npm --prefix tests test -- axe-prepare-page.spec.js && sh tests/scripts/with-env.sh npm --prefix tests test && sh tests/scripts/with-env.sh npm --prefix tests run verify-scope && sh tests/scripts/with-env.sh node tests/scripts/scope-snapshot.mjs --check tests/.tmp/start-snapshot-step25.json --allow tests/helpers/axe-prepare.js,tests/specs/axe-prepare-page.spec.js` → exit 0
