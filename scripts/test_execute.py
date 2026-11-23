"""
execute.py 리팩터링 안전망 테스트.
리팩터링 전후 동작이 동일한지 검증한다.

베이스: lecture/harness_engineering `main` 브랜치의 test_execute.py.
추가: HARNESS_NO_GIT 가드 테스트(TestNoGitGuard).
"""

import contextlib
import json
import os
import re
import shlex
import shutil
import signal
import subprocess
import sys
import tempfile
import textwrap
import types
from datetime import datetime, timezone, timedelta
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest

sys.path.insert(0, str(Path(__file__).parent))
import execute as ex


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(autouse=True)
def _clean_harness_env(monkeypatch):
    """하네스 실행용 셸(HARNESS_REVIEW_BACKEND=codex 등)에서 돌려도 기본값을 가정한
    테스트가 깨지지 않도록 HARNESS_* 를 비운다. 필요한 값은 각 테스트가 setenv한다."""
    for key in [k for k in os.environ if k.startswith("HARNESS_")]:
        monkeypatch.delenv(key)


def _run_via_subprocess_run(argv, *, input, cwd, timeout, kill_grace=30, env=None):
    """_run_agent_process 대역 — 에이전트 호출을 subprocess.run으로 넘긴다.
    리뷰·수정 시험의 subprocess.run 가짜(_reviewers 등)가 에이전트 호출을 그대로 받는다."""
    try:
        r = subprocess.run(argv, input=input, cwd=cwd, capture_output=True, text=True,
                           encoding="utf-8", timeout=timeout, env=env)
    except subprocess.TimeoutExpired:
        return ex.AgentRun(-1, "", "", True)
    return ex.AgentRun(r.returncode, r.stdout or "", r.stderr or "", False)


# 실제 프로세스를 띄워 _run_agent_process 자체를 보는 시험 — 대역을 끼우지 않는다
_REAL_AGENT_PROCESS = {"TestRunAgentProcess", "TestSignalExit", "TestDescendantReaping",
                       "TestTimeoutPathIsGroupOnly"}


@pytest.fixture(autouse=True)
def _agent_process_via_run(request, monkeypatch):
    if request.cls is None or request.cls.__name__ not in _REAL_AGENT_PROCESS:
        monkeypatch.setattr(ex, "_run_agent_process", _run_via_subprocess_run)


@pytest.fixture
def tmp_project(tmp_path):
    """phases/, CLAUDE.md, docs/ 를 갖춘 임시 프로젝트 구조."""
    phases_dir = tmp_path / "phases"
    phases_dir.mkdir()

    claude_md = tmp_path / "CLAUDE.md"
    claude_md.write_text("# Rules\n- rule one\n- rule two", encoding="utf-8")

    docs_dir = tmp_path / "docs"
    docs_dir.mkdir()
    (docs_dir / "arch.md").write_text("# Architecture\nSome content", encoding="utf-8")
    (docs_dir / "guide.md").write_text("# Guide\nAnother doc", encoding="utf-8")

    return tmp_path


@pytest.fixture
def phase_dir(tmp_project):
    """step 3개를 가진 phase 디렉토리."""
    d = tmp_project / "phases" / "0-mvp"
    d.mkdir()

    index = {
        "project": "TestProject",
        "phase": "mvp",
        "steps": [
            {"step": 0, "name": "setup", "status": "completed", "summary": "프로젝트 초기화 완료"},
            {"step": 1, "name": "core", "status": "completed", "summary": "핵심 로직 구현"},
            {"step": 2, "name": "ui", "status": "pending"},
        ],
    }
    (d / "index.json").write_text(json.dumps(index, indent=2, ensure_ascii=False), encoding="utf-8")
    (d / "step2.md").write_text("# Step 2: UI\n\nUI를 구현하세요.", encoding="utf-8")

    return d


@pytest.fixture
def top_index(tmp_project):
    """phases/index.json (top-level)."""
    top = {
        "phases": [
            {"dir": "0-mvp", "status": "pending"},
            {"dir": "1-polish", "status": "pending"},
        ]
    }
    p = tmp_project / "phases" / "index.json"
    p.write_text(json.dumps(top, indent=2))
    return p


@pytest.fixture
def executor(tmp_project, phase_dir):
    """테스트용 StepExecutor 인스턴스. git 호출은 별도 mock 필요."""
    with patch.object(ex, "ROOT", tmp_project):
        inst = ex.StepExecutor("0-mvp")
    # 내부 경로를 tmp_project 기준으로 재설정
    inst._root = str(tmp_project)
    inst._phases_dir = tmp_project / "phases"
    inst._phase_dir = phase_dir
    inst._phase_dir_name = "0-mvp"
    inst._index_file = phase_dir / "index.json"
    inst._top_index_file = tmp_project / "phases" / "index.json"
    return inst


# ---------------------------------------------------------------------------
# _stamp (= 이전 now_iso)
# ---------------------------------------------------------------------------

class TestStamp:
    def test_returns_kst_timestamp(self, executor):
        result = executor._stamp()
        assert "+0900" in result

    def test_format_is_iso(self, executor):
        result = executor._stamp()
        dt = datetime.strptime(result, "%Y-%m-%dT%H:%M:%S%z")
        assert dt.tzinfo is not None

    def test_is_current_time(self, executor):
        before = datetime.now(ex.StepExecutor.TZ).replace(microsecond=0)
        result = executor._stamp()
        after = datetime.now(ex.StepExecutor.TZ).replace(microsecond=0) + timedelta(seconds=1)
        parsed = datetime.strptime(result, "%Y-%m-%dT%H:%M:%S%z")
        assert before <= parsed <= after


# ---------------------------------------------------------------------------
# _read_json / _write_json
# ---------------------------------------------------------------------------

class TestJsonHelpers:
    def test_roundtrip(self, tmp_path):
        data = {"key": "값", "nested": [1, 2, 3]}
        p = tmp_path / "test.json"
        ex.StepExecutor._write_json(p, data)
        loaded = ex.StepExecutor._read_json(p)
        assert loaded == data

    def test_save_ensures_ascii_false(self, tmp_path):
        p = tmp_path / "test.json"
        ex.StepExecutor._write_json(p, {"한글": "테스트"})
        raw = p.read_text(encoding="utf-8")
        assert "한글" in raw
        assert "\\u" not in raw

    def test_save_indented(self, tmp_path):
        p = tmp_path / "test.json"
        ex.StepExecutor._write_json(p, {"a": 1})
        raw = p.read_text(encoding="utf-8")
        assert "\n" in raw

    def test_load_nonexistent_raises(self, tmp_path):
        with pytest.raises(FileNotFoundError):
            ex.StepExecutor._read_json(tmp_path / "nope.json")


# ---------------------------------------------------------------------------
# _load_guardrails
# ---------------------------------------------------------------------------

class TestLoadGuardrails:
    def test_loads_claude_md_and_docs(self, executor, tmp_project):
        with patch.object(ex, "ROOT", tmp_project):
            result = executor._load_guardrails()
        assert "# Rules" in result
        assert "rule one" in result
        assert "# Architecture" in result
        assert "# Guide" in result

    def test_sections_separated_by_divider(self, executor, tmp_project):
        with patch.object(ex, "ROOT", tmp_project):
            result = executor._load_guardrails()
        assert "---" in result

    def test_docs_sorted_alphabetically(self, executor, tmp_project):
        with patch.object(ex, "ROOT", tmp_project):
            result = executor._load_guardrails()
        arch_pos = result.index("arch")
        guide_pos = result.index("guide")
        assert arch_pos < guide_pos

    def test_no_claude_md(self, executor, tmp_project):
        (tmp_project / "CLAUDE.md").unlink()
        with patch.object(ex, "ROOT", tmp_project):
            result = executor._load_guardrails()
        assert "CLAUDE.md" not in result
        assert "Architecture" in result

    def test_no_docs_dir(self, executor, tmp_project):
        import shutil
        shutil.rmtree(tmp_project / "docs")
        with patch.object(ex, "ROOT", tmp_project):
            result = executor._load_guardrails()
        assert "Rules" in result
        assert "Architecture" not in result

    def test_empty_project(self, tmp_path):
        with patch.object(ex, "ROOT", tmp_path):
            # executor가 필요 없는 static-like 동작이므로 임시 인스턴스
            phases_dir = tmp_path / "phases" / "dummy"
            phases_dir.mkdir(parents=True)
            idx = {"project": "T", "phase": "t", "steps": []}
            (phases_dir / "index.json").write_text(json.dumps(idx), encoding="utf-8")
            inst = ex.StepExecutor.__new__(ex.StepExecutor)
            inst._root = str(tmp_path)
            result = inst._load_guardrails()
        assert result == ""


# ---------------------------------------------------------------------------
# _build_step_context
# ---------------------------------------------------------------------------

class TestBuildStepContext:
    def test_includes_completed_with_summary(self, phase_dir):
        index = json.loads((phase_dir / "index.json").read_text(encoding="utf-8"))
        result = ex.StepExecutor._build_step_context(index)
        assert "Step 0 (setup): 프로젝트 초기화 완료" in result
        assert "Step 1 (core): 핵심 로직 구현" in result

    def test_excludes_pending(self, phase_dir):
        index = json.loads((phase_dir / "index.json").read_text(encoding="utf-8"))
        result = ex.StepExecutor._build_step_context(index)
        assert "ui" not in result

    def test_excludes_completed_without_summary(self, phase_dir):
        index = json.loads((phase_dir / "index.json").read_text(encoding="utf-8"))
        del index["steps"][0]["summary"]
        result = ex.StepExecutor._build_step_context(index)
        assert "setup" not in result
        assert "core" in result

    def test_empty_when_no_completed(self):
        index = {"steps": [{"step": 0, "name": "a", "status": "pending"}]}
        result = ex.StepExecutor._build_step_context(index)
        assert result == ""

    def test_has_header(self, phase_dir):
        index = json.loads((phase_dir / "index.json").read_text(encoding="utf-8"))
        result = ex.StepExecutor._build_step_context(index)
        assert result.startswith("## 이전 Step 산출물")


# ---------------------------------------------------------------------------
# _build_preamble
# ---------------------------------------------------------------------------

class TestBuildPreamble:
    def test_includes_project_name(self, executor):
        result = executor._build_preamble("", "")
        assert "TestProject" in result

    def test_includes_guardrails(self, executor):
        result = executor._build_preamble("GUARD_CONTENT", "")
        assert "GUARD_CONTENT" in result

    def test_includes_step_context(self, executor):
        ctx = "## 이전 Step 산출물\n\n- Step 0: done"
        result = executor._build_preamble("", ctx)
        assert "이전 Step 산출물" in result

    def test_agent_must_not_commit(self, executor):
        """(구 commit 예시 시험 대체) 커밋은 하네스만 — 에이전트에게 commit을 금지한다."""
        result = executor._build_preamble("", "")
        assert "git commit" in result and "하네스가 검증 후 커밋" in result

    def test_lists_allowed_paths(self, executor):
        executor._allowed = ["src/", "tests/"]
        result = executor._build_preamble("", "")
        assert "src/, tests/" in result

    def test_includes_rules(self, executor):
        result = executor._build_preamble("", "")
        assert "작업 규칙" in result
        assert "AC" in result

    def test_no_retry_section_by_default(self, executor):
        result = executor._build_preamble("", "")
        assert "이전 시도 실패" not in result

    def test_retry_section_with_prev_error(self, executor):
        result = executor._build_preamble("", "", prev_error="타입 에러 발생")
        assert "이전 시도 실패" in result
        assert "타입 에러 발생" in result

    def test_includes_max_retries(self, executor):
        result = executor._build_preamble("", "")
        assert str(ex.StepExecutor.MAX_RETRIES) in result

    def test_result_file_protocol_not_index(self, executor):
        """(구 index 경로 시험 대체) 상태는 RESULT_FILE로 보고하고 index.json은 하네스가 쓴다."""
        result = executor._build_preamble("", "")
        assert "RESULT_FILE" in result
        assert "index.json은 건드리지 마라" in result


# ---------------------------------------------------------------------------
# _update_top_index
# ---------------------------------------------------------------------------

class TestUpdateTopIndex:
    def test_completed(self, executor, top_index):
        executor._top_index_file = top_index
        executor._update_top_index("completed")
        data = json.loads(top_index.read_text(encoding="utf-8"))
        mvp = next(p for p in data["phases"] if p["dir"] == "0-mvp")
        assert mvp["status"] == "completed"
        assert "completed_at" in mvp

    def test_error(self, executor, top_index):
        executor._top_index_file = top_index
        executor._update_top_index("error")
        data = json.loads(top_index.read_text(encoding="utf-8"))
        mvp = next(p for p in data["phases"] if p["dir"] == "0-mvp")
        assert mvp["status"] == "error"
        assert "failed_at" in mvp

    def test_blocked(self, executor, top_index):
        executor._top_index_file = top_index
        executor._update_top_index("blocked")
        data = json.loads(top_index.read_text(encoding="utf-8"))
        mvp = next(p for p in data["phases"] if p["dir"] == "0-mvp")
        assert mvp["status"] == "blocked"
        assert "blocked_at" in mvp

    def test_other_phases_unchanged(self, executor, top_index):
        executor._top_index_file = top_index
        executor._update_top_index("completed")
        data = json.loads(top_index.read_text(encoding="utf-8"))
        polish = next(p for p in data["phases"] if p["dir"] == "1-polish")
        assert polish["status"] == "pending"

    def test_nonexistent_dir_is_noop(self, executor, top_index):
        executor._top_index_file = top_index
        executor._phase_dir_name = "no-such-dir"
        original = json.loads(top_index.read_text(encoding="utf-8"))
        executor._update_top_index("completed")
        after = json.loads(top_index.read_text(encoding="utf-8"))
        for p_before, p_after in zip(original["phases"], after["phases"]):
            assert p_before["status"] == p_after["status"]

    def test_no_top_index_file(self, executor, tmp_path):
        executor._top_index_file = tmp_path / "nonexistent.json"
        executor._update_top_index("completed")  # should not raise


# ---------------------------------------------------------------------------
# _require_base (mocked git)
# ---------------------------------------------------------------------------

def _branch_git(executor, *, on="develop", branch_exists=False, ancestor=0,
                merge_base="a" * 40, checkout_rc=0, head_rc=0, calls=None):
    """_require_base용 git 대역. 명령 종류로 응답을 고른다."""
    def run(*args):
        if calls is not None:
            calls.append(args)
        if args[:2] == ("rev-parse", "--abbrev-ref"):
            return MagicMock(returncode=head_rc, stdout=on + "\n",
                             stderr="not a git repo" if head_rc else "")
        if args[:2] == ("rev-parse", "--verify"):
            return MagicMock(returncode=0 if branch_exists else 1, stdout="", stderr="")
        if args[:2] == ("merge-base", "--is-ancestor"):
            return MagicMock(returncode=ancestor, stdout="",
                             stderr="fatal: bad ref" if ancestor > 1 else "")
        if args[:1] == ("merge-base",):
            return MagicMock(returncode=0, stdout=merge_base + "\n", stderr="")
        if args[:1] == ("checkout",):
            return MagicMock(returncode=checkout_rc, stdout="",
                             stderr="dirty tree" if checkout_rc else "")
        return MagicMock(returncode=0, stdout="", stderr="")
    executor._no_git = False
    executor._run_git = run


# ---------------------------------------------------------------------------
# HARNESS_NO_GIT 가드 (이 repo의 머지 패치 — admin-api는 git repo가 아님)
# ---------------------------------------------------------------------------

# ---------------------------------------------------------------------------
# _commit_step (mocked)
# ---------------------------------------------------------------------------

