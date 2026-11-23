"""E. execute — 외부 descriptor·승인 결속·sandbox 구현·Astra 코드 리뷰 게이트 (E2E).

실제 spawn: 가짜 claude/codex 실행파일 + 실제 /usr/bin/sandbox-exec. 원격 호출 없음.
"""
import json
import os
import subprocess
import sys
import textwrap
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent))
import approval as ap  # noqa: E402
import execute as ex  # noqa: E402
import plan_manifest as pm  # noqa: E402
import plan_session as ps  # noqa: E402
import review_plan as rp  # noqa: E402
import runner as rn  # noqa: E402
from conftest import (FIXTURE_APPROVER, FIXTURE_THREAD, git, make_plan,  # noqa: E402
                      write_policy)

pytestmark = pytest.mark.skipif(not Path(rn.SANDBOX_EXEC).exists(), reason="sandbox-exec 없음")

REPO_SCRIPTS = Path(__file__).resolve().parent
VENV_PY = REPO_SCRIPTS.parent / ".venv" / "bin" / "python"
# conftest의 가짜 fixture policy ID(실제 운영 ID 아님)
THREAD, USER = FIXTURE_THREAD, FIXTURE_APPROVER
SID = "11111111-2222-3333-4444-555555555555"
BRANCH = "feat/DEMO-74/demo"

FAKE_CLAUDE = textwrap.dedent("""\
    #!/bin/sh
    # 가짜 구현 Claude — sandbox 안에서 실행된다.
    prompt=$(cat)
    printf '%s\\n' "$*" >> "$FAKE_LOG"
    res=$(printf '%s\\n' "$prompt" | sed -n 's/^RESULT_FILE: //p' | head -1)
    step=$(printf '%s\\n' "$prompt" | sed -n 's/^STEP_NUMBER: //p' | head -1)
    # 보호 경로 쓰기 시도(sandbox가 막아야 한다)
    echo evil >> phases/demo/step1.md 2>/dev/null
    echo evil >> CLAUDE.md 2>/dev/null
    git commit --allow-empty -qm sneaky 2>/dev/null
    mkdir -p src
    if [ -n "$FAKE_LINGER" ]; then
      ( sleep 1; echo "LINGER = 1" >> src/step0.py ) &
    fi
    if [ -n "$step" ]; then
      if [ "$step" != "$FAKE_SKIP_FILE" ]; then echo "VALUE_$step = $step" > "src/step$step.py"; fi
      status=${FAKE_STEP_STATUS:-completed}
      printf '{"status":"%s","summary":"step %s done","error_message":"e","blocked_reason":"b"}' \\
        "$status" "$step" > "$res"
      if [ "$FAKE_ATTACK" = "result-symlink" ]; then rm -f "$res"; ln -s "$FAKE_EXT" "$res"; fi
    else
      echo "# fixed" >> src/step0.py
      printf '{"status":"%s","ac":"tests ok"}' "${FAKE_FIX_STATUS:-passed}" > "$res"
    fi
    echo '{"type":"result","result":"ok"}'
""")

FAKE_CODEX = textwrap.dedent("""\
    #!/bin/sh
    prompt=$(cat)
    printf '%s\\n' "$*" >> "$FAKE_CODEX_LOG"
    head=$(printf '%s\\n' "$prompt" | sed -n 's/^REVIEWED_HEAD: //p' | head -1)
    mode=${FAKE_REVIEW:-clean}
    if [ "$mode" = "major-once" ]; then
      if [ -f "$FAKE_STATE" ]; then mode=clean; else touch "$FAKE_STATE"; mode=major; fi
    fi
    case "$mode" in
      garbage) echo "I think it is fine"; exit 0;;
      fail) exit 1;;
      degraded) printf '{"status":"degraded","reason":"too big","reviewed_head":"%s","review_model":"gpt-6-astra","findings":[]}' "$head";;
      wronghead) printf '{"status":"complete","reviewed_head":"%s","review_model":"gpt-6-astra","findings":[]}' "0000000000000000000000000000000000000000";;
      wrongmodel) printf '{"status":"complete","reviewed_head":"%s","review_model":"gpt-5","findings":[]}' "$head";;
      critical) printf '{"status":"complete","reviewed_head":"%s","review_model":"gpt-6-astra","findings":[{"severity":"critical","file":"src/step0.py","line":1,"title":"bad","detail":"d"}]}' "$head";;
      major) printf '{"status":"complete","reviewed_head":"%s","review_model":"gpt-6-astra","findings":[{"severity":"major","file":"src/step0.py","line":1,"title":"fixme","detail":"d"}]}' "$head";;
      *) printf '{"status":"complete","reviewed_head":"%s","review_model":"gpt-6-astra","findings":[]}' "$head";;
    esac
""")


