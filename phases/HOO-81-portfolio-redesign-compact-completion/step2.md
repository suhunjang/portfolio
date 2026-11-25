# Compact Step 2 — hero-first-screen (r19)

- 목적: hero DOM 순서·tagline과 1280×800 첫 화면 AC(원 §3)를 구현한다.
- 예상 16분, hard timeout 30분. 선행: step 1. 공통 선행조건 §C0.
- 허용 파일(exact):
  - `index.html`: section#hero 내부의 직계 순서·tagline만
  - `js/main.js`: `setText('heroTagline', PROFILE.tagline);` 1줄만
  - `css/style.css`: hero 1열 간격·STATS·featured 반응형·`.hero-tagline` 비색 타이포만
  - `tests/specs/featured.spec.js`: 보강
- runtime: §C4
- 금지: `js/data.js`, 색, 문구 변경, hero 2열(step 3), 섹션·nav

## 작업
1. `featured.spec.js`에 assertion을 보강하고 RED를 확인한다.
   - hero 직계 자식 순서가 원 §3과 같다. `#heroTagline`은 `PROFILE.tagline`이다.
   - CTA·eyebrow·typed·`#heroFeatured`의 role과 label이 유지된다.
   - STATS는 375에서 2×2, 768과 1280에서 4×1이다.
   - featured는 375/768/1280에서 1/2/3열이다.
   - desktop-dark/light 1280×800에서 원 §3 첫 화면 AC를 모두 만족한다.
2. 구현한다.

## AC
- `OWN_SPEC tests/specs/featured.spec.js`
- `T specs/featured.spec.js specs/content-static.spec.js`
- `DI`
- `T <GS>`
