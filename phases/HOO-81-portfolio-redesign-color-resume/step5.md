# Color-resume Step 5 — coordinator-manifest-validate

- 존재 이유: wave 2 manifest의 tagged-union 계약과 최소 권한 검증, 그리고 manifest에서 wave 2 contract를 도출하는 기능을 확정한다(Astra v59 #7·#8).
- 시간: agent 예상 ≤20분. 근거: 검증 함수 1개, contract 도출 함수 1개, 표 기반 spec. owner map은 step 2를 재사용한다. Harness hard timeout은 30분.
- 선행: 0~4
- 공통 규칙: 원 §9 + §C1·§C5·§C9
- gate: `XGATE 5`
- 허용(exact): `tests/helpers/parallel-wave-manifest.js`, `tests/specs/parallel-wave-manifest.spec.js`(둘 다 신규), `tests/scripts/parallel-wave.mjs`(dispatch 추가만)
- runtime: R0 + `tests/.tmp/parallel/**`
- 추가 금지: guard 상수 정의(step 7에서 함), 사이트 수정, 다른 파일 수정

## 작업
1. `XSNAP 5`
2. `parallel-wave-manifest.js`를 작성한다.
   - export: `validateManifest`, `wave2Contract`
   - 동작은 §C9 검사 전부다. guard 상수는 주입한 경로에서 import한다. 기본 경로는 `tests/helpers/design-guard-color-rules.js`이고 상수가 없으면 `[]`로 본다.
   - `registerWaveContract(2, wave2Contract)`로 등록한다.
3. CLI에 `validate-manifest`를 연결한다.
4. spec을 작성한다. synthetic collected, CSS, JS, proof를 쓴다.
   - 정상 color·nested 혼합 → PASS
   - 실패 사례:
     - collectedSha 불일치
     - target 누락
     - target 중복
     - 허용되지 않은 rule
     - 잘못된 change type
     - change.targets ⊄ shard.targets
     - change.file ∉ shard.files
     - shard.files·anchors가 최소 집합이 아님
     - color base가 실제와 불일치
     - `to` token이 정의되지 않음
     - proof sha 불일치
     - nested anchor가 없음
     - nested `before` 불일치
     - requiredCommands가 다름
     - color 투영 불일치
     - 위반 0인데 shard가 비어 있지 않음
   - 위반 0이고 모든 배열이 빔 → PASS
   - `wave2Contract`의 lane이 `steps: ['focus']`, `checkpointSteps: ['focus']`, requiredCommands, port 4180~4184, importOrder로 정확하다.

## AC
- `T parallel-wave-manifest.spec.js parallel-wave-record.spec.js parallel-wave-contract.spec.js && FULL && VS && XGATE 5 tests/helpers/parallel-wave-manifest.js,tests/specs/parallel-wave-manifest.spec.js,tests/scripts/parallel-wave.mjs tests/helpers/parallel-wave-manifest.js,tests/specs/parallel-wave-manifest.spec.js`
