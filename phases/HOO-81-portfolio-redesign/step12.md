# Step 12 — featured-projects

- 예상 시간: 18분
- 실행 횟수: featured spec 2회, 전체 테스트 1회, verify-scope 1회
- 선행 step: 0~11 completed

## 공통: 시작 전 필수 확인 (read-first)

1. 저장소 지침을 읽는다: `CLAUDE.md`(중앙 Harness 계약), `README.md`. 하위 디렉터리에 `CLAUDE.md`나 `AGENTS.md`가 있으면 함께 읽는다.
2. 설계 문서를 읽는다.
   - `docs/superpowers/specs/2026-07-29-quiet-executive-redesign-design.md`
   - `docs/superpowers/specs/2026-11-23-portfolio-layout-redesign-design.md` §5 (대표 카드 마크업, 함수 계약, data.js), §7, §8.3(회귀)
3. index.json에서 step 0~11이 completed인지 확인한다. 아니면 중단한다.
4. projectGrid 렌더링, `openProjectModal(idx)`, `lastFocused`, 이벤트 위임, data.js index 1·5·7을 확인한다.
5. 빌더 read-only 경로: `CLAUDE.md`, `docs/**`, `phases/**`, `.harness/**`, `.claude/**`, `.codex/**`, `pytest.ini`, `.python-version`, `.gitattributes`, 루트 `.gitignore`
6. 명령 권한
   - Git 상태를 바꾸는 명령과 Harness 운영 명령은 하네스만 실행한다.
   - 검증용 Git 읽기 명령(rev-parse, diff, show, ls-files, ls-tree, status, log)은 허용한다.
   - main 직접 변경, merge, deploy는 금지다.
7. 공통 실행 계약: npm·node 명령은 `sh tests/scripts/with-env.sh <명령>`으로 실행한다.

## tracked source 허용 파일 (exact)

- `index.html`: `#heroStats` 바로 뒤에 빈 컨테이너 `<div id=heroFeatured aria-label=대표 프로젝트></div>`를 추가하는 것만
- `js/data.js`: `featured: true,` 3줄만
- `js/main.js`: `renderFeaturedProjects`, `openProjectModal` 시그니처, `#heroFeatured` 위임만
- `css/style.css`: `.featured-card`, `.featured-title`, `.featured-blurb` 규칙만
- `tests/specs/featured.spec.js`

## runtime 쓰기 허용 경로 (추적 금지)

- `tests/.tmp/**`, `tests/.npm-cache/**`, `tests/test-results/**`, `tests/playwright-report/**`

## 수정 금지

- `css/themes.css`
- hero의 그 밖의 순서, tagline, 섹션, nav
- 기존 tests, fixtures, helper
- 새 target의 자동 편입

## 작업 (TDD)

1. `featured.spec.js`를 먼저 작성하고 실패를 확인한다. 6개 project에서 실행하고 collector는 고정 순서로 쓴다.
   - 카드 3개: `button[type=button]`, `data-project` 1·5·7
   - 각 카드에 span 2개가 1개씩, 금지 자손 0개
   - 텍스트가 데이터와 일치하고 span은 block
   - background-image가 none
   - 카드마다 click으로 열고 button·backdrop·esc로 닫으면 포커스가 카드로 돌아온다. 모달 제목이 일치한다.
   - Enter로 열고 esc로 닫았을 때도 포커스가 돌아온다.
2. data.js: featured 3줄을 추가한다.
3. index.html: 컨테이너를 추가한다.
4. main.js
   - `renderFeaturedProjects`: span과 `esc()`를 쓰고 그리드 직후에 호출한다.
   - `openProjectModal(projectIndex, triggerElement = document.activeElement)`
   - projectGrid 호출을 `(idx, card)`로 바꾼다.
   - `#heroFeatured` 위임
5. style.css: 카드 기본 스타일을 토큰만으로 정의하고, span은 block으로 둔다.
6. axe에서 새 target이 나오면
   - 이 step의 마크업이 원인이면 허용 파일 안에서 고친다.
   - 식별을 잃은 경우면 중단하고 재계획을 요청한다.

## 완료 기준 (AC)

- `sh tests/scripts/with-env.sh npm --prefix tests test -- featured.spec.js && sh tests/scripts/with-env.sh npm --prefix tests test && sh tests/scripts/with-env.sh npm --prefix tests run verify-scope` → 모두 통과
