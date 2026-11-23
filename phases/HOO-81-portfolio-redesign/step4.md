# Step 4 — axe-baseline

- 예상 시간: 20분
- 실행 횟수: 수집 테스트 1회, 병합 1회, 일반 테스트 1회(각 웹서버 1회), verify-scope 1회
- 선행 step: 0~3 completed

## 공통: 시작 전 필수 확인 (read-first)

1. 저장소 지침을 읽는다: `CLAUDE.md`(중앙 Harness 계약), `README.md`. 하위 디렉터리에 `CLAUDE.md`나 `AGENTS.md`가 있으면 함께 읽는다.
2. 설계 문서를 읽는다.
   - `docs/superpowers/specs/2026-07-29-quiet-executive-redesign-design.md`
   - `docs/superpowers/specs/2026-11-23-portfolio-layout-redesign-design.md` §8.1, §8.3
3. index.json에서 step 0~3이 completed인지 확인한다. 아니면 중단한다.
4. 현재 코드를 확인한다.
   - 모달 DOM과 `ensureLightbox`
   - JS 렌더 영역
   - themes.css의 토큰
   - `tests/helpers/modal.js`
5. 다음 경로는 read-only다.
   - `CLAUDE.md`, `docs/**`, `phases/**`
   - `.harness/**`, `.claude/**`, `.codex/**`
   - `pytest.ini`, `.python-version`, `.gitattributes`, 루트 `.gitignore`
6. git과 Harness 운영 명령은 하네스만 실행한다. main 직접 변경, merge, deploy는 금지다.
7. 공통 실행 계약: npm·node 명령은 모두 `sh tests/scripts/with-env.sh <명령>`으로 실행한다.

## tracked source 허용 파일 (exact)

- `tests/specs/axe.spec.js`
- `tests/helpers/axe.js`
- `tests/fixtures/axe-baseline.json`

## runtime 쓰기 허용 경로 (추적 금지)

- `tests/.tmp/**`
- `tests/.npm-cache/**`
- `tests/test-results/**`
- `tests/playwright-report/**`

## 수정 금지

- `tests/` 밖의 모든 파일
- 기존 tests 파일

## 작업

### 1. `tests/helpers/axe.js` (library 겸 CLI)

import할 때 fixture를 읽지 않는다. export 목록:

- `runAxe(page, { include })`: wcag2a·wcag2aa 규칙 중 serious와 critical만 반환한다.
- `COLLECT_DIR`
- `EXPECTED_FILES`: 10개
  - `page-{mobile,tablet,desktop}-{dark,light}.json`
  - `modal-desktop-{dark,light}.json`
  - `lightbox-desktop-{dark,light}.json`
- `writeCollected(scenario, project, violations)`: 위반이 없으면 `[]`를 쓴다.
- `mergeCollected()`: 수집 파일 목록이 `EXPECTED_FILES`와 정확히 같지 않으면 throw한다.
- `validateBaseline(entries) => string[]`
- `checkRegression(violations, baseline, scenario, project) => string[]`
  - 새 key와 새 target을 오류로 반환한다.
  - 사라진 key와 target은 허용한다.
- `loadBaseline()`: 호출될 때만 fixture를 읽는다.

CLI
- `--reset`
- `--merge`: 결과를 `tests/.tmp/axe-collected.json`에 쓴다. 10개 파일 검증에 실패하면 exit 1로 끝난다.

### 2. `tests/specs/axe.spec.js`

시나리오
- page: 6개 project, reducedMotion reduce
- modal: desktop-dark와 desktop-light, `#projectModal`만 include
- lightbox: desktop-dark와 desktop-light, `.lightbox`만 include

수집 모드 (`AXE_COLLECT=1`)
- `loadBaseline`을 호출하지 않는다.
- 실제 fixture 스키마 검사와 회귀 판정은 `test.skip`으로 건너뛴다.
- `writeCollected`만 호출한다.
- 합성 스키마 테스트는 실행한다.

일반 모드
- `checkRegression`이 `[]`를 반환해야 한다.
- `validateBaseline(loadBaseline())`이 `[]`를 반환해야 한다.
- 합성 테스트도 실행한다.

합성 테스트 (desktop-dark에서 1회)
- a) 통과: 혼합 color-contrast
  - fixes `[{t1, css-token, [css/themes.css]}, {t2, css-rule, [css/style.css]}]`
  - 항목 fixFiles는 두 파일 모두
- b) 거부: fixFiles 합집합 불일치
- c) 거부: target에 대한 fix 누락
- d) 거부: targets에 없는 target
- e) 거부: fixFiles가 비어 있지 않은 text-change
- f) 거부: 알 수 없는 fixKind
- g) `checkRegression`이 새 target을 오류로 반환한다.
- h) `checkRegression`이 사라진 target은 오류로 보지 않는다.

### 3. 수집 (이 순서대로)

1. `sh tests/scripts/with-env.sh node tests/helpers/axe.js --reset`
2. `AXE_COLLECT=1 sh tests/scripts/with-env.sh npm --prefix tests test -- axe.spec.js`
3. `sh tests/scripts/with-env.sh node tests/helpers/axe.js --merge`

### 4. fixture 생성

- target별로 §8.3 규칙에 따라 분류해 `fixes`를 채운다.
- 항목 `fixFiles`에는 그 target들의 fixFiles 합집합을 넣는다.
- 위반이 없으면 fixture는 `[]`이다.
- text-change가 나오면 로그에 명시한다.

### 5. 일반 모드로 확인한다.

## 완료 기준 (AC)

- `sh tests/scripts/with-env.sh node tests/helpers/axe.js --reset && AXE_COLLECT=1 sh tests/scripts/with-env.sh npm --prefix tests test -- axe.spec.js && sh tests/scripts/with-env.sh node tests/helpers/axe.js --merge` → exit 0
- `sh tests/scripts/with-env.sh npm --prefix tests test && sh tests/scripts/with-env.sh npm --prefix tests run verify-scope` → 통과
