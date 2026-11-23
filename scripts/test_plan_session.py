"""B. Discord↔Claude 계획 세션 — read-only argv, session resume, lock, idempotency, recovery.

가짜 `claude` 실행파일을 PATH에 두고 **실제로 spawn**한다(원격 호출 없음).
"""
import fcntl
import hashlib
import json
import os
import subprocess
import sys
import textwrap
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent))
import plan_session as ps  # noqa: E402
import plan_manifest as pm  # noqa: E402
from conftest import git, DESIGN  # noqa: E402

THREAD = "10002"  # 가짜 fixture thread ID(운영 ID 아님)
SID = "11111111-2222-3333-4444-555555555555"

FAKE_CLAUDE = textwrap.dedent("""\
    #!/bin/sh
    printf '%s\\n' "$@" >> "$FAKE_ARGV_LOG"
    echo "--END--" >> "$FAKE_ARGV_LOG"
    cat > "$FAKE_STDIN_LOG"
    if [ -n "$FAKE_SLEEP" ]; then sleep "$FAKE_SLEEP"; fi
    cat "$FAKE_RESPONSE"
    exit "${FAKE_RC:-0}"
""")


def stream(text, sid=SID, skills=("superpowers:brainstorming", "grilling"), is_error=False):
    lines = [{"type": "system", "subtype": "init", "session_id": sid}]
    for s in skills:
        lines.append({"type": "assistant", "session_id": sid, "message": {"content": [
            {"type": "tool_use", "name": "Skill", "input": {"skill": s}}]}})
    lines.append({"type": "result", "subtype": "success", "is_error": is_error,
                  "result": text, "session_id": sid})
    return "\n".join(json.dumps(x, ensure_ascii=False) for x in lines) + "\n"


class Env:
    def __init__(self, tmp_path, monkeypatch):
        self.root = tmp_path / "repo"
        self.root.mkdir()
        git(self.root, "init", "-q", "-b", "main")
        git(self.root, "config", "user.email", "t@e.com")
        git(self.root, "config", "user.name", "T")
        (self.root / ".gitignore").write_text(".harness/\n", encoding="utf-8")
        (self.root / "README.md").write_text("x\n", encoding="utf-8")
        git(self.root, "add", "-A")
        git(self.root, "commit", "-q", "-m", "init")
        self.rt = tmp_path / "runtime"
        bindir = tmp_path / "bin"
        bindir.mkdir()
        exe = bindir / "claude"
        exe.write_text(FAKE_CLAUDE, encoding="utf-8")
        exe.chmod(0o755)
        self.argv_log = tmp_path / "argv.log"
        self.stdin_log = tmp_path / "stdin.log"
        self.response = tmp_path / "response.jsonl"
        monkeypatch.setenv("PATH", f"{bindir}:{os.environ['PATH']}")
        monkeypatch.setenv("FAKE_ARGV_LOG", str(self.argv_log))
        monkeypatch.setenv("FAKE_STDIN_LOG", str(self.stdin_log))
        monkeypatch.setenv("FAKE_RESPONSE", str(self.response))
        for k in ("FAKE_SLEEP", "FAKE_RC"):
            monkeypatch.delenv(k, raising=False)
        skill = tmp_path / "skills" / "grilling" / "SKILL.md"
        skill.parent.mkdir(parents=True)
        skill.write_text("name: grilling\n", encoding="utf-8")
        monkeypatch.setattr(ps, "GRILLING_SKILL_PATHS", (skill,))
        self.skill = skill
        self.respond(stream("질문 1: 무엇을 만들까요?"))

    def respond(self, text):
        self.response.write_text(text, encoding="utf-8")

    def calls(self):
        if not self.argv_log.exists():
            return []
        out, cur = [], []
        for line in self.argv_log.read_text(encoding="utf-8").splitlines():
            if line == "--END--":
                out.append(cur)
                cur = []
            else:
                cur.append(line)
        return out

    def s(self, **kw):
        return ps.Session(self.root, self.rt, THREAD, **kw)

    def state(self):
        return json.loads((self.rt / f"{THREAD}.json").read_text(encoding="utf-8"))


@pytest.fixture
def env(tmp_path, monkeypatch):
    return Env(tmp_path, monkeypatch)


def _start(env, msg="m1", prompt="로그인 기능을 만들고 싶다"):
    return env.s().start(msg, prompt)


def _post(env, discord_id="p1"):
    st = env.state()
    h = st["pendingOutbound"]["hash"]
    env.s().begin_post(h)
    env.s().record_posted(h, discord_id)


