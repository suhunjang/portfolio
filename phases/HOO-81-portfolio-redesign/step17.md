# Step 17 — content-data-baseline

- 목적: BASE data·index fixture 생성과 데이터 보존 검사(PROJECTS 13개·순서 포함).
- 예상 16분 / 선행 0~16 / 공통 절차 설계 §15 / 종료 gate: CLI
- read-first: 설계 §3, §6, §7.1, §7.2-1, §7.3
- tracked 허용(exact): `tests/scripts/make-fixtures.mjs`, `tests/fixtures/baseline-data.json`, `tests/fixtures/baseline-index.html`, `tests/helpers/content.js`(신규: `norm`, `readLiveData`, `normalizeFeatured`만), `tests/specs/content-data.spec.js`, `tests/package.json`(`fixtures` script 추가만)
- runtime: R0
- 금지: §15.7, `extractStatic`(step 18)

## 작업

1. 시작 snapshot: `python3 -I tests/scripts/start-snapshot.py step17`
2. `make-fixtures.mjs`: `git show BASE:js/data.js` vm 평가 → `baseline-data.json`, `git show BASE:index.html` → `baseline-index.html`. `fixtures` script 추가 후 실행.
3. `content.js`: `norm`, `readLiveData`, `normalizeFeatured`(structuredClone, index 1·5·7만).
4. `content-data.spec.js`(6 project): normalizeFeatured 입력 불변·금지 index throw; `normalizeFeatured(await readLiveData(page))` = baseline deep-equal; featured 없음 또는 1·5·7만; email·phone·social 빈 값; 렌더 개수 stats 4, timeline = CAREER 길이, project-card 13, strengths 6; `#projectGrid` 카드 `data-project` 순서가 0~12이고 project-title 배열 = baseline 순서.

## AC

- `sh tests/scripts/with-env.sh npm --prefix tests test -- content-data.spec.js && sh tests/scripts/with-env.sh npm --prefix tests test && sh tests/scripts/with-env.sh npm --prefix tests run verify-scope && sh tests/scripts/with-env.sh node tests/scripts/scope-snapshot.mjs --check tests/.tmp/start-snapshot-step17.json --allow tests/scripts/make-fixtures.mjs,tests/fixtures/baseline-data.json,tests/fixtures/baseline-index.html,tests/helpers/content.js,tests/specs/content-data.spec.js,tests/package.json` → exit 0
