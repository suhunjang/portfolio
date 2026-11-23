import subprocess
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

sys.path.insert(0, str(Path(__file__).parent))
import cross_review as cr


class TestParseTarget:
    def test_no_args_defaults_to_diff(self):
        assert cr._parse_target([]) == ("diff", None)

    def test_diff_explicit(self):
        assert cr._parse_target(["diff"]) == ("diff", None)

    def test_diff_with_ref(self):
        assert cr._parse_target(["diff", "HEAD~3"]) == ("diff", "HEAD~3")

    def test_spec_with_path(self):
        assert cr._parse_target(["spec", "docs/a.md"]) == ("spec", "docs/a.md")

    def test_plan_with_task(self):
        assert cr._parse_target(["plan", "0-mvp"]) == ("plan", "0-mvp")

    def test_spec_without_path_exits(self):
        with pytest.raises(SystemExit):
            cr._parse_target(["spec"])

    def test_plan_without_task_exits(self):
        with pytest.raises(SystemExit):
            cr._parse_target(["plan"])

    def test_unknown_kind_exits(self):
        with pytest.raises(SystemExit):
            cr._parse_target(["bogus"])


class TestCollectDiff:
    def test_returns_diff_text(self):
        mock = MagicMock(returncode=0, stdout="diff --git a/x b/x\n", stderr="")
        with patch("subprocess.run", return_value=mock):
            assert "diff --git" in cr._collect_diff("HEAD")

    def test_empty_diff_returns_empty(self):
        mock = MagicMock(returncode=0, stdout="", stderr="")
        with patch("subprocess.run", return_value=mock):
            assert cr._collect_diff("HEAD") == ""

    def test_uses_given_ref(self):
        mock = MagicMock(returncode=0, stdout="", stderr="")
        with patch("subprocess.run", return_value=mock) as m:
            cr._collect_diff("HEAD~2")
        assert "HEAD~2" in m.call_args[0][0]


class TestCollectSpec:
    def test_reads_file(self, tmp_path, monkeypatch):
        monkeypatch.setattr(cr, "ROOT", tmp_path)
        f = tmp_path / "spec.md"
        f.write_text("# hello", encoding="utf-8")
        assert "# hello" in cr._collect_spec("spec.md")

    def test_missing_file_exits(self, tmp_path, monkeypatch):
        monkeypatch.setattr(cr, "ROOT", tmp_path)
        with pytest.raises(SystemExit):
            cr._collect_spec("nope.md")

    def test_path_traversal_exits(self, tmp_path, monkeypatch):
        monkeypatch.setattr(cr, "ROOT", tmp_path)
        with pytest.raises(SystemExit):
            cr._collect_spec("../outside.md")


class TestReviewCriteria:
    def test_has_all_kinds(self):
        assert set(cr.REVIEW_CRITERIA) == {"diff", "spec"}

    def test_diff_criteria_forbids_style_nits(self):
        assert "스타일" in cr.REVIEW_CRITERIA["diff"]


class TestRunReview:
    def test_uses_readonly_sandbox(self, monkeypatch):
        mock = MagicMock(returncode=0, stdout="CLEAN", stderr="")
        with patch("subprocess.run", return_value=mock) as m:
            cr._run_review("diff", "some diff")
        argv = m.call_args[0][0]
        assert argv[:2] == ["codex", "exec"]
        assert "--sandbox" in argv and "read-only" in argv
        assert argv[argv.index("--model") + 1] == "gpt-6-astra"
        assert "--dangerously-bypass-approvals-and-sandbox" not in argv

    def test_ignores_env_sandbox_override(self, monkeypatch):
        """리뷰는 항상 read-only — HARNESS_CODEX_SANDBOX를 따르지 않는다."""
        monkeypatch.setenv("HARNESS_CODEX_SANDBOX", "workspace-write")
        mock = MagicMock(returncode=0, stdout="CLEAN", stderr="")
        with patch("subprocess.run", return_value=mock) as m:
            cr._run_review("diff", "some diff")
        argv = m.call_args[0][0]
        assert "read-only" in argv
        assert "workspace-write" not in argv

    def test_body_and_criteria_go_to_stdin(self, monkeypatch):
        mock = MagicMock(returncode=0, stdout="CLEAN", stderr="")
        with patch("subprocess.run", return_value=mock) as m:
            cr._run_review("diff", "MARKER_DIFF_BODY")
        stdin = m.call_args[1]["input"]
        assert "MARKER_DIFF_BODY" in stdin
        assert "스타일" in stdin  # diff 기준이 들어감

    def test_nonzero_returncode_is_failure(self, monkeypatch):
        mock = MagicMock(returncode=1, stdout="", stderr="boom")
        with patch("subprocess.run", return_value=mock):
            assert cr._run_review("diff", "d") is False

    def test_empty_stdout_is_failure(self, monkeypatch):
        """codex가 0으로 끝나도 아무 말 없으면 리뷰가 아니다."""
        mock = MagicMock(returncode=0, stdout="   ", stderr="")
        with patch("subprocess.run", return_value=mock):
            assert cr._run_review("diff", "d") is False

    def test_missing_codex_cli_is_failure(self, monkeypatch):
        with patch("subprocess.run", side_effect=FileNotFoundError()):
            assert cr._run_review("diff", "d") is False

    def test_timeout_is_failure(self, monkeypatch):
        with patch("subprocess.run",
                   side_effect=subprocess.TimeoutExpired("codex", 900)):
            assert cr._run_review("diff", "d") is False


