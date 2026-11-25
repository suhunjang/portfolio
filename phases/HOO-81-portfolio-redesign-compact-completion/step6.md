# Compact Step 6 — component-states (r23·r26·r27, clamp·stripe 담당)

- 목적: hit target 44px 이상, 비색 hover/active, blurb line clamp 3, `.strength-card::before` stripe 제거.
- 예상 18분, hard timeout 30분. 선행: step 5. 공통 선행조건 §C0.
- 허용 파일(exact):
  - `css/style.css`: 대상 요소의 hit target, `:hover`·`:active`의 transform·opacity·transition, `.featured-blurb`·카드 blurb clamp, BASE `.strength-card::before` 삭제. 모두 비색만.
  - `tests/specs/final-contract.spec.js`: 보강
- runtime: §C4
- 금지:
  - `index.html`, `js/*`
  - 색 선언·순서
  - 무한 장식 애니메이션 제거
  - print(step 7)

## 작업
1. `final-contract.spec.js`에 assertion을 보강하고 RED를 확인한다. 측정 전에 유한 애니메이션이 끝날 때까지 기다린다.
   - 6 project에서 다음 요소의 rect가 tokens.`hitTargetMinPx`(44) 이상이다:
     - `.nav-link`(보이는 것), `#menuToggle`(보이면), `#themeToggle`, `.hero-cta .btn`
     - `.featured-card` 3개, `#projectGrid .project-card` 13개
     - `#contactActions a`(있으면), `.scroll-hint`(보이면)
   - desktop-dark/light에서 `.hero-cta .btn`·`.featured-card`·`#projectGrid .project-card`의 hover와 active 상태:
     - 각각 transform 또는 opacity가 default와 다르다.
     - color·backgroundColor·borderColor는 default와 같다.
   - `.featured-blurb` 3개와 grid 카드 blurb 13개의 `-webkit-line-clamp`가 `3`이다. textContent는 `PROJECTS[i].blurb`와 같다. 카드 0의 모달 `.modal-blurb`는 clamp가 `none`이고 전문이 보인다.
   - `.strength-card::before`의 content가 `none`이거나 rect 0이다. `.strength-card` 6개의 순서와 내용은 `STRENGTHS`와 같다.
2. 구현한다.

## AC
- `OWN_SPEC tests/specs/final-contract.spec.js`
- `T specs/final-contract.spec.js specs/featured.spec.js specs/ui-regression.spec.js`
- `DI`
- `T <GS>`