def _round(env, msg, text="답변"):
    env.respond(stream(f"질문 for {msg}"))
    env.s().resume(msg, text)
    _post(env, "p-" + msg)


class TestArgv:
    def test_plan_argv_read_only(self):
        argv = ps.build_plan_argv()
        assert argv[:2] == ["claude", "-p"]
        assert argv[argv.index("--permission-mode") + 1] == "plan"
        assert argv[argv.index("--allowedTools") + 1] == "Read,Glob,Grep,Skill"
        dis = argv[argv.index("--disallowedTools") + 1].split(",")
        for t in ("Write", "Edit", "Bash", "NotebookEdit"):
            assert t in dis
        assert "--dangerously-skip-permissions" not in argv
        assert "bypassPermissions" not in argv
        assert "--add-dir" not in argv
        assert "--resume" not in argv

    def test_resume_argv_uses_exact_session(self):
        argv = ps.build_plan_argv(SID)
        assert argv[argv.index("--resume") + 1] == SID
        assert "--dangerously-skip-permissions" not in argv
        assert argv[argv.index("--permission-mode") + 1] == "plan"

    def test_rejects_bad_session_id(self):
        with pytest.raises(ps.SessionError):
            ps.build_plan_argv("--dangerously-skip-permissions")

    @pytest.mark.parametrize("tid", ["../x", "abc", "", "1/2"])
    def test_rejects_bad_thread_id(self, env, tid):
        with pytest.raises(ps.SessionError):
            ps.Session(env.root, env.rt, tid)


class TestStartResume:
    def test_start_saves_session_and_outbound(self, env):
        out = _start(env)
        st = env.state()
        assert st["sessionId"] == SID
        assert st["status"] == "awaiting-post"
        assert st["grillingInvoked"] is True
        assert st["inflight"] is None
        text = "질문 1: 무엇을 만들까요?"
        assert st["pendingOutbound"]["text"] == text
        assert st["pendingOutbound"]["hash"] == hashlib.sha256(text.encode()).hexdigest()
        assert out["outboundHash"] == st["pendingOutbound"]["hash"]
        prompt = env.stdin_log.read_text(encoding="utf-8")
        assert "grilling" in prompt and "brainstorming" in prompt
        assert "로그인 기능" in prompt
        assert "--resume" not in env.calls()[0]

    def test_all_followups_use_same_resume_id(self, env):
        _start(env)
        _post(env)
        _round(env, "m2")
        _round(env, "m3")
        calls = env.calls()
        assert len(calls) == 3
        for c in calls[1:]:
            assert c[c.index("--resume") + 1] == SID
            assert "--dangerously-skip-permissions" not in c

    def test_start_twice_rejected(self, env):
        _start(env)
        with pytest.raises(ps.SessionError):
            env.s().start("m9", "again")

    def test_resume_before_post_rejected(self, env):
        _start(env)
        with pytest.raises(ps.SessionError):
            env.s().resume("m2", "x")
        assert len(env.calls()) == 1

    def test_duplicate_message_not_resent(self, env):
        _start(env)
        _post(env)
        _round(env, "m2")
        with pytest.raises(ps.DuplicateMessage):
            env.s().resume("m2", "same again")
        with pytest.raises(ps.DuplicateMessage):
            env.s().resume("m1", "start id reused")
        assert len(env.calls()) == 2

    def test_session_id_change_requires_recovery(self, env):
        _start(env)
        _post(env)
        env.respond(stream("x", sid="99999999-2222-3333-4444-555555555555"))
        with pytest.raises(ps.RecoveryRequired):
            env.s().resume("m2", "x")
        assert env.state()["status"] == "recovery-required"
        assert env.state()["sessionId"] == SID

    def test_missing_grilling_skill_fails_closed(self, env):
        env.skill.unlink()
        with pytest.raises(ps.SessionError):
            _start(env)
        assert env.calls() == []

    def test_grilling_not_invoked_blocks_agreement(self, env):
        env.respond(stream("q", skills=("superpowers:brainstorming",)))
        _start(env)
        _post(env)
        env.respond(stream("q2", skills=()))
        env.s().resume("m2", "a")
        _post(env, "p2")
        assert env.state()["grillingInvoked"] is False
        with pytest.raises(ps.SessionError):
            env.s().record_agreement("agree-1")

    def test_docs_diff_before_agreement_fails(self, env):
        _start(env)
        _post(env)
        (env.root / "docs").mkdir()
        (env.root / "docs" / "x.md").write_text("premature", encoding="utf-8")
        with pytest.raises(ps.SessionError):
            env.s().resume("m2", "x")
        assert len(env.calls()) == 1

    def test_docs_diff_created_during_call_requires_recovery(self, env, monkeypatch):
        _start(env)
        _post(env)
        real = ps.Session._invoke

        def sneaky(self, *a, **k):
            r = real(self, *a, **k)
            (env.root / "phases").mkdir(exist_ok=True)
            (env.root / "phases" / "x.json").write_text("{}", encoding="utf-8")
            return r
        monkeypatch.setattr(ps.Session, "_invoke", sneaky)
        with pytest.raises(ps.RecoveryRequired):
            env.s().resume("m2", "x")


