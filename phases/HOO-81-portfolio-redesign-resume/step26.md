# Resume Step 26 — component-hover-active (원 step 49, §R10 분기)

- 목적: 원 §11.2 step 49 비색 hover·active와 상태별 BASE 색 보존.
- 16분 / 선행 0~25 / 공통 원 §9 + §R1·§R10 / gate `RGATE_B 26`
- 허용(exact): `css/style.css`(`.hero-cta .btn`·`.featured-card`·`#projectGrid .project-card`의 `:hover`·`:active`에서 transform·opacity·transition만), `tests/specs/component-hover.spec.js`(신규)
- 분기 R: `tests/specs/component-hover.spec.js`
- runtime: R0
- 추가 금지: `index.html`, `js/*`, 색 선언·순서, hit·clamp, focus-visible, helper·generator·fixture·기존 spec, `measureStateSequence` 밖 측정, page 단위 테마 주입, start snapshot 수정·재생성, existing 분기에서 R 파일 수정

## 작업
1. `RSNAP 26` → `RBRANCH 26 tests/specs/component-hover.spec.js`.
   - `existing`: 작업 2~3 생략, 쓰기 없는 AC 전체 실행 → 통과 시 `resume step26: no-op`, 실패 시 tracked 불변 중단·재계획.
   - `new`: 아래 진행. `branch-mixed`면 중단.
2. `DI`(`Components.dc.html` 읽기만). RED spec(`desktop-dark`·`desktop-light`, §THEME `test`의 `context`·url `/`, `measureStateSequence`만): `hero-cta-btn-{i}`·`grid-card-0`·`grid-card-1` 상태별 색 3속성 = fixture[project 테마]; 첫 `.featured-card` = `grid-card-1`; hover·active 각각 transform 또는 opacity ≠ default; outline-color = default.
3. style.css(guard 통과).

## AC
- `DI && W node tests/scripts/make-state-colors.mjs --check && T component-hover.spec.js state-sequence.spec.js state-colors.spec.js component-hit.spec.js GS && FULL && VS && RGATE_B 26 css/style.css,tests/specs/component-hover.spec.js tests/specs/component-hover.spec.js`