class TestCommitStep:
    """하네스만 커밋한다: 허용 경로 코드 → feat, 하네스 index → chore, hook 비활성."""

    def _git(self, executor, status, calls, staged=True):
        def fake_git(*args):
            calls.append(args)
            if args[:1] == ("status",):
                return MagicMock(returncode=0, stdout=status, stderr="")
            if args[:2] == ("diff", "--cached"):
                return MagicMock(returncode=1 if staged else 0)
            return MagicMock(returncode=0, stdout="", stderr="")
        executor._run_git = fake_git

    def test_two_phase_commit(self, executor):
        calls = []
        self._git(executor, "?? src/ui.py\0 M phases/0-mvp/index.json\0", calls)
        executor._allowed = ["src/"]
        executor._commit_step(2, "ui")
        adds = [c for c in calls if c[0] == "add"]
        assert adds[0] == ("add", "-A", "--", "src/ui.py")
        assert adds[1] == ("add", "-A", "--", "phases/0-mvp/index.json")
        commits = [c for c in calls if "commit" in c]
        assert len(commits) == 2
        assert all(c[:2] == ("-c", "core.hooksPath=/dev/null") for c in commits)
        assert "feat(mvp):" in commits[0][-1] and "chore(mvp):" in commits[1][-1]

    def test_no_code_changes_skips_feat_commit(self, executor):
        calls = []
        self._git(executor, " M phases/0-mvp/index.json\0", calls)
        executor._commit_step(2, "ui")
        commits = [c for c in calls if "commit" in c]
        assert len(commits) == 1 and "chore" in commits[0][-1]

    def test_disallowed_change_blocks_without_commit(self, executor, top_index):
        calls = []
        self._git(executor, " M README.md\0?? src/ok.py\0", calls)
        executor._allowed = ["src/"]
        with pytest.raises(SystemExit) as e:
            executor._commit_step(2, "ui")
        assert e.value.code == 3
        assert not [c for c in calls if "commit" in c or c[0] == "add"]

    def test_commit_failure_is_not_swallowed(self, executor, top_index):
        def fake_git(*args):
            if args[:1] == ("status",):
                return MagicMock(returncode=0, stdout="?? src/a.py\0", stderr="")
            if args[:2] == ("diff", "--cached"):
                return MagicMock(returncode=1)
            if "commit" in args:
                return MagicMock(returncode=1, stdout="", stderr="boom")
            return MagicMock(returncode=0, stdout="", stderr="")
        executor._run_git = fake_git
        with pytest.raises(SystemExit) as e:
            executor._commit_step(2, "ui")
        assert e.value.code == 3

class TestInvokeAgent:
    """구현 에이전트 호출: 게이트 → sandbox로 감싼 bypass argv → snapshot step 본문 →
    RESULT_FILE 결과 수집. 출력 기록은 repo 밖 output dir."""

    @pytest.fixture(autouse=True)
    def _arm(self, executor):
        self.order = []
        executor._gate = lambda where: self.order.append(("gate", where))
        executor._sandboxed = lambda argv: ["SANDBOX"] + list(argv)

    def test_invokes_agent_with_correct_args(self, executor):
        step = {"step": 2, "name": "ui"}
        with patch.object(ex, "_run_agent_process",
                          return_value=ex.AgentRun(0, '{"result": "ok"}', "", False)) as mock_run:
            executor._invoke_agent(step, "PREAMBLE\n")
        cmd = mock_run.call_args[0][0]
        assert cmd[0] == "SANDBOX" and cmd[1:3] == ["claude", "-p"]
        assert "--dangerously-skip-permissions" in cmd
        assert "PREAMBLE" not in " ".join(cmd)
        stdin_prompt = mock_run.call_args[1]["input"]
        assert "PREAMBLE" in stdin_prompt and "UI를 구현하세요" in stdin_prompt
        assert "STEP_NUMBER: 2" in stdin_prompt
        assert f"RESULT_FILE: {executor._out_dir / 'step2-result.json'}" in stdin_prompt
        assert mock_run.call_args[1]["env"]["TMPDIR"].startswith(str(executor._out_dir))
        assert self.order == [("gate", "step 2")]

    def test_gate_runs_before_agent(self, executor):
        def gate(where):
            raise SystemExit(3)
        executor._gate = gate
        with patch.object(ex, "_run_agent_process") as mock_run:
            with pytest.raises(SystemExit):
                executor._invoke_agent({"step": 2, "name": "ui"}, "p")
        mock_run.assert_not_called()

    def test_prompt_comes_from_snapshot(self, executor):
        snap = MagicMock()
        snap.read.return_value = "SNAPSHOT BODY".encode("utf-8")
        executor._approved = types.SimpleNamespace(snapshot=snap)
        with patch.object(ex, "_run_agent_process",
                          return_value=ex.AgentRun(0, "{}", "", False)) as mock_run:
            executor._invoke_agent({"step": 2, "name": "ui"}, "p")
        snap.read.assert_called_once_with("phases/0-mvp/step2.md")
        assert "SNAPSHOT BODY" in mock_run.call_args[1]["input"]
        assert "UI를 구현하세요" not in mock_run.call_args[1]["input"]

    def test_saves_output_and_result(self, executor):
        def agent(argv, **kw):
            (executor._out_dir / "step2-result.json").write_text(
                json.dumps({"status": "completed", "summary": "ui done"}), encoding="utf-8")
            return ex.AgentRun(0, '{"ok": true}', "", False)
        with patch.object(ex, "_run_agent_process", side_effect=agent):
            out = executor._invoke_agent({"step": 2, "name": "ui"}, "preamble")
        assert out["result"] == {"status": "completed", "summary": "ui done"}
        data = json.loads((executor._out_dir / "step2-output.json").read_text(encoding="utf-8"))
        assert data["step"] == 2 and data["exitCode"] == 0 and data["timedOut"] is False

    def test_stale_result_file_is_removed_first(self, executor):
        (executor._out_dir / "step2-result.json").write_text('{"status": "completed"}')
        with patch.object(ex, "_run_agent_process",
                          return_value=ex.AgentRun(0, "{}", "", False)):
            out = executor._invoke_agent({"step": 2, "name": "ui"}, "p")
        assert out["result"] is None

    def test_malformed_result_is_not_completed(self, executor):
        def agent(argv, **kw):
            (executor._out_dir / "step2-result.json").write_text("not json")
            return ex.AgentRun(0, "{}", "", False)
        with patch.object(ex, "_run_agent_process", side_effect=agent):
            out = executor._invoke_agent({"step": 2, "name": "ui"}, "p")
        assert out["result"]["status"] is None

    def test_nonexistent_step_file_exits(self, executor):
        with pytest.raises(SystemExit) as exc_info:
            executor._invoke_agent({"step": 99, "name": "nonexistent"}, "preamble")
        assert exc_info.value.code == 1

    def test_timeout_is_1800(self, executor):
        with patch.object(ex, "_run_agent_process",
                          return_value=ex.AgentRun(0, "{}", "", False)) as mock_run:
            executor._invoke_agent({"step": 2, "name": "ui"}, "preamble")
        assert mock_run.call_args[1]["timeout"] == ex.StepExecutor.STEP_TIMEOUT == 1800

    def test_timeout_marks_output(self, executor):
        with patch.object(ex, "_run_agent_process",
                          return_value=ex.AgentRun(-1, "partial", "", True)):
            output = executor._invoke_agent({"step": 2, "name": "ui"}, "preamble")
        assert output["timedOut"] is True
        data = json.loads((executor._out_dir / "step2-output.json").read_text(encoding="utf-8"))
        assert data["timedOut"] is True and data["stdout"] == "partial"

    def test_timeout_warns_once_without_abnormal_exit(self, executor, capsys):
        with patch.object(ex, "_run_agent_process",
                          return_value=ex.AgentRun(-1, "", "", True)):
            executor._invoke_agent({"step": 2, "name": "ui"}, "preamble")
        out = capsys.readouterr().out
        assert "step 시간 초과" in out and "비정상 종료" not in out

class TestStepTimeout:
    STEP = {"step": 2, "name": "ui"}

    def _run(self, executor, top_index, agent_side_effect):
        with patch.object(executor, "_invoke_agent", side_effect=agent_side_effect) as inv, \
             patch.object(executor, "_commit_step") as commit, \
             patch.object(executor, "_update_top_index") as upd:
            with pytest.raises(SystemExit) as exc:
                executor._execute_single_step(self.STEP, "")
        return exc.value.code, inv, commit, upd

    def _step2(self, executor):
        index = json.loads(executor._index_file.read_text(encoding="utf-8"))
        return next(s for s in index["steps"] if s["step"] == 2)

    def _assert_timeout_error(self, executor, code, inv, commit, upd):
        assert code == 1
        assert inv.call_count == 1
        s = self._step2(executor)
        assert s["status"] == "error"
        assert s["error_message"].startswith("[시간 초과 1800초]")
        assert "나눠" in s["error_message"]
        assert "failed_at" in s
        commit.assert_not_called()
        upd.assert_called_once_with("error")

    def test_timeout_errors_without_retry(self, executor, top_index):
        code, inv, commit, upd = self._run(executor, top_index, [{"timedOut": True}])
        self._assert_timeout_error(executor, code, inv, commit, upd)

    def test_timeout_beats_completed(self, executor, top_index):
        def agent(step, preamble):
            index = json.loads(executor._index_file.read_text(encoding="utf-8"))
            for s in index["steps"]:
                if s["step"] == 2:
                    s["status"] = "completed"
            executor._index_file.write_text(json.dumps(index), encoding="utf-8")
            return {"timedOut": True}

        code, inv, commit, upd = self._run(executor, top_index, agent)
        self._assert_timeout_error(executor, code, inv, commit, upd)

    def test_timeout_line_shows_elapsed_and_guide(self, executor, top_index, capsys):
        # 경과 시간은 progress_indicator 블록을 나간 뒤에야 채워진다(안에서 읽으면 늘 0s).
        def agent(step, preamble):
            import time as _t
            _t.sleep(1.1)
            return {"timedOut": True}

        self._run(executor, top_index, agent)
        out = capsys.readouterr().out
        m = re.search(r"시간 초과 \[(\d+)s\]", out)
        assert m and int(m.group(1)) >= 1
        assert "Error: [시간 초과 1800초]" in out

    @pytest.mark.parametrize("broken", [
        b"",
        b'{"steps": [{"step": 0',
        '{"steps": [{"summary": "프'.encode("utf-8")[:-1],
        None,
    ], ids=["empty", "truncated-json", "truncated-utf8", "deleted"])
    def test_timeout_with_broken_index_uses_snapshot(self, executor, top_index, capsys, broken):
        # 에이전트가 index.json을 다시 쓰다 강제 종료되면 파일이 비거나 잘린다(None은 지워짐).
        # 그래도 실행 직전에 읽은 index로 step error·top index error·분할 안내를 남겨야 한다.
        def agent(step, preamble):
            if broken is None:
                executor._index_file.unlink()
            else:
                executor._index_file.write_bytes(broken)
            return {"timedOut": True}

        code, inv, commit, upd = self._run(executor, top_index, agent)
        self._assert_timeout_error(executor, code, inv, commit, upd)
        assert "Error: [시간 초과 1800초]" in capsys.readouterr().out
        index = json.loads(executor._index_file.read_text(encoding="utf-8"))
        assert [s["status"] for s in index["steps"]] == ["completed", "completed", "error"]


# ---------------------------------------------------------------------------
# progress_indicator (= 이전 Spinner)
# ---------------------------------------------------------------------------

class TestProgressIndicator:
    def test_context_manager(self):
        import time
        with ex.progress_indicator("test") as pi:
            time.sleep(0.15)
        assert pi.elapsed >= 0.1

    def test_elapsed_increases(self):
        import time
        with ex.progress_indicator("test") as pi:
            time.sleep(0.2)
        assert pi.elapsed > 0


# ---------------------------------------------------------------------------
# main() CLI 파싱 (mocked)
# ---------------------------------------------------------------------------

class TestMainCli:
    @pytest.fixture(autouse=True)
    def _no_signal_install(self):
        # main()이 POSIX에서 pytest 프로세스에 SIGTERM·SIGHUP 처리기를 남기지 않게 한다
        with patch.object(ex, "_install_signal_exit"):
            yield

    def test_no_args_exits(self):
        with patch("sys.argv", ["execute.py"]):
            with pytest.raises(SystemExit) as exc_info:
                ex.main()
            assert exc_info.value.code == 2  # argparse exits with 2

    def test_invalid_phase_dir_exits(self):
        with patch("sys.argv", ["execute.py", "nonexistent"]):
            with patch.object(ex, "ROOT", Path("/tmp/fake_nonexistent")):
                with pytest.raises(SystemExit) as exc_info:
                    ex.main()
                assert exc_info.value.code == 1

    def test_missing_index_exits(self, tmp_project):
        (tmp_project / "phases" / "empty").mkdir()
        with patch("sys.argv", ["execute.py", "empty"]):
            with patch.object(ex, "ROOT", tmp_project):
                with pytest.raises(SystemExit) as exc_info:
                    ex.main()
                assert exc_info.value.code == 1

    def _desc(self, task="0-mvp"):
        return {"task": task}

    def test_missing_descriptor_exits_1(self, monkeypatch):
        monkeypatch.setenv("HARNESS_REVIEW_BACKEND", "codex")
        monkeypatch.setenv("HARNESS_REVIEW_MODEL", "gpt-6-astra")
        with patch("sys.argv", ["execute.py", "0-mvp"]), \
                patch.object(ex, "StepExecutor") as se:
            with pytest.raises(SystemExit) as e:
                ex.main()
        assert e.value.code == 1
        se.assert_not_called()

    def test_push_flag_exits_2(self):
        with patch("sys.argv", ["execute.py", "0-mvp", "--push"]), \
                patch.object(ex, "StepExecutor") as se:
            with pytest.raises(SystemExit) as e:
                ex.main()
        assert e.value.code == 2
        se.assert_not_called()

    def test_base_flag_reaches_executor(self):
        with patch("sys.argv", ["execute.py", "0-mvp", "--base", "develop"]), \
                patch.object(ex, "preflight"), \
                patch("runner.load_descriptor", return_value=self._desc()), \
                patch("runner.consume_ticket"), \
                patch.object(ex, "StepExecutor") as se:
            ex.main()
        assert se.call_args.kwargs.get("base") == "develop"
        assert se.call_args.kwargs.get("descriptor") == self._desc()

    def test_missing_ticket_exits_1(self, monkeypatch):
        """descriptor가 있어도 supervisor가 발급한 1회용 ticket 없이는 실행하지 않는다."""
        monkeypatch.delenv("HARNESS_LAUNCH_TICKET", raising=False)
        with patch("sys.argv", ["execute.py", "0-mvp"]), \
                patch.object(ex, "preflight"), \
                patch("runner.load_descriptor", return_value=self._desc()), \
                patch.object(ex, "StepExecutor") as se:
            with pytest.raises(SystemExit) as e:
                ex.main()
        assert e.value.code == 1
        se.assert_not_called()

    def test_descriptor_task_mismatch_exits(self):
        with patch("sys.argv", ["execute.py", "0-mvp"]), \
                patch.object(ex, "preflight"), \
                patch("runner.load_descriptor", return_value=self._desc("other")), \
                patch.object(ex, "StepExecutor") as se:
            with pytest.raises(SystemExit) as e:
                ex.main()
        assert e.value.code == 1
        se.assert_not_called()

    def test_installs_signal_exit_before_run(self):
        calls = []
        with patch("sys.argv", ["execute.py", "0-mvp"]), \
                patch.object(ex, "preflight"), \
                patch("runner.load_descriptor", return_value=self._desc()), \
                patch("runner.consume_ticket"), \
                patch.object(ex, "_install_signal_exit",
                             side_effect=lambda: calls.append("signals")), \
                patch.object(ex, "StepExecutor") as se:
            se.return_value.run.side_effect = lambda: calls.append("run")
            ex.main()
        assert calls == ["signals", "run"]

    def test_run_without_descriptor_fails_closed(self, executor):
        """직접 만든 StepExecutor(descriptor 없음)는 run()에서 즉시 거부한다."""
        with pytest.raises(SystemExit) as e:
            executor.run()
        assert e.value.code == 1

