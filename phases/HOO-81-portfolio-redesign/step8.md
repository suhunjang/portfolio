# Step 8 — axe-remediation

- 예상 시간: 15분
- 실행 횟수: 테스트 2회, verify-scope 1회
- 선행 step: 0~7 completed

## 공통: 시작 전 필수 확인 (read-first)

1. 저장소 지침을 읽는다: `CLAUDE.md`(하네스 계약 포함), `README.md`. 하위 디렉터리에 `CLAUDE.md`나 `AGENTS.md`가 있으면 함께 읽는다.
2. 설계 문서를 읽는다.
   - `docs/superpowers/specs/2026-07-29-quiet-executive-redesign-design.md` (톤 유지)
   - `docs/superpowers/specs/2026-11-23-portfolio-layout-redesign-design.md` §7-6, §8.3
3. index.json에서 step 0~7이 completed인지 확인한다. 아니면 중단한다.
4. `tests/fixtures/axe-baseline.json`을 읽고 다음을 확인한다.
   - `validateBaseline` 오류가 0건이다.
   - 이번 step의 허용 파일은 항목 `fixFiles`의 합집합(= fixes의 합집합)이다.
   - fixture가 `[]`이면 사이트 파일은 수정하지 않고, 위반 0건만 확인한다.
   - text-change target이 있으면 즉시 중단하고 보고한다.
5. 다음 경로는 read-only다.
   - `CLAUDE.md`, `docs/**`, `phases/**`, `.harness/**`
   - 하네스 managed 파일: `scripts/**`, `.claude/**`, `.codex/**`, `templates/**`, `harness-manifest.json`, `pytest.ini`, `.python-version`, `.gitattributes`, 루트 `.gitignore`
6. git add·commit·push는 하네스만 한다. main 직접 변경, merge, deploy는 금지다.
7. 공통 실행 계약: npm·node 명령은 모두 `sh tests/scripts/with-env.sh <명령>`으로 실행한다.

## tracked source 허용 파일 (exact)

아래 사이트 파일은 `fixFiles` 합집합에 포함된 경우에만 수정할 수 있다.

- `css/themes.css`: 토큰 명도 값만
- `css/style.css`: 위반 target selector 규칙만
- `js/main.js`: 위반 target 렌더 속성만
- `index.html`: 위반 target 요소의 aria-*, role, alt, lang, tabindex, for 속성만. 요소 추가·삭제·이동과 텍스트 변경은 금지

`tests/fixtures/axe-baseline.json`은 항상 허용한다. 단 `[]`로 바꾸는 수정만 할 수 있다.

## runtime 쓰기 허용 경로 (추적 금지)

- `tests/.tmp/**`
- `tests/.npm-cache/**`
- `tests/test-results/**`
- `tests/playwright-report/**`

## 수정 금지

- `js/data.js`
- `fixFiles`에 없는 사이트 파일
- spec 파일과 다른 fixture

## 중단 조건

구조나 문구를 바꿔야 하는 target이 있으면 사이트 파일을 수정하지 않는다. key, target, 사유를 보고하고 중단한다. 하네스가 step 5 또는 6을 재개한다.

## 작업

1. 각 항목의 `fixes`를 target 단위로 순회한다. 각 target의 fixKind와 fixFiles 범위 안에서 최소한으로 수정한다.
   - css-token: `css/themes.css`의 토큰 명도
   - css-rule: `css/style.css`의 규칙
   - js-render: `js/main.js`의 속성
   - static-markup: `index.html`의 속성
   - 한 항목 안에 css-token과 css-rule이 섞여 있으면 target마다 따로 처리한다.
2. `tests/fixtures/axe-baseline.json`을 `[]`로 바꾼다.
3. axe 10개 시나리오 모두에서 serious/critical 위반이 0건인지 확인한다.

## 완료 기준 (AC)

- `sh tests/scripts/with-env.sh npm --prefix tests test && sh tests/scripts/with-env.sh npm --prefix tests run verify-scope`가 모두 통과한다.
- `axe-baseline.json`이 `[]`이다.
- content.spec와 layout.spec에 회귀가 없다.