class TestTouchState:
    def test_creates_state_file(self, tmp_path, monkeypatch):
        monkeypatch.setattr(cr, "STATE_FILE", tmp_path / ".claude" / ".st")
        cr._touch_state()
        assert (tmp_path / ".claude" / ".st").exists()

    def test_writes_fingerprint_not_prose(self, tmp_path, monkeypatch):
        """state에는 '<HEAD sha> <diff 해시>'가 들어가야 한다.

        nudge hook이 이 문자열을 그대로 비교하므로 형식이 계약이다.
        """
        st = tmp_path / ".st"
        monkeypatch.setattr(cr, "STATE_FILE", st)
        cr._touch_state()
        head, _, digest = st.read_text(encoding="utf-8").strip().partition(" ")
        assert len(head) == 40 and all(c in "0123456789abcdef" for c in head)
        assert len(digest) == 64, f"sha256 자리가 아님: {digest!r}"

    def test_fingerprint_survives_non_utf8_bytes(self, monkeypatch):
        """비-UTF-8 바이트가 섞여도 예외 없이 지문을 낸다.

        여기서 터지면 hook의 `|| exit 0`이 삼켜 **이후 알림이 영영 사라진다**
        (조용한 실패 — 이 도구에서 가장 나쁜 실패 모드).
        """
        def fake_run(argv, **kw):
            return MagicMock(returncode=0, stdout=b"\xff\xfe binary \x80")
        with patch("subprocess.run", side_effect=fake_run):
            fp = cr._worktree_fingerprint()
        assert len(fp.split(" ")[-1]) == 64

    def test_fingerprint_raises_when_git_fails(self, monkeypatch):
        """git이 실패하면 실패한 출력을 정상 지문으로 쓰면 안 된다."""
        def fake_run(argv, **kw):
            return MagicMock(returncode=128, stdout=b"", stderr=b"fatal")
        with patch("subprocess.run", side_effect=fake_run):
            with pytest.raises(RuntimeError):
                cr._worktree_fingerprint()

    def test_fingerprint_changes_when_worktree_changes(self, tmp_path, monkeypatch):
        st = tmp_path / ".st"
        monkeypatch.setattr(cr, "STATE_FILE", st)
        monkeypatch.setattr(cr, "_worktree_fingerprint", lambda: "sha_a hash_a")
        cr._touch_state()
        first = st.read_text(encoding="utf-8")
        monkeypatch.setattr(cr, "_worktree_fingerprint", lambda: "sha_a hash_b")
        cr._touch_state()
        assert st.read_text(encoding="utf-8") != first


