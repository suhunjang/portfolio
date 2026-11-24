# Step 39 — featured-projects

- 목적: 대표 프로젝트 3개 카드와 모달 연결(색은 기존 `.project-card` 색 규칙의 featured 대응 선택자 추가로만).
- 예상 19분 / 선행 0~38 / 공통 절차 설계 §15 / 종료 gate: CLI
- read-first: 설계 §5, §7, §8.3, §16(DESIGN_HASH_CHECK 후 `DesktopTop.dc.html`·`Components.dc.html` 읽기 전용), §16.4
- tracked 허용(exact): `index.html`(`#heroStats` 바로 뒤 `#heroFeatured` 마크업만), `js/data.js`(`featured: true,` 3줄만), `js/main.js`(`renderFeaturedProjects`, `openProjectModal` 시그니처, 위임만), `css/style.css`(`.featured-*` 비색 배치 규칙과 기존 `.project-card` 색 규칙 선택자 목록에 featured 대응 선택자 추가만), `tests/specs/featured.spec.js`
- runtime: R0
- 금지: §15.7, 새 색 선언(기존 규칙에 색 선언·같은 prop 다른 값 추가 포함), hero 순서·tagline·섹션·nav, 기존 tests, 새 target 자동 편입

## 작업 (TDD)

1. 시작 snapshot: `python3 -I tests/scripts/start-snapshot.py step39` → `python3 -I tests/scripts/design-intake-check.py`
2. `featured.spec.js`(6 project) 먼저 실패 확인: 컨테이너 1개·div·role `region`·aria-label `대표 프로젝트`·`#heroStats` 다음 형제; 카드 3개 `button[type=button]`, data-project 1·5·7, span 2개, 금지 자손 0, 텍스트 일치, span block, background-image none; 카드 click 후 button·backdrop·esc 닫기 → 카드 포커스, 제목 일치, Enter·esc 복귀; `findProjectWithShots`·`prepareForAxe({ scenario: 'modal', projectIndex: 1 })`가 grid 카드만 사용; `.featured-card` 색 3속성이 `#projectGrid .project-card`와 같음.
3. 구현(`esc()` 이스케이프, 그리드 직후 호출). axe 새 target은 색 변경 없이 허용 파일 안에서 해결, 식별 손실이면 중단·재계획.

## AC

- `python3 -I tests/scripts/design-intake-check.py && sh tests/scripts/with-env.sh npm --prefix tests test -- featured.spec.js css-parse.spec.js color-vocab.spec.js design-guard-color-rules.spec.js design-guard-color.spec.js design-guard-css.spec.js design-guard.spec.js && sh tests/scripts/with-env.sh npm --prefix tests test && sh tests/scripts/with-env.sh npm --prefix tests run verify-scope && sh tests/scripts/with-env.sh node tests/scripts/scope-snapshot.mjs --check tests/.tmp/start-snapshot-step39.json --allow index.html,js/data.js,js/main.js,css/style.css,tests/specs/featured.spec.js` → exit 0
