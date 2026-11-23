# Step 7 — axe-baseline-regression

- 예상 시간: 18분
- 실행 횟수: 테스트 2회, verify-scope 1회
- 선행 step: 0~6 completed

## 공통: 시작 전 필수 확인 (read-first)

1. 저장소 지침 `CLAUDE.md`(중앙 Harness 계약)와 `README.md`를 읽는다. 하위 디렉터리에 `CLAUDE.md`나 `AGENTS.md`가 있으면 함께 읽는다.
2. 설계 문서를 읽는다.
   - `docs/superpowers/specs/2026-07-29-quiet-executive-redesign-design.md`
   - `docs/superpowers/specs/2026-11-23-portfolio-layout-redesign-design.md` §8.3 (step 7: baseline 스키마, 회귀 판정, 누락 정책, `FIX_FILES_BY_KIND`)
3. index.json에서 step 0~6이 completed인지 확인한다. 아니면 중단한다.
4. axe.js의 `Violation`과 수집 함수를 확인한다.
5. 빌더 read-only 경로: `CLAUDE.md`, `docs/**`, `phases/**`, `.harness/**`, `.claude/**`, `.codex/**`, `pytest.ini`, `.python-version`, `.gitattributes`, 루트 `.gitignore`
6. 명령 권한
   - Git 상태를 바꾸는 명령과 Harness 운영 명령은 하네스만 실행한다.
   - 검증용 Git 읽기 명령(rev-parse, diff, show, ls-files, ls-tree, status, log)은 허용한다.
   - main 직접 변경, merge, deploy는 금지다.
7. 공통 실행 계약: npm·node 명령은 `sh tests/scripts/with-env.sh <명령>`으로 실행한다.

## tracked source 허용 파일 (exact)

- `tests/helpers/axe.js` (추가만)
- `tests/specs/axe-helper.spec.js` (추가만)

## runtime 쓰기 허용 경로 (추적 금지)

- `tests/.tmp/axe-helper-test-*/**`, `tests/.tmp/**`
- `tests/.npm-cache/**`, `tests/test-results/**`, `tests/playwright-report/**`

## 수정 금지

- `tests/` 밖 전부
- 그 밖의 tests 파일
- fixtures
- step 5·6에서 만든 동작

## 작업

1. axe.js에 step 7 계약을 구현한다.
   - `BASELINE_PATH`, `FIX_FILES_BY_KIND`
   - `baselineExists`, `loadBaseline`, `resolveBaselineMode`, `validateBaseline`, `checkRegression`, `assertEmptyFile`
   - CLI: `--assert-empty [path]`
2. axe-helper.spec.js에 추가한다 (desktop-dark).
   - `validateBaseline`
     - 통과
       - 혼합 color-contrast: css-token `[css/themes.css]` + css-rule `[css/style.css]`
       - js-render `[js/main.js]`
       - static-markup `[index.html]`
       - text-change `[]`
     - 거부 (오대응)
       - css-token `[css/style.css]`
       - css-rule `[css/themes.css]`
       - js-render `[index.html]`
       - static-markup `[js/main.js]`
       - text-change `[index.html]`
     - 거부 (빈 배열): css-token, css-rule, js-render, static-markup 각각 `[]`
     - 거부 (여분): js-render `[js/main.js, index.html]`
     - 거부 (기타): 합집합 불일치, fix 누락, targets 밖의 target, 알 수 없는 kind
   - `checkRegression`
     - 새 key나 target이 있으면 오류다.
     - 사라진 것은 허용한다.
     - 입력을 바꾸지 않는다.
   - `resolveBaselineMode` (경로는 독립 디렉터리)
     - 파일 있음 → check
     - 파일 없음 + `env: {}` → throw (기본 누락 실패)
     - 파일 없음 + `{ AXE_ALLOW_MISSING_BASELINE: '1' }` → skip
     - 파일 없음 + 값 `'true'` → throw
   - `loadBaseline`: 파일 없음, 잘못된 JSON, `{}` → throw
   - subprocess `--assert-empty`
     - `[]` → 0
     - `[{}]`, `{}`, 잘못된 JSON, 파일 없음 → 1

## 완료 기준 (AC)

- `sh tests/scripts/with-env.sh npm --prefix tests test -- axe-helper.spec.js && sh tests/scripts/with-env.sh npm --prefix tests test && sh tests/scripts/with-env.sh npm --prefix tests run verify-scope` → 통과
