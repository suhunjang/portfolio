# Color-resume Step 4 — coordinator-record-verify

- 존재 이유: 자기참조가 없는 envelope, attempt 기반 record, current pointer, git object 재구성 검증(`verify-record`)을 확정한다(Astra v59 #4·#5·#8).
- 시간: agent 예상 ≤20분. 근거: 직렬화 1개, 검증 함수 1개(step 2·3 함수 재사용), synthetic repo 시나리오 spec. Harness hard timeout은 30분.
- 선행: 0~3
- 공통 규칙: 원 §9 + §C1·§C8
- gate: `XGATE 4`
- 허용(exact): `tests/helpers/parallel-wave-record.js`, `tests/specs/parallel-wave-record.spec.js`(둘 다 신규), `tests/scripts/parallel-wave.mjs`(dispatch 추가만)
- runtime: R0 + `tests/.tmp/parallel/**`
- 추가 금지: 실제 SCR 경로에 쓰기, 다른 파일 수정

## 작업
1. `XSNAP 4`
2. `parallel-wave-record.js`를 작성한다.
   - export: `canon`, `envelope`, `record`, `verifyRecord`, `readCurrent`
   - 동작은 §C8 그대로다.
3. CLI에 연결한다.
4. spec을 작성한다. synthetic repo를 쓴다.
   - envelope:
     - 정상 → PASS
     - payload 변조 → `record:hash`
     - payloadSha256 변조 → `record:hash`
     - runtime과 external이 1byte 다름 → `record:mismatch`
   - record dry-run → 파일·pointer 불변. `--apply` → 세 파일 생성
   - 정상 시나리오: wave 1 prologue와 lane 3개 → verify PASS
   - retry 시나리오: overlap → retry → adopt → verify PASS
   - 실패 사례:
     - 잘못된 attempt base → `record:attempt-base`
     - 없는 adopt id → `record:adopt`
     - integration tree 불일치 → `record:composite`
     - HEAD 불일치 → `record:head`
   - wave 2:
     - 정상 lane(`steps: ['focus']`) → PASS
     - focus checkpoint 누락 → `lane:checkpoints`
     - 잘못된 command → `lane:commands:focus`
     - 빈 wave(`lanes: []`, `importOrder: []`) → verify PASS
   - pointer: runRoot prefix가 다르면 `runroot:invalid`

## AC
- `T parallel-wave-record.spec.js parallel-wave-run.spec.js parallel-wave-anchor.spec.js && FULL && VS && XGATE 4 tests/helpers/parallel-wave-record.js,tests/specs/parallel-wave-record.spec.js,tests/scripts/parallel-wave.mjs tests/helpers/parallel-wave-record.js,tests/specs/parallel-wave-record.spec.js`