class TestCheckBlockers:
    def _make_executor_with_steps(self, tmp_project, steps):
        d = tmp_project / "phases" / "test-phase"
        d.mkdir(exist_ok=True)
        index = {"project": "T", "phase": "test", "steps": steps}
        (d / "index.json").write_text(json.dumps(index), encoding="utf-8")

        with patch.object(ex, "ROOT", tmp_project):
            inst = ex.StepExecutor.__new__(ex.StepExecutor)
        inst._root = str(tmp_project)
        inst._phases_dir = tmp_project / "phases"
        inst._phase_dir = d
        inst._phase_dir_name = "test-phase"
        inst._index_file = d / "index.json"
        inst._top_index_file = tmp_project / "phases" / "index.json"
        inst._phase_name = "test"
        inst._total = len(steps)
        return inst

    def test_error_step_exits_1(self, tmp_project):
        steps = [
            {"step": 0, "name": "ok", "status": "completed"},
            {"step": 1, "name": "bad", "status": "error", "error_message": "fail"},
        ]
        inst = self._make_executor_with_steps(tmp_project, steps)
        with pytest.raises(SystemExit) as exc_info:
            inst._check_blockers()
        assert exc_info.value.code == 1

    def test_blocked_step_exits_2(self, tmp_project):
        steps = [
            {"step": 0, "name": "ok", "status": "completed"},
            {"step": 1, "name": "stuck", "status": "blocked", "blocked_reason": "API key"},
        ]
        inst = self._make_executor_with_steps(tmp_project, steps)
        with pytest.raises(SystemExit) as exc_info:
            inst._check_blockers()
        assert exc_info.value.code == 2


# ---------------------------------------------------------------------------
# needs-review 상태 + 종료코드 3 (파트 2A — 리뷰 게이트)
# ---------------------------------------------------------------------------

class TestNeedsReview:
    def test_update_top_index_needs_review(self, executor, top_index):
        executor._top_index_file = top_index
        executor._update_top_index("needs-review")
        data = json.loads(top_index.read_text(encoding="utf-8"))
        mvp = next(p for p in data["phases"] if p["dir"] == "0-mvp")
        assert mvp["status"] == "needs-review"
        assert "review_at" in mvp

    def test_mark_needs_review_exits_3(self, executor, top_index):
        executor._top_index_file = top_index
        with pytest.raises(SystemExit) as exc:
            executor._mark_needs_review("critical finding")
        assert exc.value.code == 3

    def test_mark_needs_review_sets_task_status(self, executor, top_index):
        executor._top_index_file = top_index
        with pytest.raises(SystemExit):
            executor._mark_needs_review("critical finding")
        idx = json.loads(executor._index_file.read_text(encoding="utf-8"))
        assert idx.get("status") == "needs-review"
        assert idx.get("review_reason") == "critical finding"


# ---------------------------------------------------------------------------
# needs-review 로 막힌 phase 는 재개를 거부한다
# ---------------------------------------------------------------------------

class TestNeedsReviewBlocksResume:
    def _mark(self, executor, **extra):
        idx = json.loads(executor._index_file.read_text(encoding="utf-8"))
        idx["status"] = "needs-review"
        idx["review_reason"] = "critical finding"
        idx["review_at"] = "2026-07-31T12:00:00+0900"
        idx.update(extra)
        executor._index_file.write_text(json.dumps(idx), encoding="utf-8")

    def test_check_blockers_exits_3_when_phase_needs_review(self, executor):
        """사람이 리뷰를 판단하기 전에 재실행하면 review.json 을 덮어쓴다."""
        self._mark(executor)
        with pytest.raises(SystemExit) as exc:
            executor._check_blockers()
        assert exc.value.code == 3

    def test_check_blockers_passes_when_phase_status_reset(self, executor):
        """사람이 pending/completed 로 되돌리면 재개된다."""
        self._mark(executor)
        idx = json.loads(executor._index_file.read_text(encoding="utf-8"))
        idx["status"] = "pending"
        executor._index_file.write_text(json.dumps(idx), encoding="utf-8")
        executor._check_blockers()  # 종료하지 않아야 한다

    def test_check_blockers_passes_when_no_phase_status(self, executor):
        """status 필드가 없는 기존 phase 는 그대로 통과한다(하위호환)."""
        executor._check_blockers()

    def test_candidate_clears_review_fields(self, executor, top_index):
        """candidate(완료 metadata) commit은 낡은 needs-review 흔적을 남기지 않는다."""
        executor._top_index_file = top_index
        executor._gate = lambda where: None
        calls = []

        def fake_git(*args):
            calls.append(args)
            if args[:1] == ("status",):
                n = sum(1 for c in calls if c[:1] == ("status",))
                out = " M phases/0-mvp/index.json\0" if n == 1 else ""
                return MagicMock(returncode=0, stdout=out, stderr="")
            if args[:2] == ("diff", "--cached"):
                return MagicMock(returncode=1)
            return MagicMock(returncode=0, stdout="d" * 40 + "\n", stderr="")
        executor._run_git = fake_git
        self._mark(executor)
        executor._make_candidate()
        idx = json.loads(executor._index_file.read_text(encoding="utf-8"))
        assert idx.get("status") == "completed"
        assert "review_reason" not in idx and "review_at" not in idx
        commits = [c for c in calls if "commit" in c]
        assert len(commits) == 1 and "mark phase completed" in commits[0][-1]
        assert executor._candidate_sha == "d" * 40


# ---------------------------------------------------------------------------
# 리뷰 1단 — 구조화 review.json 생성 + 모델 선택 (파트 2A)
# ---------------------------------------------------------------------------

_REAL_RUN = subprocess.run  # patch("subprocess.run") 안에서도 진짜 git을 부르기 위해
BASE_SHA = "b" * 40
CLEAN = {"status": "complete", "findings": []}
_OUT_RE = re.compile(r"^RESULT_NAME: (\S+)$", re.M)
_HEAD = "c" * 40


def _f(severity, file="a.py", line=1, title="t", detail="d"):
    """리뷰 결과 스키마의 finding 하나."""
    return {"severity": severity, "file": file, "line": line,
            "title": title, "detail": detail}


def _fake_git(files=None, *, calls=None, head="c" * 40, recount=None):
    """_run_git 대역. diff --numstat/--name-status(-z)만 흉내 낸다.

    files: (path, added, deleted, status[, old_path]) — added/deleted가
    None이면 바이너리('-'). status는 git name-status 글자(A/M/D/R100).
    recount: {path: added} — -z 없는 numstat(리뷰어 명령과 같은 묶음 재계산)이
    manifest와 다르게 세는 상황을 만든다. pathspec(`--` 뒤)만 센다.
    """
    files = files if files is not None else [("a.py", 10, 0, "M")]

    def plain_numstat(spec):
        out = []
        for f in files:
            path, a, d = f[:3]
            old = f[4] if len(f) > 4 else None
            if spec is not None and path not in spec and old not in spec:
                continue
            a = (recount or {}).get(path, a)
            out.append(f"{'-' if a is None else a}\t{'-' if d is None else d}\t{path}\n")
        return "".join(out)

    def numstat():
        out = []
        for f in files:
            path, a, d, _st = f[:4]
            old = f[4] if len(f) > 4 else None
            a_s = "-" if a is None else str(a)
            d_s = "-" if d is None else str(d)
            out.append(f"{a_s}\t{d_s}\t\0{old}\0{path}\0" if old
                       else f"{a_s}\t{d_s}\t{path}\0")
        return "".join(out)

    def name_status():
        out = []
        for f in files:
            path, _a, _d, st = f[:4]
            old = f[4] if len(f) > 4 else None
            out.append(f"{st}\0{old}\0{path}\0" if old else f"{st}\0{path}\0")
        return "".join(out)

    def run(*args):
        if calls is not None:
            calls.append(args)
        if "--numstat" in args and "-z" not in args:
            spec = set(args[args.index("--") + 1:]) if "--" in args else None
            return MagicMock(returncode=0, stdout=plain_numstat(spec), stderr="")
        if "--numstat" in args:
            return MagicMock(returncode=0, stdout=numstat(), stderr="")
        if "--name-status" in args:
            return MagicMock(returncode=0, stdout=name_status(), stderr="")
        if args[:2] == ("rev-parse", "HEAD"):
            return MagicMock(returncode=0, stdout=head + "\n", stderr="")
        return MagicMock(returncode=0, stdout="", stderr="")
    return run


def _arm_review(executor, files=None, *, calls=None, exclude=None, recount=None):
    """리뷰 단계를 돌릴 수 있게 한다: 고정된 기준 SHA + 가짜 diff.

    descriptor에 묶인 _gate/_run_tests/_sandboxed는 여기서 무력화한다 — 리뷰 회차 로직만
    단위로 본다. 그 게이트 자체는 test_execute_gates.py가 실제 spawn·sandbox로 검증한다.
    """
    idx = json.loads(executor._index_file.read_text(encoding="utf-8"))
    idx["baseBranch"] = "develop"
    idx["reviewBaseSha"] = BASE_SHA
    if exclude is not None:
        idx["reviewExclude"] = exclude
    executor._index_file.write_text(json.dumps(idx, ensure_ascii=False), encoding="utf-8")
    executor._run_git = _fake_git(files, calls=calls, recount=recount)
    executor._gate = lambda where: None
    executor._sandboxed = lambda argv: list(argv)

    def fake_tests():
        executor._tested_sha = executor._head()
    executor._run_tests = fake_tests


_FIX_RE = re.compile(r"^RESULT_FILE: (\S+)$", re.M)


def _astra(obj, head=_HEAD):
    """리뷰 결과 dict에 strict 계약 필드(reviewed_head·review_model)를 채운다."""
    if isinstance(obj, dict) and obj.get("status") == "complete":
        obj = dict(obj)
        obj.setdefault("reviewed_head", head)
        obj.setdefault("review_model", "gpt-6-astra")
    return obj


def _reviewers(executor, respond=None, *, calls=None, fixer=None):
    """subprocess.run 대역. git은 진짜로 넘기고, 리뷰어·수정 에이전트 호출만 가짜로 받는다.

    리뷰어(codex)는 파일을 쓰지 않고 stdout JSON으로 답한다 — 하네스가 evidence로 기록한다.
    respond(prompt, out)가 dict/str을 돌려주면 그 내용이 stdout이 되고(dict면 reviewed_head·
    review_model을 채운다), None이면 빈 stdout(결과 누락)이다.
    fixer(prompt, out)는 수정 에이전트(프롬프트에 RESULT_FILE)를 받는다 — 저장소를 바꾸고
    결과 JSON(dict) 또는 None(결과 없음)을 돌려준다.
    """
    def fake_run(cmd, **kw):
        if cmd and cmd[0] == "git":
            return _REAL_RUN(cmd, **kw)
        prompt = kw.get("input", "")
        m = _OUT_RE.search(prompt)
        if not m:
            fm = _FIX_RE.search(prompt)
            assert fm and fixer is not None, "예상하지 못한 에이전트 호출"
            out = Path(fm.group(1))
            obj = fixer(prompt, out)
            if obj is not None:
                out.write_text(json.dumps(obj, ensure_ascii=False), encoding="utf-8")
            return MagicMock(returncode=0, stdout="{}", stderr="")
        assert cmd[:2] == ["codex", "exec"], cmd
        if calls is not None:
            calls.append(prompt)
        out = executor._review_dir / m.group(1)
        obj = respond(prompt, out) if respond else CLEAN
        if obj is None:
            return MagicMock(returncode=0, stdout="", stderr="")
        hm = re.search(r"^REVIEWED_HEAD: (\S+)$", prompt, re.M)
        stdout = obj if isinstance(obj, str) else json.dumps(
            _astra(obj, hm.group(1) if hm else _HEAD), ensure_ascii=False)
        return MagicMock(returncode=0, stdout=stdout, stderr="")
    return fake_run


def _reviewer_writes(executor, obj=None, captured=None, *, then=None):
    """첫 리뷰 호출에 obj(기본 CLEAN)를, 그 뒤 호출(수정 후 재리뷰)에는
    then(기본 obj와 같음)을 답하는 대역."""
    payload = obj if obj is not None else CLEAN
    later = then if then is not None else payload
    n = {"i": 0}
    def respond(prompt, out):
        if captured is not None:
            captured["input"] = prompt
        n["i"] += 1
        return payload if n["i"] == 1 else later
    return _reviewers(executor, respond)


class TestReviewArgv:
    """(구 HARNESS_REVIEW_MODEL·/code-review 플러그인 시험 대체) 리뷰어는 항상
    codex gpt-6-astra read-only이며 stdout strict JSON 계약을 프롬프트에 싣는다."""

    @pytest.mark.parametrize("model", [None, "claude-sonnet-5", "o3"])
    def test_review_argv_ignores_env_model(self, monkeypatch, model):
        if model:
            monkeypatch.setenv("HARNESS_REVIEW_MODEL", model)
        argv = ex.build_code_review_argv()
        assert argv[argv.index("--model") + 1] == "gpt-6-astra"
        assert argv[argv.index("--sandbox") + 1] == "read-only"

    def _prompt(self, executor):
        captured = {}
        _arm_review(executor)
        with patch("subprocess.run",
                   side_effect=_reviewer_writes(executor, captured=captured)):
            executor._run_review()
        return captured["input"]

    def test_prompt_requires_strict_stdout_contract(self, executor):
        prompt = self._prompt(executor)
        assert f"REVIEWED_HEAD: {_HEAD}" in prompt
        assert '"review_model": "gpt-6-astra"' in prompt
        assert '"status": "complete"' in prompt
        assert "stdout" in prompt and "파일을 쓰지 마라" in prompt
        assert "degraded" in prompt

    def test_prompt_has_review_criteria_and_schema(self, executor):
        prompt = self._prompt(executor)
        assert "correctness" in prompt and "보안" in prompt
        assert "severity" in prompt and "detail" in prompt
        assert "RESULT_NAME: review-bundle-1.json" in prompt

    def test_reviewer_is_invoked_as_codex(self, executor):
        cmds = []
        _arm_review(executor)
        fake = _reviewers(executor)

        def spy(cmd, **kw):
            if cmd[0] != "git":
                cmds.append(cmd)
            return fake(cmd, **kw)
        with patch("subprocess.run", side_effect=spy):
            executor._run_review()
        assert cmds and all(c == ex.build_code_review_argv() for c in cmds)

