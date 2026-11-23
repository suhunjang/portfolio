# Step 5 — axe-helper

- 예상 시간: 20분
- 실행 횟수: 테스트 2회(합성 검증 포함), verify-scope 1회
- 선행 step: 0~4 completed

## 공통: 시작 전 필수 확인 (read-first)

1. 저장소 지침을 읽는다: `CLAUDE.md`(중앙 Harness 계약), `README.md`. 하위 디렉터리에 `CLAUDE.md`나 `AGENTS.md`가 있으면 함께 읽는다.
2. 설계 문서를 읽는다.
   - `docs/superpowers/specs/2026-07-29-quiet-executive-redesign-design.md`
   - `docs/superpowers/specs/2026-11-23-portfolio-layout-redesign-design.md` §8.1, §8.3 (canonical target 식별, helper, 스키마, 회귀 판정)
3. index.json에서 step 0~4가 completed인지 확인한다. 아니면 중단한다.
4. 현재 코드에서 JS 렌더 영역 id, `data-project` 사용처, landmark 요소를 확인한다.
5. 다음은 수정하지 않는다(read-only): `CLAUDE.md`, `docs/**`, `phases/**`, `.harness/**`, `.claude/**`, `.codex/**`, `pytest.ini`, `.python-version`, `.gitattributes`, 루트 `.gitignore`
6. 명령 권한
   - Git 상태를 바꾸는 명령과 Harness 운영 명령은 하네스만 실행한다.
   - 검증용 Git 읽기 명령(rev-parse, diff, show, ls-files, ls-tree, status, log)은 허용한다.
   - main 직접 변경, merge, deploy는 금지다.
7. 공통 실행 계약: npm·node 명령은 `sh tests/scripts/with-env.sh <명령>`으로 실행한다.

## tracked source 허용 파일 (exact)

- `tests/helpers/axe.js`
- `tests/specs/axe-helper.spec.js`

## runtime 쓰기 허용 경로 (추적 금지)

- `tests/.tmp/**` (합성 fixture 임시 파일 포함)
- `tests/.npm-cache/**`, `tests/test-results/**`, `tests/playwright-report/**`

## 수정 금지

- `tests/` 밖의 모든 파일
- 기존 tests 파일
- `tests/fixtures/axe-baseline.json`과 `tests/specs/axe.spec.js` (다음 step에서 만든다)

## 범위

이 step은 helper, 스키마, canonical 식별, 회귀 판정, 합성 검증만 만든다. 실제 시나리오 수집과 fixture 생성은 하지 않는다.

## 작업

### 1. `tests/helpers/axe.js`

import할 때 fixture를 읽지 않는다.

- `canonicalTargetInPage`: 브라우저에서 실행하는 함수. 요소를 받아 §8.3 규칙의 `{ anchor, text }`를 반환한다.
  - anchor 우선순위: `featured:N` → `project:N` → `#id` → landmark → `document`
  - text
    - norm(textContent)를 쓴다. 비어 있으면 aria-label, alt, title, src 파일명 순으로 대체한다.
    - 숫자는 `#`으로 바꾼다.
    - 80자까지만 쓴다.
    - 고정 alias 표를 적용한다.
- `canonicalFromDescriptor({ ruleId, anchor, text }): string`
  - 순수 함수. `{ruleId}::{anchor}::{textSig}`를 반환한다.
- `runAxe(page, { include })`
  - AxeBuilder(wcag2a, wcag2aa)로 serious·critical 위반만 모은다.
  - 각 node의 selector로 같은 page에서 `canonicalTargetInPage`를 실행한다.
  - 반환: `{ ruleId, impact, selectors, targets }[]`. targets는 중복을 제거한 canonical key다.
- `COLLECT_DIR`, `EXPECTED_FILES`(10개)
- `writeCollected(scenario, project, violations)`
- `mergeCollected()`: 수집 파일이 정확히 10개가 아니면 throw한다.
- `validateBaseline(entries): string[]`: target별 `fixes` 스키마를 검사한다.
- `checkRegression(violations, baseline, scenario, project): string[]`
  - 새 key나 새 canonical target은 오류다.
  - 사라진 것은 허용한다.
  - baseline을 수정하지 않는다.
- `loadBaseline()`
- CLI: `--reset`, `--merge`, `--assert-empty [path]`
  - `--assert-empty`의 기본 path는 `tests/fixtures/axe-baseline.json`이다.
  - 정확히 빈 JSON 배열이면 exit 0이다.
  - 없음, 파싱 실패, 배열 아님, 원소가 1개 이상이면 exit 1이다.

### 2. `tests/specs/axe-helper.spec.js` (합성 검증, desktop-dark만)

canonical 안정성: `page.setContent`로 실제 axe를 돌려 확인한다.
- a) 같은 color-contrast canonical key가 나온다.
  - 변경 전: `section#career` 안 `h3`의 저대비 텍스트 `01 — Career`
  - 변경 후: `main`으로 감싸 이동하고 `span`으로 바꾼 뒤 텍스트를 `04 — Career`로 변경
- b) `[data-project=5]` 안의 같은 텍스트는 div에서 p로 바뀌어도 key가 같다.
- c) 텍스트가 다르면 key가 다르다.
- d) `project:5`와 `featured:5`는 서로 다른 key다.
- e) alias: `05 — Stack & Contact`와 `05 — Contact`는 같은 key다.

스키마
- 통과: 혼합 color-contrast
- 거부
  - 합집합 불일치
  - fix 누락
  - targets 밖의 target
  - 비어 있지 않은 text-change
  - 알 수 없는 fixKind

회귀 판정
- 새 canonical target은 오류다.
- 사라진 target은 오류가 아니다.
- 판정 후 baseline 객체가 바뀌지 않는다.

`--assert-empty`
- `child_process`로 node를 실행한다. 테스트 프로세스가 이미 래퍼 환경 안이다.
- `tests/.tmp` 아래 임시 파일로 확인한다.
  - `[]` → 0
  - `[{}]` → 1
  - `{}` → 1
  - 잘못된 JSON → 1
  - 파일 없음 → 1

## 완료 기준 (AC)

- `sh tests/scripts/with-env.sh npm --prefix tests test && sh tests/scripts/with-env.sh npm --prefix tests run verify-scope`가 통과한다.
- axe-helper.spec.js의 합성 검증이 모두 통과한다.
