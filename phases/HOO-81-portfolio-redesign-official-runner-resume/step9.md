# Step 9: focus-modal

## Always-on invariants
Do not modify historical phase records/evidence. Preserve all copy, numbers, font assets/weights, information architecture, 3 featured project identities, all 13 PROJECTS and order. No new copy, section, image, icon, project or placeholder content. css/themes.css is read-only; if it or index.html is required outside the listed lane, stop and replan. Implementation workers must not commit, push, merge, edit the canonical phase index, or write outside their exact lane files. Run only focused tests in lanes; canonical FULL/UI/a11y run at steps 12 and 14.

## Exact work order
### Bound historical contract: `phases/HOO-81-portfolio-redesign-resume/step28.md`
SHA-256 `80f55c2b5487663e0680ab2a0d25ee83c48af0604ebfbd4747518819128abcfb`

# Resume Step 28 — focus-trap-modal (원 step 51)

- 목적: 원 §6.1 `trapFocus` 구현과 모달 연결.
- 17분 / 선행 0~27 / 공통 원 §9 + §R1·§R2 no-op·§R11 / gate `RGATE 28`
- 허용(exact): `js/main.js`(`trapFocus`·모달 trap만), `tests/specs/focus-modal.spec.js`(신규)
- 필수 산출물(REQ): `tests/specs/focus-modal.spec.js,js/main.js`
- runtime: R0
- 추가 금지: `index.html`, `js/data.js`, `css/*`, lightbox 코드

## 작업
1. `RSNAP 28` → no-op 첫 probe `REQ 28 tests/specs/focus-modal.spec.js,js/main.js`. PASS면 나머지 AC 실행 → 통과 시 `resume step28: no-op`. REQ FAIL 또는 AC 실패면 아래 작업 후 완전한 AC 재실행.
2. RED spec(desktop-dark/light, mobile-dark): 마지막→Tab→첫, 첫→Shift+Tab→마지막, 밖으로 안 나감; button·backdrop·esc 닫기 후 트리거 복귀; `#heroFeatured`·`#projectGrid` 트리거; 2회 열고 닫아도 Tab 한 칸.
3. 구현.

## AC
- `REQ 28 tests/specs/focus-modal.spec.js,js/main.js && T focus-modal.spec.js && FULL && VS && RGATE 28 js/main.js,tests/specs/focus-modal.spec.js`(첫 명령 stdout `required-artifacts step128: OK 2`)


Concrete anchors: existing `openProjectModal(idx)`, `closeProjectModal()`, modal click/keydown handlers. Trap Tab/Shift+Tab inside the open modal and restore the exact trigger on close; do not change lightbox behavior here.

## Exact write boundary
focus-modal: js/main.js, tests/specs/focus-modal.spec.js

## Acceptance
Run every argv in this step’s immutable `index.json.acceptanceCommands` in order. Any nonzero exit blocks the next step.
