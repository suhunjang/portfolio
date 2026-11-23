# Step 4 — axe-baseline

- 예상 시간: 18분
- 실행 횟수: 수집 테스트 1회, 병합 1회, 전체 테스트 1회(각 웹서버 1회), verify-scope 1회
- 선행 step: 0~3 completed

## 공통: 시작 전 필수 확인 (read-first)

1. 저장소 지침을 읽는다: `CLAUDE.md`(하네스 계약 포함), `README.md`. 하위 디렉터리에 `CLAUDE.md`나 `AGENTS.md`가 있으면 함께 읽는다.
2. 설계 문서를 읽는다.
   - `docs/superpowers/specs/2026-07-29-quiet-executive-redesign-design.md`
   - `docs/superpowers/specs/2026-11-23-portfolio-layout-redesign-design.md`의 §8.1, §8.3 (수집, fixture 스키마, target별 분류, 스키마 검증)
3. index.json에서 step 0~3이 completed인지 확인한다. 아니면 중단한다.
4. 현재 코드를 확인한다.
   - 모달 DOM과 `ensureLightbox`
   - JS 렌더 영역 id
   - themes.css 색 토큰
   - `tests/helpers/modal.js`
5. 다음 경로는 read-only다.
   - `CLAUDE.md`, `docs/**`, `phases/**`, `.harness/**`
   - 하네스 managed 파일: `scripts/**`, `.claude/**`, `.codex/**`, `templates/**`, `harness-manifest.json`, `pytest.ini`, `.python-version`, `.gitattributes`, 루트 `.gitignore`
6. git add·commit·push는 하네스만 한다. main 직접 변경, merge, deploy는 금지다.

## tracked source 허용 파일 (exact)

- `tests/specs/axe.spec.js`
- `tests/helpers/axe.js`
- `tests/fixtures/axe-baseline.json`

## runtime 쓰기 허용 경로 (추적 금지)

- `tests/.tmp/**` (`tests/.tmp/axe-collected/`, `tests/.tmp/axe-collected.json` 포함)
- `tests/test-results/**`
- `tests/playwright-report/**`

## 수정 금지

- `tests/` 밖의 모든 파일
- 기존 tests 파일

## 작업

### 1. `tests/helpers/axe.js` (라이브러리 겸 CLI)

export 목록:

- `runAxe(page, { include }) => { ruleId, impact, targets }[]`
  - AxeBuilder로 wcag2a와 wcag2aa를 검사한다.
  - serious/critical만 반환한다.
  - targets는 node target을 문자열로 바꾼 배열이다.
- `COLLECT_DIR`: `tests/.tmp/axe-collected`의 절대경로. `import.meta.url` 기준으로 계산한다.
- `EXPECTED_FILES`: 아래 10개 파일명
  - `page-{mobile,tablet,desktop}-{dark,light}.json` 6개
  - `modal-desktop-dark.json`, `modal-desktop-light.json`
  - `lightbox-desktop-dark.json`, `lightbox-desktop-light.json`
- `writeCollected(scenario, project, violations)`
  - `COLLECT_DIR/{scenario}-{project}.json`에 기록한다.
  - 위반이 없으면 `[]`를 쓴다.
- `mergeCollected() => entries`
  - 디렉터리 파일 목록이 `EXPECTED_FILES`와 정확히 같아야 한다. 누락이나 여분이 있으면 throw한다.
  - 같으면 key 단위로 병합해 반환한다.
- `validateBaseline(entries) => string[]`
  - 설계 §8.3 스키마 오류 목록을 반환한다.
  - 검사 항목
    - 필수 필드가 있는지
    - fixKind가 허용된 값인지
    - 각 target에 fix가 정확히 1개 대응하는지, targets에 없는 target이 없는지
    - text-change이면 fixFiles가 빈 배열인지
    - fixFiles가 허용된 4개 파일의 부분집합인지
    - 항목 fixFiles가 fixes 합집합과 같은지
- `loadBaseline()`

CLI (`node tests/helpers/axe.js <command>`로 직접 실행할 때)
- `--reset`: `COLLECT_DIR`를 삭제하고 다시 만든다.
- `--merge`: `mergeCollected()` 결과를 `tests/.tmp/axe-collected.json`에 쓴다. 10개 검증에 실패하면 exit 1로 끝난다.

### 2. `tests/specs/axe.spec.js`

검사 시나리오
- page: 6개 project, reducedMotion reduce
- modal: desktop-dark/light에서 Motion-O 모달을 열고, `#projectModal`만 include한다.
- lightbox: desktop-dark/light에서 lightbox를 열고, `.lightbox`만 include한다.

실행 모드
- `AXE_COLLECT=1`일 때
  - 판정하지 않는다.
  - 각 테스트는 `writeCollected(scenario, project.name, violations)`만 호출한다.
  - 파일이 테스트마다 따로 생기므로 병렬로 실행해도 충돌하지 않는다.
- 그 밖의 경우
  - fixture에 없는 key가 나오면 실패한다.
  - fixture에만 있고 실행 결과에서 사라진 key는 허용한다.

스키마 테스트 (desktop-dark에서 1회)
- 실제 `axe-baseline.json`에 `validateBaseline`을 돌려 오류가 0건이다.
- 합성 사례
  - a) 통과: 혼합 color-contrast
    - targets 2개
    - fixes = `[{target: t1, fixKind: css-token, fixFiles: [css/themes.css]}, {target: t2, fixKind: css-rule, fixFiles: [css/style.css]}]`
    - 항목 fixFiles = `[css/themes.css, css/style.css]`
  - b) 거부: a에서 항목 fixFiles만 `[css/themes.css]`로 바꾼 경우
  - c) 거부: target 하나의 fix가 없는 경우
  - d) 거부: targets에 없는 target
  - e) 거부: text-change인데 fixFiles가 비어 있지 않은 경우
  - f) 거부: 알 수 없는 fixKind

### 3. 수집 실행 (아래 순서대로)

1. `node tests/helpers/axe.js --reset`
2. `AXE_COLLECT=1 npm --prefix tests test -- axe.spec.js`
3. `node tests/helpers/axe.js --merge` (exit 0이어야 하며 `tests/.tmp/axe-collected.json`이 생성된다)

### 4. `tests/fixtures/axe-baseline.json` 확정

- 병합 결과의 각 항목에 대해 target마다 §8.3 분류 규칙으로 `fixes`를 채운다.
- 항목 `fixFiles`에는 그 합집합을 기록한다.
- 위반이 없으면 `[]`이다.
- text-change target이 있으면 로그에 명시한다. 이는 step 8의 중단 사유가 된다.

## 완료 기준 (AC)

- `node tests/helpers/axe.js --reset && AXE_COLLECT=1 npm --prefix tests test -- axe.spec.js && node tests/helpers/axe.js --merge`가 exit 0이다. 10개 파일 검증도 여기에 포함된다.
- `npm --prefix tests test && npm --prefix tests run verify-scope`가 통과한다. 스키마 테스트도 여기에 포함된다.
