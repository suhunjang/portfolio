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
3. 계약: step 7 API. spec: `checkIdentity` 필드별·순서; `computeIdentity` parity 일치·다른 root throw·root symlink·`.harness` 조상 symlink·lock FIFO에서 BASE verify·lock open 없음; 변경 판정 표; unsafe 우선; 전체 순서; 입력 불변.

## AC (모두 exit 0)

1. `sh tests/scripts/with-env.sh npm --prefix tests test -- scope-snapshot-identity.spec.js && sh tests/scripts/with-env.sh npm --prefix tests test && python3 -I tests/scripts/start-snapshot.py step7`
2. 범위 gate: `python3 -I - step7 'tests/scripts/scope-snapshot.mjs,tests/specs/scope-snapshot-identity.spec.js' '' <<'PY'` + 설계 §11.7 C 코드 블록 본문(그대로) + `PY`