def _review_runner(repo):
    def run(argv, *, input, cwd, timeout, kill_grace=30):
        obj = {"task": "demo", "review_backend": "codex", "review_model": "gpt-6-astra",
               "reviewed_plan_sha": pm.build_manifest(repo, "demo").sha,
               "verdict": "clean", "findings": []}
        return ex.AgentRun(0, json.dumps(obj), "", False)
    return run


def _make_harness_repo(base):
    """현재 scripts의 runner 코드로 'Astra-reviewed harness commit'을 흉내 낸다."""
    h = base / "harness"
    (h / "scripts").mkdir(parents=True)
    for name in rn.RUNNER_FILES:
        (h / "scripts" / name).write_bytes((REPO_SCRIPTS / name).read_bytes())
    git(h, "init", "-q", "-b", "main")
    git(h, "config", "user.email", "t@e.com")
    git(h, "config", "user.name", "T")
    git(h, "add", "-A")
    git(h, "commit", "-q", "-m", "reviewed harness")
    return h, git(h, "rev-parse", "HEAD")


class World:
    def __init__(self, tmp_path, monkeypatch, **plan_extra):
        base = Path(os.path.realpath(tmp_path))
        self.base = base
        self.repo = base / "repo"
        self.repo.mkdir()
        r = self.repo
        git(r, "init", "-q", "-b", "main")
        git(r, "config", "user.email", "t@e.com")
        git(r, "config", "user.name", "T")
        (r / ".gitignore").write_text(".harness/\n__pycache__/\n", encoding="utf-8")
        (r / "CLAUDE.md").write_text("# rules\n", encoding="utf-8")
        (r / "README.md").write_text("readme\n", encoding="utf-8")
        git(r, "add", "-A")
        git(r, "commit", "-q", "-m", "init")
        self.main_sha = git(r, "rev-parse", "main")
        git(r, "checkout", "-q", "-b", BRANCH)
        plan_extra.setdefault(
            "testCommand", ["/bin/sh", "-c", "test -f src/step0.py && test -f src/step1.py"])
        make_plan(r, **plan_extra)
        git(r, "add", "-A")
        git(r, "commit", "-q", "-m", "docs: plan")
        self.plan_commit = git(r, "rev-parse", "HEAD")
        self.ev = base / "evidence"
        self.ev.mkdir()
        self.out = base / "out"
        self.rt = base / "runtime"
        s = ps.Session(r, self.rt, THREAD)
        st = ps._new_state(THREAD)
        st.update(status="idle", sessionId=SID, turns=3, grillingInvoked=True,
                  agreementMessageId="agree-1", processedMessageIds=["m1", "m2"])
        self.rt.mkdir()
        s._save(st)
        code, _, review_sha = rp.run_review(r, "demo", self.ev, "DEMO-74", runner=_review_runner(r))
        assert code == 0
        body = f"APPROVE DEMO-74 PLAN {self.plan_commit} REVIEW {review_sha}"
        self.approval_sha = ap.record_approval(
            session=s, repo=r, task="demo", issue="DEMO-74", message_id="appr-1", user_id=USER,
            body=body, plan_commit=self.plan_commit, evidence_dir=self.ev)["recordSha"]
        # 외부 runner home: Astra-reviewed harness commit에서 export한 코드 + 고정 pin
        self.harness, self.harness_commit = _make_harness_repo(base)
        self.runner_home = base / "runnerhome"
        rn.export_runner(self.harness, self.harness_commit, self.runner_home / "scripts")
        (self.runner_home / ".venv").symlink_to(REPO_SCRIPTS.parent / ".venv")
        # runner home도 하네스 설치 root다 — 자기 .harness/policy.json만 읽는다.
        write_policy(self.runner_home)
        self.pin = self.runner_home / "control-pin.json"
        rn.pin_control(r, self.plan_commit, self.harness, self.harness_commit, self.pin)
        self.desc = base / "runner" / "launch.json"
        rn.prepare("demo", self.ev, self.approval_sha, self.out, self.desc, control_pin=self.pin,
                   repo=r)
        bindir = base / "bin"
        bindir.mkdir()
        for name, body in (("claude", FAKE_CLAUDE), ("codex", FAKE_CODEX)):
            (bindir / name).write_text(body, encoding="utf-8")
            (bindir / name).chmod(0o755)
        self.claude_log = self.out / "claude.log"  # sandbox 안에서 쓸 수 있는 유일한 곳
        self.codex_log = base / "codex.log"
        self.env = {
            "PATH": f"{bindir}:{os.environ['PATH']}",
            "FAKE_LOG": str(self.claude_log), "FAKE_CODEX_LOG": str(self.codex_log),
            "FAKE_STATE": str(base / "review-state"),
            "HARNESS_REVIEW_BACKEND": "codex", "HARNESS_REVIEW_MODEL": "gpt-6-astra",
        }
        for k in [k for k in os.environ if k.startswith(("HARNESS_", "FAKE_"))]:
            monkeypatch.delenv(k)
        for k, v in self.env.items():
            monkeypatch.setenv(k, v)

    def run_cli(self, *extra, env=None, drop=(), runner_home=None):
        """외부 supervisor(runner launch)로 실행한다 — 운영 경로."""
        home = runner_home or self.runner_home
        e = dict(os.environ)
        e.update(env or {})
        for k in drop:
            e.pop(k, None)
        return subprocess.run([str(home / ".venv/bin/python"), str(home / "scripts/runner.py"),
                               "launch", "--descriptor", str(self.desc),
                               "--repo-root", str(self.repo), *extra],
                              capture_output=True, text=True, env=e, timeout=300)

    def run_execute_direct(self, *extra, env=None):
        """supervisor 없이 execute.py를 직접 띄운다(거부돼야 한다)."""
        e = dict(os.environ, HARNESS_LAUNCH_DESCRIPTOR=str(self.desc))
        e.update(env or {})
        return subprocess.run([str(VENV_PY), str(self.runner_home / "scripts" / "execute.py"),
                               "demo", "--repo-root", str(self.repo), *extra],
                              capture_output=True, text=True, env=e, timeout=300)

    def claude_calls(self):
        return self.claude_log.read_text().splitlines() if self.claude_log.exists() else []

    def codex_calls(self):
        return self.codex_log.read_text().splitlines() if self.codex_log.exists() else []

    def head(self):
        return git(self.repo, "rev-parse", "HEAD")

    def index(self):
        return json.loads((self.repo / "phases/demo/index.json").read_text())

    def final(self):
        p = self.ev / "demo" / "final.json"
        return json.loads(p.read_text()) if p.exists() else None