class TestReviewGate:
    def _seed_review(self, executor, obj):
        (executor._phase_dir / "review.json").write_text(
            json.dumps(obj, ensure_ascii=False), encoding="utf-8")

    def test_critical_marks_needs_review(self, executor, top_index, monkeypatch):
        executor._no_git = False
        executor._top_index_file = top_index
        _arm_review(executor)
        monkeypatch.delenv("HARNESS_REVIEW_MODEL", raising=False)
        reached = {"fix": False}
        executor._apply_review_fixes = lambda f: reached.__setitem__("fix", True)
        with patch("subprocess.run", side_effect=_reviewer_writes(executor, {
                "status": "complete", "findings": [_f("critical")]})):
            with pytest.raises(SystemExit) as exc:
                executor._run_review()
        assert exc.value.code == 3
        # critical 분기로 막혔음을 확인 — 리뷰 실패 경로로 exit 3이 나면
        # 이 테스트는 critical 로직을 한 줄도 검증하지 못한다.
        assert reached["fix"] is False, "critical은 수정 단계 전에 막아야 한다"

    def test_minor_only_calls_fixer(self, executor, monkeypatch):
        executor._no_git = False
        _arm_review(executor)
        monkeypatch.delenv("HARNESS_REVIEW_MODEL", raising=False)
        called = {"fix": False}
        def fake_fix(findings):
            called["fix"] = True
            return None  # 성공
        executor._apply_review_fixes = fake_fix
        with patch("subprocess.run", side_effect=_reviewer_writes(executor, {
                "status": "complete", "findings": [_f("minor")]}, then=CLEAN)):
            executor._run_review()
        assert called["fix"] is True

    def test_clean_skips_fixer(self, executor, monkeypatch):
        executor._no_git = False
        _arm_review(executor)
        monkeypatch.delenv("HARNESS_REVIEW_MODEL", raising=False)
        called = {"fix": False}
        executor._apply_review_fixes = lambda f: called.__setitem__("fix", True)
        with patch("subprocess.run", side_effect=_reviewer_writes(executor)):
            executor._run_review()
        assert called["fix"] is False

    def test_nit_is_not_sent_to_fixer(self, executor, monkeypatch):
        """플러그인의 nit(스타일/네이밍)은 자동 수정 대상이 아니다.

        하네스 분기는 critical/major/minor만 알았다. nit이 그대로 흘러가면
        저자가 거절할 수 있는 취향 지적에 수정 에이전트가 코드를 건드린다.
        """
        executor._no_git = False
        _arm_review(executor)
        monkeypatch.delenv("HARNESS_REVIEW_MODEL", raising=False)
        called = {"fix": False}
        executor._apply_review_fixes = lambda f: called.__setitem__("fix", True)
        with patch("subprocess.run", side_effect=_reviewer_writes(executor, {
                "status": "complete", "findings": [_f("nit", title="네이밍")]})):
            executor._run_review()
        assert called["fix"] is False, "nit만 있으면 수정 에이전트를 부르지 않는다"

    def test_nit_filtered_out_of_mixed_findings(self, executor, monkeypatch):
        """major와 nit이 섞이면 major만 수정 대상으로 넘긴다."""
        executor._no_git = False
        _arm_review(executor)
        monkeypatch.delenv("HARNESS_REVIEW_MODEL", raising=False)
        passed = {}
        executor._apply_review_fixes = lambda f: passed.__setitem__("f", f)
        with patch("subprocess.run", side_effect=_reviewer_writes(executor, {
                "status": "complete", "findings": [
                    _f("major", "a.py", title="진짜 버그"),
                    _f("nit", "b.py", title="네이밍")]}, then=CLEAN)):
            executor._run_review()
        sevs = [x["severity"] for x in passed["f"]]
        assert sevs == ["major"], f"nit이 걸러지지 않았다: {sevs}"

    def test_missing_plugin_blocks_phase(self, executor, top_index, monkeypatch):
        """플러그인 미설치로 리뷰가 실패하면 phase를 막는다 — 조용히 통과 금지.

        '플러그인 필수' 결정의 핵심. 리뷰 없이 phase가 성공으로 남으면
        리뷰되지 않은 코드가 통과한다(오늘 nudge에서 고친 조용한 실패와 동류).
        """
        executor._no_git = False
        executor._top_index_file = top_index
        _arm_review(executor)
        monkeypatch.delenv("HARNESS_REVIEW_MODEL", raising=False)
        # 리뷰 에이전트가 review.json을 남기지 못한 상태(플러그인 없음)
        with patch("subprocess.run",
                   return_value=MagicMock(returncode=0, stdout="", stderr="")):
            with pytest.raises(SystemExit) as exc:
                executor._run_review()
        assert exc.value.code == 3

    def test_withheld_status_is_reported_as_withheld_verdict(self, executor, top_index,
                                                             monkeypatch, capsys):
        """리뷰어가 status≠complete로 사유만 남기면 '판정 보류'로 알린다.

        /code-review는 범위를 다 보지 못하면(범위 축소 요청·DEGRADED) 판정 없이
        사유만 남긴다. 이를 '플러그인 설치 확인 필요'로 알리면 사람이 엉뚱한
        곳(설치)을 고친다 — 0-foundation phase 끝 리뷰에서 실제로 오판했다.
        """
        executor._no_git = False
        executor._top_index_file = top_index
        _arm_review(executor)
        monkeypatch.delenv("HARNESS_REVIEW_MODEL", raising=False)
        with patch("subprocess.run", side_effect=_reviewer_writes(executor, {
                "status": "withheld", "reason": "범위 축소 요청", "findings": []})):
            with pytest.raises(SystemExit) as exc:
                executor._run_review()
        assert exc.value.code == 3
        reason = json.loads(executor._index_file.read_text(encoding="utf-8"))["review_reason"]
        assert "판정 보류" in reason and "review.md" in reason
        assert "플러그인" not in reason
        assert "플러그인" not in capsys.readouterr().out
        md = (executor._phase_dir / "review.md").read_text(encoding="utf-8")
        assert "범위 축소 요청" in md, "사람이 읽을 기록에 리뷰어 사유가 남아야 한다"

    def test_empty_reviewer_stdout_blocks(self, executor, top_index):
        """(구 플러그인 미설치 시험 대체) 리뷰어가 아무것도 내지 않으면 needs-review."""
        executor._top_index_file = top_index
        _arm_review(executor)
        with patch("subprocess.run",
                   return_value=MagicMock(returncode=0, stdout="", stderr="")):
            with pytest.raises(SystemExit) as e:
                executor._run_review()
        assert e.value.code == 3
        reason = json.loads(executor._index_file.read_text(encoding="utf-8"))["review_reason"]
        assert "결과를 읽을 수 없음" in reason

    def test_stale_review_json_does_not_pass_gate(self, executor, top_index, monkeypatch):
        """이전 실행이 남긴 review.json으로 게이트를 통과하면 안 된다.

        exists()만 보면, 리뷰 에이전트가 이번에 아무것도 생성하지 않아도
        낡은 결과를 신뢰해 통과한다 — '플러그인 필수' 차단을 우회하는 구멍.
        """
        executor._no_git = False
        executor._top_index_file = top_index
        _arm_review(executor)
        monkeypatch.delenv("HARNESS_REVIEW_MODEL", raising=False)
        # 이전 실행이 남긴 clean 결과(최종본과 묶음 결과 둘 다)
        self._seed_review(executor, CLEAN)
        (executor._phase_dir / "review-bundle-1.json").write_text(
            json.dumps(CLEAN), encoding="utf-8")
        # 이번 리뷰 에이전트는 아무 파일도 쓰지 않는다(플러그인 없음)
        with patch("subprocess.run",
                   return_value=MagicMock(returncode=0, stdout="", stderr="")):
            with pytest.raises(SystemExit) as exc:
                executor._run_review()
        assert exc.value.code == 3, "낡은 review.json으로 통과하면 안 된다"

    def test_unlink_failure_blocks_phase(self, executor, top_index, monkeypatch):
        """낡은 review.json 삭제가 실패하면 막는다.

        삼키면 낡은 결과가 남아 이번 리뷰로 오인된다 — stale 구멍이 부활한다.
        """
        executor._no_git = False
        executor._top_index_file = top_index
        _arm_review(executor)
        monkeypatch.delenv("HARNESS_REVIEW_MODEL", raising=False)
        self._seed_review(executor, CLEAN)
        with patch.object(Path, "unlink", side_effect=OSError("locked")):
            with pytest.raises(SystemExit) as exc:
                executor._run_review()
        assert exc.value.code == 3

    @pytest.mark.parametrize("exc", [
        FileNotFoundError("claude not found"),
        OSError("exec format error"),
        subprocess.TimeoutExpired("claude", 900),
    ])
    def test_spawn_failure_blocks_phase(self, executor, top_index, monkeypatch, exc):
        """리뷰 에이전트를 띄우지 못해도 needs-review로 막는다.

        예외가 그대로 올라가면 phase 상태가 갱신되지 않은 채 실행기가 죽는다
        — 막지도, 통과시키지도 않은 어중간한 상태가 남는다.
        """
        executor._no_git = False
        executor._top_index_file = top_index
        _arm_review(executor)
        monkeypatch.delenv("HARNESS_REVIEW_MODEL", raising=False)
        with patch("subprocess.run", side_effect=exc):
            with pytest.raises(SystemExit) as e:
                executor._run_review()
        assert e.value.code == 3

    def test_review_agent_failure_blocks_phase(self, executor, top_index, monkeypatch):
        """리뷰 에이전트 자체가 실패해도 막는다(비차단이던 동작을 뒤집는다)."""
        executor._no_git = False
        executor._top_index_file = top_index
        _arm_review(executor)
        monkeypatch.delenv("HARNESS_REVIEW_MODEL", raising=False)
        with patch("subprocess.run",
                   return_value=MagicMock(returncode=1, stdout="", stderr="not found")):
            with pytest.raises(SystemExit) as exc:
                executor._run_review()
        assert exc.value.code == 3

    def test_harness_writes_review_md_and_merged_json(self, executor, monkeypatch):
        """사람이 읽을 review.md와 합친 review.json은 하네스가 직접 쓴다.

        예전엔 리뷰어가 두 파일을 다 써야 했고, 마크다운이 빠지면 막았다.
        이제 리뷰어는 묶음 결과 JSON만 쓰고, 최종 기록은 하네스가 남기므로
        에이전트가 중간에 죽어도 기록이 빠진 채 통과하는 일이 없다.
        """
        executor._no_git = False
        _arm_review(executor)
        monkeypatch.delenv("HARNESS_REVIEW_MODEL", raising=False)
        with patch("subprocess.run", side_effect=_reviewer_writes(executor, {
                "status": "complete", "findings": [_f("nit", title="이름")]})):
            executor._run_review()
        md = (executor._phase_dir / "review.md").read_text(encoding="utf-8")
        merged = json.loads((executor._phase_dir / "review.json").read_text(encoding="utf-8"))
        assert f"{BASE_SHA}...HEAD" in md
        assert "이름" in md
        assert merged["status"] == "complete"
        assert [f["title"] for f in merged["findings"]] == ["이름"]

    def test_malformed_review_json_blocks_phase(self, executor, top_index, monkeypatch):
        """깨진 review.json을 clean으로 읽으면 안 된다.

        파싱 실패를 삼키고 빈 findings를 돌려주면, 리뷰가 실제로 무엇을
        찾았든 phase가 조용히 통과한다. 조용한 실패 금지(CLAUDE.md).
        """
        executor._no_git = False
        executor._top_index_file = top_index
        _arm_review(executor)
        monkeypatch.delenv("HARNESS_REVIEW_MODEL", raising=False)
        with patch("subprocess.run",
                   side_effect=_reviewers(executor, lambda p, o: "{findings: [")):
            with pytest.raises(SystemExit) as exc:
                executor._run_review()
        assert exc.value.code == 3, "깨진 review.json이 clean으로 통과했다"

    def test_fixer_revalidation_fail_marks_needs_review(self, executor, top_index, monkeypatch):
        executor._no_git = False
        executor._top_index_file = top_index
        _arm_review(executor)
        monkeypatch.delenv("HARNESS_REVIEW_MODEL", raising=False)
        reached = {"fix": False}
        def failing_fix(findings):
            reached["fix"] = True
            return "AC 재검증 실패: npm test"  # 실패 사유
        executor._apply_review_fixes = failing_fix
        with patch("subprocess.run", side_effect=_reviewer_writes(executor, {
                "status": "complete", "findings": [_f("major")]})):
            with pytest.raises(SystemExit) as exc:
                executor._run_review()
        assert exc.value.code == 3
        assert reached["fix"] is True, "수정 단계까지 도달해야 이 경로를 검증한다"


# ---------------------------------------------------------------------------
# 리뷰 기준 고정 + 3,000줄 초과 자동 분할
# (설계: docs/superpowers/specs/2026-10-23-harness-review-split-design.md)
# ---------------------------------------------------------------------------

def _idx(executor):
    return json.loads(executor._index_file.read_text(encoding="utf-8"))


def _set_idx(executor, **fields):
    idx = _idx(executor)
    idx.update(fields)
    executor._index_file.write_text(json.dumps(idx, ensure_ascii=False), encoding="utf-8")


def _manifest(executor):
    return json.loads((executor._review_dir / "review-manifest.json").read_text(encoding="utf-8"))


def _out_name(prompt):
    return _OUT_RE.search(prompt).group(1).rsplit("/", 1)[-1]


class TestReviewBase:
    """동작 1 — 비교 기준은 명시한 브랜치에서 한 번 정해 index.json에 고정한다."""

    def test_no_base_anywhere_exits_before_checkout(self, executor, capsys):
        calls = []
        _branch_git(executor, calls=calls)
        with pytest.raises(SystemExit) as e:
            executor._require_base()
        assert e.value.code == 1
        assert not any(a[0] == "checkout" for a in calls)
        assert "기준 브랜치" in capsys.readouterr().out

    def test_no_base_runs_no_step(self, executor):
        """브랜치가 있다는 이유만으로 develop·main을 고르지 않는다 — step 전에 멈춘다."""
        _branch_git(executor)
        ran = []
        executor._invoke_agent = lambda *a, **k: ran.append(a)
        with pytest.raises(SystemExit) as e:
            executor.run()
        assert e.value.code == 1
        assert ran == []

    def test_cli_base_pins_merge_base(self, executor):
        executor._cli_base = "develop"
        _branch_git(executor, merge_base="d" * 40)
        executor._require_base()
        idx = _idx(executor)
        assert idx["reviewBaseSha"] == "d" * 40
        assert "baseBranch" not in idx, "baseBranch는 계획의 불변 필드 — 하네스가 쓰지 않는다"

    def test_index_base_branch_used_without_cli(self, executor):
        _set_idx(executor, baseBranch="develop")
        calls = []
        _branch_git(executor, merge_base="e" * 40, calls=calls)
        executor._require_base()
        assert ("merge-base", "--is-ancestor", "develop", "HEAD") in calls
        assert _idx(executor)["reviewBaseSha"] == "e" * 40

    def test_stored_sha_is_reused(self, executor):
        _set_idx(executor, baseBranch="develop", reviewBaseSha="1" * 40)
        executor._cli_base = "develop"
        calls = []
        _branch_git(executor, on="feat-mvp", merge_base="2" * 40, calls=calls)
        executor._require_base()
        assert _idx(executor)["reviewBaseSha"] == "1" * 40
        assert not any(a[0] == "merge-base" and "--is-ancestor" not in a for a in calls), \
            "저장된 기준 SHA를 다시 계산하면 안 된다"

    def test_cli_base_differs_from_stored_exits(self, executor):
        _set_idx(executor, baseBranch="develop", reviewBaseSha="1" * 40)
        executor._cli_base = "main"
        calls = []
        _branch_git(executor, calls=calls)
        with pytest.raises(SystemExit) as e:
            executor._require_base()
        assert e.value.code == 1
        assert not any(a[0] == "checkout" for a in calls)

    def test_start_not_containing_base_exits(self, executor):
        executor._cli_base = "develop"
        calls = []
        _branch_git(executor, ancestor=1, calls=calls)
        with pytest.raises(SystemExit) as e:
            executor._require_base()
        assert e.value.code == 1
        assert not any(a[0] == "checkout" for a in calls)
        assert "reviewBaseSha" not in _idx(executor)

    def test_never_checks_out_and_checks_current_head(self, executor):
        """(구 '기존 브랜치 검사' 대체) 자동 branch 전환 없음 — 현재 HEAD만 검사한다."""
        executor._cli_base = "develop"
        calls = []
        _branch_git(executor, on="main", branch_exists=True, calls=calls)
        executor._require_base()
        assert ("merge-base", "--is-ancestor", "develop", "HEAD") in calls
        assert not any(a[0] in ("checkout", "switch", "branch") for a in calls)

    def test_base_must_match_descriptor(self, executor):
        executor._cli_base = "develop"
        executor._desc = {"baseBranch": "main"}
        _branch_git(executor)
        with pytest.raises(SystemExit) as e:
            executor._require_base()
        assert e.value.code == 1

    def test_unknown_base_branch_exits(self, executor):
        executor._cli_base = "nope"
        _branch_git(executor, ancestor=128)
        with pytest.raises(SystemExit) as e:
            executor._require_base()
        assert e.value.code == 1


