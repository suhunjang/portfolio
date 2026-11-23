"""E. 외부 runner 계약 — sandbox-exec profile, launch descriptor, control hash, git ref 불변.

sandbox 시험은 실제 /usr/bin/sandbox-exec로 프로세스를 띄워 허용/거부를 확인한다.
"""
import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent))
import runner as rn  # noqa: E402
import plan_manifest as pm  # noqa: E402
from conftest import git  # noqa: E402

HAS_SANDBOX = Path(rn.SANDBOX_EXEC).exists()
needs_sandbox = pytest.mark.skipif(not HAS_SANDBOX, reason="sandbox-exec 없음")


@pytest.fixture
def layout(tmp_path):
    base = Path(os.path.realpath(tmp_path))
    clone = base / "clone"
    for d in ("src", "tests", "phases/demo", "scripts", ".claude", ".codex",
              "docs/superpowers/specs"):
        (clone / d).mkdir(parents=True)
    (clone / "CLAUDE.md").write_text("rules", encoding="utf-8")
    (clone / "scripts/execute.py").write_text("print(1)", encoding="utf-8")
    (clone / ".claude/settings.json").write_text("{}", encoding="utf-8")
    (clone / ".codex/hooks.json").write_text("{}", encoding="utf-8")
    (clone / "phases/demo/step0.md").write_text("# s", encoding="utf-8")
    git(clone, "init", "-q", "-b", "main")
    git(clone, "config", "user.email", "t@e.com")
    git(clone, "config", "user.name", "T")
    git(clone, "add", "-A")
    git(clone, "commit", "-q", "-m", "init")
    git(clone, "checkout", "-q", "-b", "feat/DEMO-74/demo")
    ev = base / "evidence"
    ev.mkdir()
    out = base / "out"
    out.mkdir()
    sibling = base / "sibling"
    sibling.mkdir()
    return {"base": base, "clone": clone, "ev": ev, "out": out, "sibling": sibling}


def _profile(layout, **kw):
    text = rn.build_profile(layout["clone"], ["src/", "tests/"], output_dir=layout["out"],
                            protected=[layout["ev"], layout["sibling"]], metadata_paths=[], **kw)
    p = layout["ev"] / "sandbox.sb"
    sha = rn.write_read_only(p, text)
    return p, sha


def _try_write(profile, target):
    r = subprocess.run(rn.wrap_argv(profile, ["/bin/sh", "-c", 'echo x > "$1"', "sh",
                                              str(target)]), capture_output=True, text=True)
    return r.returncode == 0


class TestProfileText:
    def test_deny_default_and_allowlist(self, layout):
        text = rn.build_profile(layout["clone"], ["src/", "tests/", "README.md"],
                                output_dir=layout["out"], protected=[], metadata_paths=[])
        assert "(deny default)" in text
        assert f'(subpath "{layout["clone"]}/src")' in text
        assert f'(literal "{layout["clone"]}/README.md")' in text
        for p in (".git", "phases", "scripts", ".claude", ".codex", ".harness"):
            assert f'(deny file-write* (subpath "{layout["clone"]}/{p}"))' in text
        assert f'(subpath "{layout["clone"]}")' not in text.split("(deny file-write*")[0]

    def test_rejects_protected_allowlist(self, layout):
        with pytest.raises(rn.RunnerError):
            rn.build_profile(layout["clone"], ["phases/"], output_dir=layout["out"],
                             protected=[], metadata_paths=[])

    def test_rejects_output_inside_clone(self, layout):
        with pytest.raises(rn.RunnerError):
            rn.build_profile(layout["clone"], ["src/"], output_dir=layout["clone"] / "src/o",
                             protected=[], metadata_paths=[])

    def test_rejects_quote_injection(self, layout):
        with pytest.raises(rn.RunnerError):
            rn.build_profile(layout["clone"], ['src/") (allow default) ("/'],
                             output_dir=layout["out"], protected=[], metadata_paths=[])

    def test_wrap_argv(self, tmp_path):
        assert rn.wrap_argv(tmp_path / "p.sb", ["claude", "-p"]) == [
            "/usr/bin/sandbox-exec", "-f", str(tmp_path / "p.sb"), "claude", "-p"]


