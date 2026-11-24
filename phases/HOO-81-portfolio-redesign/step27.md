# Step 27 — ui-regression

- 목적: 테마·최초 방문·메뉴·scrollspy·typing·reduced-motion 회귀.
- 17분 / 선행 0~26 / 공통 §9 / gate GATE
- 허용(exact): `tests/specs/ui-regression.spec.js`, `tests/specs/first-visit.spec.js`
- runtime: R0

## 작업
1. `SNAP 27`
2. ui-regression(6 project): 토글 `data-theme`·`THEME_KEY` 새로고침 유지; mobile `#navLinks.open`·`aria-expanded="true"`, 링크 클릭 후 닫힘; desktop 스크롤스파이 §4 정확한 문법(projects); typing 변화; `reducedMotion: 'reduce'`에서 `#typed` = `roles[0]`, `.reveal` 즉시 `.in`. first-visit: fixture 없이 desktop-dark, colorScheme light·dark 따름.

## AC
- `T ui-regression.spec.js first-visit.spec.js && FULL && VS && GATE 27 tests/specs/ui-regression.spec.js,tests/specs/first-visit.spec.js`
