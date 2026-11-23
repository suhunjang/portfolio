# Step 13 — axe-canonical

- 목적: axe canonical target 식별 helper.
- 예상 19분 / 선행 0~12 / 공통 절차 설계 §15
- read-first: 설계 §8.1, §8.3(canonical, 안정성 범위, step 13)
- tracked 허용(exact): `tests/helpers/axe.js`(신규), `tests/specs/axe-helper.spec.js`(신규)
- runtime: R0
- 금지: §15.7

## 작업

1. 시작 snapshot: `python3 -I tests/scripts/start-snapshot.py step13`
2. `axe.js`: `ALIASES`, `canonicalTargetInPage`, `canonicalFromDescriptor`, `runAxe`.
3. `axe-helper.spec.js`(desktop-dark, setContent + 실제 axe): section#career subtree 이동·h3→span·01→04에도 key 같음; h3만 section 밖 이동하면 다름; `[data-project=5]` 안 div→p 같음; 텍스트 다르면 다름; `project:5`≠`featured:5`; alias 적용 시 같음.

## AC

- `sh tests/scripts/with-env.sh npm --prefix tests test -- axe-helper.spec.js && sh tests/scripts/with-env.sh npm --prefix tests test && sh tests/scripts/with-env.sh npm --prefix tests run verify-scope && sh tests/scripts/with-env.sh node tests/scripts/scope-snapshot.mjs --check tests/.tmp/start-snapshot-step13.json --allow tests/helpers/axe.js,tests/specs/axe-helper.spec.js` → exit 0