@needs_sandbox
class TestSandboxProbe:
    """실제 sandbox-exec spawn으로 허용/거부 경계를 확인한다."""

    def test_allowed_source_and_output_writes(self, layout):
        prof, _ = _profile(layout)
        assert _try_write(prof, layout["clone"] / "src/new.py")
        assert _try_write(prof, layout["clone"] / "tests/test_new.py")
        assert _try_write(prof, layout["out"] / "result.json")

    @pytest.mark.parametrize("rel", ["phases/demo/step0.md", "phases/demo/index.json",
                                     "scripts/execute.py", ".claude/settings.json",
                                     ".codex/hooks.json", "CLAUDE.md", ".git/HEAD",
                                     ".git/config", ".git/hooks/pre-commit",
                                     ".git/refs/heads/main", "README.md",
                                     "docs/superpowers/specs/x.md", ".harness/x"])
    def test_protected_clone_paths_denied(self, layout, rel):
        prof, _ = _profile(layout)
        target = layout["clone"] / rel
        before = target.read_bytes() if target.exists() else None
        assert not _try_write(prof, target)
        assert (target.read_bytes() if target.exists() else None) == before

    def test_evidence_sibling_and_original_denied(self, layout):
        prof, _ = _profile(layout)
        assert not _try_write(prof, layout["ev"] / "approval.json")
        assert not _try_write(prof, layout["sibling"] / "x")
        assert not _try_write(prof, layout["base"] / "elsewhere")
        assert not _try_write(prof, Path.home() / ".harness-sandbox-probe")
        assert not (Path.home() / ".harness-sandbox-probe").exists()

    def test_sandboxed_git_cannot_move_refs(self, layout):
        prof, _ = _profile(layout)
        clone = layout["clone"]
        before = rn.git_fingerprint(clone, "refs/heads/feat/DEMO-74/demo")
        head = git(clone, "rev-parse", "HEAD")
        for cmd in (["git", "update-ref", "refs/heads/main", head],
                    ["git", "commit", "--allow-empty", "-m", "x"],
                    ["git", "checkout", "-q", "main"],
                    ["git", "config", "core.hooksPath", "/tmp"]):
            r = subprocess.run(rn.wrap_argv(prof, cmd), cwd=clone, capture_output=True)
            assert r.returncode != 0, cmd
        assert rn.git_fingerprint(clone, "refs/heads/feat/DEMO-74/demo") == before
        assert git(clone, "rev-parse", "--abbrev-ref", "HEAD") == "feat/DEMO-74/demo"

    def test_probe_records_results(self, layout):
        prof, _ = _profile(layout)
        res = rn.probe(prof, allowed=[layout["clone"] / "src/probe.txt"],
                       denied=[layout["clone"] / "phases/demo/probe.txt", layout["ev"] / "p"])
        assert res["ok"] is True
        assert all(r["wrote"] for r in res["allowed"])
        assert not any(r["wrote"] for r in res["denied"])

    def test_probe_fails_when_boundary_broken(self, layout):
        text = "(version 1)\n(allow default)\n"
        p = layout["ev"] / "open.sb"
        rn.write_read_only(p, text)
        res = rn.probe(p, allowed=[layout["clone"] / "src/a"], denied=[layout["ev"] / "b"])
        assert res["ok"] is False


