# Step 8 — axe-remediation

- 예상 시간: 15분
- 실행 횟수: 테스트 2회, verify-scope 1회
- 선행 step: 0~7 completed

## 공통: 시작 전 필수 확인 (read-first)

1. 저장소 지침을 읽는다: `CLAUDE.md`(중앙 Harness 계약), `README.md`. 하위 디렉터리에 `CLAUDE.md`나 `AGENTS.md`가 있으면 함께 읽는다.
2. 설계 문서를 읽는다.
   - `docs/superpowers/specs/2026-07-29-quiet-executive-redesign-design.md`
   - `docs/superpowers/specs/2026-11-23-portfolio-layout-redesign-design.md` §7.2-6, §8.3
3. index.json에서 step 0~7이 completed인지 확인한다. 아니면 중단한다.
4. `tests/fixtures/axe-baseline.json`을 확인한다.
   - `validateBaseline` 결과 오류가 0건이어야 한다.
   - 이번 step에서 수정할 수 있는 파일은 항목들의 `fixFiles` 합집합이다.
   - fixture가 `[]`이면 사이트 파일을 수정하지 않는다.
   - text-change 항목이 있으면 즉시 중단한다.
5. 다음 경로는 read-only다.
   - `CLAUDE.md`, `docs/**`, `phases/**`
   - `.harness/**`, `.claude/**`, `.codex/**`
   - `pytest.ini`, `.python-version`, `.gitattributes`, 루트 `.gitignore`
6. git과 Harness 운영 명령은 하네스만 실행한다. main 직접 변경, merge, deploy는 금지다.
7. 공통 실행 계약: npm·node 명령은 모두 `sh tests/scripts/with-env.sh <명령>`으로 실행한다.

## tracked source 허용 파일 (exact)

`fixFiles` 합집합에 들어 있는 파일만 아래 범위 안에서 수정한다.

- `css/themes.css`: 토큰 명도
- `css/style.css`: target에 걸린 규칙
- `js/main.js`: target 렌더링 속성
- `index.html`: target 요소의 aria-*, role, alt, lang, tabindex, for 속성만

그리고 `tests/fixtures/axe-baseline.json`을 `[]`로 바꾸는 것만 허용한다.

## runtime 쓰기 허용 경로 (추적 금지)

- `tests/.tmp/**`
- `tests/.npm-cache/**`
- `tests/test-results/**`
- `tests/playwright-report/**`

## 수정 금지

- `js/data.js`
- `fixFiles`에 없는 사이트 파일
- spec과 다른 fixture

## 중단 조건

구조나 문구를 바꿔야만 해결되는 target이 있으면 사이트를 수정하지 않는다. 해당 key, target, 사유를 보고하고 중단한다.

## 작업

1. target 단위로 순회하며, 각 fixKind가 허용하는 범위 안에서 최소한으로 수정한다.
2. fixture를 `[]`로 바꾼다.
3. axe 10개 시나리오 모두에서 위반이 0건인지 확인한다.

## 완료 기준 (AC)

- `sh tests/scripts/with-env.sh npm --prefix tests test && sh tests/scripts/with-env.sh npm --prefix tests run verify-scope`가 모두 통과한다.
- `axe-baseline.json`이 `[]`이다.
- content.spec와 layout.spec에 회귀가 없다.
