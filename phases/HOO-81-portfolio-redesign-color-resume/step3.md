# Color-resume Step 3 — coordinator-run-fanin-retry

- 존재 이유: worker 실행(spawn/poll/kill), lane commit, fan-in, integration commit, retry 계획, cleanup을 `--apply` 규칙으로 구현한다(Astra v59 #4·#5·#6).
- 시간: agent 예상 ≤20분. 근거: 명령 7개는 git·child_process 호출을 얇게 감싼 것이다. 실제 `claude` 대신 가짜 worker script(node)로 테스트한다. Harness hard timeout은 30분.
- 선행: 0~2
- 공통 규칙: 원 §9 + §C1·§C4·§C7
- gate: `XGATE 3`
- 허용(exact): `tests/helpers/parallel-wave-run.js`, `tests/specs/parallel-wave-run.spec.js`(둘 다 신규), `tests/scripts/parallel-wave.mjs`(dispatch 추가만)
- runtime: R0 + `tests/.tmp/parallel/**`
- 추가 금지:
  - 실제 `claude` 실행
  - 테스트가 띄우지 않은 PID에 신호 보내기
  - merge·cherry-pick
  - canonical 저장소에 `--apply` 실행(spec은 synthetic repo만 사용)
  - 다른 파일 수정

## 작업
1. `XSNAP 3`
2. `parallel-wave-run.js`를 작성한다.
   - export: `runWorkers`, `commitLane`, `fanIn`, `commitIntegration`, `planRetry`, `cleanup`, `compositeTree`
   - 동작은 §C4·§C7 그대로다.
   - 테스트용으로 poll 간격과 stall 시간을 주입하는 옵션을 둔다. 기본값은 30초와 1200초다.
3. CLI에 연결한다.
4. spec을 작성한다. synthetic repo와 가짜 worker를 쓴다.
   - run-workers --apply:
     - 정상 종료 → `finished`, PID와 sessionId가 run JSON에 기록된다
     - exit≠0 → `failed`
     - checkpoint가 멈춤(stall 2초 주입) → 그 PID만 종료되고 `stalled`
     - 같은 사례의 dry-run은 spawn하지 않는다
   - commit-lane: contract 밖 파일이 있으면 FAIL. 정상이면 exact 파일만 commit된다.
   - fan-in:
     - dry-run → canonical 파일·index·runRoot 불변이고 composite tree만 출력
     - `--apply` → index tree = composite, `fanin-<w>-<stage>.json`이 생성된다
     - 패치를 변조하면 `fan-in:bytes` 또는 apply 실패
   - commit-integration: index tree가 composite와 다르면 FAIL
   - plan-retry --overlap: 뒤 lane이 선택되고 새 base = 앞 lane을 적용한 composite의 `commit-tree`다
   - plan-retry --spec:
     - owner가 1개면 그 lane
     - owner가 0개 또는 2개 이상이면 `retry:ambiguous-owner`
     - GS spec이면 `retry:common-gate`
   - cleanup: verify가 실패하면 아무것도 지우지 않는다. dry-run은 불변이다.

## AC
- `T parallel-wave-run.spec.js parallel-wave-anchor.spec.js parallel-wave.spec.js && FULL && VS && XGATE 3 tests/helpers/parallel-wave-run.js,tests/specs/parallel-wave-run.spec.js,tests/scripts/parallel-wave.mjs tests/helpers/parallel-wave-run.js,tests/specs/parallel-wave-run.spec.js`