class TestNoHeadFallback:
    def test_missing_base_sha_blocks_without_head1(self, executor, top_index):
        """기준 SHA가 없으면 HEAD~1로 대신 리뷰하지 않고 막는다.

        HEAD~1 폴백은 여러 step 중 마지막 커밋만 리뷰하는 구멍이었다.
        """
        executor._top_index_file = top_index
        executor._no_git = False
        gcalls, prompts = [], []
        executor._run_git = _fake_git(calls=gcalls)
        with patch("subprocess.run", side_effect=_reviewers(executor, calls=prompts)):
            with pytest.raises(SystemExit) as e:
                executor._run_review()
        assert e.value.code == 3
        assert not any("HEAD~1" in a for call in gcalls for a in call)
        assert prompts == []
        assert "reviewBaseSha" in _idx(executor)["review_reason"]


def _git_ok(repo, *args):
    r = _REAL_RUN(["git", "-c", "user.email=t@example.com", "-c", "user.name=t",
                   "-c", "commit.gpgsign=false", "-c", "core.hooksPath=no-hooks",
                   "-c", "core.autocrlf=false", *args],
                  cwd=str(repo), capture_output=True, text=True, encoding="utf-8")
    assert r.returncode == 0, r.stderr
    return r.stdout.strip()


def _commit_all(repo, msg):
    _git_ok(repo, "add", "-A")
    _git_ok(repo, "commit", "-q", "--no-verify", "-m", msg)


@pytest.fixture
def git_repo(executor, tmp_project):
    """tmp_project를 진짜 git 저장소로 만든다: main(init) ← develop(dev.txt)."""
    _git_ok(tmp_project, "init", "-q")
    _git_ok(tmp_project, "symbolic-ref", "HEAD", "refs/heads/main")
    _commit_all(tmp_project, "init")
    _git_ok(tmp_project, "checkout", "-q", "-b", "develop")
    (tmp_project / "dev.txt").write_text("dev\n", encoding="utf-8")
    _commit_all(tmp_project, "dev")
    _arm_real(executor)
    return tmp_project


def _arm_real(executor):
    """진짜 git으로 리뷰 회차를 돌린다. descriptor에 묶인 게이트·sandbox 테스트만 대역
    (그 게이트 자체는 test_execute_gates.py가 실제 spawn으로 검증)."""
    executor._gate = lambda where: None
    executor._sandboxed = lambda argv: list(argv)
    # 운영처럼 리뷰 evidence·에이전트 출력은 repo 밖에 둔다(작업 트리를 더럽히지 않는다)
    outside = Path(os.path.realpath(tempfile.mkdtemp(prefix="harness-ev-")))  # descriptor처럼 realpath
    executor._review_dir = outside / "code-review"
    executor._out_dir = outside / "out"

    def fake_tests():
        executor._tested_sha = executor._head()
    executor._run_tests = fake_tests


def _on_feature(executor, repo, branch="feat-mvp"):
    """runner가 독립 clone을 승인 branch에 올려 둔 상태를 만든 뒤 기준을 고정한다."""
    r = _REAL_RUN(["git", "rev-parse", "--verify", "-q", branch], cwd=str(repo),
                  capture_output=True, text=True)
    _git_ok(repo, "checkout", "-q", *(["-b"] if r.returncode else []), branch)
    executor._require_base()


class TestReviewBaseRealGit:
    def test_pins_merge_base_then_reuses_after_base_moves(self, executor, git_repo):
        dev_tip = _git_ok(git_repo, "rev-parse", "develop")
        executor._cli_base = "develop"
        _on_feature(executor, git_repo)
        assert _git_ok(git_repo, "rev-parse", "--abbrev-ref", "HEAD") == "feat-mvp"
        assert _idx(executor)["reviewBaseSha"] == dev_tip
        (git_repo / "work.txt").write_text("work\n", encoding="utf-8")
        _commit_all(git_repo, "work")
        # develop이 앞으로 가고 작업 브랜치가 그걸 병합하면 merge-base가 바뀐다
        _git_ok(git_repo, "checkout", "-q", "develop")
        (git_repo / "dev2.txt").write_text("dev2\n", encoding="utf-8")
        _commit_all(git_repo, "dev2")
        _git_ok(git_repo, "checkout", "-q", "feat-mvp")
        _git_ok(git_repo, "merge", "-q", "--no-edit", "develop")
        assert _git_ok(git_repo, "merge-base", "develop", "HEAD") != dev_tip
        executor._cli_base = "develop"  # 재개(baseBranch는 승인 계획 값과 같다)
        executor._require_base()
        assert _idx(executor)["reviewBaseSha"] == dev_tip, "재개 때 기준을 다시 잡으면 안 된다"

    def test_start_without_base_tip_exits_and_switches_nothing(self, executor, git_repo):
        _git_ok(git_repo, "checkout", "-q", "main")  # develop의 커밋이 없다
        executor._cli_base = "develop"
        with pytest.raises(SystemExit) as e:
            executor._require_base()
        assert e.value.code == 1
        assert _git_ok(git_repo, "rev-parse", "--abbrev-ref", "HEAD") == "main"
        r = _REAL_RUN(["git", "rev-parse", "--verify", "-q", "feat-mvp"],
                      cwd=str(git_repo), capture_output=True, text=True)
        assert r.returncode != 0, "브랜치를 만들거나 전환하면 안 된다"


class TestReviewManifestRealGit:
    def test_manifest_lists_deleted_renamed_binary(self, executor, git_repo):
        body = "".join(f"line {i}\n" for i in range(40))
        (git_repo / "keep.txt").write_text("a\n", encoding="utf-8")
        (git_repo / "gone.txt").write_text("bye\n", encoding="utf-8")
        (git_repo / "old_name.py").write_text(body, encoding="utf-8")
        _commit_all(git_repo, "files on develop")
        executor._cli_base = "develop"
        _on_feature(executor, git_repo)
        (git_repo / "keep.txt").write_text("a\nb\n", encoding="utf-8")
        (git_repo / "gone.txt").unlink()
        _git_ok(git_repo, "mv", "old_name.py", "new_name.py")
        (git_repo / "img.bin").write_bytes(b"\x00\x01\x02binary\x00")
        (git_repo / "한글 파일.md").write_text("내용\n", encoding="utf-8")
        _commit_all(git_repo, "phase work")
        prompts = []
        with patch("subprocess.run", side_effect=_reviewers(executor, calls=prompts)):
            executor._run_review()
        m = _manifest(executor)
        by = {f["path"]: f for f in m["files"]}
        assert by["gone.txt"]["status"] == "deleted"
        assert by["new_name.py"]["status"] == "renamed"
        assert by["new_name.py"]["oldPath"] == "old_name.py"
        assert by["img.bin"]["binary"] is True
        assert by["keep.txt"]["status"] == "modified" and by["keep.txt"]["added"] == 1
        assert "한글 파일.md" in by, "non-ASCII 경로가 깨지면 안 된다"
        assert m["reviewBaseSha"] == _git_ok(git_repo, "rev-parse", "develop")
        # 전부 리뷰 묶음에 배정되고 리뷰어에게 넘어간다(rename은 옛 경로도 함께)
        assert all(f["bundle"] == 1 for f in m["files"])
        for p in ("gone.txt", "new_name.py", "old_name.py", "img.bin", "keep.txt", "한글 파일.md"):
            assert p in prompts[0]


class TestReviewSplit:
    """동작 2·3 — 크기 판정, manifest, 자동 분할, 교차 리뷰."""

    SPLIT = [("src/a.ts", 1500, 0, "M"), ("src/b.ts", 1501, 0, "M")]

    def test_3000_added_is_one_code_review(self, executor):
        prompts = []
        _arm_review(executor, [("src/a.ts", 2000, 0, "M"), ("src/b.ts", 1000, 5, "M")])
        with patch("subprocess.run", side_effect=_reviewers(executor, calls=prompts)):
            executor._run_review()
        assert len(prompts) == 1
        assert "codex gpt-6-astra" in prompts[0]
        assert f"{BASE_SHA}...HEAD" in prompts[0]
        m = _manifest(executor)
        assert m["mode"] == "single" and m["totalAdded"] == 3000
        assert len(m["bundles"]) == 1

    def test_3001_added_splits_and_cross_reviews(self, executor):
        prompts = []
        _arm_review(executor, self.SPLIT)
        with patch("subprocess.run", side_effect=_reviewers(executor, calls=prompts)):
            executor._run_review()
        m = _manifest(executor)
        assert m["mode"] == "split" and m["totalAdded"] == 3001
        assert len(m["bundles"]) == 2
        assert all(b["added"] <= 3000 for b in m["bundles"])
        assert [_out_name(p) for p in prompts] == [
            "review-bundle-1.json", "review-bundle-2.json", "review-cross.json"]
        assert "src/a.ts" in prompts[0] and "src/b.ts" not in prompts[0]
        assert "src/b.ts" in prompts[1] and "src/a.ts" not in prompts[1]
        assert all("codex gpt-6-astra" in p for p in prompts[:2])
        assert "경계" in prompts[2] and "review-manifest.json" in prompts[2]
        assert "src/a.ts" in prompts[2] and "src/b.ts" in prompts[2]

    def test_prompts_name_sha_range_not_branch(self, executor):
        prompts = []
        _arm_review(executor, self.SPLIT)
        with patch("subprocess.run", side_effect=_reviewers(executor, calls=prompts)):
            executor._run_review()
        for p in prompts:
            assert f"{BASE_SHA}...HEAD" in p
            assert "develop...HEAD" not in p and "main...HEAD" not in p

    def test_single_file_over_limit_blocks_before_review(self, executor, top_index):
        executor._top_index_file = top_index
        prompts = []
        _arm_review(executor, [("src/huge.ts", 3001, 0, "A"), ("src/a.ts", 10, 0, "M")])
        with patch("subprocess.run", side_effect=_reviewers(executor, calls=prompts)):
            with pytest.raises(SystemExit) as e:
                executor._run_review()
        assert e.value.code == 3
        assert prompts == [], "리뷰를 시작하지 않아야 한다"
        reason = _idx(executor)["review_reason"]
        assert "src/huge.ts" in reason and "3001" in reason

    def test_review_exclude_is_published_and_not_reviewed(self, executor):
        prompts = []
        _arm_review(executor, [("fixtures/big.json", 9000, 0, "A"), ("src/a.ts", 10, 0, "M")],
                    exclude=[{"glob": "fixtures/*", "reason": "생성 데이터(사람이 따로 검수)"}])
        with patch("subprocess.run", side_effect=_reviewers(executor, calls=prompts)):
            executor._run_review()
        assert len(prompts) == 1 and "fixtures/big.json" not in prompts[0]
        m = _manifest(executor)
        big = next(f for f in m["files"] if f["path"] == "fixtures/big.json")
        assert big["excluded"] is True and big["bundle"] is None
        assert big["excludeReason"] == "생성 데이터(사람이 따로 검수)"
        assert m["totalAdded"] == 10
        md = (executor._phase_dir / "review.md").read_text(encoding="utf-8")
        assert "fixtures/big.json" in md and "생성 데이터(사람이 따로 검수)" in md

    def test_malformed_review_exclude_blocks(self, executor, top_index):
        executor._top_index_file = top_index
        prompts = []
        _arm_review(executor, exclude=[{"glob": "fixtures/*"}])  # reason 없음
        with patch("subprocess.run", side_effect=_reviewers(executor, calls=prompts)):
            with pytest.raises(SystemExit) as e:
                executor._run_review()
        assert e.value.code == 3
        assert prompts == []

    @pytest.mark.parametrize("target,case", [
        ("review-bundle-2.json", "missing"),
        ("review-bundle-2.json", "timeout"),
        ("review-bundle-2.json", "degraded"),
        ("review-bundle-2.json", "schema"),
        ("review-bundle-2.json", "empty"),
        ("review-cross.json", "missing"),
    ])
    def test_incomplete_result_blocks(self, executor, top_index, target, case):
        executor._top_index_file = top_index
        _arm_review(executor, self.SPLIT)
        def respond(prompt, out):
            if out.name != target:
                return CLEAN
            if case == "missing":
                return None
            if case == "timeout":
                raise subprocess.TimeoutExpired("claude", 900)
            if case == "degraded":
                return {"status": "degraded", "reason": "차원 하나 실패", "findings": []}
            if case == "schema":
                return {"status": "complete", "findings": [_f("blocker")]}
            return {}
        with patch("subprocess.run", side_effect=_reviewers(executor, respond)):
            with pytest.raises(SystemExit) as e:
                executor._run_review()
        assert e.value.code == 3
        label = "교차 리뷰" if target == "review-cross.json" else "묶음 2"
        assert label in _idx(executor)["review_reason"]

    def test_empty_object_is_rejected(self, executor, top_index):
        """`{}`는 findings=[]로 읽혀 통과하던 구멍이다."""
        executor._top_index_file = top_index
        _arm_review(executor)
        executor._apply_review_fixes = lambda f: pytest.fail("수정 단계에 가면 안 된다")
        with patch("subprocess.run", side_effect=_reviewer_writes(executor, {})):
            with pytest.raises(SystemExit) as e:
                executor._run_review()
        assert e.value.code == 3

    def test_duplicates_merged_keeping_highest_severity(self, executor):
        _arm_review(executor, self.SPLIT)
        n = {"i": 0}
        def respond(prompt, out):
            n["i"] += 1
            if n["i"] > 3:
                return CLEAN  # 수정 후 재리뷰
            sev = {"review-bundle-1.json": "minor", "review-bundle-2.json": "nit",
                   "review-cross.json": "major"}[out.name]
            return {"status": "complete", "findings": [_f(sev, "src/a.ts", 7, "같은 문제")]}
        passed = {}
        executor._apply_review_fixes = lambda f: passed.__setitem__("f", f)
        with patch("subprocess.run", side_effect=_reviewers(executor, respond)):
            executor._run_review()
        assert [(f["severity"], f["title"]) for f in passed["f"]] == [("major", "같은 문제")]
        r1 = json.loads((executor._phase_dir / "review-r1.json").read_text(encoding="utf-8"))
        assert [f["severity"] for f in r1["findings"]] == ["major"]

    def test_review_md_lists_bundles_and_cross_review(self, executor):
        _arm_review(executor, self.SPLIT)
        with patch("subprocess.run", side_effect=_reviewers(executor)):
            executor._run_review()
        md = (executor._phase_dir / "review.md").read_text(encoding="utf-8")
        for s in ("묶음 1", "묶음 2", "src/a.ts", "src/b.ts", "교차 리뷰", "review-manifest.json"):
            assert s in md, f"review.md에 '{s}'가 없다"


