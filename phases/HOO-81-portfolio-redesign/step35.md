# Step 35 — section-layout

- 목적: 섹션 여백·Career·그리드 반응형.
- 예상 16분 / 선행 0~34 / 공통 절차 설계 §15 / 종료 gate: CLI
- read-first: 설계 §6, §9; 섹션 CSS, timeline, 그리드
- tracked 허용(exact): `css/style.css`(섹션 여백, Career, 그리드, `.subsection-title`만), `tests/specs/layout.spec.js`
- runtime: R0
- 금지: §15.7, `index.html`, `js/*`, `css/themes.css`

## 작업 (TDD)

1. 시작 snapshot: `python3 -I tests/scripts/start-snapshot.py step35`
2. `layout.spec.js`(6 project): 가로 스크롤 없음, projectGrid·strengthsGrid 3/2/1열, Career 375 세로·768/1280 가로, 375 highlights 보임, career~contact padding-top 동일, `.subsection-title` font-weight ≤ h2.
3. style.css(토큰만). axe 새 target은 step 32 규칙.

## AC

- `sh tests/scripts/with-env.sh npm --prefix tests test -- layout.spec.js && sh tests/scripts/with-env.sh npm --prefix tests test && sh tests/scripts/with-env.sh npm --prefix tests run verify-scope && sh tests/scripts/with-env.sh node tests/scripts/scope-snapshot.mjs --check tests/.tmp/start-snapshot-step35.json --allow css/style.css,tests/specs/layout.spec.js` → exit 0
