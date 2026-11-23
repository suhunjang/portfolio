# Step 5 — axe-canonical

- 예상 시간: 18분
- 실행 횟수: 테스트 2회, verify-scope 1회
- 선행 step: 0~4 completed

## 공통: 시작 전 필수 확인 (read-first)

1. 저장소 지침을 읽는다: `CLAUDE.md`(중앙 Harness 계약), `README.md`. 하위 디렉터리에 `CLAUDE.md`나 `AGENTS.md`가 있으면 함께 읽는다.
2. 설계 문서를 읽는다.
   - `docs/superpowers/specs/2026-07-29-quiet-executive-redesign-design.md`
   - `docs/superpowers/specs/2026-11-23-portfolio-layout-redesign-design.md` §8.1, §8.3 (canonical target 식별)
3. index.json에서 step 0~4가 completed인지 확인한다. 아니면 중단한다.
4. 현재 코드에서 JS 렌더 영역, `data-project`, landmark를 확인한다.
5. 빌더 read-only 경로: `CLAUDE.md`, `docs/**`, `phases/**`, `.harness/**`, `.claude/**`, `.codex/**`, `pytest.ini`, `.python-version`, `.gitattributes`, 루트 `.gitignore`
6. 명령 권한
   - Git 상태를 바꾸는 명령과 Harness 운영 명령은 하네스만 실행한다.
   - 검증용 Git 읽기 명령(rev-parse, diff, show, ls-files, ls-tree, status, log)은 허용한다.
   - main 직접 변경, merge, deploy는 금지다.
7. 공통 실행 계약: npm·node 명령은 `sh tests/scripts/with-env.sh <명령>`으로 실행한다.

## tracked source 허용 파일 (exact)

- `tests/helpers/axe.js` (신규)
- `tests/specs/axe-helper.spec.js` (신규)

## runtime 쓰기 허용 경로 (추적 금지)

- `tests/.tmp/**`, `tests/.npm-cache/**`, `tests/test-results/**`, `tests/playwright-report/**`

## 수정 금지

- `tests/` 밖 전부
- 기존 tests 파일
- 이 step은 식별만 다룬다. 스키마, 회귀 판정, 수집 CLI는 step 6에서 다룬다.

## 작업

### 1. `tests/helpers/axe.js`

- `ALIASES`: §8.3의 고정 alias 2개
- `canonicalTargetInPage(el)` (브라우저에서 실행)
  - `{ anchor, text }`를 반환한다.
  - anchor 우선순위: featured → project → id → landmark → document
  - text: norm 적용, 비면 대체 속성 사용, 숫자는 `#`, 80자 제한, alias 적용
- `canonicalFromDescriptor({ ruleId, anchor, text }): string`
- `runAxe(page, { include })`
  - wcag2a·wcag2aa의 serious/critical 위반만 다룬다.
  - node마다 같은 page에서 canonical을 계산한다.
  - 반환: `{ ruleId, impact, selectors, targets }[]`. targets는 중복을 제거한다.

### 2. `tests/specs/axe-helper.spec.js` (desktop-dark)

`page.setContent`로 실제 axe를 실행해 DOM 이동 안정성을 확인한다.

- a) 같은 key: `section#career`의 `h3` 안 `01 — Career`를 `main`으로 이동하고 `span`으로 바꾼 뒤 텍스트를 `04 — Career`로 변경해도 color-contrast key가 같다.
- b) 같은 key: `[data-project=5]` 안에서 div를 p로 바꿔도 같다.
- c) 텍스트가 다르면 key가 다르다.
- d) `project:5`와 `featured:5`는 서로 다른 key다.
- e) alias가 적용되면 같은 key다.

## 완료 기준 (AC)

- `sh tests/scripts/with-env.sh npm --prefix tests test -- axe-helper.spec.js` → 통과
- `sh tests/scripts/with-env.sh npm --prefix tests test && sh tests/scripts/with-env.sh npm --prefix tests run verify-scope` → 통과
