이 프로젝트는 Discord↔Claude 하네스(macOS, **하네스 모드 전용**)를 사용한다. 아래 흐름 밖으로 나가지 마라.

---

## 0. 실행 모드

1차 범위는 **하네스 모드 하나**다. SDD(`brainstorming → writing-plans →
subagent-driven-development`) 실행 경로는 이 사본에 없다 — 사용자에게 모드를 묻거나
SDD로 라우팅하지 마라. 계획 대화는 Discord 스레드 ↔ `plan_session.py`로 진행한다.

전체 흐름:

1. **계획 대화** — `plan-session start/resume`(read-only Claude, `grilling` 질문 라운드).
   응답은 `begin-post` → Discord 게시 → `record-posted`로 결속.
2. **합의** — 대표의 합의 메시지를 `record-agreement`로 기록(구현 승인 아님).
3. **문서화** — `materialize`가 같은 세션의 strict JSON을 허용 경로
   (`docs/superpowers/specs/*.md`, `phases/<task>/`)에만 쓴다. 사람이 feature branch에 커밋.
4. **계획 리뷰** — `review-plan <task> --issue <ISSUE> --repo-root <TARGET> --evidence-dir <E>`
   (codex gpt-6-astra read-only, target 독립 clone 명시).
   findings가 있으면 자동 수정하지 않는다(종료코드 4). 같은 세션으로 재생성 → 새 hash로 재리뷰.
5. **구현 승인** — 대표의 **별도** 메시지
   `APPROVE <ISSUE> PLAN <plan commit SHA> REVIEW <review record SHA>`를 `record-approval`로
   결속. 승인 record와 approved-plan snapshot은 repo 밖 evidence에 생긴다.
6. **실행** — Ryan이 Astra-reviewed harness commit의 runner 코드를 repo 밖 runner home으로
   `export`하고, clone의 reviewed 계획 commit으로 control `pin`을 고정한다. `prepare`가 sandbox
   profile·launch descriptor를 만들고, 외부 supervisor `runner launch`가 독립 검증 뒤 **자기
   (pinned) execute.py**를 1회용 ticket과 함께 띄운다. execute 직접 실행은 거부된다.
7. **확인·push** — `runner verify-final`로 tested = reviewed = HEAD·clean tree 확인 뒤
   Ryan이 feature branch만 push하고 PR을 만든다. merge·deploy·main 변경 금지.

---

## 워크플로우

### A. 탐색

`/docs/` 하위 문서(ARCHITECTURE, ADR 등)를 읽고 프로젝트의 기획·아키텍처·설계 의도를 파악한다(read-only).

### B. 논의

구체화하거나 기술적으로 결정해야 할 사항은 `grilling` 질문 라운드로 하나씩 묻는다. 질문 원문이 Discord에 그대로 게시된다.

### C. Step 설계

사용자가 구현 계획 작성을 지시하면 여러 step으로 나뉜 초안을 작성해 피드백을 요청한다.

설계 원칙:

1. **Scope 최소화** — 하나의 step에서 하나의 레이어 또는 모듈만 다룬다. 여러 모듈을 동시에 수정해야 하면 step을 쪼갠다.
2. **자기완결성** — 각 step 파일은 독립된 Claude 세션에서 실행된다. "이전 대화에서 논의한 바와 같이" 같은 외부 참조는 금지한다. 필요한 정보는 전부 파일 안에 적는다.
3. **사전 준비 강제** — 관련 문서 경로와 이전 step에서 생성/수정된 파일 경로를 명시한다. 세션이 코드를 읽고 맥락을 파악한 뒤 작업하도록 유도한다.
4. **시그니처 수준 지시** — 함수/클래스의 인터페이스만 제시하고 내부 구현은 에이전트 재량에 맡긴다. 단, 설계 의도에서 벗어나면 안 되는 핵심 규칙(멱등성, 보안, 데이터 무결성 등)은 반드시 명시한다.
5. **AC는 실행 가능한 커맨드** — "~가 동작해야 한다" 같은 추상적 서술이 아닌 `npm run build && npm test` 같은 실제 실행 가능한 검증 커맨드를 포함한다.
6. **주의사항은 구체적으로** — "조심해라" 대신 "X를 하지 마라. 이유: Y" 형식으로 적는다.
7. **네이밍** — step name은 kebab-case slug로, 해당 step의 핵심 모듈/작업을 한두 단어로 표현한다 (예: `project-setup`, `api-layer`, `auth-flow`).
8. **step 예산** — step 하나는 에이전트 예상 소요 20분 이하로 잡는다(하네스 제한 30분 = `STEP_TIMEOUT` 1800초). 예상이 20분을 넘으면 원래 작업 경계대로 나누고 step마다 자기 AC를 둔다. 뒤 step이 앞 step의 빌드 산출물을 재사용한다고 가정하지 마라. 이유: 다음 빌드가 덮는다. 아래 신호가 보이면 예상 소요를 다시 따진다(신호 자체가 major는 아니다): 서로 독립인 작업 3개 이상 / 빌드 4회 이상 / 서버 기동이 다른 큰 작업과 같이 있음 / 1,000줄 넘는 기존 파일 둘 이상을 크게 고침.