class TestControlAndGit:
    def test_control_sha_detects_change(self, layout):
        clone = layout["clone"]
        a = rn.control_sha(clone)
        (clone / "scripts/execute.py").write_text("print(2)", encoding="utf-8")
        assert rn.control_sha(clone) != a

    def test_control_sha_ignores_pycache(self, layout):
        clone = layout["clone"]
        a = rn.control_sha(clone)
        (clone / "scripts/__pycache__").mkdir()
        (clone / "scripts/__pycache__/x.pyc").write_bytes(b"\0")
        assert rn.control_sha(clone) == a

    def test_control_sha_covers_claude_settings_and_claude_md(self, layout):
        clone = layout["clone"]
        a = rn.control_sha(clone)
        (clone / ".claude/settings.json").write_text('{"x":1}', encoding="utf-8")
        b = rn.control_sha(clone)
        (clone / "CLAUDE.md").write_text("changed", encoding="utf-8")
        assert len({a, b, rn.control_sha(clone)}) == 3

    def test_git_fingerprint_ignores_feature_ref_only(self, layout):
        clone = layout["clone"]
        ref = "refs/heads/feat/DEMO-74/demo"
        a = rn.git_fingerprint(clone, ref)
        (clone / "src/a.py").write_text("x", encoding="utf-8")
        git(clone, "add", "-A")
        git(clone, "commit", "-q", "-m", "feat")
        assert rn.git_fingerprint(clone, ref) == a
        git(clone, "branch", "other")
        assert rn.git_fingerprint(clone, ref) != a

    @pytest.mark.parametrize("mutate", [
        lambda c: git(c, "config", "core.hooksPath", "/tmp"),
        lambda c: (c / ".git/hooks/pre-commit").write_text("#!/bin/sh\n"),
        lambda c: git(c, "update-ref", "refs/heads/main", git(c, "rev-parse", "HEAD")),
        lambda c: git(c, "symbolic-ref", "HEAD", "refs/heads/main"),
        lambda c: git(c, "update-ref", "refs/remotes/origin/main", git(c, "rev-parse", "HEAD")),
    ])
    def test_git_fingerprint_detects(self, layout, mutate):
        clone = layout["clone"]
        (clone / "src/a.py").write_text("x", encoding="utf-8")
        git(clone, "add", "-A")
        git(clone, "commit", "-q", "-m", "feat")
        a = rn.git_fingerprint(clone, "refs/heads/feat/DEMO-74/demo")
        mutate(clone)
        assert rn.git_fingerprint(clone, "refs/heads/feat/DEMO-74/demo") != a


def _harness(base):
    """현재 runner 코드로 만든 'reviewed harness commit'."""
    h = base / "harness"
    (h / "scripts").mkdir(parents=True)
    here = Path(__file__).resolve().parent
    for name in rn.RUNNER_FILES:
        (h / "scripts" / name).write_bytes((here / name).read_bytes())
    git(h, "init", "-q", "-b", "main")
    git(h, "config", "user.email", "t@e.com")
    git(h, "config", "user.name", "T")
    git(h, "add", "-A")
    git(h, "commit", "-q", "-m", "reviewed")
    return h, git(h, "rev-parse", "HEAD")


