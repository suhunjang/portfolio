# Step 7 — scope-snapshot-identity (재검증)

- 목적: identity 계산·대조와 순수 변경·정책 판정(unsafe 우선). §8.6.
- 18분 / 선행 0~6 / 공통 §9 / gate CGATE
- 허용(exact): `tests/scripts/scope-snapshot.mjs`(step 7 API), `tests/specs/scope-snapshot-identity.spec.js`
- runtime: R0
- 추가 금지: step 1~4 동작, 파일 쓰기 기능

## 작업
1. `SNAP 7` → AC → no-op / 수정.
2. spec: `checkIdentity` 같음 `[]`, projectRoot·head·base·harness 4하위 각각 `identity-mismatch:{field}`·여러 필드 순서; `computeIdentity` 실제 parity 일치·다른 root throw·가짜 root symlink·`.harness` 조상 symlink·lock FIFO → `UnsafePathError`(`rev-parse --verify`·lock open 없음); 판정: `CLAUDE.md` 시작 ` M`/h1 그대로 0·원복 `outside-tests:`·삭제·변경; `tests/playwright.config.js` allow 밖 `tests-changed:`·안 0; tests 파일 변경·사라진 untracked·walk 전용 fixture 변경 `tests-changed:`; `README.md` xy만 `status-changed:`; 새 `?? docs/x.md` `outside-tests:`; EXEMPT 0; GUARDED `outside-tests:`; `?? tests/node_modules/…` `runtime-visible:`; rename 양쪽; unsafe 우선(`['symlink:b','non-regular:a']`+변경+require-absent → 정확히 snapshot-not-first, `non-regular:a`, `symlink:b`); 전체 순서; 입력 불변.

## AC
1. `T scope-snapshot-identity.spec.js && FULL && SNAP 7`
2. `CGATE 7 tests/scripts/scope-snapshot.mjs,tests/specs/scope-snapshot-identity.spec.js`