@pytest.fixture
def w(tmp_path, monkeypatch):
    return World(tmp_path, monkeypatch)


class TestDirectEntryFailsClosed:
    def test_no_descriptor(self, w):
        e = dict(os.environ)
        e.pop("HARNESS_LAUNCH_DESCRIPTOR", None)
        r = subprocess.run([str(VENV_PY), str(w.runner_home / "scripts" / "execute.py"),
                            "demo", "--repo-root", str(w.repo)], capture_output=True,
                           text=True, env=e)
        assert r.returncode == 1 and "descriptor" in (r.stdout + r.stderr)
        assert w.claude_calls() == []

    def test_direct_execute_without_supervisor_ticket(self, w):
        r = w.run_execute_direct()
        assert r.returncode == 1 and "ticket" in (r.stdout + r.stderr)
        assert w.claude_calls() == []

    def test_push_flag_rejected(self, w):
        r = w.run_cli("--push")
        assert r.returncode == 2 and "--push" in (r.stdout + r.stderr)
        assert w.claude_calls() == []

    def test_no_git_rejected(self, w):
        r = w.run_cli(env={"HARNESS_NO_GIT": "1"})
        assert r.returncode == 1 and "HARNESS_NO_GIT" in (r.stdout + r.stderr)
        assert w.claude_calls() == []

    @pytest.mark.parametrize("env,drop", [
        ({}, ("HARNESS_REVIEW_BACKEND",)),
        ({"HARNESS_REVIEW_BACKEND": "claude"}, ()),
        ({}, ("HARNESS_REVIEW_MODEL",)),
        ({"HARNESS_REVIEW_MODEL": "gpt-5"}, ()),
        ({"HARNESS_IMPL_BACKEND": "codex"}, ()),
    ])
    def test_review_policy_required(self, w, env, drop):
        r = w.run_cli(env=env, drop=drop)
        assert r.returncode == 1
        assert w.claude_calls() == []

    def test_writable_descriptor_rejected(self, w):
        w.desc.chmod(0o644)
        r = w.run_cli()
        assert r.returncode == 1 and w.claude_calls() == []

    def test_task_mismatch_rejected(self, w):
        r = subprocess.run([str(VENV_PY), str(w.runner_home / "scripts" / "execute.py"), "other",
                            "--repo-root", str(w.repo)], capture_output=True, text=True,
                           env=dict(os.environ, HARNESS_LAUNCH_DESCRIPTOR=str(w.desc)))
        assert r.returncode == 1 and w.claude_calls() == []

    def test_control_change_rejected(self, w):
        (w.repo / "CLAUDE.md").write_text("# rules weakened\n", encoding="utf-8")
        git(w.repo, "commit", "-qam", "weaken")
        r = w.run_cli()
        assert r.returncode == 1 and w.claude_calls() == []

    def test_wrong_branch_no_auto_checkout(self, w):
        git(w.repo, "checkout", "-q", "-b", "feat/DEMO-74/other")
        r = w.run_cli()
        assert r.returncode == 1
        assert git(w.repo, "rev-parse", "--abbrev-ref", "HEAD") == "feat/DEMO-74/other"
        assert w.claude_calls() == []

    def test_base_mismatch_rejected(self, w):
        r = w.run_cli("--base", "develop")
        assert r.returncode == 1 and w.claude_calls() == []

    def test_plan_change_after_approval_blocks_step0(self, w):
        p = w.repo / "phases/demo/step1.md"
        p.write_bytes(p.read_bytes() + b"!")
        r = w.run_cli()
        assert r.returncode == 1 and "계획" in (r.stdout + r.stderr)
        assert w.claude_calls() == []

    def test_first_run_head_must_be_plan_commit(self, w):
        (w.repo / "README.md").write_text("extra\n")
        git(w.repo, "commit", "-qam", "chore: extra")
        r = w.run_cli()
        assert r.returncode == 1 and w.claude_calls() == []

    def test_dirty_tree_rejected(self, w):
        (w.repo / "README.md").write_text("dirty\n")
        r = w.run_cli()
        assert r.returncode == 1 and w.claude_calls() == []


