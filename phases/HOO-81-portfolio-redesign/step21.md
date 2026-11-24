# Step 21 — ui-regression

- 목적: 테마·최초 방문·메뉴·scrollspy·typing·reduced-motion 회귀.
- 예상 17분 / 선행 0~20 / 공통 절차 설계 §15 / 종료 gate: CLI
- read-first: 설계 §3, §6, §7.4, §11.4
- tracked 허용(exact): `tests/specs/ui-regression.spec.js`, `tests/specs/first-visit.spec.js`
- runtime: R0
- 금지: §15.7

## 작업

1. 시작 snapshot: `python3 -I tests/scripts/start-snapshot.py step21`
2. `ui-regression.spec.js`(6 project): 테마 토글·유지; mobile 메뉴 open/close; desktop 스크롤스파이 정확히 `const link = page.locator('.nav-link[href="#projects"]'); await link.click(); await expect(link).toHaveClass(/active/);`; typing; reduced-motion.
3. `first-visit.spec.js`: fixture 없이 desktop-dark, colorScheme light·dark.

## AC

- `sh tests/scripts/with-env.sh npm --prefix tests test -- ui-regression.spec.js first-visit.spec.js && sh tests/scripts/with-env.sh npm --prefix tests test && sh tests/scripts/with-env.sh npm --prefix tests run verify-scope && sh tests/scripts/with-env.sh node tests/scripts/scope-snapshot.mjs --check tests/.tmp/start-snapshot-step21.json --allow tests/specs/ui-regression.spec.js,tests/specs/first-visit.spec.js` → exit 0
