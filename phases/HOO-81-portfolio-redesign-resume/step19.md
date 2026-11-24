# Resume Step 19 — section-structure (원 step 44)

- 목적: 원 §4 FINAL 섹션·nav·kicker·heading.
- 19분 / 선행 0~18 / 공통 원 §9 + §R1·§R2 no-op / gate `RGATE 19`
- 허용(exact): `index.html`(hero 밖 섹션 subtree 이동·kicker·Stack &amp; Contact 분리·nav 순서·scroll-hint, 속성은 원 §9 (a)·(b)만), `js/main.js`(스크롤스파이 배열·skill-group h4만), `tests/specs/structure.spec.js`
- runtime: R0
- 추가 금지: `css/*`, `js/data.js`, hero 내부, 표에 없는 문구, (a)·(b) 밖 속성, 새 섹션·이미지·아이콘

## 작업
1. `RSNAP 19` → `DI`(`DesktopExplore.dc.html` 읽기만).
2. RED spec(6 project): 섹션·nav·kicker·h2·section `class` 정확히 원 §4; subsection h3 1개; skillsGrid about 안·h4; contact; `.scroll-hint` `href === '#career'`; heading 계층; `#heroFeatured` 유지; 카드 13개 순서; 스크롤스파이 원 §4 문법(about).
3. subtree 통째 이동, axe canonical 점검(식별 손실이면 중단·재계획).

## AC
- `DI && T structure.spec.js GS && FULL && VS && RGATE 19 index.html,js/main.js,tests/specs/structure.spec.js`(content-static.spec에서 final 성립)