class TestFingerprintFlag:
    """nudge hook이 지문을 얻는 경로. hook과의 계약이므로 깨지면 안 된다."""

    def test_fingerprint_flag_prints_and_exits_zero(self, monkeypatch, capsys):
        monkeypatch.setattr(cr, "_worktree_fingerprint", lambda: "sha digest")
        with pytest.raises(SystemExit) as e:
            cr.main(["--fingerprint"])
        assert e.value.code == 0
        assert capsys.readouterr().out.strip() == "sha digest"

    def test_fingerprint_flag_does_not_invoke_codex(self, monkeypatch):
        """지문 조회는 순수 조회다 — 리뷰를 돌리면 안 된다(Stop hook마다 실행됨)."""
        monkeypatch.setattr(cr, "_worktree_fingerprint", lambda: "sha digest")
        called = []
        monkeypatch.setattr(cr, "_run_review",
                            lambda k, b: called.append(1) or True)
        with pytest.raises(SystemExit):
            cr.main(["--fingerprint"])
        assert not called, "지문 조회가 codex를 부르면 안 된다"

    def test_fingerprint_flag_does_not_touch_state(self, monkeypatch):
        """조회가 state를 갱신하면 미리뷰 코드가 리뷰된 것으로 표시된다."""
        monkeypatch.setattr(cr, "_worktree_fingerprint", lambda: "sha digest")
        touched = []
        monkeypatch.setattr(cr, "_touch_state", lambda: touched.append(1))
        with pytest.raises(SystemExit):
            cr.main(["--fingerprint"])
        assert not touched


class TestMain:
    def test_empty_diff_exits_zero_without_review(self, monkeypatch):
        monkeypatch.setattr(cr, "_collect_diff", lambda ref: "")
        called = []
        monkeypatch.setattr(cr, "_run_review",
                            lambda k, b: called.append(1) or True)
        with pytest.raises(SystemExit) as e:
            cr.main([])
        assert e.value.code == 0
        assert not called, "빈 diff에 codex를 부르면 안 된다"

    def test_state_not_touched_on_review_failure(self, monkeypatch):
        monkeypatch.setattr(cr, "_collect_diff", lambda ref: "d")
        monkeypatch.setattr(cr, "_run_review", lambda k, b: False)
        touched = []
        monkeypatch.setattr(cr, "_touch_state", lambda: touched.append(1))
        with pytest.raises(SystemExit) as e:
            cr.main([])
        assert e.value.code == 2
        assert not touched, "리뷰 실패 시 state를 갱신하면 안 된다"

    def test_state_touched_on_success(self, monkeypatch):
        monkeypatch.setattr(cr, "_collect_diff", lambda ref: "d")
        monkeypatch.setattr(cr, "_run_review", lambda k, b: True)
        touched = []
        monkeypatch.setattr(cr, "_touch_state", lambda: touched.append(1))
        with pytest.raises(SystemExit) as e:
            cr.main([])
        assert e.value.code == 0
        assert touched

    def test_spec_review_does_not_touch_state(self, tmp_path, monkeypatch):
        """spec 리뷰는 코드 state를 갱신하면 안 된다.

        state는 "tracked 파일이 마지막 리뷰 이후 바뀌었나"를 재는 기준인데,
        설계 문서를 리뷰했다고 코드가 리뷰된 것으로 표시되면 미리뷰 코드가
        조용히 묻힌다. 실측으로 확인된 버그(2026-07-21): spec 리뷰 한 번에
        nudge가 조용해졌다.
        """
        monkeypatch.setattr(cr, "_collect_spec", lambda p: "# spec 본문")
        monkeypatch.setattr(cr, "_run_review", lambda k, b: True)
        touched = []
        monkeypatch.setattr(cr, "_touch_state", lambda: touched.append(1))
        with pytest.raises(SystemExit) as e:
            cr.main(["spec", "docs/a.md"])
        assert e.value.code == 0
        assert not touched, "spec 리뷰가 코드 리뷰 state를 갱신하면 안 된다"

    def test_plan_delegates_to_review_plan(self, monkeypatch):
        mock = MagicMock(returncode=0)
        with patch("subprocess.run", return_value=mock) as m:
            with pytest.raises(SystemExit):
                cr.main(["plan", "0-mvp"])
        cmd = m.call_args[0][0]
        assert "review_plan.py" in " ".join(str(c) for c in cmd)
        assert "0-mvp" in cmd

    def test_plan_delegation_forwards_evidence_dir(self):
        mock = MagicMock(returncode=0)
        with patch("subprocess.run", return_value=mock) as m:
            with pytest.raises(SystemExit):
                cr.main(["plan", "0-mvp", "--evidence-dir", "/ev"])
        assert m.call_args[0][0][-3:] == ["0-mvp", "--evidence-dir", "/ev"]