class TestDescriptor:
    def _desc(self, layout, **over):
        prof = layout["ev"] / "sandbox.sb"
        if prof.exists():
            prof.chmod(0o644)
            prof.unlink()
        prof, psha = _profile(layout)
        h, hc = _harness(layout["base"]) if not (layout["base"] / "harness").exists() else (
            layout["base"] / "harness", git(layout["base"] / "harness", "rev-parse", "HEAD"))
        pin = layout["base"] / "pin.json"
        if not pin.exists():
            rn.pin_control(layout["clone"], "HEAD", h, hc, pin)
        p, pin_sha = rn.load_pin(pin, layout["clone"])
        d = rn.build_descriptor(
            task="demo", repo_root=layout["clone"], branch="feat/DEMO-74/demo",
            base_branch="main", evidence_dir=layout["ev"], approval_record_sha="a" * 64,
            sandbox_profile=prof, output_dir=layout["out"], control_pin=pin,
            control_pin_sha=pin_sha, control=p["controlSha"])
        d.update(over)
        path = layout["base"] / "launch.json"
        if path.exists():
            path.chmod(0o644)
            path.unlink()
        rn.write_read_only(path, json.dumps(d))
        return path, d

    def test_round_trip(self, layout):
        path, d = self._desc(layout)
        got = rn.load_descriptor(path, layout["clone"])
        assert got["controlSha"] == rn.control_sha(layout["clone"])
        assert got["manifestCodeSha"] == pm.code_sha()

    def test_missing_rejected(self, layout):
        with pytest.raises(rn.RunnerError):
            rn.load_descriptor(None, layout["clone"])
        with pytest.raises(rn.RunnerError):
            rn.load_descriptor(layout["base"] / "nope.json", layout["clone"])

    def test_writable_rejected(self, layout):
        path, _ = self._desc(layout)
        path.chmod(0o644)
        with pytest.raises(rn.RunnerError):
            rn.load_descriptor(path, layout["clone"])

    def test_inside_repo_rejected(self, layout):
        path, d = self._desc(layout)
        inside = layout["clone"] / "launch.json"
        rn.write_read_only(inside, json.dumps(d))
        with pytest.raises(rn.RunnerError):
            rn.load_descriptor(inside, layout["clone"])

    def test_symlink_rejected(self, layout):
        path, _ = self._desc(layout)
        link = layout["base"] / "link.json"
        link.symlink_to(path)
        with pytest.raises(rn.RunnerError):
            rn.load_descriptor(link, layout["clone"])

    def test_control_change_rejected(self, layout):
        path, _ = self._desc(layout)
        (layout["clone"] / "scripts/execute.py").write_text("print('gate removed')")
        with pytest.raises(rn.RunnerError):
            rn.load_descriptor(path, layout["clone"])

    def test_profile_change_rejected(self, layout):
        path, d = self._desc(layout)
        prof = Path(d["sandboxProfile"])
        prof.chmod(0o644)
        prof.write_text("(version 1)(allow default)")
        prof.chmod(0o444)
        with pytest.raises(rn.RunnerError):
            rn.load_descriptor(path, layout["clone"])

    @pytest.mark.parametrize("over", [{"repoRoot": "/tmp"}, {"extra": 1}, {"version": 1},
                                      {"branch": "main"}, {"baseBranch": "develop"},
                                      {"controlPin": None}, {"controlPinSha": "0" * 64},
                                      {"containmentToken": "/legacy/token"},
                                      {"approvalRecordSha": "xyz"},
                                      {"manifestCodeSha": "0" * 64},
                                      {"outputDir": "<missing-dir>"}])
    def test_bad_fields_rejected(self, layout, over):
        if over.get("outputDir") == "<missing-dir>":
            # 호스트 중립: 이 테스트가 만든 임시 root 아래의 존재하지 않는 절대경로
            over = {"outputDir": str(layout["base"] / "nonexistent-out")}
        path, _ = self._desc(layout, **over)
        with pytest.raises(rn.RunnerError):
            rn.load_descriptor(path, layout["clone"])

    def test_output_inside_evidence_rejected(self, layout):
        (layout["ev"] / "o").mkdir()
        path, _ = self._desc(layout, outputDir=str(layout["ev"] / "o"))
        with pytest.raises(rn.RunnerError):
            rn.load_descriptor(path, layout["clone"])

    def test_branch_pattern_comes_from_policy(self, layout, monkeypatch):
        """descriptor branch 패턴의 issue key는 policy issueKeyPattern이다."""
        import runtime
        from conftest import FIXTURE_POLICY
        pol = dict(FIXTURE_POLICY, issueKeyPattern="PROJ-[0-9]+", issueScopedThreads={})
        parsed = runtime.parse_policy(json.dumps(pol).encode("utf-8"))
        monkeypatch.setattr(runtime, "policy", lambda: parsed)
        path, _ = self._desc(layout, branch="feat/PROJ-3/demo")
        assert rn.load_descriptor(path, layout["clone"])["branch"] == "feat/PROJ-3/demo"
        path, _ = self._desc(layout)  # feat/DEMO-74/demo — 이 policy에서는 패턴 밖
        with pytest.raises(rn.RunnerError):
            rn.load_descriptor(path, layout["clone"])


class TestExtraProtectedPaths:
    """원본 템플릿 같은 호스트 전용 보호 경로는 코드 상수가 아니라
    policy.local.json의 extraProtectedPaths다(배포 코드에 호스트 절대경로 없음)."""

    def test_no_host_constant(self):
        assert not hasattr(rn, "ORIGINAL_TEMPLATE")

    def test_local_policy_paths_are_denied_and_not_writable_roots(self, layout, monkeypatch):
        import runtime
        orig = layout["sibling"] / "original-template"
        orig.mkdir()
        monkeypatch.setattr(runtime, "extra_protected_paths", lambda: [str(orig)])
        text = rn.build_profile(layout["clone"], ["src/"], output_dir=layout["out"],
                                protected=[layout["ev"]], metadata_paths=[])
        assert '(deny file-write* (subpath "%s"))' % orig in text
        with pytest.raises(rn.RunnerError):
            rn.build_profile(layout["clone"], ["src/"], output_dir=orig / "out",
                             protected=[layout["ev"]], metadata_paths=[])

    def test_symlinked_extra_path_is_denied_by_real_path(self, layout, monkeypatch):
        """보호 경로가 symlink로 주어져도 deny 규칙은 실제 경로(다른 보호 경로와 같은 realpath 처리)."""
        import runtime
        real = layout["sibling"] / "real-template"
        real.mkdir()
        link = layout["base"] / "template-link"
        link.symlink_to(real, target_is_directory=True)
        monkeypatch.setattr(runtime, "extra_protected_paths", lambda: [str(link)])
        text = rn.build_profile(layout["clone"], ["src/"], output_dir=layout["out"],
                                protected=[layout["ev"]], metadata_paths=[])
        assert '(deny file-write* (subpath "%s"))' % real in text

    @needs_sandbox
    def test_local_policy_path_write_denied_by_real_sandbox(self, layout, monkeypatch):
        import runtime
        orig = layout["sibling"] / "original-template"
        orig.mkdir()
        monkeypatch.setattr(runtime, "extra_protected_paths", lambda: [str(orig)])
        prof, _ = _profile(layout)
        assert not _try_write(prof, orig / "x")
        assert not (orig / "x").exists()


