# Step 47 — state-colors-fixture

- 목적: BASE 상태 색 fixture generator(`make-state-colors.mjs`), fixture 생성, schema 검증, `--check` 재현성 검증. 사이트 파일은 바꾸지 않는다.
- 예상 18분 / 선행 0~46 / 공통 절차 설계 §15 / 종료 gate: CLI
- read-first: 설계 §3(`THEME_KEY`), §11.7(테스트 격리), §16.2(step 46 helper, step 47 fixture); `tests/helpers/state-sequence.js`(import만)
- tracked 허용(exact): `tests/scripts/make-state-colors.mjs`(신규), `tests/fixtures/component-state-colors.json`(신규), `tests/specs/state-colors.spec.js`(신규)
- runtime: R0 + Playwright 브라우저 실행(`tests/.tmp/state-colors-<pid>/`)
- 금지: §15.7, 사이트 파일, helper·기존 spec 수정, fixture 손편집, `measureStateSequence` 밖의 상태 측정, Git 쓰기

## 작업

1. 시작 snapshot: `python3 -I tests/scripts/start-snapshot.py step47`
2. `make-state-colors.mjs`(래퍼로 실행, Git은 `git show <BASE>:<path>` 읽기만):
   - `@playwright/test`의 `chromium`을 띄우고 테마(`dark`, `light`)마다 context 하나(viewport 1280×800)를 만든다. context `route('http://base.invalid/**')`에서 경로별 `git show <BASE>:<path>` 내용을 제공(BASE에 없는 경로 404, Google Fonts 요청은 통과), BASE `js/main.js`에서 `THEME_KEY` 값을 정규식으로 추출해 context `addInitScript`로 테마 설정
   - 키마다 `measureStateSequence(context, { url: 'http://base.invalid/index.html', selector, nth })`: `hero-cta-btn-{i}`(`.hero-cta .btn`, nth i, BASE 개수만큼), `grid-card-0`, `grid-card-1`(`#projectGrid .project-card[data-project="0"|"1"]`). 결과 중 color·backgroundColor·borderColor만 기록
   - 출력 `{ "schemaVersion": 1, "base": "<BASE>", "themes": { "dark": { "<key>": { "default": { "color", "backgroundColor", "borderColor" }, "hover": {…}, "active": {…} } }, "light": {…} } }`, 키 정렬·2칸 들여쓰기·끝 개행 1개
   - 인자: 없음 → `tests/fixtures/component-state-colors.json` 쓰기; `--check [--fixture <path>]` → 메모리에서 다시 만들어 지정 파일(기본 위 fixture) bytes와 비교, 다르면 stderr `state-colors: mismatch` exit 1, 같으면 stdout `state-colors: OK` exit 0; 그 밖 인자 exit 2
3. fixture 생성: `sh tests/scripts/with-env.sh node tests/scripts/make-state-colors.mjs`
4. `state-colors.spec.js`(node 전용, desktop-dark만, subprocess timeout 60초):
   - schema: 최상위 키 정확히 `schemaVersion, base, themes`; `schemaVersion === 1`; `base` = BASE; `themes` 키 정확히 `dark, light`; 각 테마 키 집합 = `hero-cta-btn-0..n-1`(n ≥ 1, `tests/fixtures/baseline-index.html`의 `.hero-cta .btn` 개수와 같음) ∪ `grid-card-0`, `grid-card-1`; 각 키 상태 정확히 `default, hover, active`; 각 상태 필드 정확히 `color, backgroundColor, borderColor`(비어 있지 않은 문자열)
   - 직렬화: 파일 bytes = 키 정렬 `JSON.stringify(…, null, 2) + '\n'`
   - `--check`: 기본 실행 exit 0·stdout `state-colors: OK`; `tests/.tmp/state-colors-<pid>/` 사본에서 값 하나를 바꾼 뒤 `--check --fixture <사본>` → exit 1·stderr `state-colors: mismatch`; 원본 fixture bytes 불변; 사본 디렉터리 삭제

## AC

- `sh tests/scripts/with-env.sh node tests/scripts/make-state-colors.mjs --check && sh tests/scripts/with-env.sh npm --prefix tests test -- state-colors.spec.js state-sequence.spec.js && sh tests/scripts/with-env.sh npm --prefix tests test && sh tests/scripts/with-env.sh npm --prefix tests run verify-scope && sh tests/scripts/with-env.sh node tests/scripts/scope-snapshot.mjs --check tests/.tmp/start-snapshot-step47.json --allow tests/scripts/make-state-colors.mjs,tests/fixtures/component-state-colors.json,tests/specs/state-colors.spec.js --require-absent tests/scripts/make-state-colors.mjs,tests/fixtures/component-state-colors.json,tests/specs/state-colors.spec.js` → exit 0 (첫 명령 stdout `state-colors: OK`)