class TestHappyPath:
    def test_full_run(self, w):
        r = w.run_cli()
        assert r.returncode == 0, r.stdout[-3000:] + r.stderr[-2000:]
        calls = w.claude_calls()
        assert len(calls) == 2
        for c in calls:
            assert "--dangerously-skip-permissions" in c
        # 구현 Claude는 sandbox 안에서만: 보호 경로 쓰기 시도가 실패했다
        assert b"evil" not in (w.repo / "phases/demo/step1.md").read_bytes()
        assert "weakened" not in (w.repo / "CLAUDE.md").read_text()
        assert "sneaky" not in git(w.repo, "log", "--format=%s")
        assert (w.repo / "src/step0.py").exists() and (w.repo / "src/step1.py").exists()
        idx = w.index()
        assert [s["status"] for s in idx["steps"]] == ["completed", "completed"]
        assert idx["status"] == "completed"
        # tested = reviewed = HEAD, PASS 뒤 commit 없음
        fin = w.final()
        assert fin["testedSha"] == fin["reviewedSha"] == w.head()
        assert rn.verify_final(w.repo, w.ev / "demo/final.json") == w.head()
        assert git(w.repo, "status", "--porcelain", "--untracked-files=all") == ""
        log = git(w.repo, "log", "-1", "--format=%s")
        assert "mark phase completed" in log
        assert git(w.repo, "rev-parse", "main") == w.main_sha
        assert git(w.repo, "rev-parse", "--abbrev-ref", "HEAD") == BRANCH
        codex = w.codex_calls()
        assert codex and all("gpt-6-astra" in c and "read-only" in c for c in codex)
        # 리뷰 evidence는 repo 밖
        assert list((w.ev / "demo/code-review").glob("review-record-*.json"))
        assert not list((w.repo / "phases/demo").glob("review*"))

    def test_resume_after_completion_is_noop_safe(self, w):
        assert w.run_cli().returncode == 0
        head = w.head()
        r = w.run_cli()
        # 재실행(resume)도 게이트를 다시 통과하고, 새 commit을 만들지 않는다
        assert r.returncode == 0, r.stdout[-2000:]
        assert w.head() == head
        assert w.final()["reviewedSha"] == head


class TestRunnerCli:
    """외부 runner CLI(probe·verify-final)를 실제 프로세스로 돌린다."""

    def _cli(self, w, *args):
        return subprocess.run([str(VENV_PY), str(w.runner_home / "scripts" / "runner.py"), *args,
                               "--descriptor", str(w.desc), "--repo-root", str(w.repo)],
                              capture_output=True, text=True, timeout=120)

    def test_probe_proves_boundary_with_real_profile(self, w):
        r = self._cli(w, "probe")
        assert r.returncode == 0, r.stdout + r.stderr
        res = json.loads((w.ev / "demo/runner/probe.json").read_text())
        assert res["ok"] and all(x["wrote"] for x in res["allowed"])
        denied = {Path(x["path"]).parent.name for x in res["denied"]}
        assert {"phases", "scripts", ".git", ".claude", ".codex"} <= denied
        assert not any(x["wrote"] for x in res["denied"])

    def test_verify_final_after_run(self, w):
        assert w.run_cli().returncode == 0
        r = self._cli(w, "verify-final")
        assert r.returncode == 0, r.stderr
        assert json.loads(r.stdout)["head"] == w.head()

    def test_verify_final_rejects_post_review_commit(self, w):
        assert w.run_cli().returncode == 0
        (w.repo / "src" / "late.py").write_text("x = 1\n")
        git(w.repo, "add", "-A")
        git(w.repo, "commit", "-qm", "post-review change")
        r = self._cli(w, "verify-final")
        assert r.returncode == 1 and "push 거부" in r.stderr


