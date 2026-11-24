# Step 39 — component-states

- 목적: component state(default/hover/active/open, 비색 속성만), 44px hit target, blurb line clamp 3, strength 장식 stripe 제거(선택).
- 예상 19분 / 선행 0~38 / 공통 절차 설계 §15 / 종료 gate: CLI
- read-first: 설계 §3, §16.2~§16.4(DESIGN_HASH_CHECK 후 `Components.dc.html`·`MobileMenu.dc.html` 읽기 전용); fixture tokens; main.js 카드 blurb 렌더 요소(셀렉터를 spec 상수 `CARD_BLURB`로 확정)
- tracked 허용(exact): `css/style.css`(상태·hit target·line clamp 규칙과 `.strength-card::before` 삭제만), `tests/specs/component-states.spec.js`(신규)
- runtime: R0
- 금지: §15.7, `index.html`, `js/*`, `css/themes.css`, 색 선언·색 역할 변경, focus-visible outline 변경(step 41)

## 작업 (TDD)

1. 시작 snapshot: `python3 -I tests/scripts/start-snapshot.py step39` → `python3 -I tests/scripts/design-intake-check.py`
2. `component-states.spec.js`(6 project) 먼저 실패 확인
   - hit target: 설계 §16.2 대상 중 보이는 요소(mobile은 메뉴를 연 상태의 `.nav-link` 포함, 모달은 열어서 `.modal-close`)의 bbox width·height ≥ tokens.hitTargetMinPx
   - hover·active(desktop, `.hero-cta .btn`, `.featured-card`, `#projectGrid .project-card`): hover(또는 mouse down) 중 computed `transform` 또는 `opacity`가 default와 다르고, `color`·`background-color`·`border-color`·`outline-color`는 default와 같음
   - open: `#menuToggle` 클릭 후 `aria-expanded="true"`·`#navLinks.open`, 모달 열림 시 body `modal-open`; 열린 상태의 `.nav-link`·`.modal-close` 색 속성이 기존 값과 같음(열기 전 측정값과 비교)
   - line clamp: `.featured-blurb`와 `#projectGrid` `CARD_BLURB`의 computed `-webkit-line-clamp` = `3`, textContent는 해당 `PROJECTS[i].blurb` 전문(norm), 모달 `.modal-blurb`는 clamp 없음
   - strength stripe: `.strength-card::before`가 있으면 content `none` 또는 display `none`이어도 되고 없어도 됨(어느 쪽이든 통과), strength 카드 텍스트 불변
3. style.css(색 선언 없음; guard 통과).

## AC

- `python3 -I tests/scripts/design-intake-check.py && sh tests/scripts/with-env.sh npm --prefix tests test -- component-states.spec.js design-guard.spec.js && sh tests/scripts/with-env.sh npm --prefix tests test && sh tests/scripts/with-env.sh npm --prefix tests run verify-scope && sh tests/scripts/with-env.sh node tests/scripts/scope-snapshot.mjs --check tests/.tmp/start-snapshot-step39.json --allow css/style.css,tests/specs/component-states.spec.js --require-absent tests/specs/component-states.spec.js` → exit 0
