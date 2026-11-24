# Step 20 — modal-regression

- 목적: modal.js helper와 모달·lightbox 회귀(BASE 사이트에서 통과).
- 예상 18분 / 선행 0~19 / 공통 절차 설계 §15 / 종료 gate: CLI
- read-first: 설계 §3, §5, §7.4, §11.4
- tracked 허용(exact): `tests/helpers/modal.js`(신규), `tests/specs/modal-regression.spec.js`(신규)
- runtime: R0
- 금지: §15.7

## 작업

1. 시작 snapshot: `python3 -I tests/scripts/start-snapshot.py step20`
2. `modal.js`: 설계 §7.4 그대로.
3. spec(6 project): click·Enter 열기, 제목, `modal-open`; 세 닫기 경로 후 포커스 복귀·해제; desktop lightbox `findProjectWithShots`·`.shot-zoom` 열림; Esc 1회 lightbox만, 2회 모달.

## AC

- `sh tests/scripts/with-env.sh npm --prefix tests test -- modal-regression.spec.js && sh tests/scripts/with-env.sh npm --prefix tests test && sh tests/scripts/with-env.sh npm --prefix tests run verify-scope && sh tests/scripts/with-env.sh node tests/scripts/scope-snapshot.mjs --check tests/.tmp/start-snapshot-step20.json --allow tests/helpers/modal.js,tests/specs/modal-regression.spec.js` → exit 0