### D. 계획 파일 (materialize가 쓴다)

#### D-1. `phases/{task-name}/index.json`

```json
{
  "project": "<프로젝트명>",
  "phase": "<task-name>",
  "baseBranch": "main",
  "designDoc": "docs/superpowers/specs/2026-11-22-<topic>-design.md",
  "allowedPaths": ["src/", "tests/"],
  "testCommand": ["./.venv/bin/python", "-m", "pytest", "-q"],
  "steps": [
    { "step": 0, "name": "project-setup", "status": "pending" },
    { "step": 1, "name": "core-types", "status": "pending" }
  ]
}
```

**불변 필드**(canonical plan hash 대상 — 승인 후 바꾸면 실행이 막힌다):
`project`, `phase`, `baseBranch`, `designDoc`, `allowedPaths`, `testCommand`, `reviewExclude`(선택),
각 step의 `step`·`name`. 설계 문서 1개와 열거된 모든 `step{N}.md`의 bytes도 hash에 들어간다.

- `allowedPaths`: 구현 Claude가 쓸 수 있는 source/test 경로만. `dir/`는 하위 전체, 그 외는 그
  파일 하나. `phases/`·`scripts/`·`.claude/`·`.codex/`·`.git/`·`.harness/`·
  `docs/superpowers/specs/`·`CLAUDE.md` 등 보호 경로와 겹치면 manifest가 거부한다.
- `testCommand`: candidate SHA에서 sandbox 안에서 실행할 전체 테스트 argv.
- `reviewExclude`(선택): `[{ "glob": "fixtures/*", "reason": "..." }]` — reason 필수.
- 계획 파일은 regular file만 허용한다(symlink·hardlink·symlink 상위 디렉터리, 누락·추가
  `step*.md`, 비연속 번호 거부).

**가변 필드**(hash 제외, schema로 제한, 하네스만 쓴다): phase `status`·`review_reason`·
`review_at`·`created_at`·`completed_at`·`reviewBaseSha`, step `status`·`summary`·`started_at`·
`completed_at`·`failed_at`·`blocked_at`·`error_message`·`blocked_reason`. 그 밖의 키는 거부된다.

`phases/index.json`(top-level, `{"phases": [{"dir": ..., "status": ...}]}`)은 하네스가 상태를 갱신한다.

#### D-2. `phases/{task-name}/step{N}.md` (각 step마다 1개)

```markdown
# Step {N}: {이름}

> 예상 소요: {분}분 (빌드 {n}회 · 서버 {n}회) — 20분을 넘으면 나눈다

## 읽어야 할 파일

먼저 아래 파일들을 읽고 프로젝트의 아키텍처와 설계 의도를 파악하라:

- `/docs/ARCHITECTURE.md`
- `/docs/ADR.md`
- {이전 step에서 생성/수정된 파일 경로}

이전 step에서 만들어진 코드를 꼼꼼히 읽고, 설계 의도를 이해한 뒤 작업하라.

## 작업

{구체적인 구현 지시. 파일 경로, 클래스/함수 시그니처, 로직 설명을 포함.
코드 스니펫은 인터페이스/시그니처 수준만 제시하고, 구현체는 에이전트에게 맡겨라.
단, 설계 의도에서 벗어나면 안 되는 핵심 규칙은 명확히 박아넣어라.}

## Acceptance Criteria

```bash
./.venv/bin/python -m pytest -q   # 예: 프로젝트의 실제 검증 명령
```


## 검증 절차

1. 위 AC 커맨드를 실행한다.
2. CLAUDE.md CRITICAL 규칙·ARCHITECTURE·ADR을 벗어나지 않았는지 확인한다.
3. 하네스가 프롬프트에 준 `RESULT_FILE`에 결과 JSON을 쓴다(index.json은 건드리지 않는다):
   - 성공 → `{"status": "completed", "summary": "산출물 한 줄 요약"}`
   - 3회 시도 후 실패 → `{"status": "error", "error_message": "..."}`
   - 사용자 개입 필요 → `{"status": "blocked", "blocked_reason": "..."}`
4. git commit을 하지 않는다 — 하네스가 allowedPaths diff를 검증한 뒤 커밋한다.

## 금지사항

- {이 step에서 하지 말아야 할 것. "X를 하지 마라. 이유: Y" 형식}
- 기존 테스트를 깨뜨리지 마라
```