class TestReviewGate:
    @pytest.mark.parametrize("mode", ["garbage", "fail", "degraded", "wronghead",
                                      "wrongmodel", "critical"])
    def test_review_failures_block(self, w, mode):
        r = w.run_cli(env={"FAKE_REVIEW": mode})
        assert r.returncode == 3, r.stdout[-2000:]
        assert w.index()["status"] == "needs-review"
        assert w.final() is None

    def test_findings_fixed_then_rereviewed_on_new_head(self, w):
        r = w.run_cli(env={"FAKE_REVIEW": "major-once"})
        assert r.returncode == 0, r.stdout[-3000:]
        fin = w.final()
        assert fin["testedSha"] == fin["reviewedSha"] == w.head()
        assert fin["reviewedSha"] != fin["candidateSha"]
        assert "fix(" in git(w.repo, "log", "-1", "--format=%s")
        assert len(w.codex_calls()) == 2

    def test_fix_failure_blocks(self, w):
        r = w.run_cli(env={"FAKE_REVIEW": "major", "FAKE_FIX_STATUS": "failed"})
        assert r.returncode == 3
        assert w.final() is None

    def test_failing_tests_block_before_review(self, w):
        r = w.run_cli(env={"FAKE_SKIP_FILE": "1"})
        assert r.returncode == 3, r.stdout[-2000:]
        assert w.index()["status"] == "needs-review"
        assert "테스트" in w.index()["review_reason"]
        assert w.codex_calls() == []
        assert w.final() is None

    def test_plan_review_failure_and_code_review_failure_independent(self, w):
        """계획 리뷰가 최신 실패로 바뀌면 execute 전에 막히고, 코드 리뷰 실패는 별도로 막힌다."""
        rp.run_review(w.repo, "demo", w.ev, "DEMO-74", runner=lambda *a, **k: ex.AgentRun(0, "x", "", False))
        r = w.run_cli()
        assert r.returncode == 1 and w.claude_calls() == []


class TestInProcessDrift:
    """실행 도중 계획 변경·git ref 변경을 주입한다(in-process)."""

    def _executor(self, w):
        d = rn.load_descriptor(w.desc, w.repo)
        return ex.StepExecutor("demo", descriptor=d)

    def test_plan_change_between_steps_blocks(self, w, monkeypatch):
        e = self._executor(w)
        real = e._commit_step

        def commit_then_tamper(n, name):
            real(n, name)
            if n == 0:
                p = w.repo / "phases/demo/step1.md"
                p.write_bytes(p.read_bytes() + b"tamper")
        monkeypatch.setattr(e, "_commit_step", commit_then_tamper)
        with pytest.raises(SystemExit) as exc:
            e.run()
        assert exc.value.code == 3
        assert len(w.claude_calls()) == 1
        assert w.final() is None

    def test_ref_change_during_agent_blocks(self, w, monkeypatch):
        e = self._executor(w)
        real = ex._run_agent_process

        def run_and_move(argv, **kw):
            res = real(argv, **kw)
            git(w.repo, "update-ref", "refs/heads/main", w.plan_commit)
            return res
        monkeypatch.setattr(ex, "_run_agent_process", run_and_move)
        with pytest.raises(SystemExit) as exc:
            e.run()
        assert exc.value.code == 3
        assert w.final() is None

    def test_control_change_mid_run_blocks(self, w, monkeypatch):
        e = self._executor(w)
        real = e._commit_step

        def commit_then_tamper(n, name):
            real(n, name)
            (w.repo / "CLAUDE.md").write_text("# no gates\n")
        monkeypatch.setattr(e, "_commit_step", commit_then_tamper)
        with pytest.raises(SystemExit) as exc:
            e.run()
        assert exc.value.code == 3

    def test_disallowed_change_not_committed(self, w, monkeypatch):
        """sandbox 밖 경로 변경이 생기면(이중 방어) 커밋하지 않고 막는다."""
        e = self._executor(w)
        real = ex._run_agent_process

        def run_and_escape(argv, **kw):
            res = real(argv, **kw)
            (w.repo / "README.md").write_text("escaped\n")
            return res
        monkeypatch.setattr(ex, "_run_agent_process", run_and_escape)
        with pytest.raises(SystemExit) as exc:
            e.run()
        assert exc.value.code == 3
        assert "escaped" not in git(w.repo, "show", "HEAD:README.md")

    def test_step_prompt_comes_from_snapshot(self, w, monkeypatch):
        """worktree 계획을 바꿨다 복원해도, 실행 입력은 승인 snapshot이다."""
        e = self._executor(w)
        prompts = []
        real = ex._run_agent_process

        def capture(argv, **kw):
            prompts.append(kw["input"])
            return real(argv, **kw)
        monkeypatch.setattr(ex, "_run_agent_process", capture)
        e.run()
        assert "작업 0" in prompts[0] and "작업 1" in prompts[1]
        assert all("STEP_NUMBER" in p and "RESULT_FILE" in p for p in prompts[:2])

    def test_no_commit_after_review_pass(self, w, monkeypatch):
        e = self._executor(w)
        heads = {}
        real_review = e._run_review

        def spy():
            real_review()
            heads["after_review"] = w.head()
        monkeypatch.setattr(e, "_run_review", spy)
        e.run()
        assert w.head() == heads["after_review"] == w.final()["reviewedSha"]


