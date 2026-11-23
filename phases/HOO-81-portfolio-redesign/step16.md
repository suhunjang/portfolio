# Step 16 — section-structure

- 예상 시간: 18분
- 실행 횟수: structure spec 2회, 전체 테스트 1회, verify-scope 1회
- 선행 step: 0~15 completed

## 공통: 시작 전 필수 확인 (read-first)

1. 저장소 지침을 읽는다: `CLAUDE.md`(중앙 Harness 계약), `README.md`. 하위 디렉터리에 `CLAUDE.md`나 `AGENTS.md`가 있으면 함께 읽는다.
2. 설계 문서를 읽는다.
   - `docs/superpowers/specs/2026-07-29-quiet-executive-redesign-design.md`
   - `docs/superpowers/specs/2026-11-23-portfolio-layout-redesign-design.md` §5(컨테이너 마크업), §6(스크롤스파이 locator 예시 포함), §7, §8.3(canonical 안정성 범위, entry key, 회귀), §11.4
3. index.json에서 step 0~15가 completed인지 확인한다. 아니면 중단한다.
4. 섹션, nav, scroll-hint, 스크롤스파이, skillsGrid, content-exceptions final, baseline canonical을 확인한다.
5. 빌더 read-only 경로: `CLAUDE.md`, `docs/**`, `phases/**`, `.harness/**`, `.claude/**`, `.codex/**`, `pytest.ini`, `.python-version`, `.gitattributes`, 루트 `.gitignore`
6. 명령 권한
   - Git 상태를 바꾸는 명령과 Harness 운영 명령은 하네스만 실행한다.
   - 검증용 Git 읽기 명령(rev-parse, diff, show, ls-files, ls-tree, status, log)은 허용한다.
   - main 직접 변경, merge, deploy는 금지다.
7. 공통 실행 계약: npm·node 명령은 `sh tests/scripts/with-env.sh <명령>`으로 실행한다.

## tracked source 허용 파일 (exact)

- `index.html` (hero 밖의 섹션, nav, scroll-hint)
- `js/main.js` (스크롤스파이 배열과 skill-group h4만)
- `tests/specs/structure.spec.js`

## runtime 쓰기 허용 경로 (추적 금지)

- `tests/.tmp/**`, `tests/.npm-cache/**`, `tests/test-results/**`, `tests/playwright-report/**`

## 수정 금지

- `css/*`, `js/data.js`
- hero 내부(`#heroFeatured` 포함)
- fixtures, helper, 기존 spec
- 섹션 표에 없는 문구

## 작업 (TDD)

1. `structure.spec.js`를 먼저 작성한다 (6개 project).
   - 섹션, nav, kicker, h2가 §6과 일치한다.
   - subsection h3가 1개다.
   - skillsGrid는 about 안에 있고 h4를 쓴다.
   - contact와 scroll-hint가 맞다.
   - heading 계층이 올바르다.
   - 섹션을 이동한 뒤에도 `#heroFeatured`가 `div[role=region][aria-label=대표 프로젝트]`로 유지된다.
   - 스크롤스파이 (desktop), 정확히 다음 문법을 쓴다:
     - `const link = page.locator('.nav-link[href="#about"]');`
     - `await link.click();`
     - `await expect(link).toHaveClass(/active/);`
2. index.html
   - 섹션 subtree를 통째로 이동해 anchor를 보존한다.
   - kicker를 바꾼다.
   - Stack &amp; Contact를 분리한다.
   - nav, scroll-hint, section-alt를 맞춘다.
3. main.js: 스크롤스파이 배열, skill-group h4
4. axe canonical 점검 (필수)
   - 식별을 잃은 경우: 즉시 중단하고 보고한 뒤 재계획을 요청한다.
   - 새로 만든 요소의 신규 위반: 허용 파일 안에서 고친다.
   - 자동 편입은 금지다.

## 완료 기준 (AC)

- `sh tests/scripts/with-env.sh npm --prefix tests test -- structure.spec.js && sh tests/scripts/with-env.sh npm --prefix tests test && sh tests/scripts/with-env.sh npm --prefix tests run verify-scope` → 모두 통과
- content-static.spec에서 final 상태가 성립한다.