---

### E. 실행 (외부 runner만)

명령은 모두 고정 실행기 `./.venv/bin/python scripts/harness.py`를 거친다. `/usr/bin/python3`(3.9)나
repo 밖 interpreter는 거부된다. 승인자·승인 thread·issue key 규칙·리뷰 model은 하네스 root의 `.harness/policy.json`이 정한다.
evidence 경로(`<E>`)는 repo 밖 회사 경로다
(예: `<회사 evidence root>/<repo>` — 호스트 경로는 문서·코드에 고정하지 않는다).

```bash
export HARNESS_REVIEW_BACKEND=codex HARNESS_REVIEW_MODEL=gpt-6-astra
H="./.venv/bin/python scripts/harness.py"

# 1) 계획 세션 (thread 상태: .harness/runtime/<thread>.json, gitignored)
$H plan-session start  --thread-id <T> --request-message-id <M> --prompt-file req.txt
$H plan-session begin-post    --thread-id <T> --outbound-hash <H>   # 게시 직전(본문 출력)
$H plan-session record-posted --thread-id <T> --outbound-hash <H> --discord-message-id <D>
$H plan-session resume --thread-id <T> --message-id <M2> --prompt-file answer.txt
$H plan-session record-agreement --thread-id <T> --message-id <AGREE>
$H plan-session materialize --thread-id <T> --task <task> --output-json /tmp/mat.json
git add docs/superpowers/specs phases/<task> && git commit -m "docs(<task>): plan"

# 2) 계획 리뷰 — 0 clean / 4 findings(자동 수정 없음) / 2 실패 / 1 target preflight
$H review-plan <task> --issue <ISSUE> --repo-root <CLONE> --evidence-dir <E>

# 3) 구현 승인 — 별도 메시지, exact 본문
$H plan-session record-approval --thread-id <T> --message-id <APPROVE> \
   --approver-user-id <U> --plan-commit <SHA40> --body-file approve.txt \
   --task <task> --issue <ISSUE> --evidence-dir <E>

# 4) 외부 runner home(<RH>, repo 밖): reviewed runner 코드 export + control pin
$H runner export --harness-repo <HARNESS> --commit <ASTRA_REVIEWED_SHA> --dest <RH>/scripts
#   (<RH>/.venv는 bootstrap_venv.py로 승인 interpreter에서 만든다)
#   <RH>/.harness/policy.json(+선택 policy.local.json)도 둔다 — runner home도 하네스 설치 root라
#   승인자·thread·issue key·리뷰 model을 그 policy에서만 읽는다(없거나 틀리면 거부).
RP="<RH>/.venv/bin/python <RH>/scripts/runner.py"
$RP pin-control --clone <CLONE> --reviewed-commit <PLAN_SHA40> \
   --harness-repo <HARNESS> --harness-commit <ASTRA_REVIEWED_SHA> --out <RH>/control-pin.json
$RP prepare --task <task> --evidence-dir <E> --approval-sha <SHA64> --repo-root <CLONE> \
   --output-dir <OUT> --descriptor-out <RH>/launch.json --control-pin <RH>/control-pin.json
$RP probe --descriptor <RH>/launch.json --repo-root <CLONE>
$RP launch --descriptor <RH>/launch.json --repo-root <CLONE> --base main
$RP verify-final --descriptor <RH>/launch.json --repo-root <CLONE>
```

#### 게이트 요약

