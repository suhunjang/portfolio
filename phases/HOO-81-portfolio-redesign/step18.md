# Step 18 — content-data-baseline

- 목적: BASE data·index fixture와 데이터 보존 검사(PROJECTS 13개·순서 포함).
- 예상 16분 / 선행 0~17 / 공통 절차 설계 §15 / 종료 gate: CLI
- read-first: 설계 §3, §6, §7.1, §7.2-1, §7.3
- tracked 허용(exact): `tests/scripts/make-fixtures.mjs`, `tests/fixtures/baseline-data.json`, `tests/fixtures/baseline-index.html`, `tests/helpers/content.js`(신규: `norm`, `readLiveData`, `normalizeFeatured`만), `tests/specs/content-data.spec.js`, `tests/package.json`(`fixtures` 추가만)
- runtime: R0
- 금지: §15.7, `extractStatic`

## 작업

1. 시작 snapshot: `python3 -I tests/scripts/start-snapshot.py step18`
2. `make-fixtures.mjs`(BASE data.js vm 평가, BASE index.html), `fixtures` script 추가 후 실행.
3. `content.js` 3함수.
4. `content-data.spec.js`(6 project): normalizeFeatured 불변·throw; baseline deep-equal; featured 1·5·7만; 빈 연락처; 렌더 개수(stats 4, timeline = CAREER, project-card 13, strengths 6); `#projectGrid` 카드 `data-project` 0~12 순서와 제목 배열 = baseline.

## AC

- `sh tests/scripts/with-env.sh npm --prefix tests test -- content-data.spec.js && sh tests/scripts/with-env.sh npm --prefix tests test && sh tests/scripts/with-env.sh npm --prefix tests run verify-scope && sh tests/scripts/with-env.sh node tests/scripts/scope-snapshot.mjs --check tests/.tmp/start-snapshot-step18.json --allow tests/scripts/make-fixtures.mjs,tests/fixtures/baseline-data.json,tests/fixtures/baseline-index.html,tests/helpers/content.js,tests/specs/content-data.spec.js,tests/package.json` → exit 0
