# Resume Step 18 — featured-projects (원 step 41)

- 목적: 원 §3 대표 카드 3개·모달 연결(색은 featured 대응 선택자 추가로만).
- 19분 / 선행 0~17 / 공통 원 §9 + §R1·§R2 no-op / gate `RGATE 18`
- 허용(exact): `index.html`(`#heroStats` 바로 뒤 `#heroFeatured`만), `js/data.js`(`featured: true,` 3줄만), `js/main.js`(`renderFeaturedProjects`, `openProjectModal` 시그니처, 위임만), `css/style.css`(`.featured-*` 비색 배치와 기존 `.project-card` 색 규칙(`:hover`·`:active` 포함) 선택자에 featured 대응 추가만), `tests/specs/featured.spec.js`
- runtime: R0
- 추가 금지: 원 §11.3 전체(새 색 선언·순서 변경·token 중복 포함), hero 순서·tagline·섹션·nav, 기존 tests, 새 axe target 편입

## 작업
1. `RSNAP 18` → `DI`(이후 `DesktopTop.dc.html`·`Components.dc.html` 읽기만).
2. RED spec(6 project): 컨테이너 1개·div·role `region`·aria-label `대표 프로젝트`·`#heroStats` 다음 형제; 카드 3개 `button[type=button]`, data-project 1·5·7, span 2개, 금지 자손 0, 텍스트, span block, background-image none; click 후 button·backdrop·esc 닫기 → 카드 포커스, 제목, Enter·esc 복귀; `findProjectWithShots`·`prepareForAxe({ scenario: 'modal', projectIndex: 1 })`는 grid만; `.featured-card` 색 3속성 = `#projectGrid .project-card`.
3. 구현(`esc()`, 그리드 직후). axe 새 target은 색 변경 없이 해결, 식별 손실이면 중단·재계획.

## AC
- `DI && T featured.spec.js GS && FULL && VS && RGATE 18 index.html,js/data.js,js/main.js,css/style.css,tests/specs/featured.spec.js`
