# Step 19 — hero-first-screen

- 예상 시간: 18분
- 실행 횟수: hero spec 2회, 전체 테스트 1회, verify-scope 1회
- 선행 step: 0~18 completed

## 공통: 시작 전 필수 확인 (read-first)

1. 저장소 지침을 읽는다: `CLAUDE.md`(중앙 Harness 계약), `README.md`. 하위 디렉터리에 `CLAUDE.md`나 `AGENTS.md`가 있으면 함께 읽는다.
2. 설계 문서를 읽는다.
   - `docs/superpowers/specs/2026-07-29-quiet-executive-redesign-design.md`
   - `docs/superpowers/specs/2026-11-23-portfolio-layout-redesign-design.md` §5 (히어로 순서, tagline 계약, 첫 화면 AC), §9
3. index.json에서 step 0~18이 completed인지 확인한다. 아니면 중단한다.
4. hero 마크업, reveal, 여백, `#heroFeatured`, `setText` 시그니처를 확인한다.
5. 빌더 read-only 경로: `CLAUDE.md`, `docs/**`, `phases/**`, `.harness/**`, `.claude/**`, `.codex/**`, `pytest.ini`, `.python-version`, `.gitattributes`, 루트 `.gitignore`
6. 명령 권한
   - Git 상태를 바꾸는 명령과 Harness 운영 명령은 하네스만 실행한다.
   - 검증용 Git 읽기 명령(rev-parse, diff, show, ls-files, ls-tree, status, log)은 허용한다.
   - main 직접 변경, merge, deploy는 금지다.
7. 공통 실행 계약: npm·node 명령은 `sh tests/scripts/with-env.sh <명령>`으로 실행한다.

## tracked source 허용 파일 (exact)

- `index.html` (section#hero 내부만. `#heroFeatured`의 마크업은 그대로 둔다)
- `js/main.js`: 정확히 `setText('heroTagline', PROFILE.tagline);` 1줄만 추가
- `css/style.css` (hero, `#heroStats`, `#heroFeatured` 배치 규칙만)
- `tests/specs/hero.spec.js`

## runtime 쓰기 허용 경로 (추적 금지)

- `tests/.tmp/**`, `tests/.npm-cache/**`, `tests/test-results/**`, `tests/playwright-report/**`

## 수정 금지

- `js/data.js`, `css/themes.css`
- 대표 카드 렌더링·모달 로직
- `#heroFeatured`의 속성
- 섹션, nav
- 기존 tests, fixtures, helper

## 작업 (TDD)

1. `hero.spec.js`를 먼저 작성해 실패를 확인한다. 6개 project에서 실행하고 collector는 고정 순서로 쓴다.
   - hero DOM 순서가 §5 1~8과 같다.
   - tagline
     - `p.hero-tagline`의 id가 `heroTagline`이다.
     - `document.getElementById('heroTagline').textContent`가 `PROFILE.tagline`과 같다.
   - CTA가 맞고, eyebrow·typed가 유지된다.
   - `#heroFeatured`의 `role=region`과 `aria-label`이 유지된다.
   - STATS: 375에서 2×2, 768·1280에서 4×1
   - featured: 375 1열, 768 2열, 1280 3열
   - 첫 화면 AC (desktop, 실제 폰트)
     - `document.fonts.ready`를 기다린다.
     - scrollY는 0이다.
     - 대상 6개 모두: visible, 크기 > 0, 조상까지 visibility·opacity(`expect.poll`), 1280×800 경계 안
2. index.html: hero 순서를 바꾸고 `p.hero-tagline#heroTagline`을 추가한다.
3. main.js: 정확히 `setText('heroTagline', PROFILE.tagline);`를 추가한다.
4. style.css
   - eyebrow와 typing을 줄인다.
   - 여백을 조정한다.
   - STATS와 featured를 반응형으로 만든다.
   - blurb는 2줄 clamp
   - 토큰만 쓴다. 문구는 줄이지 않는다.
5. axe 새 target은 step 18과 같은 규칙을 따른다.

## 완료 기준 (AC)

- `sh tests/scripts/with-env.sh npm --prefix tests test -- hero.spec.js && sh tests/scripts/with-env.sh npm --prefix tests test && sh tests/scripts/with-env.sh npm --prefix tests run verify-scope` → 모두 통과