# ---------------------------------------------------------------------------
# Astra 리뷰 회귀 — 실행 단계 (B1·M1·M2·M4·M5)
# ---------------------------------------------------------------------------

class TestB1ExecutionBoundary:
    def test_execution_on_main_rejected(self, w):
        git(w.repo, "branch", "-f", "main", "HEAD")
        git(w.repo, "checkout", "-q", "main")
        r = w.run_cli()
        assert r.returncode == 1 and w.claude_calls() == []
        assert git(w.repo, "rev-parse", "main") == w.plan_commit

    def test_descriptor_for_other_clone_rejected(self, w, tmp_path):
        other = tmp_path / "other-clone"
        git(tmp_path, "clone", "-q", str(w.repo), str(other))
        r = subprocess.run([str(w.runner_home / ".venv/bin/python"),
                            str(w.runner_home / "scripts/runner.py"), "launch",
                            "--descriptor", str(w.desc), "--repo-root", str(other)],
                           capture_output=True, text=True)
        assert r.returncode == 1 and w.claude_calls() == []

    def test_linked_worktree_rejected(self, w, tmp_path):
        wt = tmp_path / "wt"
        git(w.repo, "worktree", "add", "-q", "-b", "feat/DEMO-74/wt", str(wt), "HEAD")
        r = subprocess.run([str(w.runner_home / ".venv/bin/python"),
                            str(w.runner_home / "scripts/runner.py"), "launch",
                            "--descriptor", str(w.desc), "--repo-root", str(wt)],
                           capture_output=True, text=True)
        assert r.returncode == 1 and w.claude_calls() == []


class TestM1ReviewBaseBound:
    def test_narrowed_review_base_rejected_before_steps(self, w):
        p = w.repo / "phases/demo/index.json"
        d = json.loads(p.read_text())
        d["reviewBaseSha"] = w.plan_commit  # 계획 commit 이후만 리뷰하도록 좁히기
        p.write_text(json.dumps(d))
        r = w.run_cli()
        assert r.returncode == 1 and "reviewBaseSha" in (r.stdout + r.stderr)
        assert w.claude_calls() == []

    def test_substitution_before_review_blocks(self, w, monkeypatch):
        """resume 전·실행 중 index의 reviewBaseSha를 HEAD로 바꿔도 리뷰는 승인된 기준을 쓰거나 막힌다."""
        e = ex.StepExecutor("demo", descriptor=rn.load_descriptor(w.desc, w.repo))
        real = e._make_candidate

        def tamper_then_candidate():
            p = w.repo / "phases/demo/index.json"
            d = json.loads(p.read_text())
            d["reviewBaseSha"] = w.head()
            p.write_text(json.dumps(d))
            real()
        monkeypatch.setattr(e, "_make_candidate", tamper_then_candidate)
        with pytest.raises(SystemExit) as exc:
            e.run()
        assert exc.value.code == 3
        assert "reviewBaseSha" in w.index()["review_reason"]
        assert w.codex_calls() == [] and w.final() is None

    def test_review_uses_approved_base(self, w):
        assert w.run_cli().returncode == 0
        rec = json.loads(next((w.ev / "demo/approvals").glob("*.json")).read_text())
        m = json.loads((w.ev / "demo/code-review/review-manifest.json").read_text())
        assert m["reviewBaseSha"] == rec["reviewBaseSha"] == w.main_sha

    def test_empty_review_range_blocks(self, tmp_path, monkeypatch):
        w = World(tmp_path, monkeypatch, reviewExclude=[{"glob": "*", "reason": "전부 제외"}])
        r = w.run_cli()
        assert r.returncode == 3, r.stdout[-2000:]
        assert "리뷰할 변경" in w.index()["review_reason"]
        assert w.final() is None