class TestLock:
    def test_concurrent_call_rejected(self, env):
        _start(env)
        _post(env)
        lock = env.rt / f"{THREAD}.lock"
        fd = os.open(lock, os.O_RDWR | os.O_CREAT)
        fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        try:
            with pytest.raises(ps.LockBusy):
                env.s().resume("m2", "x")
        finally:
            os.close(fd)
        assert len(env.calls()) == 1
        assert "m2" not in env.state()["processedMessageIds"]

    def test_concurrent_process_rejected(self, env, tmp_path):
        """실제 두 프로세스: 하나가 Claude 호출 중(lock 보유)이면 다른 하나는 거부."""
        _start(env)
        _post(env)
        holder = subprocess.Popen([sys.executable, "-c", textwrap.dedent(f"""
            import fcntl, os, time
            fd = os.open({str(env.rt / (THREAD + '.lock'))!r}, os.O_RDWR | os.O_CREAT)
            fcntl.flock(fd, fcntl.LOCK_EX)
            print('locked', flush=True)
            time.sleep(5)
        """)], stdout=subprocess.PIPE, text=True)
        try:
            assert holder.stdout.readline().strip() == "locked"
            with pytest.raises(ps.LockBusy):
                env.s().resume("m2", "x")
        finally:
            holder.kill()
            holder.wait()


