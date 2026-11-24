# Step 37 — section-structure

- 목적: FINAL 섹션 순서·nav·kicker·heading 재구성(§6).
- 예상 19분 / 선행 0~36 / 공통 절차 설계 §15 / 종료 gate: CLI
- read-first: 설계 §5, §6, §7, §8.3, §11.4, §12(step 37 예외), §16(DESIGN_HASH_CHECK 후 `DesktopExplore.dc.html` 읽기 전용); content-exceptions final
- tracked 허용(exact): `index.html`(hero 밖 섹션 subtree 이동·kicker·Stack &amp; Contact 분리·nav 순서·scroll-hint 위치; 속성 변경은 설계 §12의 (a)·(b)만), `js/main.js`(스크롤스파이 배열과 skill-group h4만), `tests/specs/structure.spec.js`
- runtime: R0
- 금지: §15.7, `css/*`, `js/data.js`, hero 내부, 표에 없는 문구, (a)·(b) 밖 속성 변경, 새 섹션·이미지·아이콘

## 작업 (TDD)

1. 시작 snapshot: `python3 -I tests/scripts/start-snapshot.py step37` → `python3 -I tests/scripts/design-intake-check.py`
2. `structure.spec.js`(6 project): 섹션·nav·kicker·h2가 §6과 일치, section `class` 정확히 §6 표, subsection h3 1개, skillsGrid는 about 안·h4, contact, `.scroll-hint` `href === '#career'`, heading 계층, `#heroFeatured` 유지, PROJECTS 카드 13개 순서 불변, desktop 스크롤스파이 정확히 `const link = page.locator('.nav-link[href="#about"]'); await link.click(); await expect(link).toHaveClass(/active/);`.
3. index.html·main.js 변경. axe canonical 점검(식별 손실이면 중단·재계획).

## AC

- `python3 -I tests/scripts/design-intake-check.py && sh tests/scripts/with-env.sh npm --prefix tests test -- structure.spec.js design-guard.spec.js && sh tests/scripts/with-env.sh npm --prefix tests test && sh tests/scripts/with-env.sh npm --prefix tests run verify-scope && sh tests/scripts/with-env.sh node tests/scripts/scope-snapshot.mjs --check tests/.tmp/start-snapshot-step37.json --allow index.html,js/main.js,tests/specs/structure.spec.js` → exit 0, content-static.spec에서 final 성립
