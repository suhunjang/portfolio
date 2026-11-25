# Step 1: featured-projects

## Always-on invariants
Do not modify historical phase records/evidence. Preserve all copy, numbers, font assets/weights, information architecture, 3 featured project identities, all 13 PROJECTS and order. No new copy, section, image, icon, project or placeholder content. css/themes.css is read-only; if it or index.html is required outside the listed lane, stop and replan. Implementation workers must not commit, push, merge, edit the canonical phase index, or write outside their exact lane files. Run only focused tests in lanes; canonical FULL/UI/a11y run at steps 12 and 14.

## Exact work order
### Bound historical contract: `phases/HOO-81-portfolio-redesign-resume/step18.md`
SHA-256 `2257f62944d6ec4ca95c96f8144a3c4463c2b1ee7030f759f7ae7d896b116cc9`

# Resume Step 18 — featured-projects (원 step 41)

- 목적: 원 §3 대표 카드 3개·모달 연결(색은 featured 대응 선택자 추가로만).
- 19분 / 선행 0~17 / 공통 원 §9 + §R1·§R2 no-op·§R11 / gate `RGATE 18`
- 허용(exact): `index.html`(`#heroStats` 바로 뒤 `#heroFeatured`만), `js/data.js`(`featured: true,` 3줄만), `js/main.js`(`renderFeaturedProjects`, `openProjectModal` 시그니처, 위임만), `css/style.css`(`.featured-*` 비색 배치와 기존 `.project-card` 색 규칙(`:hover`·`:active` 포함) 선택자에 featured 대응 추가만), `tests/specs/featured.spec.js`
- 필수 산출물(REQ): `tests/specs/featured.spec.js,index.html,js/data.js,js/main.js,css/style.css`
- runtime: R0
- 추가 금지: 원 §11.3 전체(새 색 선언·순서 변경·token 중복 포함), hero 순서·tagline·섹션·nav, 기존 tests, 새 axe target 편입

## 작업
1. `RSNAP 18` → no-op 첫 probe `REQ 18 tests/specs/featured.spec.js,index.html,js/data.js,js/main.js,css/style.css`. PASS면 나머지 AC 실행 → 통과 시 `resume step18: no-op`. REQ FAIL 또는 AC 실패면 아래 작업 후 완전한 AC 재실행.
2. `DI`(이후 `DesktopTop.dc.html`·`Components.dc.html` 읽기만). RED spec(6 project): 컨테이너 1개·div·role `region`·aria-label `대표 프로젝트`·`#heroStats` 다음 형제; 카드 3개 `button[type=button]`, data-project 1·5·7, span 2개, 금지 자손 0, 텍스트, span block, background-image none; click 후 button·backdrop·esc 닫기 → 카드 포커스, 제목, Enter·esc 복귀; `findProjectWithShots`·`prepareForAxe({ scenario: 'modal', projectIndex: 1 })`는 grid만; `.featured-card` 색 3속성 = `#projectGrid .project-card`.
3. 구현(`esc()`, 그리드 직후). axe 새 target은 색 변경 없이 해결, 식별 손실이면 중단·재계획.

## AC
- `REQ 18 tests/specs/featured.spec.js,index.html,js/data.js,js/main.js,css/style.css && DI && T featured.spec.js GS && FULL && VS && RGATE 18 index.html,js/data.js,js/main.js,css/style.css,tests/specs/featured.spec.js`(첫 명령 stdout `required-artifacts step118: OK 5`)


Concrete anchors: project records are existing indices 1, 5, 7 only; insert `#heroFeatured` immediately after `#heroStats`; implement `renderFeaturedProjects()` and delegate to existing `openProjectModal(idx)` without changing that signature. Featured cards are buttons, not nested interactive containers; click/Enter opens the matching modal and close/backdrop/Escape returns focus to the originating card.

## Exact write boundary
featured-implementation: index.html, js/data.js, js/main.js, css/style.css, tests/specs/featured.spec.js

## Acceptance
Run every argv in this step’s immutable `index.json.acceptanceCommands` in order. Any nonzero exit blocks the next step.
