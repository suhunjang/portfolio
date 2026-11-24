# Step 7 — scope-snapshot-identity (재검증)

- 목적: identity 계산·대조와 순수 변경·정책 판정(unsafe 우선)을 확인한다. §11.6 재검증 모드.
- 예상 18분 / 선행 0~6 / 공통 절차 설계 §15 / 종료 gate: S reused + inline C
- read-first: 설계 §11.1, §11.5, §11.6, §11.7
- tracked 허용(exact): `tests/scripts/scope-snapshot.mjs`(step 7 API), `tests/specs/scope-snapshot-identity.spec.js`
- runtime: R0
- 금지: §15.7, step 1~4 함수 동작, 파일 쓰기 기능

## 작업

1. 시작 snapshot: `python3 -I tests/scripts/start-snapshot.py step7`
2. AC 실행 → 통과면 no-op, 실패면 계약 안에서 수정.
3. 계약: step 7 API. spec: `checkIdentity` 같음 `[]`, projectRoot·head·base·harness 4하위 필드 각각 `identity-mismatch:{field}`, 여러 필드 순서; `computeIdentity` 실제 parity 일치·다른 root(`tests/.tmp`) throw·가짜 fs/git의 root symlink·`.harness` 조상 symlink·lock FIFO → `UnsafePathError`, `rev-parse --verify`·lock open 없음; 변경 판정(`CLAUDE.md` 시작 ` M`/h1 그대로 0·원복 `outside-tests:`·삭제·내용 변경; `tests/playwright.config.js` allow 밖 `tests-changed:`·allow 안 0; 깨끗한 tests 파일 변경·사라진 untracked·walk 전용 fixture 변경 `tests-changed:`; `README.md` xy만 → `status-changed:`; 새 `?? docs/x.md` `outside-tests:`; EXEMPT 0; GUARDED `outside-tests:`; `?? tests/node_modules/…` `runtime-visible:`; rename 양쪽); unsafe 우선(`['symlink:b','non-regular:a']` + 변경 + require-absent → 정확히 snapshot-not-first, `non-regular:a`, `symlink:b`, allow 무관); 전체 순서; 입력 불변.

## AC (모두 exit 0)

1. `sh tests/scripts/with-env.sh npm --prefix tests test -- scope-snapshot-identity.spec.js && sh tests/scripts/with-env.sh npm --prefix tests test && python3 -I tests/scripts/start-snapshot.py step7`
2. 범위 gate: `python3 -I - step7 'tests/scripts/scope-snapshot.mjs,tests/specs/scope-snapshot-identity.spec.js' '' <<'PY'` + 설계 §11.7 C 코드 블록 본문(그대로) + `PY`
