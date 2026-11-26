# Color-resume Step 1 — coordinator-contract-doctor-prepare

- 존재 이유: CLI 골격, `--apply` 공통 규칙, `WAVE1_CONTRACT`·fileRules 상수, `doctor`, `prepare`를 확정한다(Astra v59 #1·#2·#4).
- 시간: agent 예상 ≤20분. 근거: 상수 선언, 인자 파서, 외부 명령 2종 검사, 경로·argv 생성 함수, synthetic repo 1개로 테스트. Harness hard timeout은 30분.
- 선행: 0
- 공통 규칙: 원 §9 + §C1·§C4·§C5
- gate: `XGATE 1`
- 허용(exact): `tests/scripts/parallel-wave.mjs`, `tests/helpers/parallel-wave-contract.js`, `tests/specs/parallel-wave.spec.js`, `tests/specs/parallel-wave-contract.spec.js`(모두 신규)
- runtime: R0 + `tests/.tmp/parallel/**`
- 추가 금지:
  - 실제 `claude` 실행
  - 실제 `SCR_PREFIX` 경로에 쓰기. spec은 테스트 전용 prefix를 주입하는 export 옵션을 쓴다.
  - 생성 argv에 `--bare`·`--dangerously-skip-permissions` 포함
  - schema fixture 파일 추가
  - 다른 파일 수정

## 작업
1. `XSNAP 1`
2. `parallel-wave-contract.js`를 작성한다.
   - export: `WAVE1_CONTRACT`(§C5 그대로), `FILE_RULE_TYPES`, `SCR_PREFIX`, `RUN_ID_RE`, `assertRunRoot`, `doctor`, `prepare`
   - wave 2 contract 공급 함수를 등록하는 hook `registerWaveContract(2, fn)`를 둔다. 구현은 step 5에서 한다.
3. `parallel-wave.mjs`를 작성한다. 하위 명령 dispatch, 인자 오류 exit 2, `--apply` 공통 규칙을 넣고, `doctor`·`prepare`를 연결한다.
4. spec을 작성한다. synthetic repo는 `tests/.tmp/parallel/spec-<pid>-*`에 git init하고 finally에서 그 디렉터리만 지운다.
   - `parallel-wave.spec.js`:
     - 알 수 없는 하위 명령 → exit 2
     - `--apply` 없는 prepare → canonical 파일·index·ref와 runRoot가 불변(전후 hash 비교)
     - `--apply` prepare → worktree·branch·symlink·prompt·run JSON attempt가 생성됨
     - 잘못된 runRoot → `runroot:invalid`
   - `parallel-wave-contract.spec.js`:
     - WAVE1_CONTRACT의 lane·steps·port·importOrder·fileRules 경로 목록이 §C5와 exact로 같다. 신규 spec 13개, helper 2개, script, fixture, `js/data.js`가 포함돼 있다.
     - doctor 정상 사례 PASS
     - doctor 실패 사례: `--setting-sources` 누락 → `doctor:flag-missing`, `OPENROUTER_API_KEY` 설정 → `doctor:forbidden-env`, 포트 점유 → `doctor:port-busy`
     - prepare argv에 `--setting-sources user`가 있고 금지 flag는 없다. allowlist는 requiredCommands를 `Bash(<exact>)`로 감싼 것이다.

## AC
- `T parallel-wave.spec.js parallel-wave-contract.spec.js && PW prepare --wave 1 --run-root /Users/hoon/.hermes/profiles/ryan/cache/scratch/HOO-81-parallel-dryrun01 --base $(git rev-parse HEAD) --lanes A,B,C,D,E && FULL && VS && XGATE 1 tests/scripts/parallel-wave.mjs,tests/helpers/parallel-wave-contract.js,tests/specs/parallel-wave.spec.js,tests/specs/parallel-wave-contract.spec.js tests/scripts/parallel-wave.mjs,tests/helpers/parallel-wave-contract.js,tests/specs/parallel-wave.spec.js,tests/specs/parallel-wave-contract.spec.js`
- 여기의 prepare는 dry-run이라 파일을 쓰지 않는다.
