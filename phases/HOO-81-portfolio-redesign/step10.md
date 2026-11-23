# Step 10 — axe-remediation

- 예상 시간: 15분
- 실행 횟수: 테스트 2회, `--assert-empty` 1회, verify-scope 1회
- 선행 step: 0~9 completed

## 공통: 시작 전 필수 확인 (read-first)

1. 저장소 지침을 읽는다: `CLAUDE.md`(중앙 Harness 계약), `README.md`. 하위 디렉터리에 `CLAUDE.md`나 `AGENTS.md`가 있으면 함께 읽는다.
2. 설계 문서를 읽는다.
   - `docs/superpowers/specs/2026-07-29-quiet-executive-redesign-design.md`
   - `docs/superpowers/specs/2026-11-23-portfolio-layout-redesign-design.md` §7.2-6, §8.3
3. index.json에서 step 0~9가 completed인지 확인한다. 아니면 중단한다.
4. `tests/fixtures/axe-baseline.json`을 확인한다.
   - `validateBaseline` 오류가 0이어야 한다.
   - 이번 step의 허용 파일은 `fixFiles` 합집합이다.
   - fixture가 `[]`이면 사이트 파일을 수정하지 않는다.
   - text-change가 있으면 중단한다.
5. 빌더 read-only 경로: `CLAUDE.md`, `docs/**`, `phases/**`, `.harness/**`, `.claude/**`, `.codex/**`, `pytest.ini`, `.python-version`, `.gitattributes`, 루트 `.gitignore`
6. 명령 권한
   - Git 상태를 바꾸는 명령과 Harness 운영 명령은 하네스만 실행한다.
   - 검증용 Git 읽기 명령(rev-parse, diff, show, ls-files, ls-tree, status, log)은 허용한다.
   - main 직접 변경, merge, deploy는 금지다.
7. 공통 실행 계약: npm·node 명령은 `sh tests/scripts/with-env.sh <명령>`으로 실행한다.

## tracked source 허용 파일 (exact)

`fixFiles` 합집합에 속한 파일만 아래 범위에서 수정한다.

- `css/themes.css`: 토큰 명도
- `css/style.css`: target 규칙
- `js/main.js`: target 렌더 속성
- `index.html`: target 요소의 aria-*, role, alt, lang, tabindex, for 속성만

그리고 `tests/fixtures/axe-baseline.json`은 `[]`로 바꾸는 것만 허용한다.

## runtime 쓰기 허용 경로 (추적 금지)

- `tests/.tmp/**`, `tests/.npm-cache/**`, `tests/test-results/**`, `tests/playwright-report/**`

## 수정 금지

- `js/data.js`
- `fixFiles`에 없는 사이트 파일
- spec, helper, 다른 fixture

## 중단 조건

구조나 문구를 바꿔야만 해결되는 target이 있으면 사이트를 수정하지 않는다. 보고하고 중단한다.

## 작업

1. canonical target 단위로, 각 target의 fixKind 범위 안에서 최소한으로 수정한다.
2. fixture를 `[]`로 바꾼다.
3. axe 10개 시나리오가 모두 0건인지 확인한다.

## 완료 기준 (AC)

다음이 모두 성공해야 완료다.

- `sh tests/scripts/with-env.sh node tests/helpers/axe.js --assert-empty`: fixture가 정확히 빈 JSON 배열이 아니면 exit 1이다.
- `sh tests/scripts/with-env.sh npm --prefix tests test`: 일반 axe 테스트를 포함한다.
- `sh tests/scripts/with-env.sh npm --prefix tests run verify-scope`
- content.spec와 layout.spec에 회귀가 없다.
