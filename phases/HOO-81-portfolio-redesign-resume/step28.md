# Resume Step 28 — print-pdf (원 step 53)

- 목적: 원 §7 인쇄(clamp 해제)·PDF.
- 17분 / 선행 0~27 / 공통 원 §9 + §R1·§R2 no-op / gate `RGATE 28`
- 허용(exact): `css/style.css`(`@media print`만, 색 선언 없음), `tests/specs/print.spec.js`
- runtime: R0
- 추가 금지: `index.html`, `js/*`, 색 규칙 순서, PDF 파서 의존성

## 작업
1. `RSNAP 28`
2. RED spec(desktop-dark/light): `pdfPageCount(buf) = (buf.toString('latin1').match(/\/Type\s*\/Page\b/g) || []).length` 자체 검증(`/Pages`만 0, `/Page` 1, `/Type/Page` 1); A: 본문·featured visible·opacity 1, reveal 비어 있지 않음, 인터랙션·modal 숨김, lightbox 없음/none, print에서 `.featured-blurb`·카드 blurb clamp `none`/`unset`, PDF > 10240·count ≥ 1; B: screen lightbox visible → print에서 lightbox·modal none, PDF 동일.
3. `@media print`.

## AC
- `T print.spec.js GS && FULL && VS && RGATE 28 css/style.css,tests/specs/print.spec.js`
