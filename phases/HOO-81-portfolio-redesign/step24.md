# Step 24 — content-data-baseline

- 목적: BASE data·index fixture와 데이터 보존(§5, PROJECTS 13·순서).
- 16분 / 선행 0~23 / 공통 §9 / gate GATE
- 허용(exact): `tests/scripts/make-fixtures.mjs`, `tests/fixtures/baseline-data.json`, `tests/fixtures/baseline-index.html`, `tests/helpers/content.js`(신규: `norm`, `readLiveData`, `normalizeFeatured`만), `tests/specs/content-data.spec.js`, `tests/package.json`(`fixtures` 추가만)
- runtime: R0

## 작업
1. `SNAP 24`
2. `make-fixtures.mjs`: `git show BASE:js/data.js` vm 평가 → `baseline-data.json`, `git show BASE:index.html` → `baseline-index.html`; `fixtures` script 추가 후 실행.
3. `normalizeFeatured`(structuredClone, index 1·5·7만, 그 밖·true 아님 throw).
4. spec(6 project): normalizeFeatured 불변·throw; `normalizeFeatured(await readLiveData(page))` = baseline; featured 없음 또는 1·5·7만; email·phone·social 빈 값; stats 4·timeline = CAREER 길이·project-card 13·strengths 6; `#projectGrid` `data-project` 0~12 순서·제목 = baseline.

## AC
- `T content-data.spec.js && FULL && VS && GATE 24 tests/scripts/make-fixtures.mjs,tests/fixtures/baseline-data.json,tests/fixtures/baseline-index.html,tests/helpers/content.js,tests/specs/content-data.spec.js,tests/package.json`
