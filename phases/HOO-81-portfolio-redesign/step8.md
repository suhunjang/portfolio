# Step 8 — axe-remediation

- 예상 시간: 15분
- 실행 횟수: 테스트 2회, verify-scope 1회
- 선행 step: 0~7 completed

## 공통: 시작 전 필수 확인 (read-first)

1. 저장소 지침을 읽는다: `CLAUDE.md`(하네스 계약 포함)와 `README.md`. 하위 디렉터리에 `CLAUDE.md`나 `AGENTS.md`가 있으면 그것도 읽는다.
2. 설계 문서를 읽는다.
   - `docs/superpowers/specs/2026-07-29-quiet-executive-redesign-design.md`: 대비를 조정할 때도 톤을 유지한다.
   - `docs/superpowers/specs/2026-11-23-portfolio-layout-redesign-design.md`: §7-6, §8.3
3. index.json에서 step 0~7이 completed인지 확인한다. 아니면 중단한다.
4. `tests/fixtures/axe-baseline.json`을 읽는다.
   - `validateBaseline` 결과 오류가 0건인지 확인한다.
   - 이번 step의 허용 파일을 확정한다. 허용 파일은 항목 `fixFiles`의 합집합이며, 이는 `fixes[].fixFiles`의 합집합과 같다.
   - fixture가 `[]`이면 사이트 파일은 수정하지 않고, 위반 0건만 확인한다.
   - text-change target이 있으면 즉시 중단하고 보고한다.
5. 다음 경로는 read-only다.
   - `CLAUDE.md`, `docs/**`, `phases/**`, `.harness/**`
   - 하네스 managed 파일: `scripts/**`, `.claude/**`, `.codex/**`, `templates/**`, `harness-manifest.json`, `pytest.ini`, `.python-version`, `.gitattributes`, 루트 `.gitignore`
6. git add·commit·push는 하네스만 한다. main 직접 변경, merge, deploy는 금지다.

## tracked source 허용 파일 (exact)

아래 파일은 fixture의 `fixFiles` 합집합에 포함된 경우에만 수정할 수 있다.

- `css/themes.css`: 색 토큰의 명도 값만 바꾼다. 토큰 이름과 구조는 그대로 둔다.
- `css/style.css`: 위반 target selector와 관련된 규칙만 바꾼다.
- `js/main.js`: 위반 target의 렌더 마크업 속성만 바꾼다.
- `index.html`: 위반 target 요소의 aria-*, role, alt, lang, tabindex, for 속성만 바꾼다. 요소 추가·삭제·이동과 텍스트 변경은 금지한다.

`tests/fixtures/axe-baseline.json`은 항상 수정할 수 있지만, `[]`로 비우는 것만 허용한다.

## runtime 쓰기 허용 경로 (추적 금지)

- `tests/.tmp/**`
- `tests/test-results/**`
- `tests/playwright-report/**`

## 수정 금지

- `js/data.js`
- `fixFiles`에 없는 사이트 파일
- spec 파일과 다른 fixture

## 중단 조건

다음에 해당하면 사이트 파일을 수정하지 않고 중단한다.
- 구조 변경이 필요한 target
- 문구 변경이 필요한 target

이때 key, target, 사유를 보고한다. 하네스가 담당 구현 step(5 또는 6)을 다시 연다.

## 작업

1. 각 항목의 `fixes` 배열을 target 단위로 순회하며, 각 target의 `fixKind`와 `fixFiles` 범위 안에서만 최소한으로 수정한다.
   - css-token: 해당 target 색이 쓰는 토큰의 명도를 `css/themes.css`에서 조정한다.
   - css-rule: 해당 target selector 규칙을 `css/style.css`에서 수정한다.
   - js-render: 해당 target 렌더 속성을 `js/main.js`에서 수정한다.
   - static-markup: 해당 target 요소 속성을 `index.html`에서 수정한다.
   - 같은 color-contrast 항목에 css-token target과 css-rule target이 섞여 있으면, target마다 각자의 분류에 따라 따로 처리한다.
2. `tests/fixtures/axe-baseline.json`을 `[]`로 바꾼다.
3. axe.spec의 10개 시나리오(page 6조합, modal 2테마, lightbox 2테마) 모두에서 serious/critical 위반이 0건인지 확인한다.

## 완료 기준 (AC)

- `npm --prefix tests test && npm --prefix tests run verify-scope`가 모두 통과한다.
- `axe-baseline.json`이 `[]`다.
- content.spec와 layout.spec에 회귀가 없다. 이것으로 구조와 문구가 그대로임을 확인한다.
