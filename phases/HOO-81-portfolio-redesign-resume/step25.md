# Resume Step 25 — component-clamp-stripe (원 step 50)

- 목적: blurb line clamp 3, 본문 보존, 선택적 stripe 제거.
- 15분 / 선행 0~24 / 공통 원 §9 + §R1·§R2 no-op / gate `RGATE 25`
- 허용(exact): `css/style.css`(`.featured-blurb`·`CARD_BLURB` line clamp 비색 규칙, BASE `.strength-card::before` 삭제만), `tests/specs/component-clamp.spec.js`(신규)
- runtime: R0
- 추가 금지: `index.html`, `js/*`, 색 선언·순서, 그 밖 strength 규칙, print(resume 28), helper·기존 spec

## 작업
1. `RSNAP 25` → `DI`(`DesktopExplore.dc.html`·`Components.dc.html` 읽기만).
2. RED spec(6 project, 읽기 전 `waitForFiniteAnimations`, spec 상수 `CARD_BLURB`): `.featured-blurb` 3·grid 카드 13 `-webkit-line-clamp` = `3`; textContent(norm) = `PROJECTS[i].blurb`; 카드 0 모달 `.modal-blurb` clamp `none`·전문; `.strength-card` 6개 = `STRENGTHS` 순서·내용.
3. style.css.

## AC
- `DI && T component-clamp.spec.js component-hover.spec.js component-hit.spec.js GS && FULL && VS && RGATE 25 css/style.css,tests/specs/component-clamp.spec.js tests/specs/component-clamp.spec.js`
