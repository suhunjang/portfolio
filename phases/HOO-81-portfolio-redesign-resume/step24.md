# Resume Step 24 — component-hover-active (원 step 49)

- 목적: 원 §11.2 step 49 비색 hover·active와 상태별 BASE 색 보존.
- 16분 / 선행 0~23 / 공통 원 §9 + §R1·§R2 no-op / gate `RGATE 24`
- 허용(exact): `css/style.css`(`.hero-cta .btn`·`.featured-card`·`#projectGrid .project-card`의 `:hover`·`:active`에서 transform·opacity·transition만), `tests/specs/component-hover.spec.js`(신규)
- runtime: R0
- 추가 금지: `index.html`, `js/*`, 색 선언·순서, hit·clamp, focus-visible, helper·generator·fixture·기존 spec, `measureStateSequence` 밖 측정, page 단위 테마 주입

## 작업
1. `RSNAP 24` → `DI`(`Components.dc.html` 읽기만).
2. RED spec(`desktop-dark`·`desktop-light`, §THEME `test`의 `context`·url `/`, `measureStateSequence`만): `hero-cta-btn-{i}`·`grid-card-0`·`grid-card-1` 상태별 색 3속성 = fixture[project 테마]; 첫 `.featured-card` = `grid-card-1`; hover·active 각각 transform 또는 opacity ≠ default; outline-color = default.
3. style.css(guard 통과).

## AC
- `DI && W node tests/scripts/make-state-colors.mjs --check && T component-hover.spec.js state-sequence.spec.js state-colors.spec.js component-hit.spec.js GS && FULL && VS && RGATE 24 css/style.css,tests/specs/component-hover.spec.js tests/specs/component-hover.spec.js`