| 단계 | 막는 조건 | 결과 |
|---|---|---|
| plan-session | 동시 호출(lock), 중복 message ID, inflight 잔존, timeout/비정상 종료, session_id 변경, 합의 전 docs/phases diff, grilling 미설치·미호출 | 거부(1/4/5) 또는 `recovery-required`(3) |
| review-plan | backend≠codex·model≠gpt-6-astra, 누락·손상·degraded·schema/model/hash 불일치, 리뷰 중 계획 변경, timeout | 2(실패)·4(findings) |
| record-approval | 승인자/thread 불일치, 본문 exact 불일치, 합의·대화 message 재사용, 승인 message 재결속, HEAD≠plan commit, dirty plan, 최신 clean review 아님 | 거부 |
| supervisor `launch` | runner 코드≠reviewed pin, clone control≠reviewed commit pin, pin·descriptor 쓰기 가능·repo 안, 정책 미명시, base≠main, 승인 검증 실패; 실행 뒤 main·다른 ref·config·hooks·branch 변경, final 불일치 | 1(사전)·3(사후, final 폐기) |
| execute preflight | supervisor ticket 없음·재사용·만료, descriptor 문제, `--push`, `HARNESS_NO_GIT`, main·detached·패턴 밖 branch, linked worktree·다른 clone, 승인 session 결속 없음, 이 승인의 최초 실행인데 HEAD≠plan commit(승인별 start marker), index `reviewBaseSha`≠승인 기준, 계획 drift, dirty tree | 종료코드 1·2, step 0 전 |
| 매 Claude 호출·테스트·리뷰·finalize | 계획 hash·승인·control·profile·git metadata(HEAD/config/hooks/다른 ref) 변경, 에이전트의 직접 commit, allowedPaths 밖 변경 | `needs-review`(3) |
| 테스트·리뷰 | 에이전트·테스트 프로세스 그룹 미종료, 실행 뒤 HEAD·control 변경, testCommand 실패, 빈 리뷰 범위, 리뷰 누락·degraded·형식/모델/reviewed_head 불일치, critical, 수정 후 major 잔존 | `needs-review`(3) |

#### execute가 하는 것

- step prompt는 승인 **snapshot**에서 만든다(worktree 계획을 바꿨다 복원해도 실행 입력 불변).
- 구현 Claude: `/usr/bin/sandbox-exec -f <profile> claude -p --dangerously-skip-permissions ...`.
  profile은 deny-default이고 allowedPaths·출력 디렉터리·Claude 최소 metadata(`~/.claude/*`,
  `~/.claude.json*`, Caches/claude-cli-nodejs)만 쓰기 허용 — `/private/tmp` 같은 공용 경로는 없다
  (TMPDIR=<OUT>/tmp). 출력 디렉터리가 clone·sibling repo·보호 경로와 겹치면 거부한다.
  에이전트·테스트가 끝나면(성공·실패·시간 초과·중단) **하네스가 만든 프로세스 그룹만** 끄고,
  그룹이 남으면 막는다. 그 뒤 commit/test/review 전에 HEAD 불변·git metadata·branch·control·
  profile 불변과 allowedPaths 밖 변경 없음을 다시 확인한다(fail closed). 시스템 전체 PID 스캔이나
  다른 프로세스에 대한 개별 kill은 하지 않는다.
- 출력 디렉터리(<OUT>)는 **에이전트가 쓸 수 있으므로 신뢰하지 않는다**: 하네스는 거기에 쓰지 않고
  (`step*-output.json`은 `<E>/<task>/outputs/`), 결과 파일은 디렉터리 fd + `O_NOFOLLOW`로
  regular·nlink 1·1MiB 이하만 읽고, 지우기는 링크를 따라가지 않으며 `tmp/`는 매번 새로 만든다.
  `.git/`·`phases/`·`scripts/`·`.claude/`·`.codex/`·`CLAUDE.md`·evidence·원본 템플릿은 deny.
- step 결과는 `RESULT_FILE`(출력 디렉터리)로 받고 index.json은 하네스가 갱신한다.
- 커밋: 허용 경로 코드 → `feat(...)`, index → `chore(...)`(hook 비활성). 에이전트 커밋은 거부.
- 모든 step 뒤 **candidate commit**(`chore(...): mark phase completed`) → 그 SHA에서 sandbox 안
  `testCommand` → codex gpt-6-astra 리뷰(묶음 ≤3,000줄, 넘으면 분할 + 교차 리뷰).