class TestReReview:
    """동작 5 — 수정 에이전트가 끝나면 같은 기준으로 phase 전체를 한 번 다시 리뷰한다."""

    def test_rereview_runs_after_fix(self, executor):
        prompts = []
        _arm_review(executor)
        executor._apply_review_fixes = lambda f: None
        seq = iter([{"status": "complete", "findings": [_f("minor")]}, CLEAN])
        with patch("subprocess.run",
                   side_effect=_reviewers(executor, lambda p, o: next(seq), calls=prompts)):
            executor._run_review()
        assert len(prompts) == 2, "수정 뒤 재리뷰를 해야 한다"
        assert all(f"{BASE_SHA}...HEAD" in p for p in prompts), "같은 기준 SHA로 재리뷰"
        r1 = json.loads((executor._phase_dir / "review-r1.json").read_text(encoding="utf-8"))
        final = json.loads((executor._phase_dir / "review.json").read_text(encoding="utf-8"))
        assert [f["severity"] for f in r1["findings"]] == ["minor"]
        assert final["findings"] == []

    def test_major_left_after_fix_blocks(self, executor, top_index):
        executor._top_index_file = top_index
        _arm_review(executor)
        executor._apply_review_fixes = lambda f: None
        with patch("subprocess.run", side_effect=_reviewer_writes(
                executor, {"status": "complete", "findings": [_f("minor")]},
                then={"status": "complete", "findings": [_f("major", title="남은 버그")]})):
            with pytest.raises(SystemExit) as e:
                executor._run_review()
        assert e.value.code == 3
        assert "재리뷰" in _idx(executor)["review_reason"]

    def test_minor_left_after_fix_passes_without_second_fix(self, executor):
        _arm_review(executor)
        fixes = []
        executor._apply_review_fixes = lambda f: fixes.append(f)
        with patch("subprocess.run", side_effect=_reviewer_writes(
                executor, {"status": "complete", "findings": [_f("major")]},
                then={"status": "complete", "findings": [_f("minor", title="사소함")]})):
            executor._run_review()
        assert len(fixes) == 1, "재리뷰는 1회 — 두 번째 수정은 없다"


class TestFixThenReReviewRealGit:
    """수정 커밋은 재리뷰 범위에 들고, 미커밋 수정·AC 실패 결과는 재리뷰 전에 막는다.

    수정 함수를 무조건 성공으로 바꾸면 "새 수정 커밋이 재리뷰 범위에 들어가는가"를
    검증하지 못한다 — 진짜 저장소에서 가짜 수정 에이전트가 실제로 커밋한다.
    """

    MINOR = {"status": "complete", "findings": [_f("minor", "src/a.ts", 1, "이름")]}

    @pytest.fixture
    def phase_repo(self, executor, git_repo):
        executor._cli_base = "develop"
        _on_feature(executor, git_repo)
        (git_repo / "src").mkdir()
        (git_repo / "src" / "a.ts").write_text("export const a = 1;\n", encoding="utf-8")
        _commit_all(git_repo, "phase work")
        return git_repo

    def _minor_then_clean(self):
        n = {"i": 0}
        def respond(prompt, out):
            n["i"] += 1
            return self.MINOR if n["i"] == 1 else CLEAN
        return respond

    def test_fix_commit_is_in_rereview_range(self, executor, phase_repo):
        """수정은 하네스가 커밋하고(fix(...)), 그 커밋이 재리뷰 범위에 든다."""
        def fixer(prompt, out):
            (phase_repo / "src" / "a.ts").write_text("export const a = 2;\n", encoding="utf-8")
            (phase_repo / "src" / "fix.ts").write_text("export const fix = 1;\n", encoding="utf-8")
            return {"status": "passed", "ac": "npm test 통과"}
        prompts = []
        with patch("subprocess.run", side_effect=_reviewers(
                executor, self._minor_then_clean(), calls=prompts, fixer=fixer)):
            executor._run_review()
        assert len(prompts) == 2
        assert "src/fix.ts" not in prompts[0] and "src/fix.ts" in prompts[1]
        assert _git_ok(phase_repo, "log", "-1", "--format=%s") == "fix(mvp): apply review findings"
        m = _manifest(executor)  # 재리뷰 회차의 manifest
        assert m["head"] == _git_ok(phase_repo, "rev-parse", "HEAD"), "재리뷰는 새 HEAD까지 본다"
        assert executor._reviewed_sha == m["head"]
        assert "src/fix.ts" in {f["path"] for f in m["files"]}
        assert _git_ok(phase_repo, "status", "--porcelain") == ""

    def test_fixer_self_commit_blocks_rereview(self, executor, phase_repo, top_index):
        """(구 '미커밋 수정' 시험 대체) 커밋은 하네스만 — 에이전트가 직접 commit하면
        검증 전 코드가 브랜치에 들어간다. HEAD가 바뀌면 재리뷰 전에 막는다."""
        def fixer(prompt, out):
            (phase_repo / "src" / "a.ts").write_text("export const a = 2;\n", encoding="utf-8")
            _git_ok(phase_repo, "add", "src")
            _git_ok(phase_repo, "commit", "-q", "--no-verify", "-m", "agent commit")
            return {"status": "passed"}
        reason = self._expect_blocked(executor, top_index, fixer)
        assert "HEAD를 바꿈" in reason

    def test_fix_outside_allowed_paths_blocks(self, executor, phase_repo, top_index):
        executor._allowed = ["src/"]
        def fixer(prompt, out):
            (phase_repo / "dev.txt").write_text("escaped\n", encoding="utf-8")
            return {"status": "passed"}
        reason = self._expect_blocked(executor, top_index, fixer)
        assert "dev.txt" in reason
        assert "escaped" not in _git_ok(phase_repo, "show", "HEAD:dev.txt")

    @pytest.mark.parametrize("result,expect", [
        ({"status": "failed", "reason": "npm test 실패"}, "npm test 실패"),
        (None, "수정 결과 파일 없음"),
        ({"status": "done"}, "형식"),
    ])
    def test_fix_without_passed_result_blocks(self, executor, phase_repo, top_index,
                                              result, expect):
        """수정 에이전트가 종료코드 0으로 끝나도 AC 결과가 passed가 아니면 막는다."""
        reason = self._expect_blocked(executor, top_index, lambda p, o: result)
        assert expect in reason

    def _expect_blocked(self, executor, top_index, fixer):
        executor._top_index_file = top_index
        _commit_all(Path(executor._root), "candidate")  # 운영처럼 candidate가 커밋된 상태
        prompts = []
        with patch("subprocess.run", side_effect=_reviewers(
                executor, self._minor_then_clean(), calls=prompts, fixer=fixer)):
            with pytest.raises(SystemExit) as e:
                executor._run_review()
        assert e.value.code == 3
        assert len(prompts) == 1, "재리뷰 전에 막아야 한다"
        return _idx(executor)["review_reason"]

    def test_source_renamed_into_phase_dir_blocks(self, executor, phase_repo, top_index):
        """하네스 폴더로 옮기는 rename은 allowedPaths 밖 변경이다."""
        executor._allowed = ["src/"]
        def fixer(prompt, out):
            _git_ok(phase_repo, "mv", "src/a.ts", "phases/0-mvp/review-notes.md")
            return {"status": "passed"}
        assert "phases/0-mvp/review-notes.md" in self._expect_blocked(executor, top_index, fixer)

    def test_review_like_file_in_phase_dir_blocks(self, executor, phase_repo, top_index):
        """하네스가 쓰지 않는 파일은 이름이 review*로 시작해도 하네스 산출물이 아니다."""
        executor._allowed = ["src/"]
        def fixer(prompt, out):
            (phase_repo / "phases" / "0-mvp" / "review-notes.md").write_text(
                "메모\n", encoding="utf-8")
            return {"status": "passed"}
        assert "review-notes.md" in self._expect_blocked(executor, top_index, fixer)

    def _rewrite_index(self, repo, **fields):
        p = repo / "phases" / "0-mvp" / "index.json"
        idx = json.loads(p.read_text(encoding="utf-8"))
        idx.update(fields)
        p.write_text(json.dumps(idx, ensure_ascii=False), encoding="utf-8")

    def test_changed_review_base_sha_blocks(self, executor, phase_repo, top_index):
        """수정 단계가 기준 SHA를 새 HEAD로 바꾸면 재리뷰가 HEAD...HEAD를 보고 통과한다."""
        def fixer(prompt, out):
            (phase_repo / "src" / "a.ts").write_text("export const a = 2;\n", encoding="utf-8")
            self._rewrite_index(phase_repo,
                                reviewBaseSha=_git_ok(phase_repo, "rev-parse", "HEAD"))
            return {"status": "passed"}
        assert "reviewBaseSha" in self._expect_blocked(executor, top_index, fixer)

    def test_changed_review_exclude_blocks(self, executor, phase_repo, top_index):
        def fixer(prompt, out):
            self._rewrite_index(phase_repo,
                                reviewExclude=[{"glob": "src/*", "reason": "리뷰 빼기"}])
            return {"status": "passed"}
        assert "reviewExclude" in self._expect_blocked(executor, top_index, fixer)

    def test_rereview_uses_pinned_sha_not_index(self, executor, phase_repo):
        """재리뷰 회차는 1차 리뷰 시작 때 고정한 cfg를 쓴다 — index.json을 다시 읽지 않는다."""
        cfg = executor._load_review_config()
        pinned = cfg["reviewBaseSha"]
        head = _git_ok(phase_repo, "rev-parse", "HEAD")
        self._rewrite_index(phase_repo, reviewBaseSha=head)
        _git_ok(phase_repo, "add", "phases/0-mvp/index.json")
        _git_ok(phase_repo, "commit", "-q", "--no-verify", "-m", "chore: base")
        prompts = []
        with patch("subprocess.run", side_effect=_reviewers(executor, calls=prompts)):
            executor._review_round(2, cfg)
        assert f"{pinned}...HEAD" in prompts[0]
        assert _manifest(executor)["reviewBaseSha"] == pinned


class TestReviewCommandParity:
    """리뷰어에게 안내하는 git 명령과 하네스의 줄 수 계산이 같은 옵션을 쓴다.

    manifest만 -M으로 세고 리뷰어 명령에 -M이 없으면, diff.renames=false
    저장소에서 큰 파일 rename이 삭제+추가로 세어져 플러그인 관문에 다시 막힌다.
    """

    def test_prompt_commands_match_recount_and_manifest_options(self, executor):
        calls, prompts = [], []
        _arm_review(executor, TestReviewSplit.SPLIT + [("src/c.ts", 5, 0, "R100", "src/old_c.ts")],
                    calls=calls)
        with patch("subprocess.run", side_effect=_reviewers(executor, calls=prompts)):
            executor._run_review()
        recounts = [c for c in calls if "--numstat" in c and "-z" not in c]
        assert len(recounts) == 2, "묶음마다 리뷰어 명령과 같은 명령으로 다시 센다"
        manifest_call = next(c for c in calls if "--numstat" in c and "-z" in c)
        for prompt, rc in zip(prompts[:2], recounts):
            opts = list(rc[:rc.index("--")])
            assert "-M" in opts
            assert [a for a in manifest_call if a != "-z"] == opts, "manifest와 옵션이 같아야 한다"
            assert shlex.join(["git", *rc]) in prompt
            assert shlex.join(["git", *["--quiet" if a == "--numstat" else a for a in rc]]) in prompt
            assert shlex.join(["git", *[a for a in rc if a != "--numstat"]]) in prompt
        assert "src/old_c.ts" in recounts[1], "rename은 옛 경로도 pathspec에 넣는다"
        cross_base = [a for a in recounts[0][:recounts[0].index("--")] if a != "--numstat"]
        assert shlex.join(["git", *cross_base]) in prompts[2], "교차 리뷰 명령도 같은 옵션"

    def test_recount_over_limit_blocks_before_review(self, executor, top_index):
        executor._top_index_file = top_index
        prompts = []
        _arm_review(executor, [("src/a.ts", 10, 0, "M")], recount={"src/a.ts": 5000})
        with patch("subprocess.run", side_effect=_reviewers(executor, calls=prompts)):
            with pytest.raises(SystemExit) as e:
                executor._run_review()
        assert e.value.code == 3
        assert prompts == [], "리뷰어를 부르기 전에 막아야 한다"
        reason = _idx(executor)["review_reason"]
        assert "묶음 1" in reason and "5000" in reason

    def test_big_rename_passes_with_renames_disabled(self, executor, git_repo):
        _git_ok(git_repo, "config", "diff.renames", "false")
        body = "".join(f"export const v{i} = {i};\n" for i in range(4000))
        (git_repo / "big.ts").write_text(body, encoding="utf-8")
        _commit_all(git_repo, "big file on develop")
        executor._cli_base = "develop"
        _on_feature(executor, git_repo)
        _git_ok(git_repo, "mv", "big.ts", "big2.ts")
        _commit_all(git_repo, "rename")
        prompts = []
        with patch("subprocess.run", side_effect=_reviewers(executor, calls=prompts)):
            executor._run_review()
        assert len(prompts) == 1
        m = _manifest(executor)
        big = next(f for f in m["files"] if f["path"] == "big2.ts")
        assert big["status"] == "renamed" and big["added"] == 0
        assert m["bundles"][0]["recounted"] <= 3000
        sha = m["reviewBaseSha"]
        assert f"--numstat -M {sha}...HEAD --" in prompts[0]
        assert " big.ts" in prompts[0], "옛 경로가 리뷰어 명령의 pathspec에 있다"


class TestPlanReviewBundles:
    @staticmethod
    def _files(*pairs):
        return [{"path": p, "added": a} for p, a in pairs]

    def test_code_and_test_share_bundle(self):
        files = self._files(("src/lib/__tests__/zeta.test.ts", 1500),
                            ("src/lib/alpha.ts", 2000), ("src/lib/zeta.ts", 1400))
        bundles = ex.plan_review_bundles(files)
        zeta = next(b for b in bundles if "src/lib/zeta.ts" in b)
        assert "src/lib/__tests__/zeta.test.ts" in zeta

    @pytest.mark.parametrize("code,test", [
        ("src/lib/site.ts", "src/lib/site.test.ts"),
        ("src/ui/Card.tsx", "src/ui/Card.test.tsx"),
        ("src/ui/Card.tsx", "src/ui/__tests__/Card.test.tsx"),
        ("scripts/check.mjs", "scripts/check.test.mjs"),
        ("scripts/execute.py", "scripts/test_execute.py"),
        ("next.config.ts", "next.config.test.ts"),
    ])
    def test_pairing_rules(self, code, test):
        assert ex._review_unit_key(code) == ex._review_unit_key(test)

    def test_deterministic_regardless_of_input_order(self):
        import random
        files = self._files(*[(f"src/m{i % 7}/f{i}.ts", (i * 397) % 1300) for i in range(40)])
        expect = ex.plan_review_bundles(files)
        rng = random.Random(0)
        for _ in range(5):
            shuffled = files[:]
            rng.shuffle(shuffled)
            assert ex.plan_review_bundles(shuffled) == expect

    def test_every_bundle_within_limit_and_every_file_once(self):
        files = self._files(*[(f"src/m{i % 7}/f{i}.ts", (i * 397) % 1300) for i in range(40)])
        added = {f["path"]: f["added"] for f in files}
        bundles = ex.plan_review_bundles(files)
        assert all(sum(added[p] for p in b) <= 3000 for b in bundles)
        assert sorted(p for b in bundles for p in b) == sorted(added)

    def test_oversized_pair_is_split_per_file(self):
        bundles = ex.plan_review_bundles(self._files(("src/a.ts", 2000), ("src/a.test.ts", 1500)))
        assert len(bundles) == 2

    def test_zero_added_files_are_still_bundled(self):
        bundles = ex.plan_review_bundles(self._files(("src/gone.ts", 0), ("img.bin", 0)))
        assert sorted(p for b in bundles for p in b) == ["img.bin", "src/gone.ts"]

    @pytest.mark.parametrize("path,prefix", [
        ("src/lib/site.ts", "src/lib"),
        ("scripts/hooks/tdd-guard.sh", "scripts/hooks"),
        ("scripts/execute.py", "scripts"),
        ("docs/specs/a.md", "docs"),
        ("sanity/schemas/post.ts", "sanity"),  # 프로젝트 고유 폴더는 한 단계만 본다
        ("README.md", ""),
    ])
    def test_review_prefix_depth(self, path, prefix):
        """src/·scripts/만 한 단계 더 깊게 묶고, 나머지 최상위 폴더는 한 단계다."""
        assert ex._review_prefix(path) == prefix


