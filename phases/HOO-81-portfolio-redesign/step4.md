# Step 4 — axe-baseline

- 예상 시간: 20분
- 실행 횟수: 수집 테스트 1회, 병합 1회, 일반 테스트 1회(각각 웹서버 1회), verify-scope 1회
- 선행 step: 0~3 completed

## 공통: 시작 전 필수 확인 (read-first)

1. 저장소 지침을 읽는다: `CLAUDE.md`(하네스 계약 포함), `README.md`. 하위 디렉터리에 `CLAUDE.md`나 `AGENTS.md`가 있으면 함께 읽는다.
2. 설계 문서를 읽는다.
   - `docs/superpowers/specs/2026-07-29-quiet-executive-redesign-design.md`
   - `docs/superpowers/specs/2026-11-23-portfolio-layout-redesign-design.md` §8.1, §8.3 (실행 모드, 수집, 스키마, 분류, 회귀 판정)
3. index.json에서 step 0~3이 completed인지 확인한다. 아니면 중단한다.
4. 현재 코드를 확인한다.
   - 모달 DOM, `ensureLightbox`
   - JS 렌더 영역
   - themes.css 토큰
   - `tests/helpers/modal.js`
5. 다음은 read-only다.
   - `CLAUDE.md`, `docs/**`, `phases/**`, `.harness/**`
   - 하네스 managed 파일: `scripts/**`, `.claude/**`, `.codex/**`, `templates/**`, `harness-manifest.json`, `pytest.ini`, `.python-version`, `.gitattributes`, 루트 `.gitignore`
6. git add·commit·push는 하네스만 한다. main 직접 변경, merge, deploy는 금지다.
7. 공통 실행 계약: npm·node 명령은 모두 `sh tests/scripts/with-env.sh <명령>`으로 실행한다.

## tracked source 허용 파일 (exact)

- `tests/specs/axe.spec.js`
- `tests/helpers/axe.js`
- `tests/fixtures/axe-baseline.json`

## runtime 쓰기 허용 경로 (추적 금지)

- `tests/.tmp/**` (`axe-collected/`, `axe-collected.json` 포함)
- `tests/.npm-cache/**`
- `tests/test-results/**`
- `tests/playwright-report/**`

## 수정 금지

- `tests/` 밖의 모든 파일
- 기존 tests 파일

## 작업

### 1. `tests/helpers/axe.js` (library 겸 CLI)

import 시점에 fixture를 읽지 않는다. export할 항목:

- `runAxe(page, { include }) => { ruleId, impact, targets }[]`
  - wcag2a·wcag2aa 기준으로 serious/critical만 반환한다.
- `COLLECT_DIR`: `tests/.tmp/axe-collected`의 절대경로
- `EXPECTED_FILES`: 다음 10개
  - `page-{mobile,tablet,desktop}-{dark,light}.json` 6개
  - `modal-desktop-{dark,light}.json` 2개
  - `lightbox-desktop-{dark,light}.json` 2개
- `writeCollected(scenario, project, violations)`: 위반이 없으면 `[]`를 쓴다.
- `mergeCollected() => entries`: 파일 목록이 `EXPECTED_FILES`와 정확히 같지 않으면 throw한다.
- `validateBaseline(entries) => string[]`: 설계 §8.3 스키마를 검사한다.
- `checkRegression(violations, baseline, scenario, project) => string[]`
  - 각 위반에 대해 다음을 확인한다.
    - key가 baseline에 있는가
    - 위반의 각 target이 그 항목의 `targets`에 있고 대응하는 `fixes` 원소가 있는가
  - 새 key와 새 target을 오류로 반환한다.
  - baseline에만 있는 key나 target(사라진 것)은 허용한다.
- `loadBaseline()`: 호출할 때만 파일을 읽는다.

CLI (`node tests/helpers/axe.js <cmd>`)
- `--reset`: `COLLECT_DIR`를 삭제하고 다시 만든다.
- `--merge`: 병합 결과를 `tests/.tmp/axe-collected.json`에 쓴다. 10개 검증에 실패하면 exit 1.

### 2. `tests/specs/axe.spec.js`

시나리오
- page: 6개 project, reducedMotion reduce
- modal: desktop-dark, desktop-light. `#projectModal`만 include
- lightbox: desktop-dark, desktop-light. `.lightbox`만 include

수집 모드 (`AXE_COLLECT=1`)
- `loadBaseline()`을 호출하지 않는다.
- 실제 fixture 스키마 테스트와 회귀 판정은 `test.skip`으로 건너뛴다.
- 각 시나리오 테스트는 `writeCollected(scenario, project.name, violations)`만 한다. 테스트마다 파일이 달라 병렬 실행에서도 충돌하지 않는다.
- 합성 스키마 테스트는 실행한다.

일반 모드
- 각 시나리오에서 `checkRegression(...)`가 `[]`를 반환해야 한다.
- 실제 fixture 스키마 테스트(desktop-dark에서 1회): `validateBaseline(loadBaseline())`가 `[]`를 반환해야 한다.
- 합성 스키마 테스트도 실행한다.

합성 스키마 테스트 (모든 모드, desktop-dark에서 1회)
- a) 통과: 혼합 color-contrast
  - targets 2개
  - fixes: `[{t1, css-token, [css/themes.css]}, {t2, css-rule, [css/style.css]}]`
  - 항목 fixFiles: 두 파일 모두
- b) 거부: a에서 항목 fixFiles가 `[css/themes.css]`뿐인 경우
- c) 거부: target 하나에 fix가 없음
- d) 거부: targets에 없는 target
- e) 거부: text-change인데 fixFiles가 비어 있지 않음
- f) 거부: 알 수 없는 fixKind
- 회귀 판정 합성 사례
  - g) baseline에 있는 key에 새 target이 나타나면 `checkRegression`이 오류를 반환한다.
  - h) baseline target 일부가 사라진 경우는 오류가 아니다.

### 3. 수집 (아래 순서 그대로)

1. `sh tests/scripts/with-env.sh node tests/helpers/axe.js --reset`
2. `AXE_COLLECT=1 sh tests/scripts/with-env.sh npm --prefix tests test -- axe.spec.js`
3. `sh tests/scripts/with-env.sh node tests/helpers/axe.js --merge`
   - exit 0이어야 하고, 결과는 `tests/.tmp/axe-collected.json`에 생긴다.

### 4. fixture 생성

- 병합 결과의 각 항목을 target별로 §8.3 규칙에 따라 분류해 `fixes`를 채운다.
- 항목 `fixFiles`에는 fixes의 합집합을 넣는다.
- `tests/fixtures/axe-baseline.json`에 쓴다. 위반이 없으면 `[]`다.
- text-change target이 있으면 로그에 명시한다. 이는 step 8의 중단 사유가 된다.

### 5. 일반 모드로 확인

일반 모드 실행으로 실제 fixture 스키마와 회귀 판정을 확인한다.

## 완료 기준 (AC)

- 수집: `sh tests/scripts/with-env.sh node tests/helpers/axe.js --reset && AXE_COLLECT=1 sh tests/scripts/with-env.sh npm --prefix tests test -- axe.spec.js && sh tests/scripts/with-env.sh node tests/helpers/axe.js --merge` → exit 0
- 일반 모드: `sh tests/scripts/with-env.sh npm --prefix tests test && sh tests/scripts/with-env.sh npm --prefix tests run verify-scope` → 통과 (실제 스키마 검사와 target 단위 회귀 판정 포함)
