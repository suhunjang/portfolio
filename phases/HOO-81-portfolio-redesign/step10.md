# Step 10 — axe-baseline-regression

- 예상 시간: 18분
- 실행 횟수: 테스트 2회, verify-scope 1회
- 선행 step: 0~9 completed

## 공통: 시작 전 필수 확인 (read-first)

1. 저장소 지침을 읽는다: `CLAUDE.md`(중앙 Harness 계약), `README.md`. 하위 디렉터리에 `CLAUDE.md`나 `AGENTS.md`가 있으면 함께 읽는다.
2. 설계 문서를 읽는다.
   - `docs/superpowers/specs/2026-07-29-quiet-executive-redesign-design.md`
   - `docs/superpowers/specs/2026-11-23-portfolio-layout-redesign-design.md` §8.3 (entry key 계약, step 10: 스키마, 회귀, 누락 정책, `FIX_FILES_BY_KIND`)
3. index.json에서 step 0~9가 completed인지 확인한다. 아니면 중단한다.
4. axe.js의 `Violation`, `MergedEntry`, `makeEntryKey`를 확인한다.
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
- 그 밖의 tests 파일, fixtures
- step 7·9에서 만든 동작 (`makeEntryKey` 포함)

## 작업

1. axe.js에 step 10 계약을 구현한다.
   - 상수: `BASELINE_PATH`, `FIX_FILES_BY_KIND`
   - 함수: `baselineExists`, `loadBaseline`, `resolveBaselineMode`, `validateBaseline`, `checkRegression`, `assertEmptyFile`
   - `validateBaseline`: `key === makeEntryKey(항목)`, key 고유, targets 중복 없음·정렬을 추가로 확인한다.
   - `checkRegression(violations, baseline, scenario, project)`: key는 `makeEntryKey({ scenario, project, ruleId })`로 만든다.
   - CLI: `--assert-empty [path]`
2. axe-helper.spec.js에 테스트를 추가한다 (desktop-dark).
   - `validateBaseline`
     - 통과: 혼합 color-contrast, js-render `[js/main.js]`, static-markup `[index.html]`, text-change `[]`
     - 거부(key): key가 `makeEntryKey`와 다름, 중복 key, targets 중복, targets 미정렬
     - 거부(파일 오대응): css-token에 `[css/style.css]`, css-rule에 `[css/themes.css]`, js-render에 `[index.html]`, static-markup에 `[js/main.js]`, text-change에 `[index.html]`
     - 거부(빈 배열): css-token·css-rule·js-render·static-markup에 `[]`
     - 거부(파일 여분): js-render에 `[js/main.js, index.html]`
     - 거부(기타): 합집합 불일치, fix 누락, targets 밖의 target, 알 수 없는 kind
   - `checkRegression`
     - 새 key 또는 새 target은 오류다.
     - 사라진 항목은 허용한다.
     - 같은 canonical target이 baseline의 `page:desktop-dark:*`에만 있을 때 `page:desktop-light`에서 나타나면 `new-key` 또는 `new-target`으로 잡힌다(다른 entry로 취급).
     - 입력을 변경하지 않는다.
   - `resolveBaselineMode`
     - 파일 있음 → check
     - 파일 없음, env `{}` → throw
     - 파일 없음, `AXE_ALLOW_MISSING_BASELINE` = `'1'` → skip
     - 파일 없음, 값이 `'true'` → throw
   - `loadBaseline`: 파일 없음, 잘못된 JSON, `{}`에서 throw
   - subprocess `--assert-empty`
     - `[]` → 0
     - `[{}]`, `{}`, 잘못된 JSON, 파일 없음 → 1

## 완료 기준 (AC)

- `sh tests/scripts/with-env.sh npm --prefix tests test -- axe-helper.spec.js && sh tests/scripts/with-env.sh npm --prefix tests test && sh tests/scripts/with-env.sh npm --prefix tests run verify-scope` → 통과
