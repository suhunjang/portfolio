# Compact Step 6 — component-states (r23·r26·r27, clamp·stripe 담당)

- 목적: 다음 네 가지를 구현한다.
  - hit target 44px 이상
  - 비색 hover/active
  - blurb clamp 3줄
  - `.strength-card::before` stripe 제거
- 예상 18분, hard timeout 30분. 선행: step 5. 공통 선행조건: §C0.
- 허용 파일(exact):
  - `css/style.css`: 색이 아닌 속성만 바꾼다. 대상은 hit target, `:hover`·`:active`의 transform·opacity·transition, clamp, BASE `.strength-card::before` 삭제다.
  - `tests/specs/final-contract.spec.js`: 보강
- runtime: §C4
- 금지: `index.html`, `js/*`, 색 변경, 무한 장식 애니메이션 제거, print

## 작업
1. `final-contract.spec.js`에 아래 assertion을 보강하고 RED를 확인한다. 측정 전에 유한 애니메이션이 끝날 때까지 기다린다.
   - **hit target**: 6개 project에서 다음 요소의 크기가 44 이상이다.
     - `.nav-link`, `#menuToggle`(보이면), `#themeToggle`, `.hero-cta .btn`
     - `.featured-card` 3개, `#projectGrid .project-card` 13개
     - `#contactActions a`(있으면), `.scroll-hint`(보이면)
   - **hover/active**: desktop-dark/light에서 세 대상 모두
     - transform 또는 opacity가 바뀐다.
     - 세 색 속성은 그대로다.
   - **clamp**
     - blurb 16개의 clamp가 `3`이다.
     - 각 textContent가 `PROJECTS[i].blurb`와 같다.
     - `.modal-blurb`는 clamp가 `none`이다.
   - **stripe**
     - `.strength-card::before`가 없거나(content none) 크기가 0이다.
     - strength 카드 6개의 순서와 내용이 `STRENGTHS`와 같다.
2. 구현한다.

## AC
- `OWN_SPEC tests/specs/final-contract.spec.js`
- `T specs/final-contract.spec.js specs/featured.spec.js specs/ui-regression.spec.js`
- `DI`
- `T <GS>`
