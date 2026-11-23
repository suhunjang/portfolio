# Step 8 — axe-remediation

- 예상 시간: 15분
- 실행 횟수: 테스트 2회, verify-scope 1회
- 선행 step: 0~7 completed

## 공통: 시작 전 필수 확인 (read-first)

1. 저장소 지침 `CLAUDE.md`(하네스 계약 포함)와 `README.md`를 읽는다. 하위 디렉터리에 `CLAUDE.md`/`AGENTS.md`가 있으면 함께 읽는다.
2. 설계 문서를 읽는다.
   - `docs/superpowers/specs/2026-07-29-quiet-executive-redesign-design.md` — 대비를 조정할 때도 톤을 유지한다.
   - `docs/superpowers/specs/2026-11-23-portfolio-layout-redesign-design.md` — §7-6, §8.3
3. index.json에서 step 0~7이 completed인지 확인한다. 아니면 중단한다.
4. `tests/fixtures/axe-baseline.json`을 읽고 이번 step의 허용 파일을 확정한다.
   - 허용 파일은 각 항목 `fixFiles`의 합집합이다.
   - fixture가 `[]`이면 사이트 파일은 수정하지 않고, 현재 axe 위반 0건인지만 확인한다.
   - text-change 항목이 있으면 즉시 중단하고 보고한다.
5. 다음 경로는 읽기 전용이다.
   - `CLAUDE.md`, `docs/**`, `phases/**`, `.harness/**`
   - 하네스 managed 파일: `scripts/**`, `.claude/**`, `.codex/**`, `templates/**`, `harness-manifest.json`, `pytest.ini`, `.python-version`, `.gitattributes`, 루트 `.gitignore`
6. git add·commit·push는 하네스만 한다. main 직접 변경, merge, deploy는 금지다.

## tracked source 허용 파일 (exact)

아래 파일은 fixture의 `fixFiles` 합집합에 들어 있을 때만 수정할 수 있다.

- `css/themes.css`: 색 토큰의 명도 값만 바꾼다. 토큰 이름과 구조는 유지한다.
- `css/style.css`: 위반 selector에 해당하는 규칙만 바꾼다.
- `js/main.js`: 위반 대상 렌더 마크업의 속성만 바꾼다.
- `index.html`: 위반 대상 요소의 aria-*, role, alt, lang, tabindex, for 속성만 바꾼다. 요소 추가·삭제·이동과 텍스트 변경은 금지다.

`tests/fixtures/axe-baseline.json`은 항상 수정할 수 있지만 `[]`로 비우는 것만 허용한다.

## runtime 쓰기 허용 경로 (추적 금지)

- `tests/.tmp/**`
- `tests/test-results/**`
- `tests/playwright-report/**`

## 수정 금지

- `js/data.js`
- `fixFiles`에 없는 사이트 파일
- spec 파일과 다른 fixture

## 중단 조건

구조 변경이나 문구 변경이 필요한 위반이 있으면 사이트 파일을 수정하지 않는다. 해당 key와 사유를 보고하고 중단한다. 하네스가 담당 구현 step(5 또는 6)을 다시 연다.

## 작업

1. fixture 항목마다 `fixKind`에 맞춰 최소한으로 수정한다.
   - css-token: themes.css의 명도 값을 조정한다.
   - css-rule: style.css의 해당 규칙을 고친다.
   - js-render: main.js에서 렌더 마크업의 속성을 고친다.
   - static-markup: index.html의 속성을 고친다.
2. `tests/fixtures/axe-baseline.json`을 `[]`로 바꾼다.
3. axe.spec를 실행해 page 6조합, modal 2테마, lightbox 2테마 모두 serious/critical 위반이 0건인지 확인한다.

## 완료 기준 (AC)

- `npm --prefix tests test && npm --prefix tests run verify-scope`가 모두 통과한다.
- `axe-baseline.json`이 `[]`이다.
- content.spec와 layout.spec에 회귀가 없다. 이것으로 구조와 문구가 그대로임을 증명한다.
