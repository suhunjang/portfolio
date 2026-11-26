# Step 28 — axe-canonical

- 목적: §6.1 canonical target, §6.2 step 28 API.
- 19분 / 선행 0~27 / 공통 §9 / gate GATE
- 허용(exact): `tests/helpers/axe.js`, `tests/specs/axe-helper.spec.js`(신규)
- runtime: R0

## 작업
1. `SNAP 28`
2. spec(desktop-dark, setContent+axe): section#career subtree 이동·h3→span·01→04 key 같음; h3만 밖 이동 다름; `[data-project=5]` 안 div→p 같음; 텍스트 다르면 다름; `project:5`≠`featured:5`; alias 적용 같음.

## AC
- `T axe-helper.spec.js && FULL && VS && GATE 28 tests/helpers/axe.js,tests/specs/axe-helper.spec.js`
