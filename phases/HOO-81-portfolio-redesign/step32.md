# Step 32 — section-structure

- 목적: 섹션 순서·nav·kicker·heading 재구성(§6).
- 예상 19분 / 선행 0~31 / 공통 절차 설계 §15
- read-first: 설계 §5(컨테이너), §6, §7, §8.3(canonical 안정성, 회귀), §11.4, §12(index.html 속성 변경 제한과 step 32 예외); content-exceptions final, baseline canonical
- tracked 허용(exact): `index.html`(hero 밖 섹션 subtree 이동·kicker·Stack &amp; Contact 분리·nav 항목 순서·scroll-hint 위치; 속성 변경은 설계 §12의 step 32 예외 두 가지만 — (a) 기존 `.scroll-hint`의 `href`를 아래 AC에 지정된 새 타깃 `#career`로 변경, (b) §6 표에 따라 section의 `class`를 변경해 `section-alt`를 표대로 맞춤(`#projects`·`#about`은 정확히 `section section-alt`, `#career`·`#strengths`·`#contact`는 정확히 `section`)), `js/main.js`(스크롤스파이 배열과 skill-group h4만), `tests/specs/structure.spec.js`
- runtime: R0
- 금지: §15.7, `css/*`, `js/data.js`, hero 내부, 표에 없는 문구, 위 (a)·(b) 밖의 index.html 속성 변경(id·data-*·aria-*·role·그 밖 href·class 등)

## 작업 (TDD)

1. 시작 snapshot: `python3 -I tests/scripts/start-snapshot.py step32`
2. `structure.spec.js`(6 project): 섹션·nav·kicker·h2가 §6과 일치, 각 section의 `class` 속성이 §6 표의 class 값과 정확히 일치, subsection h3 1개, skillsGrid는 about 안·h4, contact, `.scroll-hint`의 `href`가 정확히 `#career`, heading 계층, `#heroFeatured` 유지, desktop 스크롤스파이 정확히 `const link = page.locator('.nav-link[href="#about"]'); await link.click(); await expect(link).toHaveClass(/active/);`.
3. index.html: 섹션 subtree 통째 이동(anchor 보존), kicker, Stack &amp; Contact 분리, nav 순서, 예외 (a) `.scroll-hint` `href` → `#career`, 예외 (b) section `class`의 `section-alt`를 §6 표대로. main.js: 배열과 h4.
4. axe canonical 점검: 식별 손실이면 중단·재계획, 새 요소 신규 위반은 허용 파일 안에서 수정, 자동 편입 금지.

## AC

- `sh tests/scripts/with-env.sh npm --prefix tests test -- structure.spec.js && sh tests/scripts/with-env.sh npm --prefix tests test && sh tests/scripts/with-env.sh npm --prefix tests run verify-scope && sh tests/scripts/with-env.sh node tests/scripts/scope-snapshot.mjs --check tests/.tmp/start-snapshot-step32.json --allow index.html,js/main.js,tests/specs/structure.spec.js` → exit 0, content-static.spec에서 final 성립
- structure.spec.js 단독 실행에 `.scroll-hint` `href === '#career'`(새 타깃)와 section `class` 값 = §6 표 assertion이 포함되어 통과한다.