class TestVerifyFinal:
    def _final(self, layout, tested, reviewed):
        rn.write_read_only(layout["ev"] / "final.json", json.dumps(
            {"testedSha": tested, "reviewedSha": reviewed}))

    def test_equal_ok(self, layout):
        head = git(layout["clone"], "rev-parse", "HEAD")
        self._final(layout, head, head)
        assert rn.verify_final(layout["clone"], layout["ev"] / "final.json") == head

    def test_mismatch_rejected(self, layout):
        head = git(layout["clone"], "rev-parse", "HEAD")
        self._final(layout, head, "b" * 40)
        with pytest.raises(rn.RunnerError):
            rn.verify_final(layout["clone"], layout["ev"] / "final.json")

    def test_head_moved_after_review_rejected(self, layout):
        head = git(layout["clone"], "rev-parse", "HEAD")
        self._final(layout, head, head)
        git(layout["clone"], "commit", "-q", "--allow-empty", "-m", "post-review")
        with pytest.raises(rn.RunnerError):
            rn.verify_final(layout["clone"], layout["ev"] / "final.json")

    def test_dirty_tree_rejected(self, layout):
        head = git(layout["clone"], "rev-parse", "HEAD")
        self._final(layout, head, head)
        (layout["clone"] / "src/dirty.py").write_text("x")
        with pytest.raises(rn.RunnerError):
            rn.verify_final(layout["clone"], layout["ev"] / "final.json")


# ---------------------------------------------------------------------------
# Astra 리뷰 B2 — 쓰기 root가 clone·sibling·보호 경로와 겹치면 거부, /private/tmp 제거
# ---------------------------------------------------------------------------

class TestB2WriteRoots:
    def _build(self, layout, out, protected=None, meta=None):
        return rn.build_profile(layout["clone"], ["src/"], output_dir=out,
                                protected=protected if protected is not None else [layout["ev"]],
                                metadata_paths=meta if meta is not None else [])

    def test_output_ancestor_of_clone_rejected(self, layout):
        with pytest.raises(rn.RunnerError):
            self._build(layout, layout["base"])

    def test_output_equal_clone_rejected(self, layout):
        with pytest.raises(rn.RunnerError):
            self._build(layout, layout["clone"])

    def test_output_inside_sibling_repo_rejected(self, layout):
        sib = layout["base"] / "sibling-repo"
        (sib / "work").mkdir(parents=True)
        git(sib, "init", "-q")
        with pytest.raises(rn.RunnerError):
            self._build(layout, sib / "work")

    def test_output_containing_sibling_repo_rejected(self, layout):
        holder = layout["base"] / "holder"
        (holder / "repo").mkdir(parents=True)
        git(holder / "repo", "init", "-q")
        with pytest.raises(rn.RunnerError):
            self._build(layout, holder)

    @pytest.mark.parametrize("rel", ["", "sub"])
    def test_output_overlapping_protected_rejected(self, layout, rel):
        out = layout["ev"] / rel if rel else layout["ev"]
        out.mkdir(parents=True, exist_ok=True)
        with pytest.raises(rn.RunnerError):
            self._build(layout, out)

    def test_output_containing_protected_rejected(self, layout):
        outer = layout["base"] / "outer"
        (outer / "ev2").mkdir(parents=True)
        with pytest.raises(rn.RunnerError):
            self._build(layout, outer, protected=[outer / "ev2"])

    @pytest.mark.parametrize("meta", ["/private/tmp", "/tmp", "/", "HOME"])
    def test_broad_metadata_grant_rejected(self, layout, meta):
        m = str(Path.home()) if meta == "HOME" else meta
        with pytest.raises(rn.RunnerError):
            self._build(layout, layout["out"], meta=[m])

    def test_metadata_overlapping_clone_rejected(self, layout):
        with pytest.raises(rn.RunnerError):
            self._build(layout, layout["out"], meta=[str(layout["base"])])

    def test_defaults_have_no_tmp_grant(self):
        meta = rn.default_metadata_paths()
        assert not any(m in ("/private/tmp", "/tmp") or m.startswith(("/private/tmp/", "/tmp/"))
                       for m in meta)
        assert all(Path(m).is_absolute() and str(Path.home()) in m for m in meta)

    def test_profile_text_has_no_tmp_grant(self, layout):
        text = rn.build_profile(layout["clone"], ["src/"], output_dir=layout["out"],
                                protected=[layout["ev"]],
                                metadata_paths=rn.default_metadata_paths())
        assert '"/private/tmp"' not in text and '"/tmp"' not in text


