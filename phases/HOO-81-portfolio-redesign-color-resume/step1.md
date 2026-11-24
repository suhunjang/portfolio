# Color-resume Step 1 — parallel-coordinator

- 존재 이유: coordinator 절차(§C4~§C7)를 실행·검증할 수 있는 코드와 spec으로 고정한다. 이 step은 실제 worktree를 만들거나 worker를 실행하지 않는다.
- 시간: agent 예상 ≤20분, Harness hard timeout 30분. 선행 0. 공통 규칙: 원 §9 + §C1. gate: `XGATE 1`.
- 허용(exact): `tests/scripts/parallel-wave.mjs`, `tests/specs/parallel-wave.spec.js`(둘 다 신규)
- runtime: R0 + `tests/.tmp/parallel/**`(spec의 synthetic repo와 임시 index)
- 추가 금지:
  - 다른 helper·spec·사이트 수정
  - schema fixture 파일 추가(코드 상수만 사용)
  - 실제 `claude` 실행
  - 실제 외부 `SCR` 경로 쓰기
  - `--apply` 경로를 canonical 저장소에 실행
  - 생성 명령에 `--bare`·`--dangerously-skip-permissions`·OpenRouter 포함

## 작업
1. `XSNAP 1`
2. `parallel-wave.mjs`를 구현한다.
   - subcommand 9개: `doctor`, `prepare`, `validate-lane`, `check-overlap`, `fan-in`, `record`, `verify-record`, `validate-manifest`와 §C4의 인자·출력·실패 코드를 그대로 따른다.
   - `WAVE1_CONTRACT`(§C5)를 코드 상수로 둔다.
   - envelope 직렬화는 §C6을 따른다.
   - semantic anchor 판정은 §C4를 따른다.
   - 직렬 재시도 base 계산 함수를 export한다.
3. `parallel-wave.spec.js`를 작성한다. node, desktop-dark 기준이며 synthetic repo는 `tests/.tmp/parallel/spec-<pid>/`에 git init하고 finally에서 그 디렉터리만 삭제한다.
   - doctor: 가짜 help text에 flag가 다 있으면 PASS. `--setting-sources`가 빠지면 `doctor:flag-missing`. `OPENROUTER_API_KEY`가 설정돼 있으면 `doctor:forbidden-env`.
   - prepare dry-run: lane 6개의 worktree·branch·port·argv가 정확하다. argv에 `--setting-sources user`가 있고 `--bare`·`--dangerously-skip-permissions`가 없다. allowlist는 requiredCommands의 exact `Bash(...)`다.
   - validate-lane:
     - PASS 사례 1개
     - 잘못된 base → `lane:bad-base`
     - 허용 밖 파일 → `lane:files`
     - 허용 밖 anchor → `lane:anchor`
     - 누락 명령이나 exit≠0 → `lane:commands`
     - 누락 checkpoint → `lane:checkpoints`
     - 변조된 result → FAIL
   - check-overlap:
     - 같은 파일 disjoint hunk + 다른 anchor → PASS
     - 교차하는 hunk → FAIL
     - 같은 anchor → FAIL
   - fan-in dry-run: composite tree가 예상과 같다. 순서를 바꾸거나 패치를 변조하면 결과가 달라지거나 FAIL이다.
   - record·verify-record:
     - 정상 envelope → PASS
     - payload 변조 → `record:hash`
     - payloadSha256 변조 → `record:hash`
     - external과 runtime 1byte 차이 → `record:mismatch`
     - integration tree가 composite와 다름 → `record:composite`
   - validate-manifest:
     - 정상 → PASS
     - collectedSha 불일치, target 누락, target 중복, 허용 밖 rule, 잘못된 change type, color 투영 불일치 → 각각 FAIL
     - 위반 0인데 shard가 비어 있지 않음 → FAIL
     - 위반 0 + 빈 배열 → PASS

## AC
- `T parallel-wave.spec.js && PW prepare --wave 1 --run-root /Users/hoon/.hermes/profiles/ryan/cache/scratch/HOO-81-parallel-dryrun01 --base $(git rev-parse HEAD) && FULL && VS && XGATE 1 tests/scripts/parallel-wave.mjs,tests/specs/parallel-wave.spec.js tests/scripts/parallel-wave.mjs,tests/specs/parallel-wave.spec.js`
- prepare dry-run은 stdout JSON만 내고 파일을 쓰지 않는다.
- 실제 `PW doctor`는 coordinator가 wave 1 직전에 canonical에서 실행한다. 실패하면 실행 전 blocker로 보고한다.