class TestRecovery:
    def test_timeout_kills_and_requires_recovery(self, env, monkeypatch):
        _start(env)
        _post(env)
        monkeypatch.setenv("FAKE_SLEEP", "30")
        with pytest.raises(ps.RecoveryRequired):
            env.s(timeout=1).resume("m2", "x")
        st = env.state()
        assert st["status"] == "recovery-required"
        assert st["sessionId"] == SID
        assert st["inflight"]["messageId"] == "m2"

    def test_nonzero_exit_requires_recovery_no_resend(self, env, monkeypatch):
        _start(env)
        _post(env)
        monkeypatch.setenv("FAKE_RC", "1")
        with pytest.raises(ps.RecoveryRequired):
            env.s().resume("m2", "x")
        monkeypatch.delenv("FAKE_RC")
        with pytest.raises(ps.RecoveryRequired):
            env.s().resume("m3", "y")
        assert len(env.calls()) == 2  # 자동 재전송 없음

    def test_garbage_output_requires_recovery(self, env):
        env.respond("not json\n")
        with pytest.raises(ps.RecoveryRequired):
            _start(env)
        assert env.state()["inflight"]["messageId"] == "m1"

    def test_crash_before_session_saved(self, env, monkeypatch):
        """최초 응답 후 session ID 저장 전 crash → 자동 재호출 없이 recovery-required."""
        real_save = ps.Session._save
        n = {"saves": 0}

        def crashy(self, st):
            n["saves"] += 1
            if n["saves"] == 2:  # 호출 전 inflight 저장 다음, 결과 저장 시점
                raise KeyboardInterrupt("crash")
            return real_save(self, st)
        monkeypatch.setattr(ps.Session, "_save", crashy)
        with pytest.raises(KeyboardInterrupt):
            _start(env)
        monkeypatch.setattr(ps.Session, "_save", real_save)
        st = env.state()
        assert st["sessionId"] is None and st["inflight"]["messageId"] == "m1"
        with pytest.raises(ps.RecoveryRequired):
            env.s().start("m1b", "retry")
        with pytest.raises(ps.RecoveryRequired):
            env.s().resume("m2", "x")
        assert len(env.calls()) == 1

    def test_crash_after_post_before_record(self, env):
        """게시 성공 후 record-posted 전 crash → 재게시 대신 recovery-required."""
        _start(env)
        h = env.state()["pendingOutbound"]["hash"]
        env.s().begin_post(h)
        # (여기서 Ryan이 Discord에 게시했지만 crash로 record-posted를 못 했다)
        with pytest.raises(ps.RecoveryRequired):
            env.s().begin_post(h)
        assert env.state()["status"] == "recovery-required"

    def test_record_posted_wrong_hash(self, env):
        _start(env)
        h = env.state()["pendingOutbound"]["hash"]
        env.s().begin_post(h)
        with pytest.raises(ps.SessionError):
            env.s().record_posted("0" * 64, "p1")

    def test_resolve_requires_evidence(self, env, monkeypatch):
        _start(env)
        _post(env)
        monkeypatch.setenv("FAKE_RC", "1")
        with pytest.raises(ps.RecoveryRequired):
            env.s().resume("m2", "x")
        for op, reason, ev in (("", "r", "e"), ("ryan", "", "e"), ("ryan", "r", "")):
            with pytest.raises(ps.SessionError):
                env.s().resolve_recovery(op, reason, ev)
        assert env.state()["status"] == "recovery-required"

    def test_resolve_not_in_recovery_rejected(self, env):
        _start(env)
        _post(env)
        with pytest.raises(ps.SessionError):
            env.s().resolve_recovery("ryan", "r", "e")

    def test_resolve_appends_log_and_resumes_same_session(self, env, monkeypatch):
        _start(env)
        _post(env)
        monkeypatch.setenv("FAKE_RC", "1")
        with pytest.raises(ps.RecoveryRequired):
            env.s().resume("m2", "x")
        monkeypatch.delenv("FAKE_RC")
        env.s().resolve_recovery("ryan", "transcript 확인: m2 미전달", "transcript:abc",
                                 requeue=True)
        env.s().resolve_recovery  # noqa
        log = (env.rt / "recovery-log.jsonl").read_text(encoding="utf-8").splitlines()
        assert len(log) == 1
        entry = json.loads(log[0])
        assert entry["operator"] == "ryan" and entry["evidenceId"] == "transcript:abc"
        assert entry["previousState"]["status"] == "recovery-required"
        assert entry["previousStateSha"] and entry["evidenceSha"]
        assert entry["requeued"] == "m2"
        _round(env, "m2")
        c = env.calls()[-1]
        assert c[c.index("--resume") + 1] == SID

    def test_log_is_append_only(self, env, monkeypatch):
        _start(env)
        _post(env)
        for i, msg in enumerate(("m2", "m3")):
            monkeypatch.setenv("FAKE_RC", "1")
            with pytest.raises(ps.RecoveryRequired):
                env.s().resume(msg, "x")
            env.s().resolve_recovery("ryan", f"r{i}", f"e{i}")
        log = (env.rt / "recovery-log.jsonl").read_text(encoding="utf-8").splitlines()
        assert [json.loads(l)["reason"] for l in log] == ["r0", "r1"]

    def test_resolve_posting_binds_discord_message(self, env):
        _start(env)
        h = env.state()["pendingOutbound"]["hash"]
        env.s().begin_post(h)
        with pytest.raises(ps.RecoveryRequired):
            env.s().begin_post(h)
        env.s().resolve_recovery("ryan", "스레드에서 게시 확인", "discord:777",
                                 posted_message_id="777")
        st = env.state()
        assert st["status"] == "idle"
        assert st["posted"][-1]["discordMessageId"] == "777"


