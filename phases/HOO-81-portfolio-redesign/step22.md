# Step 22 — featured-projects

- 예상 시간: 19분
- 실행 횟수: 시작 snapshot 1회, featured spec 2회, 전체 테스트 1회, verify-scope 1회, 범위 gate 1회
- 선행 step: 0~21 completed

## 공통: 시작 전 필수 확인 (read-first)

1. 저장소 지침을 읽는다: `CLAUDE.md`(중앙 Harness 계약), `README.md`. 하위 디렉터리에 `CLAUDE.md`나 `AGENTS.md`가 있으면 함께 읽는다.
2. 설계 문서를 읽는다.
   - `docs/superpowers/specs/2026-07-29-quiet-executive-redesign-design.md`
   - `docs/superpowers/specs/2026-11-23-portfolio-layout-redesign-design.md` §5 (컨테이너 정확 마크업, 대표 카드 마크업, 함수 계약, data.js), §7, §8.3(회귀), §11.7
3. index.json에서 step 0~21이 completed인지 확인한다. 아니면 중단한다.
4. 현재 코드를 확인한다.
   - projectGrid 렌더링
   - `openProjectModal(idx)`, `lastFocused`
   - 이벤트 위임
   - data.js index 1·5·7
5. 빌더 read-only 경로: `CLAUDE.md`, `docs/**`, `phases/**`, `.harness/**`, `.claude/**`, `.codex/**`, `pytest.ini`, `.python-version`, `.gitattributes`, 루트 `.gitignore`
6. 명령 권한
   - Git 상태를 바꾸는 명령과 Harness 운영 명령은 하네스만 실행한다.
   - 검증용 Git 읽기 명령(rev-parse, diff, show, ls-files, ls-tree, status, log)과 §11.7 시작 snapshot 명령은 허용한다.
   - main 직접 변경, merge, deploy는 금지다.
7. 공통 실행 계약: npm·node 명령은 `sh tests/scripts/with-env.sh <명령>`으로 실행한다.
8. 범위 gate(§11.7): 이 step의 첫 동작은 `python3 -I tests/scripts/start-snapshot.py tests/.tmp/start-snapshot-step22.json`이다. 어떤 파일도 쓰기 전에 실행한다.

## tracked source 허용 파일 (exact)

- `index.html`: `#heroStats` 바로 뒤에 정확히 `<div id="heroFeatured" role="region" aria-label="대표 프로젝트"></div>`를 추가하는 것만 허용한다.
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
- 새 target 자동 편입

## 작업 (TDD)

1. `featured.spec.js`를 먼저 작성해 실패를 확인한다. 6개 project에서 실행하고 collector는 고정 순서로 쓴다.
   - 컨테이너
     - `#heroFeatured`가 1개다.
     - 태그는 div이고 `role` 속성이 정확히 `region`이다.
     - `aria-label`이 정확히 `대표 프로젝트`다.
     - `#heroStats`의 다음 형제 요소다.
   - 카드
     - 3개, 각각 `button[type=button]`, `data-project`는 1·5·7
     - span 2개가 각 1개, 금지 자손은 0개
     - 텍스트가 데이터와 일치하고 span은 display block
     - background-image는 none
   - 모달
     - 카드마다 click으로 연 뒤 button·backdrop·esc로 닫으면 포커스가 카드로 돌아온다.
     - 모달 제목이 일치한다.
     - Enter로 열고 esc로 닫았을 때도 포커스가 돌아온다.
   - grid 범위 회귀: 대표 카드가 생긴 뒤에도 `findProjectWithShots`와 `prepareForAxe({ scenario: 'modal', projectIndex: 1 })`가 `#projectGrid` 카드만 사용한다(모달을 닫은 뒤 포커스 복귀 대상이 grid 카드인지로 확인).
2. data.js: featured 3줄을 추가한다.
3. index.html: 위의 정확한 마크업을 추가한다.
4. main.js
   - `renderFeaturedProjects`: span만 쓰고 `esc()`로 이스케이프한다. 그리드 렌더링 직후 호출한다.
   - `openProjectModal(projectIndex, triggerElement = document.activeElement)`
   - projectGrid 호출을 `(idx, card)`로 바꾼다.
   - `#heroFeatured`에 위임을 단다.
5. style.css: 기존 토큰만 쓴다. span은 block이다.
6. axe 새 target (entry key 계약 기준)
   - 이 step의 마크업 때문이면 허용 파일 안에서 고친다.
   - 식별을 잃은 경우면 중단하고 재계획을 요청한다.

## 완료 기준 (AC)

- `sh tests/scripts/with-env.sh npm --prefix tests test -- featured.spec.js && sh tests/scripts/with-env.sh npm --prefix tests test && sh tests/scripts/with-env.sh npm --prefix tests run verify-scope && sh tests/scripts/with-env.sh node tests/scripts/scope-snapshot.mjs --check tests/.tmp/start-snapshot-step22.json --allow index.html,js/data.js,js/main.js,css/style.css,tests/specs/featured.spec.js` → 모두 통과
