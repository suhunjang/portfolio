#!/usr/bin/env python3
"""하네스 고정 실행기 — 모든 운영 명령의 단일 진입점.

Usage: ./.venv/bin/python scripts/harness.py <command> [args...]

  check          실행 환경(Python >=3.10, repo-local .venv)·.harness/policy.json 상태 확인
  bootstrap      .venv 생성/검증 (bootstrap_venv.py)
  init           target 프로젝트 설치·check·update·recover (project_init.py)
  plan-session   Discord↔Claude 계획 세션 (plan_session.py)
  review-plan    Codex gpt-6-astra 계획 리뷰 (review_plan.py)
  approval       구현 승인 검증 (approval.py)
  runner         외부 runner 계약·sandbox profile (runner.py)
  execute        승인된 계획 실행 (execute.py — launch descriptor 필수)

3.9에서도 파싱되어야 한다 — 3.10+ 문법 금지.
"""
import json
import os
import subprocess
import sys
from pathlib import Path

# 설치기 경로(init --check·--dry-run)는 target·distribution에 어떤 파일도 남기지 않는다 —
# 하네스 모듈 import가 scripts/__pycache__를 쓰지 않게 한다.
sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parent))
import runtime  # noqa: E402

SCRIPTS = Path(__file__).resolve().parent
COMMANDS = {
    "bootstrap": "bootstrap_venv.py",
    "init": "project_init.py",
    "plan-session": "plan_session.py",
    "review-plan": "review_plan.py",
    "approval": "approval.py",
    "runner": "runner.py",
    "execute": "execute.py",
}


def policy_status():
    """하네스 root의 .harness/policy.json 상태: ok·incomplete·missing·invalid."""
    path = runtime.REPO_ROOT / runtime.POLICY_REL
    out = {"path": str(path)}
    if not os.path.lexists(str(path)):
        out["status"] = "missing"
        return out
    try:
        pol = runtime.read_policy(runtime.REPO_ROOT)
    except runtime.PolicyError as e:
        out.update(status="invalid", detail=str(e))
        return out
    empty = [k for k, v in (("approverUserIds", pol.approver_user_ids),
                            ("approvalThreadIds|issueScopedThreads",
                             pol.approval_thread_ids or tuple(pol.issue_scoped_threads)))
             if not v]
    out.update(status="incomplete" if empty else "ok", reviewModel=pol.review_model)
    if empty:
        out["detail"] = "비어 있음: %s — 승인은 거부된다(fail closed)" % ", ".join(empty)
    return out


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    # bootstrap만 런타임 검사 전에 허용한다(.venv를 만드는 명령이므로).
    if argv and argv[0] == "bootstrap":
        return subprocess.call([sys.executable, str(SCRIPTS / COMMANDS["bootstrap"])] + argv[1:])
    runtime.require_runtime()
    if not argv:
        print(__doc__)
        return 2
    cmd, rest = argv[0], argv[1:]
    if cmd == "check":
        ev = runtime.runtime_evidence()
        ev["policy"] = policy_status()
        print(json.dumps(ev, ensure_ascii=False))
        if ev["policy"]["status"] in ("missing", "incomplete"):
            print("WARNING: policy %s — %s" % (ev["policy"]["status"],
                                                ev["policy"].get("detail") or ev["policy"]["path"]),
                  file=sys.stderr)
        return 1 if ev["policy"]["status"] == "invalid" else 0
    if cmd not in COMMANDS:
        print("ERROR: 알 수 없는 명령 %r. 허용: check, %s" % (cmd, ", ".join(COMMANDS)),
              file=sys.stderr)
        return 2
    return subprocess.call([sys.executable, str(SCRIPTS / COMMANDS[cmd])] + rest)


if __name__ == "__main__":
    sys.exit(main())
