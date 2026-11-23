# Step 4 — axe-baseline

- 예상 시간: 15분
- 실행 횟수: 테스트 2회(수집 1회, 검증 1회, 각각 웹서버 1회), verify-scope 1회
- 선행 step: 0~3 completed

## 공통: 시작 전 필수 확인 (read-first)

1. 저장소 지침 `CLAUDE.md`(하네스 계약 포함)와 `README.md`를 읽는다. 하위 디렉터리에 `CLAUDE.md`나 `AGENTS.md`가 있으면 함께 읽는다.
2. 설계 문서를 읽는다.
   - `docs/superpowers/specs/2026-07-29-quiet-executive-redesign-design.md`
   - `docs/superpowers/specs/2026-11-23-portfolio-layout-redesign-design.md`의 §8.1, §8.3
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

- `tests/.tmp/**`
- `tests/test-results/**`
- `tests/playwright-report/**`

## 수정 금지

- `tests/` 밖의 모든 파일
- 기존 tests 파일

## 작업

1. `tests/helpers/axe.js`를 만든다.
   - `runAxe(page, { include })`: AxeBuilder로 wcag2a, wcag2aa 태그를 검사한다. serious와 critical 위반만 `{ ruleId, impact, targets }[]`로 반환한다.
   - `loadBaseline()`
2. `tests/specs/axe.spec.js`를 만든다.
   - 시나리오
     - page: 6개 project, reducedMotion reduce
     - modal: desktop-dark와 desktop-light에서 Motion-O 모달을 열고 `#projectModal`을 include
     - lightbox: desktop-dark와 desktop-light에서 `.lightbox`를 include
   - 판정
     - 위반 key는 `{scenario}:{project}:{ruleId}`다.
     - fixture에 없는 key가 나오면 실패한다.
     - fixture에만 있고 실행에서 사라진 key는 허용한다.
   - 수집 모드: `AXE_COLLECT=1`이면 실패하지 않고 결과를 `tests/.tmp/axe-collected.json`에 기록한다.
3. `AXE_COLLECT=1 npm --prefix tests test -- axe.spec.js`로 위반을 수집한다.
4. 수집 결과를 설계 §8.3 분류 규칙에 따라 `tests/fixtures/axe-baseline.json`으로 확정한다.
   - 항목 필드: `key`, `scenario`, `project`, `ruleId`, `impact`, `targets`, `fixKind`, `fixFiles`
   - 위반이 없으면 `[]`로 둔다.
5. text-change로 분류된 항목이 있으면 실행 로그에 명시한다. 이 항목은 step 8의 중단 사유가 된다.

## 완료 기준 (AC)

- `npm --prefix tests test && npm --prefix tests run verify-scope`가 통과한다.
- `axe-baseline.json`의 모든 항목이 위 필드를 모두 갖추고 있다.
