# 프로젝트: {프로젝트명}

{이 프로젝트의 목적·기술 스택·고유 규칙을 여기에 적는다. 아래 harness 블록 밖은 프로젝트가 소유한다.}

<!-- harness:begin -->
## 하네스 계약 (Discord↔Claude 하네스 모드)

이 블록은 하네스가 요구하는 최소 규칙이다(merge-required). `harness.py init --check`가 아래
marker와 문장을 확인한다 — 지우거나 바꾸면 check·update가 `merge-needed`로 멈춘다.

- 실행 모드는 **하네스 모드 하나**다. SDD(`subagent-driven-development`) 경로로 라우팅하지 마라.
- 계획 대화는 `scripts/plan_session.py`가 read-only Claude 세션(`--permission-mode plan`)으로
  돌린다. 합의 전 파일 작성·구현 금지.
- 계획 합의 메시지와 구현 승인 메시지는 **별개**다. 승인 본문은 정확히
  `APPROVE <ISSUE> PLAN <40자 commit SHA> REVIEW <64자 review-record SHA>`.
- 승인자·승인 thread·issue key 규칙·리뷰 model은 `.harness/policy.json`이 유일한 입력이다.
  secret(토큰·비밀번호)을 넣지 마라. 호스트 전용 값은 커밋하지 않는 `.harness/policy.local.json`.
- git checkout·add·commit은 하네스(외부 runner)만 한다. 자동 branch 전환, `--push`,
  `HARNESS_NO_GIT`, 리뷰 backend 폴백은 없다(명시적으로 거부한다).
- 권한 우회(`--dangerously-skip-permissions`)는 `execute.py`의 구현·리뷰 수정 Claude에만 있고
  항상 sandbox-exec deny-default profile 안에서 돈다.
- 모든 운영 명령은 고정 실행기 `./.venv/bin/python scripts/harness.py`를 거친다.
- 하네스 managed 파일(`scripts/`, `.claude/commands/`, `.claude/skills/`, `.codex/`,
  `templates/project/`, `harness-manifest.json` 등)은 직접 고치지 마라. 갱신은
  `./.venv/bin/python scripts/harness.py init --target . --update --from-distribution <새 checkout>`.
- 흐름 상세·복구 절차는 `.claude/commands/harness.md`.
<!-- harness:end -->
