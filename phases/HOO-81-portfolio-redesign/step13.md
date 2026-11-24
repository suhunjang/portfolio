# Step 13 — design-guard

- 목적: 설계 §16.3 제외 항목(새 색·색 역할 변경·서체 asset/weight·새 이미지·아이콘)을 BASE 대비 diff로 기계 거부하는 guard를 만든다. 이후 모든 step의 전체 테스트에서 실행된다.
- 예상 19분 / 선행 0~12 / 공통 절차 설계 §15 / 종료 gate: CLI
- read-first: 설계 §3, §16.2~§16.4; BASE `css/style.css`·`css/themes.css`(`git show`로 읽기)
- tracked 허용(exact): `tests/helpers/design-guard.js`(신규), `tests/specs/design-guard.spec.js`(신규)
- runtime: R0
- 금지: §15.7, 사이트 파일

## 작업

1. 시작 snapshot: `python3 -I tests/scripts/start-snapshot.py step13`
2. `design-guard.js`: 설계 §16.4의 순수 함수 `checkCssPatch(patch, { baseCss, baseThemes })`, `checkMarkupPatch(patch, kind)`와 `collectGuardInput({ git })`(BASE→worktree `--no-renames --unified=0` patch 4종: `css/style.css`, `css/themes.css`, `index.html`, `js/main.js`, 그리고 BASE css 2종; Git 읽기만). 위반 문자열 형식은 설계 그대로.
3. `design-guard.spec.js`(node 전용, desktop-dark만)
   - 단위(합성 patch): 추가 `color: #0d0f12;` → `color-literal`·`color-prop`; `background: rgba(0,0,0,.5)`; `border: 1px solid var(--border)` → `color-prop`, `border: 0` 허용; `.x:focus-visible { outline: 2px solid var(--accent); }`(BASE 정의 토큰) 허용, 정의 없는 토큰 → `unknown-token`; `font-family:`·`@import`·`@font-face` → `font-asset`; `font-weight: 800` → `font-weight`, `600` 허용; `url(` → `asset`; `content: '★'` → `content`, `content: none` 허용; `--section-pad: 96px` 정의 후 `var(--section-pad)` 허용; 삭제 `color: var(--text-muted)`가 `.timeline-company` 블록이면 `color-removed`, `.strength-card::before` 블록이면 허용; themes patch 비어 있지 않음 → `themes-changed`; index 추가 `<img`·`<svg`·`style=` → `markup-asset`; 선택자 줄만 바뀐 경우(`.project-card,` → `.project-card, .featured-card {`) 위반 없음; 입력 불변
   - 실제 저장소: `collectGuardInput`로 현재 worktree를 검사해 위반 `[]`

## AC

- `sh tests/scripts/with-env.sh npm --prefix tests test -- design-guard.spec.js && sh tests/scripts/with-env.sh npm --prefix tests test && sh tests/scripts/with-env.sh node tests/scripts/scope-snapshot.mjs --check tests/.tmp/start-snapshot-step13.json --allow tests/helpers/design-guard.js,tests/specs/design-guard.spec.js --require-absent tests/helpers/design-guard.js,tests/specs/design-guard.spec.js` → exit 0
