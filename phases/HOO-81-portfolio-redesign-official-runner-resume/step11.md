# Step 11: print-pdf

## Always-on invariants
Do not modify historical phase records/evidence. Preserve all copy, numbers, font assets/weights, information architecture, 3 featured project identities, all 13 PROJECTS and order. No new copy, section, image, icon, project or placeholder content. css/themes.css is read-only; if it or index.html is required outside the listed lane, stop and replan. Implementation workers must not commit, push, merge, edit the canonical phase index, or write outside their exact lane files. Run only focused tests in lanes; canonical FULL/UI/a11y run at steps 12 and 14.

## Exact work order
### Bound historical contract: `phases/HOO-81-portfolio-redesign-resume/step30.md`
SHA-256 `1a4bcfee2f25d77d176275875a6a1f6630bc0b8fc41f86aa044ea6c28775fdbc`

# Resume Step 30 — print-pdf (원 step 53)

- 목적: 원 §7 인쇄(clamp 해제)·PDF.
- 17분 / 선행 0~29 / 공통 원 §9 + §R1·§R2 no-op·§R11 / gate `RGATE 30`
- 허용(exact): `css/style.css`(`@media print`만, 색 선언 없음), `tests/specs/print.spec.js`
- 필수 산출물(REQ): `tests/specs/print.spec.js,css/style.css`
- runtime: R0
- 추가 금지: `index.html`, `js/*`, 색 규칙 순서, PDF 파서 의존성

## 작업
1. `RSNAP 30` → no-op 첫 probe `REQ 30 tests/specs/print.spec.js,css/style.css`. PASS면 나머지 AC 실행 → 통과 시 `resume step30: no-op`. REQ FAIL 또는 AC 실패면 아래 작업 후 완전한 AC 재실행.
2. RED spec(desktop-dark/light): `pdfPageCount(buf) = (buf.toString('latin1').match(/\/Type\s*\/Page\b/g) || []).length` 자체 검증(`/Pages`만 0, `/Page` 1, `/Type/Page` 1); A: 본문·featured visible·opacity 1, reveal 비어 있지 않음, 인터랙션·modal 숨김, lightbox 없음/none, print에서 `.featured-blurb`·카드 blurb clamp `none`/`unset`, PDF > 10240·count ≥ 1; B: screen lightbox visible → print에서 lightbox·modal none, PDF 동일.
3. `@media print`.

## AC
- `REQ 30 tests/specs/print.spec.js,css/style.css && T print.spec.js GS && FULL && VS && RGATE 30 css/style.css,tests/specs/print.spec.js`(첫 명령 stdout `required-artifacts step130: OK 2`)


Only `@media print` declarations and print spec. Do not add PDF parser dependencies or color declarations.

## Exact write boundary
print-pdf: css/style.css, tests/specs/print.spec.js

## Acceptance
Run every argv in this step’s immutable `index.json.acceptanceCommands` in order. Any nonzero exit blocks the next step.