@needs_sandbox
class TestB2ProductionProfileProbe:
    """운영과 같은 metadata grant로 실제 sandbox 경계를 실측한다."""

    def test_production_profile_boundary(self, layout):
        text = rn.build_profile(layout["clone"], ["src/", "tests/"], output_dir=layout["out"],
                                protected=[layout["ev"]],
                                metadata_paths=rn.default_metadata_paths())
        prof = layout["ev"] / "prod.sb"
        rn.write_read_only(prof, text)
        tmp_probe = Path("/private/tmp") / f"harness-probe-{os.getpid()}"
        res = rn.probe(prof, allowed=[layout["clone"] / "src/p", layout["out"] / "p"],
                       denied=[tmp_probe, layout["sibling"] / "p", layout["base"] / "p",
                               layout["clone"] / "phases/p", layout["clone"] / ".git/p",
                               layout["ev"] / "p", Path.home() / f".harness-probe-{os.getpid()}"])
        assert res["ok"], res
        assert not tmp_probe.exists()


class TestM2Pin:
    def test_pin_from_commit_matches_clean_worktree(self, layout):
        assert rn.control_sha_at_commit(layout["clone"], "HEAD") == rn.control_sha(layout["clone"])

    def test_committed_control_change_differs_from_reviewed_pin(self, layout):
        reviewed = git(layout["clone"], "rev-parse", "HEAD")
        (layout["clone"] / "scripts/execute.py").write_text("print('no gates')")
        git(layout["clone"], "commit", "-qam", "weaken")
        assert rn.control_sha_at_commit(layout["clone"], reviewed) != rn.control_sha(layout["clone"])

    def test_runner_code_sha_from_commit_matches_export(self, layout, tmp_path):
        h, hc = _harness(layout["base"])
        dest = tmp_path / "rh" / "scripts"
        assert rn.export_runner(h, hc, dest) == rn.runner_code_sha_at_commit(h, hc)
        assert all(not ((dest / n).stat().st_mode & 0o222) for n in rn.RUNNER_FILES)

    def test_pin_inside_clone_rejected(self, layout):
        h, hc = _harness(layout["base"])
        with pytest.raises(rn.RunnerError):
            rn.pin_control(layout["clone"], "HEAD", h, hc, layout["clone"] / "pin.json")

    def test_descriptor_rejects_runner_code_drift(self, layout, tmp_path):
        path, d = TestDescriptor()._desc(layout)
        other = tmp_path / "other-runner"
        other.mkdir()
        for n in rn.RUNNER_FILES:
            (other / n).write_bytes((Path(rn.__file__).parent / n).read_bytes())
        (other / "execute.py").write_text("# tampered\n")
        with pytest.raises(rn.RunnerError):
            rn.load_descriptor(path, layout["clone"], runner_dir=other)

    def test_ticket_single_use_and_bound(self, layout):
        path, d = TestDescriptor()._desc(layout)
        d = rn.load_descriptor(path, layout["clone"])
        t = rn.write_ticket(d, path)
        rn.consume_ticket(t, path, d)
        with pytest.raises(rn.RunnerError):
            rn.consume_ticket(t, path, d)
        with pytest.raises(rn.RunnerError):
            rn.consume_ticket(None, path, d)


