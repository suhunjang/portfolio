# Step 9 — hero-featured

- 예상 시간: 20분
- 실행 횟수: 테스트 2회, verify-scope 1회
- 선행 step: 0~8 completed

## 공통: 시작 전 필수 확인 (read-first)

1. 저장소 지침을 읽는다: `CLAUDE.md`(중앙 Harness 계약), `README.md`. 하위 디렉터리에 `CLAUDE.md`나 `AGENTS.md`가 있으면 함께 읽는다.
2. 설계 문서를 읽는다.
   - `docs/superpowers/specs/2026-07-29-quiet-executive-redesign-design.md`
   - `docs/superpowers/specs/2026-11-23-portfolio-layout-redesign-design.md` §5, §7, §8.3(회귀 판정), §9
3. index.json에서 step 0~8이 completed인지 확인한다. 아니면 중단한다.
4. `tests/fixtures/axe-baseline.json`이 있는지 확인한다.
5. 현재 코드에서 다음을 확인한다.
   - hero, reveal
   - setText, projectGrid
   - 모달 함수
   - data.js의 index 1, 5, 7
6. 빌더 read-only 경로: `CLAUDE.md`, `docs/**`, `phases/**`, `.harness/**`, `.claude/**`, `.codex/**`, `pytest.ini`, `.python-version`, `.gitattributes`, 루트 `.gitignore`
7. 명령 권한
   - Git 상태를 바꾸는 명령과 Harness 운영 명령은 하네스만 실행한다.
   - 검증용 Git 읽기 명령(rev-parse, diff, show, ls-files, ls-tree, status, log)은 허용한다.
   - main 직접 변경, merge, deploy는 금지다.
8. 공통 실행 계약: npm·node 명령은 `sh tests/scripts/with-env.sh <명령>`으로 실행한다.

## tracked source 허용 파일 (exact)

- `index.html` (section#hero 내부만)
- `css/style.css`
- `js/main.js`
- `js/data.js` (`featured: true,` 3줄만)
- `tests/specs/hero.spec.js`

## runtime 쓰기 허용 경로 (추적 금지)

- `tests/.tmp/**`, `tests/.npm-cache/**`, `tests/test-results/**`, `tests/playwright-report/**`

## 수정 금지

- `css/themes.css`
- 섹션 순서와 nav
- 기존 tests, fixtures, helper
- 새 target의 baseline 자동 편입

## 작업 (TDD)

1. `tests/specs/hero.spec.js`를 먼저 작성해 실패를 확인한다. 6개 project에서 실행하고 collector는 고정 순서로 쓴다.
   - 대표 카드 3개
     - `button[type=button]`, `data-project` 값 1·5·7
     - `span.featured-title`과 `span.featured-blurb`가 각각 정확히 1개
     - 금지 자손 0개
     - 텍스트가 데이터와 일치
     - 두 span 모두 display block
   - tagline
   - 첫 화면 AC (desktop)
     - fonts.ready 완료, scrollY 0
     - 대상 6개 각각: visible, 크기 > 0, 조상 체인의 visibility·opacity, 1280×800 경계 안
   - 모달
     - 카드마다 click으로 열고 button, backdrop, esc로 닫는다. 매번 포커스가 카드로 돌아와야 한다.
     - Enter로 열고 esc로 닫는다.
     - 모달 제목
   - CTA, eyebrow·typed 유지, 카드 background-image none
2. data.js: featured 3줄을 추가한다.
3. index.html: hero 순서를 바꾼다.
4. main.js
   - setText tagline
   - `renderFeaturedProjects`: span만 쓰고 `esc()`로 이스케이프한다.
   - `openProjectModal(projectIndex, triggerElement)`
   - `#heroFeatured` click 위임
5. style.css
   - span을 block으로 한다.
   - 첫 화면 AC를 맞추도록 여백과 크기를 조정한다.
   - STATS와 featured를 반응형으로 만든다.
   - 기존 토큰만 쓴다.
6. axe 새 target이 나오면
   - 이 step의 마크업이 만든 신규 위반이면 허용 파일 안에서 고친다.
   - 식별을 보존할 수 없으면 즉시 중단하고 재계획을 요청한다.

## 완료 기준 (AC)

- `sh tests/scripts/with-env.sh npm --prefix tests test && sh tests/scripts/with-env.sh npm --prefix tests run verify-scope`가 모두 통과한다.