class TestM2Supervisor:
    def test_tampered_runner_code_refused_before_launch(self, w, tmp_path):
        evil = tmp_path / "evilhome"
        (evil / "scripts").mkdir(parents=True)
        for f in (w.runner_home / "scripts").iterdir():
            if f.is_file():
                (evil / "scripts" / f.name).write_bytes(f.read_bytes())
        ex_py = evil / "scripts/execute.py"
        ex_py.chmod(0o644)
        ex_py.write_text(ex_py.read_text() + "\n# gate removed\n")
        (evil / ".venv").symlink_to(REPO_SCRIPTS.parent / ".venv")
        write_policy(evil)  # 정책은 같게 두고 runner 코드 변조만으로 거부되는지 본다
        r = w.run_cli(runner_home=evil)
        assert r.returncode == 1 and "runner" in (r.stdout + r.stderr)
        assert w.claude_calls() == []

    def test_clone_control_drift_from_reviewed_pin_refused(self, w):
        (w.repo / "CLAUDE.md").write_text("# gates off\n")
        git(w.repo, "commit", "-qam", "weaken")
        r = w.run_cli()
        assert r.returncode == 1 and w.claude_calls() == []

    def test_pin_must_come_from_reviewed_commit(self, w):
        before = rn.control_sha_at_commit(w.repo, w.plan_commit)
        assert before == rn.control_sha(w.repo)
        (w.repo / ".claude").mkdir(exist_ok=True)
        (w.repo / ".claude/settings.json").write_text("{}")
        assert rn.control_sha(w.repo) != before  # 미커밋 control 추가도 pin과 달라진다
        r = w.run_cli()
        assert r.returncode == 1 and w.claude_calls() == []

    def test_writable_pin_refused(self, w):
        w.pin.chmod(0o644)
        r = w.run_cli()
        assert r.returncode == 1 and w.claude_calls() == []

    def test_ticket_cannot_be_reused(self, w):
        assert w.run_cli().returncode == 0
        tickets = sorted((w.ev / "demo/runner/tickets").glob("*.json"))
        assert len(tickets) == 1
        r = w.run_execute_direct(env={"HARNESS_LAUNCH_TICKET": str(tickets[0])})
        assert r.returncode == 1 and "ticket" in (r.stdout + r.stderr)

    def test_supervisor_detects_ref_tamper_by_child(self, w):
        def evil_spawn(argv, env):
            git(w.repo, "update-ref", "refs/heads/main", w.plan_commit)
            return 0
        code = rn.launch(w.desc, w.repo, base="main", spawn=evil_spawn,
                         runner_dir=w.runner_home / "scripts")
        assert code != 0
        assert w.final() is None

    def test_supervisor_runs_pinned_execute_not_repo_copy(self, w):
        argv_seen = []

        def spy(argv, env):
            argv_seen.append(argv)
            return 9
        rn.launch(w.desc, w.repo, base="main", spawn=spy, runner_dir=w.runner_home / "scripts")
        assert argv_seen and Path(argv_seen[0][1]) == w.runner_home / "scripts/execute.py"
        assert "--repo-root" in argv_seen[0]


class TestM4StartMarker:
    def test_legacy_task_marker_does_not_skip_first_run_check(self, w):
        legacy = w.ev / "demo/runs/started.json"
        legacy.parent.mkdir(parents=True)
        legacy.write_text(json.dumps({"planCommitSha": w.plan_commit}))
        (w.repo / "README.md").write_text("drift\n")
        git(w.repo, "commit", "-qam", "chore: drift")
        r = w.run_cli()
        assert r.returncode == 1 and w.claude_calls() == []

    def test_marker_written_per_approval(self, w):
        assert w.run_cli().returncode == 0
        m = json.loads((w.ev / f"demo/runs/{w.approval_sha}.json").read_text())
        assert m["approvalRecordSha"] == w.approval_sha and m["planCommitSha"] == w.plan_commit


class TestM5NoSurvivingDescendant:
    def test_lingering_writer_cannot_touch_tree_after_agent_exit(self, w):
        import time as _t
        r = w.run_cli(env={"FAKE_LINGER": "1"})
        assert r.returncode == 0, r.stdout[-3000:]
        _t.sleep(3)  # 살아남았다면 이 사이에 썼을 것이다
        assert "LINGER" not in (w.repo / "src/step0.py").read_text()
        assert git(w.repo, "status", "--porcelain", "--untracked-files=all") == ""
        assert w.final()["testedSha"] == w.final()["reviewedSha"] == w.head()

    def test_surviving_descendant_blocks(self, w, monkeypatch):
        e = ex.StepExecutor("demo", descriptor=rn.load_descriptor(w.desc, w.repo))

        def survive(argv, **kw):
            raise ex.DescendantSurvived("pid 1234")
        monkeypatch.setattr(ex, "_run_agent_process", survive)
        with pytest.raises(SystemExit) as exc:
            e.run()
        assert exc.value.code == 3
        assert "자손" in w.index()["review_reason"]