- major/minor → 수정 Claude(sandbox) → 하네스가 `fix(...)` 커밋 → 새 HEAD로 테스트·재리뷰
  (1차 때 고정한 `reviewBaseSha`·`reviewExclude` 사용, 바뀌면 `needs-review`).
- PASS 뒤에는 파일·commit을 만들지 않는다. `<E>/<task>/final.json`에
  tested = reviewed = HEAD를 기록한다. **push하지 않는다.**
- 리뷰 산출물(`review-manifest.json`·`review.json`·`review.md`·`review-record-*.json`·
  `tests-*.json`)은 `<E>/<task>/code-review/`에 쓴다 — repo SHA를 바꾸지 않는다.

#### MVP 신뢰 가정 (amendment, 2026-11-22)

- Claude Code·Codex CLI는 운영자(operator)가 선택한 **신뢰한 개발 에이전트**다. 실수·시간 초과·일반적인
  background child는 그룹 정리로 끝내고, 이후 Git·파일·SHA 불변 검증이 실패를 막는다.
- 적대적 에이전트가 프로세스 그룹을 의도적으로 벗어나는 경우(setsid·환경 삭제·double fork·
  launchd/XPC/Mach 경유 생성)의 격리는 **주장하지 않는다** — production-hardening 범위로 보류.
  private macOS API(`sandbox_check` 등)·시스템 전체 PID 스캔은 쓰지 않는다.
- sandbox profile의 쓰기 경계(허용 경로·출력 디렉터리·Claude 최소 metadata만, main·원본·evidence·
  sibling repo deny)와 에이전트 출력의 symlink/hardlink 안전 처리는 그대로 유지한다.

#### 복구

- **recovery-required**(plan-session 종료코드 3): 자동 재전송·재게시 없음. Claude session
  transcript 또는 Discord 스레드를 대조한 뒤
  `plan-session resolve-recovery --operator ryan --reason "..." --evidence-id <근거>`
  (`--requeue`: 미전달 message 재전송 허용, `--posted-message-id`: 이미 게시된 응답 결속,
  `--session-id`: transcript에서 찾은 session 복구). 해제는 `.harness/runtime/recovery-log.jsonl`에
  append-only로 남는다. session을 복구할 수 없으면 상태가 `abandoned`가 되고 새 `start`가 가능하다.
- **needs-review**(execute 종료코드 3): `<E>/<task>/code-review/review.md`와 index.json
  `review_reason`을 보고 해결한 뒤 phase `status`를 되돌려 재개한다. 계획 자체를 바꿔야 하면
  새 계획 커밋 → Astra 재리뷰 → 새 승인 메시지 순서로만 갱신한다.
- **step error/blocked/시간 초과**: 계획 분할이 필요하면 역시 재리뷰·재승인. 단순 재시도는
  step `status`를 `pending`으로 되돌리고 `error_message`·`failed_at`을 지운다.

---

### F. 하네스 설치·업데이트 (`harness.py init`)

하네스 자체 파일(managed: `scripts/`, `.claude/commands/`, `.claude/skills/`, `.codex/`, `templates/project/`,
`harness-manifest.json` 등)은 직접 고치지 않는다. 설치·검증·갱신·복구는 installer만 한다
(소유권·종료코드 상세: 하네스 source의 README).

```bash
H="./.venv/bin/python scripts/harness.py"
$H init --target . --check                  # 0 ok / 1 무결성 / 3 recover 필요 / 4 merge-needed
$H init --target . --profile ui             # profile 확장(새 seed만 생성, 기존 seed·adopted 보존)
$H init --target . --update --from-distribution <새 하네스 checkout> --dry-run
$H init --target . --update --from-distribution <새 하네스 checkout>   # 필요 시 --adopt-merged·--accept-managed-removal·--adopt-managed
$H init --target . --recover --transaction <id>   # 중단된 transaction 복구 뒤 --check
```

- 크래시로 target의 installer 파일이 섞여 실행되지 않으면 새 distribution checkout의 installer로
  같은 `--target … --recover --transaction <id>`를 실행한다(transaction 기록은 자기완결).

- merge-required(`CLAUDE.md`·`.gitignore`·`.claude/settings.json`)는 자동 교체하지 않는다. 하네스 블록·
  필수 줄·hook/permission을 수동 병합한 뒤 `--adopt-merged <path>`.
- seed(`docs/PRD.md`·`docs/UI_GUIDE.md`·`phases/index.json`·`.harness/policy.json`)는 프로젝트 소유다.