# ---------------------------------------------------------------------------
# Astra re-review B3 — 에이전트가 쓸 수 있는 저장소에 대한 신뢰 I/O
# ---------------------------------------------------------------------------

class TestB3SafeAgentIO:
    @pytest.fixture
    def area(self, tmp_path):
        base = Path(os.path.realpath(tmp_path))
        out = base / "out"
        out.mkdir()
        victim = base / "mainclone" / "victim.txt"
        victim.parent.mkdir()
        victim.write_bytes(b"PRECIOUS\n")
        return base, out, victim

    def test_read_rejects_symlink(self, area):
        base, out, victim = area
        (out / "r.json").symlink_to(victim)
        with pytest.raises(rn.RunnerError):
            rn.read_agent_file(out, "r.json")

    def test_read_rejects_hardlink(self, area):
        base, out, victim = area
        os.link(victim, out / "r.json")
        with pytest.raises(rn.RunnerError):
            rn.read_agent_file(out, "r.json")

    def test_read_rejects_fifo_without_blocking(self, area):
        base, out, victim = area
        os.mkfifo(out / "r.json")
        with pytest.raises(rn.RunnerError):
            rn.read_agent_file(out, "r.json")

    def test_read_rejects_oversize(self, area):
        base, out, victim = area
        (out / "r.json").write_bytes(b"x" * (rn.AGENT_FILE_MAX + 1))
        with pytest.raises(rn.RunnerError):
            rn.read_agent_file(out, "r.json")

    def test_read_missing_is_none_and_regular_ok(self, area):
        base, out, victim = area
        assert rn.read_agent_file(out, "r.json") is None
        (out / "r.json").write_bytes(b'{"status": "completed"}')
        assert rn.read_agent_file(out, "r.json") == b'{"status": "completed"}'

    def test_read_rejects_symlinked_directory(self, area):
        base, out, victim = area
        link = base / "outlink"
        link.symlink_to(out, target_is_directory=True)
        (out / "r.json").write_bytes(b"{}")
        with pytest.raises(rn.RunnerError):
            rn.read_agent_file(link, "r.json")

    @pytest.mark.parametrize("name", ["../x", "a/b", "", "."])
    def test_bad_names_rejected(self, area, name):
        base, out, victim = area
        with pytest.raises(rn.RunnerError):
            rn.read_agent_file(out, name)

    def test_remove_does_not_follow(self, area):
        base, out, victim = area
        (out / "r.json").symlink_to(victim)
        rn.remove_agent_entry(out, "r.json")
        assert not os.path.lexists(out / "r.json")
        assert victim.read_bytes() == b"PRECIOUS\n"

    def test_remove_hardlink_keeps_target(self, area):
        base, out, victim = area
        os.link(victim, out / "r.json")
        rn.remove_agent_entry(out, "r.json")
        assert victim.read_bytes() == b"PRECIOUS\n"

    def test_fresh_dir_replaces_symlink_swap(self, area):
        base, out, victim = area
        ext = base / "external-dir"
        ext.mkdir()
        (ext / "keep").write_bytes(b"K")
        (out / "tmp").symlink_to(ext, target_is_directory=True)
        p = rn.fresh_agent_dir(out, "tmp")
        assert p == out / "tmp" and (out / "tmp").is_dir() and not (out / "tmp").is_symlink()
        assert sorted(x.name for x in ext.iterdir()) == ["keep"]
        assert (ext / "keep").read_bytes() == b"K"

    def test_fresh_dir_replaces_file(self, area):
        base, out, victim = area
        os.link(victim, out / "tmp")
        rn.fresh_agent_dir(out, "tmp")
        assert (out / "tmp").is_dir()
        assert victim.read_bytes() == b"PRECIOUS\n"


class TestProfileHasNoOsHardening:
    """MVP amendment: profile은 쓰기 경계만 — containment token·launchd exec 차단이 없다."""

    def test_profile_has_no_containment_or_launchd_rules(self, layout):
        text = rn.build_profile(layout["clone"], ["src/"], output_dir=layout["out"],
                                protected=[layout["ev"]], metadata_paths=[])
        assert "deny process-exec" not in text and "launchctl" not in text
        assert "containment" not in text and "allow file-write-data" not in text
        assert "(deny default)" in text
