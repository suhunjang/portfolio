# Step 31 — print-pdf

- 목적: 인쇄 스타일과 PDF 검증.
- 예상 16분 / 선행 0~30 / 공통 절차 설계 §15
- read-first: 설계 §10; `@media print`, `ensureLightbox`
- tracked 허용(exact): `css/style.css`(`@media print` 블록만), `tests/specs/print.spec.js`
- runtime: R0
- 금지: §15.7, `index.html`, `js/*`, `css/themes.css`, PDF 파서 의존성

## 작업 (TDD)

1. 시작 snapshot: `python3 -I tests/scripts/start-snapshot.py step31`
2. `print.spec.js`(desktop-dark/light): `pdfPageCount(buf) = (buf.toString('latin1').match(/\/Type\s*\/Page\b/g) || []).length` 자체 검증(`/Pages`만 0, `/Page` 1, `/Type/Page` 1); A: 본문·featured visible·opacity 1, reveal 비어 있지 않음, 인터랙션·modal 숨김, lightbox 없음 또는 none, PDF > 10240바이트·count ≥ 1; B: screen에서 lightbox visible 확인 → print에서 lightbox·modal none, 본문 A와 같음, PDF 조건 동일.
3. `@media print`: reveal 보이기, featured 포함, overlay·인터랙션 숨김, modal-open 잠금 해제, 기존 숨김 유지.

## AC

- `sh tests/scripts/with-env.sh npm --prefix tests test -- print.spec.js && sh tests/scripts/with-env.sh npm --prefix tests test && sh tests/scripts/with-env.sh npm --prefix tests run verify-scope && sh tests/scripts/with-env.sh node tests/scripts/scope-snapshot.mjs --check tests/.tmp/start-snapshot-step31.json --allow css/style.css,tests/specs/print.spec.js` → exit 0