class TestReviewResultCheck:
    @pytest.mark.parametrize("obj", [
        {}, [], "x", {"status": "complete"},
        {"findings": []},
        {"status": "complete", "findings": "none"},
        {"status": "complete", "findings": [{"severity": "major", "file": "a",
                                             "line": 1, "title": "t"}]},  # detail 없음
        {"status": "complete", "findings": [_f("blocker")]},
        {"status": "complete", "findings": [_f("major", line="3")]},
        {"status": "complete", "findings": [_f("major", title="")]},
        {"status": "complete", "findings": ["major"]},
    ])
    def test_rejects_malformed(self, obj):
        assert ex.check_review_result(obj) is not None

    def test_rejects_incomplete_status(self):
        err = ex.check_review_result({"status": "degraded", "reason": "x", "findings": []})
        assert err and "degraded" in err

    def test_accepts_complete(self):
        assert ex.check_review_result(
            {"status": "complete", "findings": [_f("nit", line=None)]}) is None


class TestMergeReviewFindings:
    def test_dedupes_on_file_line_title_keeping_highest(self):
        merged = ex.merge_review_findings([
            [_f("minor", "a", 1, "x")],
            [_f("major", "a", 1, "x"), _f("nit", "a", 2, "x")],
        ])
        assert [(f["severity"], f["line"]) for f in merged] == [("major", 1), ("nit", 2)]

    def test_different_title_is_kept(self):
        merged = ex.merge_review_findings([[_f("minor", "a", 1, "x")], [_f("minor", "a", 1, "y")]])
        assert len(merged) == 2


# ---------------------------------------------------------------------------
# _build_agent_argv — 백엔드 argv 어댑터 (multi-backend Part 1)
# ---------------------------------------------------------------------------

# ---------------------------------------------------------------------------
# argv — 권한 우회는 구현 Claude에만, 리뷰는 codex gpt-6-astra read-only
# ---------------------------------------------------------------------------

class TestAgentArgv:
    def test_impl_argv_has_bypass(self):
        argv = ex.build_impl_argv()
        assert argv[:2] == ["claude", "-p"]
        assert "--dangerously-skip-permissions" in argv

    def test_review_argv_is_codex_astra_readonly(self):
        argv = ex.build_code_review_argv()
        assert argv[:2] == ["codex", "exec"]
        assert argv[argv.index("--model") + 1] == "gpt-6-astra"
        assert argv[argv.index("--sandbox") + 1] == "read-only"
        assert "--dangerously-skip-permissions" not in argv
        assert "--dangerously-bypass-approvals-and-sandbox" not in argv

    def test_no_legacy_backend_switches(self):
        for name in ("_build_agent_argv", "_codex_sandbox", "NO_GIT", "is_self_review",
                     "warn_if_self_review", "_resolve_backends"):
            assert not hasattr(ex, name), name

    def test_preflight_requires_policy(self, monkeypatch):
        with pytest.raises(SystemExit) as e:
            ex.preflight()
        assert e.value.code == 1
        monkeypatch.setenv("HARNESS_REVIEW_BACKEND", "codex")
        monkeypatch.setenv("HARNESS_REVIEW_MODEL", "gpt-6-astra")
        ex.preflight()


# 통합: 진짜 codex·claude 바이너리를 띄운다(--version만 — 원격 호출·과금 없음).
# mock은 "우리가 만든 argv가 실제로 프로세스를 띄우는가"를 증명하지 못한다.

@pytest.mark.integration
class TestBinariesSpawnForReal:
    @pytest.mark.skipif(shutil.which("codex") is None, reason="codex CLI 미설치")
    def test_review_argv_executable_spawns(self):
        r = subprocess.run([ex.build_code_review_argv()[0], "--version"],
                           capture_output=True, text=True, timeout=60)
        assert r.returncode == 0 and "codex" in r.stdout.lower()

    @pytest.mark.skipif(shutil.which("codex") is None, reason="codex CLI 미설치")
    def test_review_flags_accepted_by_installed_codex(self):
        """argv의 플래그가 설치된 codex exec에 실제로 존재하는가(--help 파싱)."""
        r = subprocess.run(["codex", "exec", "--help"], capture_output=True, text=True,
                           timeout=60)
        for flag in ("--sandbox", "--model", "--dangerously-bypass-hook-trust"):
            assert flag in r.stdout, flag

    @pytest.mark.skipif(shutil.which("claude") is None, reason="claude CLI 미설치")
    def test_impl_and_plan_flags_accepted_by_installed_claude(self):
        r = subprocess.run(["claude", "--help"], capture_output=True, text=True, timeout=60)
        for flag in ("--dangerously-skip-permissions", "--permission-mode", "--allowedTools",
                     "--disallowedTools", "--resume", "--output-format", "--verbose"):
            assert flag in r.stdout, flag


def _pid_alive(pid: int) -> bool:
    if sys.platform.startswith("win"):
        out = subprocess.run(["tasklist", "/FI", f"PID eq {pid}", "/NH"],
                             capture_output=True, text=True).stdout
        return str(pid) in out
    try:
        os.kill(pid, 0)
    except OSError:
        return False
    return True


class TestRunAgentProcess:
    """_run_agent_process — 실제 프로세스를 띄워 시간 초과 때 트리째 끄는지 본다."""

    def test_returns_output(self):
        r = ex._run_agent_process(
            [sys.executable, "-c", "import sys; print(sys.stdin.read().upper())"],
            input="abc", cwd=os.getcwd(), timeout=30)
        assert r.returncode == 0
        assert r.stdout.strip() == "ABC"
        assert r.timed_out is False

    def test_nonzero_exit(self):
        r = ex._run_agent_process(
            [sys.executable, "-c", "import sys; sys.exit(3)"],
            input="", cwd=os.getcwd(), timeout=30)
        assert r.returncode == 3
        assert r.timed_out is False

    def test_timeout_kills_tree(self, tmp_path):
        import time as _t
        pidfile = tmp_path / "child.pid"
        script = (
            "import subprocess, sys, time\n"
            "c = subprocess.Popen([sys.executable, '-c', 'import time; time.sleep(60)'])\n"
            f"open({str(pidfile)!r}, 'w').write(str(c.pid))\n"
            "print('started', flush=True)\n"
            "time.sleep(60)\n"
        )
        t0 = _t.monotonic()
        r = ex._run_agent_process([sys.executable, "-c", script], input="",
                                  cwd=str(tmp_path), timeout=3, kill_grace=10)
        assert r.timed_out is True
        assert _t.monotonic() - t0 < 25
        assert "started" in r.stdout
        pid = int(pidfile.read_text())
        deadline = _t.monotonic() + 5
        while _pid_alive(pid) and _t.monotonic() < deadline:
            _t.sleep(0.2)
        assert not _pid_alive(pid)

    def test_returns_when_agent_exits_while_descendant_holds_output(self, tmp_path):
        # 에이전트는 끝났는데 그가 띄우고 남긴 자손(서버 등)이 물려받은 출력을 쥐고 있어도
        # 시간 제한까지 기다리지 않고 바로 돌아와야 한다(10-31 phase 6 리뷰가 17시간 멈춘 모양).
        import time as _t
        pidfile = tmp_path / "grandchild.pid"
        script = (
            "import subprocess, sys\n"
            "c = subprocess.Popen([sys.executable, '-c', 'import time; time.sleep(60)'])\n"
            f"open({str(pidfile)!r}, 'w').write(str(c.pid))\n"
            "print('done', flush=True)\n"
        )
        t0 = _t.monotonic()
        try:
            r = ex._run_agent_process([sys.executable, "-c", script], input="",
                                      cwd=str(tmp_path), timeout=20, kill_grace=5)
            elapsed = _t.monotonic() - t0
        finally:
            if pidfile.exists():
                try:
                    os.kill(int(pidfile.read_text()), signal.SIGTERM)
                except OSError:
                    pass
        assert r.timed_out is False
        assert r.returncode == 0
        assert r.stdout.strip() == "done"
        assert elapsed < 10

    def test_descendant_writes_after_exit_do_not_corrupt_output(self, tmp_path):
        # 남은 자손이 물려받은 출력에 계속 써도 에이전트가 낸 출력이 덮이지 않아야 한다.
        # 출력 핸들은 복제본끼리 파일 위치를 공유한다 — 하네스가 같은 핸들을 처음으로 되감아
        # 읽으면 그동안 자손의 쓰기가 앞부분을 덮는다.
        size = 8_000_000
        pidfile = tmp_path / "grandchild.pid"
        grand = ("import sys, time\n"
                 "end = time.monotonic() + 3\n"
                 "while time.monotonic() < end:\n"
                 "    sys.stdout.write('x' * 63 + '\\n'); sys.stdout.flush()\n")
        script = (
            "import subprocess, sys, time\n"
            f"sys.stdout.write('A' * {size}); sys.stdout.flush()\n"
            f"c = subprocess.Popen([sys.executable, '-c', {grand!r}])\n"
            f"open({str(pidfile)!r}, 'w').write(str(c.pid))\n"
            "time.sleep(0.5)\n"
        )
        try:
            r = ex._run_agent_process([sys.executable, "-c", script], input="",
                                      cwd=str(tmp_path), timeout=30, kill_grace=5)
        finally:
            if pidfile.exists():
                try:
                    os.kill(int(pidfile.read_text()), signal.SIGTERM)
                except OSError:
                    pass
        assert r.timed_out is False
        assert r.stdout[:size] == "A" * size

    def test_kill_after_exit_is_harmless(self):
        real = subprocess.Popen.wait
        calls = {"n": 0}
        seen = {}

        def flaky(self, timeout=None):
            if self.args[0] != sys.executable:
                return real(self, timeout)
            calls["n"] += 1
            if calls["n"] == 1:
                # 프로세스가 확실히 끝난 뒤에 시간 초과를 낸다(끝난 프로세스에 종료 호출).
                real(self)
                seen["exited"] = self.poll() is not None
                raise subprocess.TimeoutExpired(self.args, timeout)
            return real(self, timeout)

        with patch.object(subprocess.Popen, "wait", flaky):
            r = ex._run_agent_process(
                [sys.executable, "-c", "pass"], input="", cwd=os.getcwd(),
                timeout=5, kill_grace=10)
        assert seen["exited"] is True
        assert r.timed_out is True

    def test_interrupt_kills_tree_and_reraises(self):
        real = subprocess.Popen.wait
        killed = []
        timeouts = []
        real_kill = ex._kill_process_tree

        def interrupt(self, timeout=None):
            if self.args[0] != sys.executable:  # taskkill 등 보조 호출은 그대로
                return real(self, timeout)
            raise KeyboardInterrupt

        def spy(proc, timeout=None):
            killed.append(proc)
            timeouts.append(timeout)
            real_kill(proc)

        with patch.object(subprocess.Popen, "wait", interrupt), \
                patch.object(ex, "_kill_process_tree", spy):
            with pytest.raises(KeyboardInterrupt):
                ex._run_agent_process(
                    [sys.executable, "-c", "import time; time.sleep(30)"],
                    input="", cwd=os.getcwd(), timeout=30, kill_grace=5)
        assert len(killed) == 1
        # 인터럽트 경로의 트리 종료도 kill_grace로 묶인다(taskkill이 멈춰도 다시 던진다).
        assert timeouts == [5]
        killed[0].wait(timeout=10)
        assert killed[0].poll() is not None

    def test_second_timeout_returns_partial(self):
        # 트리 종료 뒤 종료 확인까지 시간 초과여도 그때까지 받은 출력을 돌려준다
        real = subprocess.Popen.wait

        def always(self, timeout=None):
            if self.args[0] != sys.executable:  # taskkill 등 보조 호출은 그대로
                return real(self, timeout)
            try:
                real(self, timeout)
            except subprocess.TimeoutExpired:
                pass
            raise subprocess.TimeoutExpired(self.args, timeout)

        script = "import time; print('part', flush=True); time.sleep(30)"
        with patch.object(subprocess.Popen, "wait", always):
            r = ex._run_agent_process([sys.executable, "-c", script],
                                      input="", cwd=os.getcwd(), timeout=3, kill_grace=1)
        assert r.timed_out is True
        assert r.stdout.strip() == "part"

    def test_cleanup_finishes_within_kill_grace(self):
        # 트리 종료(Windows taskkill)가 멈춰도 정리 전체(종료 + 남은 출력 수거)가
        # kill_grace 안에 끝나야 한다. 종료 함수는 받은 시간만큼 멈췄다가 아무것도
        # 끄지 못한 척한다 — 시간을 안 받으면 HANG초 동안 멈춘다.
        import time as _t
        HANG = 8
        given = []

        def hung_kill(proc, timeout=None):
            given.append(timeout)
            _t.sleep(HANG if timeout is None else min(HANG, timeout))

        import tempfile as _tf
        pidf = Path(_tf.mkdtemp()) / "leader.pid"
        t0 = _t.monotonic()
        try:
            # 그룹 종료가 멈추면(아무것도 못 끄면) 리더 PID 직접 kill로 메우지 않는다 —
            # 정리 전체를 kill_grace 안에 끝내고 fail closed(DescendantSurvived)한다.
            with patch.object(ex, "_kill_process_tree", hung_kill):
                with pytest.raises(ex.DescendantSurvived):
                    ex._run_agent_process(
                        [sys.executable, "-c",
                         f"import os, time; open({str(pidf)!r}, 'w').write(str(os.getpid()));"
                         " time.sleep(30)"],
                        input="", cwd=os.getcwd(), timeout=1, kill_grace=2)
            elapsed = _t.monotonic() - t0
            assert given and given[0] is not None and given[0] <= 2
            assert elapsed < 1 + 2 + 2  # 시간 초과 1초 + kill_grace 2초 + 여유
        finally:
            if pidf.exists():  # 시험이 만든 그룹 정리(시험 자신의 프로세스)
                with contextlib.suppress(OSError, ValueError):
                    os.killpg(int(pidf.read_text()), signal.SIGKILL)

    def test_truncated_utf8_returns_partial(self):
        # 출력이 다중 바이트 문자 중간에서 끊겨도 디코딩 예외 없이 앞부분을 돌려줘야 한다.
        # strict 디코딩이면 POSIX는 두 번째 communicate가 UnicodeDecodeError를 내고,
        # Windows는 읽기 스레드가 죽어 앞부분까지 잃는다.
        script = (
            "import sys, time\n"
            "sys.stdout.buffer.write(b'ok \\xed\\x95'); sys.stdout.flush()\n"
            "time.sleep(30)\n"
        )
        r = ex._run_agent_process([sys.executable, "-c", script], input="",
                                  cwd=os.getcwd(), timeout=2, kill_grace=10)
        assert r.timed_out is True
        assert r.stdout.startswith("ok ")


