# Step 24 — axe-canonical

- 목적: axe canonical target 식별 helper.
- 예상 19분 / 선행 0~23 / 공통 절차 설계 §15 / 종료 gate: CLI
- read-first: 설계 §8.1, §8.3(step 24)
- tracked 허용(exact): `tests/helpers/axe.js`(신규), `tests/specs/axe-helper.spec.js`(신규)
- runtime: R0
- 금지: §15.7

## 작업

1. 시작 snapshot: `python3 -I tests/scripts/start-snapshot.py step24`
2. `ALIASES`, `canonicalTargetInPage`, `canonicalFromDescriptor`, `runAxe`.
3. spec(desktop-dark, setContent + 실제 axe): section#career subtree 이동·h3→span·01→04에도 key 같음; h3만 section 밖 이동하면 다름; `[data-project=5]` 안 div→p 같음; 텍스트 다르면 다름; `project:5`≠`featured:5`; alias 적용 시 같음.

## AC

- `sh tests/scripts/with-env.sh npm --prefix tests test -- axe-helper.spec.js && sh tests/scripts/with-env.sh npm --prefix tests test && sh tests/scripts/with-env.sh npm --prefix tests run verify-scope && sh tests/scripts/with-env.sh node tests/scripts/scope-snapshot.mjs --check tests/.tmp/start-snapshot-step24.json --allow tests/helpers/axe.js,tests/specs/axe-helper.spec.js` → exit 0