class TestAgreementAndMaterialize:
    def _agreed(self, env):
        _start(env)
        _post(env)
        _round(env, "m2")
        env.s().record_agreement("agree-1")

    def _payload(self, task="demo", **over):
        index = {"project": "Demo", "phase": task, "baseBranch": "main",
                 "designDoc": DESIGN, "allowedPaths": ["src/", "tests/"],
                 "testCommand": ["python3", "-m", "pytest", "-q"],
                 "steps": [{"step": 0, "name": "core", "status": "pending"}]}
        files = [{"path": DESIGN, "content": "# design\n"},
                 {"path": f"phases/{task}/index.json",
                  "content": json.dumps(index, ensure_ascii=False, indent=2)},
                 {"path": f"phases/{task}/step0.md", "content": "# Step 0\n"}]
        p = {"task": task, "files": files}
        p.update(over)
        return p

    def test_agreement_requires_question_round(self, env):
        _start(env)
        _post(env)
        with pytest.raises(ps.SessionError):
            env.s().record_agreement("agree-1")

    def test_materialize_before_agreement_rejected(self, env, tmp_path):
        _start(env)
        _post(env)
        env.respond(stream(json.dumps(self._payload())))
        with pytest.raises(ps.SessionError):
            env.s().materialize("demo", tmp_path / "out.json")
        assert not (env.root / "phases").exists()
        assert git(env.root, "status", "--porcelain", "--", "docs", "phases") == ""

    def test_materialize_writes_only_allowed_paths(self, env, tmp_path):
        self._agreed(env)
        env.respond(stream(json.dumps(self._payload(), ensure_ascii=False)))
        report = env.s().materialize("demo", tmp_path / "out.json")
        assert (env.root / "phases/demo/step0.md").read_text() == "# Step 0\n"
        assert report["planSha"] == pm.build_manifest(env.root, "demo").sha
        assert json.loads((tmp_path / "out.json").read_text())["planSha"] == report["planSha"]
        c = env.calls()[-1]
        assert "--dangerously-skip-permissions" not in c
        assert c[c.index("--resume") + 1] == SID

    @pytest.mark.parametrize("bad", [
        {"path": "scripts/evil.py", "content": "x"},
        {"path": "../outside.md", "content": "x"},
        {"path": "/abs.md", "content": "x"},
        {"path": "phases/other/step0.md", "content": "x"},
        {"path": "docs/superpowers/specs/second.md", "content": "x"},
        {"path": ".claude/settings.json", "content": "{}"},
    ])
    def test_materialize_rejects_bad_paths(self, env, tmp_path, bad):
        self._agreed(env)
        p = self._payload()
        p["files"].append(bad)
        env.respond(stream(json.dumps(p)))
        with pytest.raises(ps.SessionError):
            env.s().materialize("demo", tmp_path / "out.json")
        assert not (env.root / "phases/demo").exists()
        assert not (env.root / "scripts").exists()

    def test_materialize_rejects_invalid_plan(self, env, tmp_path):
        self._agreed(env)
        p = self._payload()
        p["files"] = [f for f in p["files"] if not f["path"].endswith("step0.md")]
        env.respond(stream(json.dumps(p)))
        with pytest.raises(ps.SessionError):
            env.s().materialize("demo", tmp_path / "out.json")

    def test_materialize_refuses_symlink_target(self, env, tmp_path):
        self._agreed(env)
        (env.root / "phases/demo").mkdir(parents=True)
        (env.root / "phases/demo/step0.md").symlink_to(tmp_path / "victim.md")
        env.respond(stream(json.dumps(self._payload())))
        with pytest.raises(ps.SessionError):
            env.s().materialize("demo", tmp_path / "out.json")
        assert not (tmp_path / "victim.md").exists()

    def test_agreement_id_cannot_be_reused(self, env):
        self._agreed(env)
        with pytest.raises(ps.SessionError):
            env.s().record_agreement("agree-2")


REAL_GRILLING = Path.home() / ".claude" / "skills" / "grilling" / "SKILL.md"


class TestCli:
    def test_help_lists_commands(self):
        r = subprocess.run([sys.executable, str(Path(ps.__file__)), "--help"],
                           capture_output=True, text=True)
        for c in ("start", "resume", "record-agreement", "record-posted", "record-approval",
                  "resolve-recovery", "materialize", "status", "begin-post"):
            assert c in r.stdout

    @pytest.mark.skipif(not REAL_GRILLING.exists(), reason="grilling 스킬 미설치")
    def test_cli_start_and_status(self, env, tmp_path):
        pf = tmp_path / "prompt.txt"
        pf.write_text("요청", encoding="utf-8")
        envv = dict(os.environ, HARNESS_RUNTIME_DIR=str(env.rt))
        r = subprocess.run([sys.executable, str(Path(ps.__file__)), "start", "--repo-root", str(env.root), "--thread-id",
                            THREAD, "--request-message-id", "m1", "--prompt-file", str(pf)],
                           capture_output=True, text=True, env=envv)
        assert r.returncode == 0, r.stdout + r.stderr
        r = subprocess.run([sys.executable, str(Path(ps.__file__)), "status", "--repo-root", str(env.root),
                            "--thread-id", THREAD], capture_output=True, text=True, env=envv)
        assert json.loads(r.stdout)["sessionId"] == SID

    def test_cli_duplicate_exit_code(self, env, tmp_path):
        pf = tmp_path / "prompt.txt"
        pf.write_text("요청", encoding="utf-8")
        envv = dict(os.environ, HARNESS_RUNTIME_DIR=str(env.rt))
        _start(env)
        _post(env)
        _round(env, "m2")
        r = subprocess.run([sys.executable, str(Path(ps.__file__)), "resume", "--repo-root", str(env.root),
                            "--thread-id", THREAD, "--message-id", "m2", "--prompt-file", str(pf)],
                           capture_output=True, text=True, env=envv)
        assert r.returncode == ps.EXIT_DUPLICATE
