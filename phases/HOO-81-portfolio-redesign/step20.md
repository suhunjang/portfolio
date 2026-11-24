# Step 20 — ui-regression

- 목적: 테마·최초 방문·메뉴·scrollspy·typing·reduced-motion 회귀(BASE 사이트에서 통과).
- 예상 17분 / 선행 0~19 / 공통 절차 설계 §15 / 종료 gate: CLI
- read-first: 설계 §3, §6(locator 문법), §7.4, §11.4
- tracked 허용(exact): `tests/specs/ui-regression.spec.js`, `tests/specs/first-visit.spec.js`
- runtime: R0
- 금지: §15.7

## 작업

1. 시작 snapshot: `python3 -I tests/scripts/start-snapshot.py step20`
2. `ui-regression.spec.js`(6 project): 테마 토글 `data-theme`·`THEME_KEY` 변경 후 새로고침 유지; mobile 메뉴 `#navLinks.open`·`aria-expanded="true"`, 링크 클릭 후 닫힘; desktop 스크롤스파이 정확히 `const link = page.locator('.nav-link[href="#projects"]'); await link.click(); await expect(link).toHaveClass(/active/);`; typing 변화; `reducedMotion: 'reduce'`에서 `#typed` = `roles[0]`, `.reveal` 즉시 `.in`.
3. `first-visit.spec.js`: fixture 없이 desktop-dark, colorScheme light·dark 각각 시스템 따름.

## AC

- `sh tests/scripts/with-env.sh npm --prefix tests test -- ui-regression.spec.js first-visit.spec.js && sh tests/scripts/with-env.sh npm --prefix tests test && sh tests/scripts/with-env.sh npm --prefix tests run verify-scope && sh tests/scripts/with-env.sh node tests/scripts/scope-snapshot.mjs --check tests/.tmp/start-snapshot-step20.json --allow tests/specs/ui-regression.spec.js,tests/specs/first-visit.spec.js` → exit 0
