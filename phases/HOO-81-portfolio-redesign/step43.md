# Step 43 — print-pdf

- 목적: 인쇄 스타일(line clamp 해제 포함)과 PDF 검증.
- 예상 17분 / 선행 0~42 / 공통 절차 설계 §15 / 종료 gate: CLI
- read-first: 설계 §10, §16.2
- tracked 허용(exact): `css/style.css`(`@media print` 블록만, 색 선언 없음), `tests/specs/print.spec.js`
- runtime: R0
- 금지: §15.7, `index.html`, `js/*`, PDF 파서 의존성

## 작업 (TDD)

1. 시작 snapshot: `python3 -I tests/scripts/start-snapshot.py step43`
2. `print.spec.js`(desktop-dark/light): `pdfPageCount(buf) = (buf.toString('latin1').match(/\/Type\s*\/Page\b/g) || []).length` 자체 검증; A·B 시나리오(§10), print에서 blurb `-webkit-line-clamp` `none`/`unset`, PDF 조건.
3. `@media print`.

## AC

- `sh tests/scripts/with-env.sh npm --prefix tests test -- print.spec.js design-guard-css.spec.js design-guard.spec.js && sh tests/scripts/with-env.sh npm --prefix tests test && sh tests/scripts/with-env.sh npm --prefix tests run verify-scope && sh tests/scripts/with-env.sh node tests/scripts/scope-snapshot.mjs --check tests/.tmp/start-snapshot-step43.json --allow css/style.css,tests/specs/print.spec.js` → exit 0
