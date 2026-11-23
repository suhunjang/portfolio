# Step 28 — section-structure

- 목적: 섹션 순서·nav·kicker·heading 재구성(§6).
- 예상 19분 / 선행 0~27 / 공통 절차 설계 §15
- read-first: 설계 §5(컨테이너), §6, §7, §8.3(canonical 안정성, 회귀), §11.4; content-exceptions final, baseline canonical
- tracked 허용(exact): `index.html`(hero 밖 섹션·nav·scroll-hint), `js/main.js`(스크롤스파이 배열과 skill-group h4만), `tests/specs/structure.spec.js`
- runtime: R0
- 금지: §15.7, `css/*`, `js/data.js`, hero 내부, 표에 없는 문구

## 작업 (TDD)

1. 시작 snapshot: `python3 -I tests/scripts/start-snapshot.py step28`
2. `structure.spec.js`(6 project): 섹션·nav·kicker·h2가 §6과 일치, subsection h3 1개, skillsGrid는 about 안·h4, contact·scroll-hint, heading 계층, `#heroFeatured` 유지, desktop 스크롤스파이 정확히 `const link = page.locator('.nav-link[href="#about"]'); await link.click(); await expect(link).toHaveClass(/active/);`.
3. index.html: 섹션 subtree 통째 이동(anchor 보존), kicker, Stack &amp; Contact 분리, nav·scroll-hint·section-alt. main.js: 배열과 h4.
4. axe canonical 점검: 식별 손실이면 중단·재계획, 새 요소 신규 위반은 허용 파일 안에서 수정, 자동 편입 금지.

## AC

- `sh tests/scripts/with-env.sh npm --prefix tests test -- structure.spec.js && sh tests/scripts/with-env.sh npm --prefix tests test && sh tests/scripts/with-env.sh npm --prefix tests run verify-scope && sh tests/scripts/with-env.sh node tests/scripts/scope-snapshot.mjs --check tests/.tmp/start-snapshot-step28.json --allow index.html,js/main.js,tests/specs/structure.spec.js` → exit 0, content-static.spec에서 final 성립
