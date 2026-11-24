# Step 23 — axe-prepare-page

- 목적: 준비 helper 공통 오류 계약과 page 준비.
- 예상 15분 / 선행 0~22 / 공통 절차 설계 §15 / 종료 gate: CLI
- read-first: 설계 §3, §8.4(step 23)
- tracked 허용(exact): `tests/helpers/axe-prepare.js`(신규: 4개 export만), `tests/specs/axe-prepare-page.spec.js`(신규)
- runtime: R0
- 금지: §15.7

## 작업

1. 시작 snapshot: `python3 -I tests/scripts/start-snapshot.py step23`
2. 설계 §8.4 step 23 계약.
3. spec(desktop-dark/light, mobile-dark): 실제 사이트 reveal·scroll; `reveal-hidden:1`; `prepareError`·`withPrepareCode`; 테마·reduced-motion 불변.

## AC

- `sh tests/scripts/with-env.sh npm --prefix tests test -- axe-prepare-page.spec.js && sh tests/scripts/with-env.sh npm --prefix tests test && sh tests/scripts/with-env.sh npm --prefix tests run verify-scope && sh tests/scripts/with-env.sh node tests/scripts/scope-snapshot.mjs --check tests/.tmp/start-snapshot-step23.json --allow tests/helpers/axe-prepare.js,tests/specs/axe-prepare-page.spec.js` → exit 0
