# Step 5 — axe-canonical

- 예상 시간: 18분
- 실행 횟수: 테스트 2회, verify-scope 1회
- 선행 step: 0~4 completed

## 공통: 시작 전 필수 확인 (read-first)

1. 저장소 지침을 읽는다: `CLAUDE.md`(중앙 Harness 계약), `README.md`. 하위 디렉터리에 `CLAUDE.md`나 `AGENTS.md`가 있으면 함께 읽는다.
2. 설계 문서를 읽는다.
   - `docs/superpowers/specs/2026-07-29-quiet-executive-redesign-design.md`
   - `docs/superpowers/specs/2026-11-23-portfolio-layout-redesign-design.md` §8.1, §8.3 (canonical 식별, 안정성 보장 범위, helper 계약 중 step 5)
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

- `tests/` 밖의 모든 파일
- 기존 tests 파일
- 이 step은 식별만 다룬다. 수집, 스키마, plan은 step 6~8에서 한다.

## 작업

1. `axe.js` (설계 §8.3 step 5 계약)
   - `ALIASES`
   - `canonicalTargetInPage(el) → { anchor, text }`
   - `canonicalFromDescriptor({ ruleId, anchor, text }) → string`
   - `runAxe(page, { include }) → Violation[]`
     - wcag2a·wcag2aa 기준, serious·critical만 다룬다.
     - node마다 canonical을 계산하고 중복을 제거한다.
2. `axe-helper.spec.js` (desktop-dark, `page.setContent`로 실제 axe 실행)
   - a) anchor를 유지한 채 이동 → 같은 key
     - `section#career` subtree 전체를 `main` 아래 다른 위치로 옮긴다. 안에는 저대비 `h3` 01 — Career가 있다.
     - 그 안에서 `h3`를 `span`으로 바꾸고 텍스트를 `04 — Career`로 바꾼다.
     - 이동 전후 color-contrast key가 같아야 한다.
   - a2) anchor 경계 밖으로 이동 → 다른 key
     - 같은 저대비 `h3`만 `section#career` 밖(`body` 직속)으로 옮긴다.
     - anchor가 `document`로 바뀌므로 key가 달라야 한다.
   - b) `[data-project=5]` 안에서 div를 p로 바꿔도 key가 같다.
   - c) 텍스트가 다르면 key가 다르다.
   - d) `project:5`와 `featured:5`는 서로 다른 key다.
   - e) alias가 적용되면 key가 같다.

## 완료 기준 (AC)

- `sh tests/scripts/with-env.sh npm --prefix tests test -- axe-helper.spec.js` → 통과
- `sh tests/scripts/with-env.sh npm --prefix tests test && sh tests/scripts/with-env.sh npm --prefix tests run verify-scope` → 통과