class TestAgentCallsUseBoundedRunner:
    """리뷰·수정 에이전트도 _run_agent_process로 띄운다 — subprocess.run은 시간 초과 뒤
    Windows에서 제한 없이 파이프를 기다려 하네스가 멈춘다(10-31 phase 6 리뷰 17시간)."""

    @staticmethod
    def _timed_out(calls):
        def fake(argv, *, input, cwd, timeout, kill_grace=30, env=None):
            calls.append(timeout)
            return ex.AgentRun(-1, "", "", True)
        return fake

    def test_reviewer_timeout(self, executor, tmp_path):
        calls = []
        _arm_review(executor)
        with patch.object(ex, "_run_agent_process", self._timed_out(calls)):
            obj, err = executor._invoke_reviewer("묶음 1/1", "prompt", tmp_path / "out.json",
                                                 head=_HEAD)
        assert obj is None
        assert err == f"시간 초과({executor.REVIEW_TIMEOUT}s)"
        assert calls == [executor.REVIEW_TIMEOUT]

    def test_fixer_timeout(self, executor):
        calls = []
        finding = {"severity": "minor", "file": "a.py", "line": 1, "title": "t", "detail": "d"}
        _arm_review(executor)
        with patch.object(ex, "_run_agent_process", self._timed_out(calls)):
            err = executor._apply_review_fixes([finding])
        assert err == "수정 에이전트 시간 초과(1800s)"
        assert calls == [1800]


class TestKillProcessTree:
    @pytest.mark.parametrize("exc", [ProcessLookupError, PermissionError])
    def test_posix_kill_errors_are_ignored(self, monkeypatch, exc):
        # 이미 거둔 그룹은 ESRCH, 거두지 않은 좀비 리더만 남은 그룹은 macOS가 EPERM을 낸다.
        # 둘 다 끌 것이 없다는 뜻이라 하네스가 예외로 죽으면 안 된다.
        calls = []

        def killpg(pid, sig):
            calls.append(pid)
            raise exc

        monkeypatch.setattr(ex.sys, "platform", "linux")
        monkeypatch.setattr(ex.signal, "SIGKILL", 9, raising=False)
        monkeypatch.setattr(ex.os, "killpg", killpg, raising=False)
        ex._kill_process_tree(MagicMock(pid=4321))
        assert calls == [4321]


class TestSignalExit:
    """_install_signal_exit — POSIX에서 SIGTERM·SIGHUP을 SystemExit으로 바꿔
    _run_agent_process의 except 경로가 새 세션의 에이전트 트리를 끄게 한다."""

    def _install(self, monkeypatch, platform, hup=signal.SIG_DFL):
        installed = {}
        monkeypatch.setattr(ex.sys, "platform", platform)
        # Windows에는 SIGHUP이 없다 — 값만 빌려 POSIX 분기를 돌린다.
        monkeypatch.setattr(ex.signal, "SIGHUP", 1, raising=False)
        monkeypatch.setattr(ex.signal, "getsignal",
                            lambda s: hup if s == ex.signal.SIGHUP else signal.SIG_DFL)
        monkeypatch.setattr(ex.signal, "signal",
                            lambda s, h: installed.__setitem__(s, h))
        ex._install_signal_exit()
        return installed

    def test_posix_installs_term_and_hup(self, monkeypatch):
        installed = self._install(monkeypatch, "linux")
        assert set(installed) == {signal.SIGTERM, 1}

    def test_nohup_keeps_hup_ignored(self, monkeypatch):
        # nohup으로 띄우면 SIGHUP이 SIG_IGN이다 — 그대로 둬야 ssh가 끊겨도 계속 돈다.
        installed = self._install(monkeypatch, "darwin", hup=signal.SIG_IGN)
        assert set(installed) == {signal.SIGTERM}

    def test_handler_raises_system_exit(self, monkeypatch):
        handler = self._install(monkeypatch, "linux")[signal.SIGTERM]
        with pytest.raises(SystemExit) as exc:
            handler(signal.SIGTERM, None)
        assert exc.value.code == 128 + signal.SIGTERM

    @pytest.mark.skipif(sys.platform.startswith("win"), reason="POSIX 신호 전용")
    def test_sigterm_kills_agent_tree(self, tmp_path):
        import threading
        import time as _t
        pidfile = tmp_path / "child.pid"
        script = (
            "import subprocess, sys, time\n"
            "c = subprocess.Popen([sys.executable, '-c', 'import time; time.sleep(60)'])\n"
            f"open({str(pidfile)!r}, 'w').write(str(c.pid))\n"
            "time.sleep(60)\n"
        )
        done = threading.Event()

        def send():
            # 손자가 뜬 뒤, wait에서 기다리는 메인 스레드에 SIGTERM을 보낸다
            while not done.is_set():
                if pidfile.exists() and pidfile.read_text():
                    signal.pthread_kill(threading.main_thread().ident, signal.SIGTERM)
                    return
                done.wait(0.05)

        old = {s: signal.getsignal(s) for s in (signal.SIGTERM, signal.SIGHUP)}
        th = threading.Thread(target=send, daemon=True)
        try:
            ex._install_signal_exit()
            th.start()
            with pytest.raises(SystemExit) as exc:
                ex._run_agent_process([sys.executable, "-c", script], input="",
                                      cwd=str(tmp_path), timeout=30, kill_grace=5)
        finally:
            done.set()
            th.join()
            for s, h in old.items():
                signal.signal(s, signal.SIG_DFL if h is None else h)
        assert exc.value.code == 128 + signal.SIGTERM
        pid = int(pidfile.read_text())
        deadline = _t.monotonic() + 5
        while _pid_alive(pid) and _t.monotonic() < deadline:
            _t.sleep(0.2)
        assert not _pid_alive(pid)


# ---------------------------------------------------------------------------
# Astra 리뷰 M5 — 에이전트가 성공 종료해도 자손이 commit/test/review까지 살아남으면 안 된다
# ---------------------------------------------------------------------------

def _wait_pidfile(p, timeout=10):
    import time as _t
    deadline = _t.monotonic() + timeout
    while _t.monotonic() < deadline:
        if p.exists() and p.read_text().strip():
            return int(p.read_text().strip())
        _t.sleep(0.05)
    raise AssertionError("pidfile not written")


class TestDescendantReaping:
    """실제 프로세스로 검증한다(대역 없음 — _REAL_AGENT_PROCESS에 등록)."""

    def test_same_group_background_child_killed_on_success(self, tmp_path):
        pidf = tmp_path / "bg.pid"
        r = ex._run_agent_process(
            ["/bin/sh", "-c", f'(sleep 60; echo late > {tmp_path}/late) & echo $! > {pidf}; exit 0'],
            input="", cwd=str(tmp_path), timeout=30)
        assert r.returncode == 0 and r.timed_out is False
        pid = _wait_pidfile(pidf)
        assert not _pid_alive(pid), "같은 그룹 자손이 성공 종료 뒤에도 살아 있다"

    def test_unkillable_group_fails_closed(self, tmp_path, monkeypatch):
        """자기 프로세스 그룹을 끄지 못하면 성공으로 돌아가지 않는다(fail closed)."""
        pidf = tmp_path / "bg.pid"
        monkeypatch.setattr(ex, "_kill_process_tree", lambda proc, timeout=None: None)
        monkeypatch.setattr(ex, "REAP_GRACE", 0.5)
        try:
            with pytest.raises(ex.DescendantSurvived):
                ex._run_agent_process(
                    ["/bin/sh", "-c", f'sleep 60 & echo $! > {pidf}; exit 0'],
                    input="", cwd=str(tmp_path), timeout=30)
        finally:
            if pidf.exists():  # 시험이 만든 프로세스 정리
                try:
                    os.kill(int(pidf.read_text()), signal.SIGKILL)
                except (OSError, ValueError):
                    pass

    def test_only_own_process_group_is_signalled(self, tmp_path, monkeypatch):
        """시스템 전체 PID 스캔·다른 PID 개별 kill이 없다: 그룹 신호는 자기 리더 pgid에만 간다."""
        bystander = subprocess.Popen(["/bin/sleep", "30"], start_new_session=True)
        sent = []
        real_killpg = ex.os.killpg

        def spy_killpg(pgid, sig):
            sent.append(pgid)
            return real_killpg(pgid, sig)
        monkeypatch.setattr(ex.os, "killpg", spy_killpg)
        single_kills = []
        real_kill = ex.os.kill
        monkeypatch.setattr(ex.os, "kill", lambda *a: single_kills.append(a))
        try:
            r = ex._run_agent_process(["/bin/sh", "-c", "sleep 30 & exit 0"], input="",
                                      cwd=str(tmp_path), timeout=30)
            monkeypatch.setattr(ex.os, "kill", real_kill)  # 시험 정리는 실제 kill 사용
            assert single_kills == [], "개별 PID kill 금지"
            assert r.returncode == 0
            assert sent and len(set(sent)) == 1 and bystander.pid not in sent
            assert bystander.poll() is None, "그룹 밖 프로세스에 신호를 보냈다"
        finally:
            bystander.kill()
            bystander.wait()

    def test_no_environment_marker_injected(self, tmp_path):
        out = tmp_path / "env.txt"
        r = ex._run_agent_process(
            ["/bin/sh", "-c", f'env > {out}'], input="", cwd=str(tmp_path), timeout=30,
            env={"PATH": "/usr/bin:/bin", "KEEP_ME": "yes"})
        assert r.returncode == 0
        text = out.read_text()
        assert "KEEP_ME=yes" in text and "HARNESS_AGENT_RUN" not in text



# ---------------------------------------------------------------------------
# Astra final amended review — 자기 프로세스 그룹 정리는 불확실하면 fail closed
# ---------------------------------------------------------------------------

class _FakeProc:
    def __init__(self, pid=424242):
        self.pid = pid
        self.returncode = 0
        self.kill_calls = 0

    def poll(self):
        return self.returncode

    def wait(self, timeout=None):
        return self.returncode

    def kill(self):  # 리더 PID 직접 kill — 호출되면 계약 위반
        self.kill_calls += 1
        raise AssertionError("리더 PID 직접 kill 금지")

    def terminate(self):
        raise AssertionError("리더 PID 직접 terminate 금지")

    def send_signal(self, sig):
        raise AssertionError("리더 PID 직접 signal 금지")


class TestReapFailsClosedOnUncertainty:
    @pytest.fixture(autouse=True)
    def _short_grace(self, monkeypatch):
        monkeypatch.setattr(ex, "REAP_GRACE", 0.3)

    def _killpg(self, monkeypatch, on_kill, on_probe):
        seen = []

        def killpg(pgid, sig):
            seen.append((pgid, sig))
            exc = on_probe if sig == 0 else on_kill
            if exc is not None:
                raise exc
        monkeypatch.setattr(ex.os, "killpg", killpg)
        return seen

    def test_permission_denied_on_kill_and_probe_raises(self, monkeypatch):
        seen = self._killpg(monkeypatch, PermissionError(1, "denied"), PermissionError(1, "denied"))
        with pytest.raises(ex.DescendantSurvived):
            ex._reap_process_group(_FakeProc())
        assert {sig for _, sig in seen} == {signal.SIGKILL, 0}

    def test_permission_denied_on_probe_only_raises(self, monkeypatch):
        self._killpg(monkeypatch, None, PermissionError(1, "denied"))
        with pytest.raises(ex.DescendantSurvived):
            ex._reap_process_group(_FakeProc())

    def test_permission_denied_on_kill_with_alive_probe_raises(self, monkeypatch):
        self._killpg(monkeypatch, PermissionError(1, "denied"), None)
        with pytest.raises(ex.DescendantSurvived):
            ex._reap_process_group(_FakeProc())

    @pytest.mark.parametrize("probe_exc", [OSError(22, "EINVAL"), RuntimeError("weird")])
    def test_any_other_probe_failure_raises(self, monkeypatch, probe_exc):
        self._killpg(monkeypatch, None, probe_exc)
        with pytest.raises(ex.DescendantSurvived):
            ex._reap_process_group(_FakeProc())

    def test_esrch_on_probe_is_positive_termination(self, monkeypatch):
        """ESRCH(그룹에 프로세스 없음)만 종료를 확정한다 — 이때만 정상 반환."""
        self._killpg(monkeypatch, PermissionError(1, "denied"), ProcessLookupError(3, "ESRCH"))
        ex._reap_process_group(_FakeProc())

    def test_alive_until_deadline_raises(self, monkeypatch):
        self._killpg(monkeypatch, None, None)
        with pytest.raises(ex.DescendantSurvived):
            ex._reap_process_group(_FakeProc())

    def test_leader_not_reaped_is_uncertain(self, monkeypatch):
        """리더를 거두지 못했으면(poll None) 그룹이 없어 보여도 종료를 확정하지 않는다."""
        self._killpg(monkeypatch, None, ProcessLookupError(3, "ESRCH"))
        proc = _FakeProc()
        proc.returncode = None
        with pytest.raises(ex.DescendantSurvived):
            ex._reap_process_group(proc)


class TestTimeoutPathIsGroupOnly:
    """시간 초과 경로: 리더 PID 직접 kill(proc.kill) 대체 경로가 없다."""

    def _forbid_leader_kill(self, monkeypatch):
        calls = []
        for name in ("kill", "terminate", "send_signal"):
            monkeypatch.setattr(subprocess.Popen, name,
                                lambda self, *a, _n=name: calls.append(_n))
        return calls

    def test_timeout_uses_group_kill_only(self, tmp_path, monkeypatch):
        calls = self._forbid_leader_kill(monkeypatch)
        sent = []
        real = ex.os.killpg
        monkeypatch.setattr(ex.os, "killpg", lambda pg, sig: (sent.append((pg, sig)), real(pg, sig)))
        r = ex._run_agent_process(["/bin/sh", "-c", "sleep 30 & sleep 30"], input="",
                                  cwd=str(tmp_path), timeout=0.5, kill_grace=5)
        assert r.timed_out is True
        assert calls == [], f"리더 PID 직접 신호: {calls}"
        assert sent and len({pg for pg, _ in sent}) == 1

    def test_timeout_with_denied_group_kill_fails_closed(self, tmp_path, monkeypatch):
        calls = self._forbid_leader_kill(monkeypatch)
        pidf = tmp_path / "leader.pid"
        real = ex.os.killpg

        def denied(pg, sig):
            if sig == signal.SIGKILL:
                raise PermissionError(1, "denied")
            return real(pg, sig)
        monkeypatch.setattr(ex.os, "killpg", denied)
        try:
            with pytest.raises(ex.DescendantSurvived):
                ex._run_agent_process(
                    ["/bin/sh", "-c", f"echo $$ > {pidf}; sleep 30"], input="",
                    cwd=str(tmp_path), timeout=0.5, kill_grace=1)
            assert calls == [], f"리더 PID 직접 신호: {calls}"
        finally:
            monkeypatch.setattr(ex.os, "killpg", real)
            if pidf.exists():  # 시험이 만든 그룹 정리
                with contextlib.suppress(OSError, ValueError):
                    os.killpg(int(pidf.read_text()), signal.SIGKILL)

    def test_source_has_no_leader_kill_fallback(self):
        src = Path(ex.__file__).read_text(encoding="utf-8")
        body = src[src.index("def _run_agent_process"):src.index("def _install_signal_exit")]
        assert "proc.kill(" not in body and "proc.terminate(" not in body