# ---------------------------------------------------------------------------
# Astra re-review B3 — 하네스는 에이전트가 심은 symlink/hardlink를 따라 쓰지 않는다
# ---------------------------------------------------------------------------

class TestB3TrustedWritesDoNotFollowAgentLinks:
    def _victim(self, w):
        v = w.base / "mainclone" / "victim.txt"
        v.parent.mkdir(exist_ok=True)
        v.write_bytes(b"MAIN CLONE CONTENT\n")
        return v

    @pytest.mark.parametrize("kind", ["symlink", "hardlink"])
    def test_planted_output_link_leaves_external_target_identical(self, w, kind):
        victim = self._victim(w)
        before = victim.read_bytes()
        for n in (0, 1):
            p = w.out / f"step{n}-output.json"
            if kind == "symlink":
                p.symlink_to(victim)
            else:
                os.link(victim, p)
        r = w.run_cli()
        assert r.returncode == 0, r.stdout[-3000:]
        assert victim.read_bytes() == before
        # 신뢰 출력은 에이전트가 못 쓰는 evidence에 있다
        assert (w.ev / "demo/outputs/step0-output.json").exists()

    def test_agent_made_result_symlink_not_followed(self, w):
        ext = w.base / "mainclone" / "forged.json"
        ext.parent.mkdir(exist_ok=True)
        ext.write_text('{"status": "completed", "summary": "forged"}')
        before = ext.read_bytes()
        r = w.run_cli(env={"FAKE_ATTACK": "result-symlink", "FAKE_EXT": str(ext)})
        assert r.returncode == 1  # 결과를 인정하지 않아 재시도 후 error
        assert ext.read_bytes() == before
        assert w.index()["steps"][0]["status"] == "error"
        assert "forged" not in json.dumps(w.index())

    def test_hardlinked_result_rejected(self, w, monkeypatch):
        e = ex.StepExecutor("demo", descriptor=rn.load_descriptor(w.desc, w.repo))
        ext = w.base / "mainclone" / "forged.json"
        ext.parent.mkdir(exist_ok=True)
        ext.write_text('{"status": "completed", "summary": "forged"}')
        before = ext.read_bytes()
        real = ex._run_agent_process

        def link_result(argv, **kw):
            res = real(argv, **kw)
            p = w.out / "step0-result.json"
            if os.path.lexists(p):
                p.unlink()
            os.link(ext, p)
            return res
        monkeypatch.setattr(ex, "_run_agent_process", link_result)
        with pytest.raises(SystemExit) as exc:
            e.run()
        assert exc.value.code == 1
        assert ext.read_bytes() == before
        assert "forged" not in json.dumps(w.index())

    def test_tmp_dir_swap_does_not_redirect_writes(self, w):
        ext = w.base / "sibling-dir"
        ext.mkdir()
        (w.out / "tmp").symlink_to(ext, target_is_directory=True)
        r = w.run_cli()
        assert r.returncode == 0, r.stdout[-3000:]
        assert list(ext.iterdir()) == []
        assert (w.out / "tmp").is_dir() and not (w.out / "tmp").is_symlink()


# ---------------------------------------------------------------------------
# MVP amendment — 실행 뒤 fail-closed 불변 검증(적대적 OS 격리는 주장하지 않는다)
# ---------------------------------------------------------------------------

class TestPostAgentInvariants:
    def test_control_change_during_agent_blocks_before_commit(self, w, monkeypatch):
        e = ex.StepExecutor("demo", descriptor=rn.load_descriptor(w.desc, w.repo))
        real = ex._run_agent_process

        def run_and_tamper(argv, **kw):
            res = real(argv, **kw)
            (w.repo / "CLAUDE.md").write_text("# gates off\n")
            return res
        monkeypatch.setattr(ex, "_run_agent_process", run_and_tamper)
        with pytest.raises(SystemExit) as exc:
            e.run()
        assert exc.value.code == 3
        assert "control" in w.index()["review_reason"]
        assert w.head() == w.plan_commit, "검증 실패 뒤에 커밋하면 안 된다"
        assert w.codex_calls() == [] and w.final() is None

    def test_head_moved_during_agent_blocks(self, w, monkeypatch):
        e = ex.StepExecutor("demo", descriptor=rn.load_descriptor(w.desc, w.repo))
        real = ex._run_agent_process

        def run_and_commit(argv, **kw):
            res = real(argv, **kw)
            git(w.repo, "commit", "-q", "--allow-empty", "-m", "agent commit")
            return res
        monkeypatch.setattr(ex, "_run_agent_process", run_and_commit)
        with pytest.raises(SystemExit) as exc:
            e.run()
        assert exc.value.code == 3
        assert "HEAD" in w.index()["review_reason"]
        assert w.final() is None
