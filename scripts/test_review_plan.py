"""C. 계획 리뷰 — codex gpt-6-astra 명시, strict schema/model/hash, 자동 수정 없음."""
import hashlib
import json
import os
import stat
import subprocess
import sys
import textwrap
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent))
import review_plan as rp  # noqa: E402
import execute as ex  # noqa: E402
import plan_manifest as pm  # noqa: E402
from conftest import git, make_harness_root, make_plan  # noqa: E402

ASTRA_ENV = {"HARNESS_REVIEW_BACKEND": "codex", "HARNESS_REVIEW_MODEL": "gpt-6-astra"}


@pytest.fixture(autouse=True)
def _clean_env(monkeypatch):
    for k in [k for k in os.environ if k.startswith("HARNESS_")]:
        monkeypatch.delenv(k)


@pytest.fixture
def root(plan_repo):
    return plan_repo


@pytest.fixture
def evidence(tmp_path):
    d = tmp_path / "evidence"
    d.mkdir()
    return d


def _result(root, task="demo", **over):
    obj = {"task": task, "review_backend": "codex", "review_model": "gpt-6-astra",
           "reviewed_plan_sha": pm.build_manifest(root, task).sha,
           "verdict": "clean", "findings": []}
    obj.update(over)
    return obj


def _finding(**over):
    f = {"severity": "major", "step_file": "step0.md", "principle": "scope",
         "summary": "too big", "fix": "split"}
    f.update(over)
    return f


class FakeRunner:
    def __init__(self, stdout="", rc=0, timed_out=False, side_effect=None):
        self.calls = []
        self.stdout, self.rc, self.timed_out, self.side_effect = stdout, rc, timed_out, side_effect

    def __call__(self, argv, *, input, cwd, timeout, kill_grace=30):
        self.calls.append({"argv": argv, "input": input, "cwd": cwd, "timeout": timeout})
        if self.side_effect:
            self.side_effect()
        out = self.stdout() if callable(self.stdout) else self.stdout
        return ex.AgentRun(self.rc, out, "", self.timed_out)


def _run(root, evidence, stdout, **kw):
    runner = FakeRunner(stdout=stdout, **kw)
    code, path, sha = rp.run_review(root, "demo", evidence, "DEMO-74", runner=runner)
    rec = json.loads(Path(path).read_text(encoding="utf-8")) if path else None
    return code, rec, sha, runner


class TestArgv:
    def test_codex_readonly_astra_explicit(self):
        argv = rp.build_review_argv()
        assert argv[:2] == ["codex", "exec"]
        assert argv[argv.index("--model") + 1] == "gpt-6-astra"
        assert argv[argv.index("--sandbox") + 1] == "read-only"
        assert "--dangerously-bypass-approvals-and-sandbox" not in argv
        assert "workspace-write" not in argv


class TestPreflight:
    @pytest.mark.parametrize("env", [{}, {"HARNESS_REVIEW_BACKEND": "codex"},
                                     {"HARNESS_REVIEW_BACKEND": "claude",
                                      "HARNESS_REVIEW_MODEL": "gpt-6-astra"},
                                     {"HARNESS_REVIEW_BACKEND": "codex",
                                      "HARNESS_REVIEW_MODEL": "o3"}])
    def test_policy_required(self, root, evidence, monkeypatch, env):
        for k, v in env.items():
            monkeypatch.setenv(k, v)
        monkeypatch.setattr(rp, "ROOT", root)
        with pytest.raises(SystemExit) as e:
            rp.main(["demo", "--repo-root", str(root), "--issue", "DEMO-74",
                     "--evidence-dir", str(evidence)])
        assert e.value.code == 1

    def test_evidence_inside_repo_rejected(self, root, monkeypatch):
        for k, v in ASTRA_ENV.items():
            monkeypatch.setenv(k, v)
        monkeypatch.setattr(rp, "ROOT", root)
        with pytest.raises(SystemExit) as e:
            rp.main(["demo", "--repo-root", str(root), "--issue", "DEMO-74",
                     "--evidence-dir", str(root / ".harness" / "ev")])
        assert e.value.code == 1

    def test_requires_all_pending(self, root, evidence):
        p = root / "phases/demo/index.json"
        d = json.loads(p.read_text(encoding="utf-8"))
        d["steps"][0]["status"] = "completed"
        p.write_text(json.dumps(d), encoding="utf-8")
        git(root, "commit", "-qam", "chore: mark completed")
        code, rec, _, runner = _run(root, evidence, "{}")
        assert code == 2 and runner.calls == []

    def test_invalid_manifest_never_spawns(self, root, evidence):
        (root / "phases/demo/step1.md").unlink()
        git(root, "commit", "-qam", "docs: drop step1")
        code, rec, _, runner = _run(root, evidence, "{}")
        assert code == 2 and runner.calls == []


class TestClean:
    def test_clean_records_evidence(self, root, evidence):
        out = json.dumps(_result(root))
        code, rec, sha, runner = _run(root, evidence, out)
        assert code == 0
        assert rec["verdict"] == "clean"
        assert rec["reviewModel"] == "gpt-6-astra" and rec["reviewBackend"] == "codex"
        assert rec["argv"] == rp.build_review_argv()
        assert rec["inputSha256"] == hashlib.sha256(runner.calls[0]["input"].encode()).hexdigest()
        assert rec["stdoutSha256"] == hashlib.sha256(out.encode()).hexdigest()
        assert rec["exitCode"] == 0
        assert rec["reviewedPlanSha"] == pm.build_manifest(root, "demo").sha
        assert rec["manifestCodeSha"] == pm.code_sha()
        latest = json.loads((evidence / "demo/plan-reviews/latest.json").read_text())
        assert latest["recordSha"] == sha and latest["verdict"] == "clean"

    def test_record_file_is_read_only_and_hash_matches(self, root, evidence):
        code, rec, sha, _ = _run(root, evidence, json.dumps(_result(root)))
        latest = json.loads((evidence / "demo/plan-reviews/latest.json").read_text())
        p = evidence / "demo/plan-reviews" / latest["recordFile"]
        assert hashlib.sha256(p.read_bytes()).hexdigest() == sha
        assert not (p.stat().st_mode & 0o222)

    def test_prompt_contains_plan_and_hash(self, root, evidence):
        _, _, _, runner = _run(root, evidence, json.dumps(_result(root)))
        prompt = runner.calls[0]["input"]
        assert pm.build_manifest(root, "demo").sha in prompt
        assert "작업 0" in prompt and "한글 설계 본문" in prompt
        assert "20분" in prompt

    def test_fenced_json_accepted(self, root, evidence):
        out = "```json\n" + json.dumps(_result(root)) + "\n```\n"
        code, rec, _, _ = _run(root, evidence, out)
        assert code == 0


class TestFindingsBlock:
    def test_findings_exit_4_no_mutation(self, root, evidence):
        before = {p: p.read_bytes() for p in (root / "phases/demo").iterdir()}
        out = json.dumps(_result(root, verdict="has_findings", findings=[_finding()]))
        code, rec, _, runner = _run(root, evidence, out)
        assert code == 4
        assert rec["verdict"] == "has_findings"
        assert len(runner.calls) == 1  # 수정 에이전트를 부르지 않는다
        assert {p: p.read_bytes() for p in (root / "phases/demo").iterdir()} == before

    def test_no_fix_function_exists(self):
        assert not hasattr(rp, "_apply_plan_fixes")

    def test_rereview_after_change_needs_new_clean(self, root, evidence):
        _run(root, evidence, json.dumps(_result(root, verdict="has_findings",
                                                findings=[_finding()])))
        (root / "phases/demo/step0.md").write_text("# Step 0\n고친 계획\n", encoding="utf-8")
        git(root, "commit", "-qam", "docs: plan v2")
        code, rec, sha, _ = _run(root, evidence, lambda: json.dumps(_result(root)))
        assert code == 0
        latest = json.loads((evidence / "demo/plan-reviews/latest.json").read_text())
        assert latest["reviewedPlanSha"] == pm.build_manifest(root, "demo").sha
        assert latest["verdict"] == "clean"


class TestStrictFailures:
    @pytest.mark.parametrize("mutate", [
        lambda r: r.update(review_model="gpt-5"),
        lambda r: r.update(review_backend="claude"),
        lambda r: r.update(task="other"),
        lambda r: r.update(reviewed_plan_sha="0" * 64),
        lambda r: r.update(verdict="degraded"),
        lambda r: r.update(verdict="clean", findings=[_finding()]),
        lambda r: r.update(verdict="has_findings", findings=[]),
        lambda r: r.update(findings=None),
        lambda r: r.pop("verdict"),
        lambda r: r.pop("review_model"),
        lambda r: r.update(extra="x"),
        lambda r: r.update(verdict="has_findings", findings=[_finding(severity="nit")]),
        lambda r: r.update(verdict="has_findings", findings=[_finding(step_file="step9.md")]),
        lambda r: r.update(verdict="has_findings", findings=[_finding(step_file="../x.md")]),
        lambda r: r.update(verdict="has_findings", findings=[_finding(fix="")]),
        lambda r: r.update(verdict="has_findings",
                           findings=[{k: v for k, v in _finding().items() if k != "principle"}]),
        lambda r: r.update(verdict="has_findings", findings=[dict(_finding(), extra=1)]),
    ])
    def test_bad_result_fails(self, root, evidence, mutate):
        obj = _result(root)
        mutate(obj)
        code, rec, _, _ = _run(root, evidence, json.dumps(obj))
        assert code == 2
        assert rec["verdict"] == "failed" and rec["failure"]

    @pytest.mark.parametrize("stdout", ["", "not json", "[]", '{"a":1} trailing'])
    def test_garbage_fails(self, root, evidence, stdout):
        code, rec, _, _ = _run(root, evidence, stdout)
        assert code == 2 and rec["verdict"] == "failed"

    def test_nonzero_exit_fails(self, root, evidence):
        code, rec, _, _ = _run(root, evidence, json.dumps(_result(root)), rc=1)
        assert code == 2 and rec["exitCode"] == 1 and rec["verdict"] == "failed"

    def test_timeout_fails(self, root, evidence):
        code, rec, _, _ = _run(root, evidence, json.dumps(_result(root)), timed_out=True)
        assert code == 2 and rec["timedOut"] is True and rec["verdict"] == "failed"

    def test_plan_changed_during_review_fails(self, root, evidence):
        out = json.dumps(_result(root))

        def change():
            (root / "phases/demo/step0.md").write_text("changed mid-review", encoding="utf-8")
        code, rec, _, _ = _run(root, evidence, out, side_effect=change)
        assert code == 2 and "변경" in rec["failure"]

    def test_failed_review_supersedes_older_clean(self, root, evidence):
        _run(root, evidence, json.dumps(_result(root)))
        _run(root, evidence, "garbage")
        latest = json.loads((evidence / "demo/plan-reviews/latest.json").read_text())
        assert latest["verdict"] == "failed"


class TestVerifyRecord:
    def _clean(self, root, evidence):
        code, rec, sha, _ = _run(root, evidence, json.dumps(_result(root)))
        latest = json.loads((evidence / "demo/plan-reviews/latest.json").read_text())
        return (evidence / "demo/plan-reviews" / latest["recordFile"]), sha

    def test_accepts_latest_clean(self, root, evidence):
        path, sha = self._clean(root, evidence)
        rec = rp.verify_clean_review(evidence, "demo", sha, pm.build_manifest(root, "demo").sha,
                                         root, "DEMO-74", git(root, "rev-parse", "HEAD"))
        assert rec["verdict"] == "clean"

    def test_rejects_wrong_sha(self, root, evidence):
        self._clean(root, evidence)
        with pytest.raises(rp.PlanReviewError):
            rp.verify_clean_review(evidence, "demo", "f" * 64,
                                   pm.build_manifest(root, "demo").sha,
                                   root, "DEMO-74", git(root, "rev-parse", "HEAD"))

    def test_rejects_stale_review_after_plan_change(self, root, evidence):
        path, sha = self._clean(root, evidence)
        (root / "phases/demo/step0.md").write_text("new", encoding="utf-8")
        with pytest.raises(rp.PlanReviewError):
            rp.verify_clean_review(evidence, "demo", sha, pm.build_manifest(root, "demo").sha,
                                   root, "DEMO-74", git(root, "rev-parse", "HEAD"))

    def test_rejects_not_latest(self, root, evidence):
        path, sha = self._clean(root, evidence)
        _run(root, evidence, json.dumps(_result(root)))  # 같은 계획 재리뷰 → 새 latest
        with pytest.raises(rp.PlanReviewError):
            rp.verify_clean_review(evidence, "demo", sha, pm.build_manifest(root, "demo").sha,
                                   root, "DEMO-74", git(root, "rev-parse", "HEAD"))

    def test_rejects_tampered_record(self, root, evidence):
        path, sha = self._clean(root, evidence)
        path.chmod(0o644)
        data = json.loads(path.read_text())
        data["reviewModel"] = "gpt-6-astra "
        path.write_text(json.dumps(data))
        with pytest.raises(rp.PlanReviewError):
            rp.verify_clean_review(evidence, "demo", sha, pm.build_manifest(root, "demo").sha,
                                   root, "DEMO-74", git(root, "rev-parse", "HEAD"))


class TestIndexIntegrityHelpers:
    """기존 무결성 검사 회귀 방지(_verify_index_integrity는 유지)."""

    def _idx(self, n):
        return {"steps": [{"step": i, "name": f"s-{i}", "status": "pending"} for i in range(n)]}

    def test_valid(self):
        assert rp._verify_index_integrity(self._idx(3)) == []

    def test_gap(self):
        idx = self._idx(3)
        idx["steps"][2]["step"] = 5
        assert rp._verify_index_integrity(idx)

    def test_non_kebab(self):
        idx = self._idx(1)
        idx["steps"][0]["name"] = "Bad_Name"
        assert rp._verify_index_integrity(idx)


class TestNoPep604:
    def test_no_pep604_annotations(self):
        import ast
        bad = []
        for path in sorted(Path(rp.__file__).parent.glob("*.py")):
            if path.name.startswith("test_") or path.name == "conftest.py":
                continue
            for node in ast.walk(ast.parse(path.read_text(encoding="utf-8"))):
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    a = node.args
                    anns = [x.annotation for x in a.posonlyargs + a.args + a.kwonlyargs]
                    anns.append(node.returns)
                elif isinstance(node, ast.AnnAssign):
                    anns = [node.annotation]
                else:
                    continue
                for ann in filter(None, anns):
                    if any(isinstance(n, ast.BinOp) and isinstance(n.op, ast.BitOr)
                           for n in ast.walk(ann)):
                        bad.append(f"{path.name}:{node.lineno}")
        assert bad == []


FAKE_CODEX = textwrap.dedent("""\
    #!/bin/sh
    # 실제 spawn 시험용 가짜 codex: argv를 기록하고 RESULT_FILE 내용을 stdout으로 낸다.
    printf '%s\\n' "$@" > "$ARGV_FILE"
    cat > /dev/null
    cat "$RESULT_FILE"
""")


class TestRealSpawn:
    """mock이 아닌 실제 프로세스 spawn으로 argv·stdout 경로를 검증한다(원격 호출 없음)."""

    def test_spawned_fake_codex_clean(self, root, evidence, tmp_path, monkeypatch):
        bindir = tmp_path / "bin"
        bindir.mkdir()
        codex = bindir / "codex"
        codex.write_text(FAKE_CODEX, encoding="utf-8")
        codex.chmod(0o755)
        res = tmp_path / "result.json"
        res.write_text(json.dumps(_result(root)), encoding="utf-8")
        monkeypatch.setenv("PATH", f"{bindir}:{os.environ['PATH']}")
        monkeypatch.setenv("RESULT_FILE", str(res))
        monkeypatch.setenv("ARGV_FILE", str(tmp_path / "argv.txt"))
        code, path, sha = rp.run_review(root, "demo", evidence, "DEMO-74")
        assert code == 0
        argv = (tmp_path / "argv.txt").read_text().split("\n")
        assert "gpt-6-astra" in argv and "read-only" in argv


class TestMainSignals:
    def test_main_installs_signal_exit(self, monkeypatch):
        """리뷰어는 새 세션에서 돈다 — SIGTERM·SIGHUP을 SystemExit으로 받아 트리를 꺼야 한다."""
        calls = []
        monkeypatch.setattr(ex, "_install_signal_exit", lambda: calls.append("signal"))
        with pytest.raises(SystemExit):
            rp.main(["demo"])  # 정책 미설정 → preflight 실패, 그 전에 신호 처리기를 단다
        assert calls == ["signal"]


# ---------------------------------------------------------------------------
# 외부 target repo CLI·preflight·record 결속
# ---------------------------------------------------------------------------

HARNESS_PY = Path(__file__).resolve().parent / "harness.py"
VENV_PY = Path(__file__).resolve().parent.parent / ".venv" / "bin" / "python"
# CLI는 fixture policy가 든 임시 하네스 root에서 띄운다(운영 policy 비의존).
# 'harness 안 evidence' 계열 테스트도 같은 root를 써야 spawn된 하네스의 ROOT와 일치한다.
CLI_HARNESS_ROOT = None


@pytest.fixture(scope="session")
def _session_harness_root(tmp_path_factory):
    return make_harness_root(tmp_path_factory.mktemp("rp-harness"))


@pytest.fixture(autouse=True)
def _cli_harness_root(_session_harness_root, monkeypatch):
    monkeypatch.setattr(sys.modules[__name__], "CLI_HARNESS_ROOT", _session_harness_root)


def _cli(args, env_extra=None, path_prefix=None):
    env = {k: v for k, v in os.environ.items() if not k.startswith("HARNESS_")}
    env.update(ASTRA_ENV)
    if path_prefix:
        env["PATH"] = "%s:%s" % (path_prefix, env["PATH"])
    env.update(env_extra or {})
    harness_py = CLI_HARNESS_ROOT / "scripts" / HARNESS_PY.name
    return subprocess.run([str(VENV_PY), str(harness_py), "review-plan"] + list(args),
                          capture_output=True, text=True, encoding="utf-8", env=env)


class TestReviewModelFromPolicy:
    """리뷰 model은 코드 상수가 아니라 .harness/policy.json reviewModel이다."""

    def test_plan_and_code_review_use_policy_model(self, monkeypatch):
        import runtime
        from conftest import FIXTURE_POLICY
        pol = runtime.parse_policy(json.dumps(dict(FIXTURE_POLICY, reviewModel="gpt-x"))
                                   .encode("utf-8"))
        monkeypatch.setattr(runtime, "policy", lambda: pol)
        assert rp.build_review_argv()[-2:] == ["--model", "gpt-x"]
        head = "a" * 40
        ok = {"status": "complete", "reviewed_head": head, "review_model": "gpt-x",
              "findings": []}
        assert ex.check_astra_review(ok, head) is None
        assert ex.check_astra_review(dict(ok, review_model="gpt-6-astra"), head) is not None
        assert not hasattr(runtime, "REQUIRED_REVIEW_MODEL")


class TestExternalCli:
    @pytest.mark.parametrize("drop", ["--repo-root", "--issue"])
    def test_repo_root_and_issue_required(self, plan_repo, evidence, drop):
        args = {"--repo-root": str(plan_repo), "--issue": "DEMO-74"}
        args.pop(drop)
        flat = ["demo", "--evidence-dir", str(evidence)]
        for k, v in args.items():
            flat += [k, v]
        r = _cli(flat)
        assert r.returncode != 0
        assert drop in r.stderr
        assert not (evidence / "demo").exists()


FAKE_CODEX_CWD = textwrap.dedent("""\
    #!/bin/sh
    # 실제 spawn 가짜 codex: cwd·argv를 기록하고 RESULT_FILE을 stdout으로 낸다.
    pwd -P > "$CWD_FILE"
    printf '%s\\n' "$@" > "$ARGV_FILE"
    cat > /dev/null
    cat "$RESULT_FILE"
""")


def _fake_codex(tmp_path, result_obj):
    bindir = tmp_path / "bin"
    bindir.mkdir(exist_ok=True)
    codex = bindir / "codex"
    codex.write_text(FAKE_CODEX_CWD, encoding="utf-8")
    codex.chmod(0o755)
    res = tmp_path / "result.json"
    res.write_text(json.dumps(result_obj), encoding="utf-8")
    env = {"RESULT_FILE": str(res), "CWD_FILE": str(tmp_path / "cwd.txt"),
           "ARGV_FILE": str(tmp_path / "argv.txt")}
    return bindir, env


def _target_args(repo, evidence, issue="DEMO-74", task="demo"):
    return [task, "--repo-root", str(repo), "--issue", issue, "--evidence-dir", str(evidence)]


class TestExternalTargetSelected:
    def test_cli_reviews_external_clone_with_target_cwd(self, plan_repo, evidence, tmp_path):
        bindir, env = _fake_codex(tmp_path, _result(plan_repo))
        r = _cli(_target_args(plan_repo, evidence), env_extra=env, path_prefix=bindir)
        assert r.returncode == 0, r.stdout + r.stderr
        assert (tmp_path / "cwd.txt").read_text().strip() == str(plan_repo.resolve())
        latest = json.loads((evidence / "demo/plan-reviews/latest.json").read_text())
        assert latest["verdict"] == "clean"
        assert latest["reviewedPlanSha"] == pm.build_manifest(plan_repo, "demo").sha


def _pf_nongit(repo, tmp):
    r = tmp / "nongit"
    r.mkdir()
    make_plan(r)
    return r


def _pf_subdir(repo, tmp):
    return repo / "phases"


def _pf_symlink(repo, tmp):
    link = tmp / "link"
    link.symlink_to(repo)
    return link


def _pf_worktree(repo, tmp):
    wt = tmp / "wt"
    git(repo, "worktree", "add", "-q", "-b", "feat/DEMO-74/wt", str(wt), "HEAD")
    return wt


def _pf_detached(repo, tmp):
    git(repo, "checkout", "-q", "--detach")
    return repo


def _pf_main(repo, tmp):
    git(repo, "branch", "-f", "main", "HEAD")
    git(repo, "checkout", "-q", "main")
    return repo


def _pf_bad_branch(repo, tmp):
    git(repo, "checkout", "-q", "-b", "feat/DEMO-75/demo")
    return repo


def _pf_base_not_main(repo, tmp):
    p = repo / "phases/demo/index.json"
    d = json.loads(p.read_text())
    d["baseBranch"] = "develop"
    p.write_text(json.dumps(d))
    git(repo, "branch", "develop", "main")
    git(repo, "commit", "-qam", "docs: develop base")
    return repo


def _pf_no_local_main(repo, tmp):
    git(repo, "branch", "-D", "main")
    return repo


def _pf_dirty_phases(repo, tmp):
    p = repo / "phases/demo/step0.md"
    p.write_text(p.read_text() + "uncommitted\n")
    return repo


def _pf_untracked_docs(repo, tmp):
    (repo / "docs/notes.md").write_text("untracked\n")
    return repo


class TestTargetPreflight:
    @pytest.mark.parametrize("setup", [
        _pf_nongit, _pf_subdir, _pf_symlink, _pf_worktree, _pf_detached, _pf_main,
        _pf_bad_branch, _pf_base_not_main, _pf_no_local_main, _pf_dirty_phases,
        _pf_untracked_docs])
    def test_bad_target_blocked_before_spawn(self, plan_repo, evidence, tmp_path, setup):
        target = setup(plan_repo, tmp_path)
        bindir, env = _fake_codex(tmp_path, _result(plan_repo))
        r = _cli(_target_args(target, evidence), env_extra=env, path_prefix=bindir)
        assert r.returncode == 1, r.stdout + r.stderr
        assert not (tmp_path / "cwd.txt").exists()
        assert not (evidence / "demo").exists()

    def test_evidence_inside_target_blocked(self, plan_repo, tmp_path):
        bindir, env = _fake_codex(tmp_path, _result(plan_repo))
        ev = plan_repo / ".harness" / "ev"
        r = _cli(_target_args(plan_repo, ev), env_extra=env, path_prefix=bindir)
        assert r.returncode == 1
        assert not (tmp_path / "cwd.txt").exists() and not ev.exists()

    def test_evidence_inside_harness_blocked(self, plan_repo, tmp_path):
        import shutil
        bindir, env = _fake_codex(tmp_path, _result(plan_repo))
        ev = CLI_HARNESS_ROOT / ".harness" / ("harness-test-ev-%d" % os.getpid())
        try:
            r = _cli(_target_args(plan_repo, ev), env_extra=env, path_prefix=bindir)
            assert r.returncode == 1
            assert not (tmp_path / "cwd.txt").exists() and not ev.exists()
        finally:
            shutil.rmtree(ev, ignore_errors=True)


BINDING_KEYS = ("issue", "repoRoot", "branch", "baseBranch", "planCommitSha", "reviewBaseSha")


def _latest_path(evidence):
    d = evidence / "demo/plan-reviews"
    latest = json.loads((d / "latest.json").read_text())
    return d / latest["recordFile"]


def _forge(evidence, mutate):
    """record를 고치고 latest.json까지 맞춰 hash 위조를 일관되게 만든다(legacy·필드 누락 재현)."""
    d = evidence / "demo/plan-reviews"
    p = _latest_path(evidence)
    rec = json.loads(p.read_text())
    mutate(rec)
    data = json.dumps(rec, indent=2, ensure_ascii=False, sort_keys=True).encode("utf-8")
    sha = hashlib.sha256(data).hexdigest()
    name = "20000101T000000000000Z-%s.json" % sha[:12]
    (d / name).write_bytes(data)
    latest = json.loads((d / "latest.json").read_text())
    latest.update(recordFile=name, recordSha=sha)
    (d / "latest.json").write_text(json.dumps(latest))
    return sha


class TestRecordBinding:
    def test_clean_record_binds_target(self, root, evidence):
        code, rec, _, _ = _run(root, evidence, json.dumps(_result(root)))
        assert code == 0
        assert rec["version"] == 2
        assert rec["issue"] == "DEMO-74"
        assert rec["repoRoot"] == str(root.resolve())
        assert rec["branch"] == "feat/DEMO-74/demo"
        assert rec["baseBranch"] == "main"
        assert rec["planCommitSha"] == git(root, "rev-parse", "HEAD")
        assert rec["reviewBaseSha"] == git(root, "merge-base", "main", "HEAD")

    def test_head_moved_during_review_fails(self, root, evidence):
        def move():
            (root / "README.md").write_text("moved\n")
            git(root, "commit", "-qam", "chore: moved mid-review")
        code, rec, _, _ = _run(root, evidence, json.dumps(_result(root)), side_effect=move)
        assert code == 2 and "HEAD" in rec["failure"]

    def test_branch_switched_during_review_fails(self, root, evidence):
        def switch():
            git(root, "checkout", "-q", "-b", "feat/DEMO-74/other")
        code, rec, _, _ = _run(root, evidence, json.dumps(_result(root)), side_effect=switch)
        assert code == 2 and "branch" in rec["failure"]


class TestVerifyBinding:
    def _clean(self, root, evidence):
        code, rec, sha, _ = _run(root, evidence, json.dumps(_result(root)))
        assert code == 0
        return sha, rec

    def _verify(self, root, evidence, sha, rec, repo=None, issue="DEMO-74", plan_commit=None,
                review_base=None):
        return rp.verify_clean_review(evidence, "demo", sha, rec["reviewedPlanSha"],
                                      repo or root, issue, plan_commit or rec["planCommitSha"],
                                      review_base=review_base)

    def test_accepts_bound(self, root, evidence):
        sha, rec = self._clean(root, evidence)
        out = self._verify(root, evidence, sha, rec, review_base=rec["reviewBaseSha"])
        assert out["planCommitSha"] == rec["planCommitSha"]

    def test_other_clone_rejected(self, root, evidence, tmp_path):
        sha, rec = self._clean(root, evidence)
        other = tmp_path / "other-clone"
        git(tmp_path, "clone", "-q", str(root), str(other))
        git(other, "branch", "-f", "main", "origin/main")
        with pytest.raises(rp.PlanReviewError, match="repoRoot"):
            self._verify(root, evidence, sha, rec, repo=other)

    def test_other_issue_rejected(self, root, evidence):
        sha, rec = self._clean(root, evidence)
        with pytest.raises(rp.PlanReviewError):
            self._verify(root, evidence, sha, rec, issue="DEMO-75")

    def test_other_branch_rejected(self, root, evidence):
        sha, rec = self._clean(root, evidence)
        git(root, "checkout", "-q", "-b", "feat/DEMO-74/other")
        with pytest.raises(rp.PlanReviewError, match="branch"):
            self._verify(root, evidence, sha, rec)

    def test_plan_commit_mismatch_rejected(self, root, evidence):
        """같은 plan bytes라도 approval이 고정한 commit과 review commit이 다르면 거부."""
        sha, rec = self._clean(root, evidence)
        (root / "README.md").write_text("same plan, new commit\n")
        git(root, "commit", "-qam", "chore: other commit")
        with pytest.raises(rp.PlanReviewError, match="planCommitSha"):
            self._verify(root, evidence, sha, rec, plan_commit=git(root, "rev-parse", "HEAD"))

    def test_review_base_mismatch_rejected(self, root, evidence):
        sha, rec = self._clean(root, evidence)
        with pytest.raises(rp.PlanReviewError, match="reviewBaseSha"):
            self._verify(root, evidence, sha, rec, review_base=rec["planCommitSha"])

    def test_descendant_head_allowed(self, root, evidence):
        sha, rec = self._clean(root, evidence)
        (root / "src").mkdir()
        (root / "src/impl.py").write_text("x = 1\n")
        git(root, "add", "-A")
        git(root, "commit", "-qm", "feat: impl")
        self._verify(root, evidence, sha, rec)

    def test_plan_commit_not_ancestor_of_head_rejected(self, root, evidence):
        sha, rec = self._clean(root, evidence)
        git(root, "checkout", "-q", "main")
        git(root, "checkout", "-q", "-B", "feat/DEMO-74/demo")  # 같은 이름, 다른 history
        make_plan(root)
        git(root, "add", "-A")
        git(root, "commit", "-qm", "docs: same plan bytes, rewritten branch")
        with pytest.raises(rp.PlanReviewError, match="조상"):
            self._verify(root, evidence, sha, rec)

    def test_main_fast_forward_allowed(self, root, evidence):
        sha, rec = self._clean(root, evidence)
        git(root, "checkout", "-q", "main")
        (root / "MAIN.md").write_text("ff\n")
        git(root, "add", "-A")
        git(root, "commit", "-qm", "chore: main moves")
        git(root, "checkout", "-q", "feat/DEMO-74/demo")
        self._verify(root, evidence, sha, rec, review_base=rec["reviewBaseSha"])

    def test_main_rewrite_rejected(self, root, evidence):
        sha, rec = self._clean(root, evidence)
        git(root, "checkout", "-q", "--orphan", "rewritten")
        git(root, "commit", "-qm", "rewritten history")
        git(root, "branch", "-f", "main", "rewritten")
        git(root, "checkout", "-q", "feat/DEMO-74/demo")
        with pytest.raises(rp.PlanReviewError, match="조상"):
            self._verify(root, evidence, sha, rec)

    def test_legacy_version_1_rejected(self, root, evidence):
        _, rec = self._clean(root, evidence)
        sha = _forge(evidence, lambda r: r.update(version=1))
        with pytest.raises(rp.PlanReviewError, match="version"):
            self._verify(root, evidence, sha, rec)

    @pytest.mark.parametrize("key", BINDING_KEYS)
    def test_missing_binding_field_rejected(self, root, evidence, key):
        _, rec = self._clean(root, evidence)
        sha = _forge(evidence, lambda r: r.pop(key))
        with pytest.raises(rp.PlanReviewError):
            self._verify(root, evidence, sha, rec)

    def test_forged_consistent_record_still_needs_binding_match(self, root, evidence):
        _, rec = self._clean(root, evidence)
        sha = _forge(evidence, lambda r: r.update(issue="DEMO-75"))
        with pytest.raises(rp.PlanReviewError, match="issue"):
            self._verify(root, evidence, sha, rec)


# ---------------------------------------------------------------------------
# exact-commit review fixes (public CLI regressions)
# ---------------------------------------------------------------------------

def _rewrite_main_unrelated_with_tag(repo):
    """tag main을 원래 base에 두고 local branch main은 관련 없는 history로 rewrite한다."""
    old_main = git(repo, "rev-parse", "refs/heads/main")
    git(repo, "tag", "main", old_main)
    tree = git(repo, "rev-parse", old_main + "^{tree}")
    orphan = git(repo, "commit-tree", tree, "-m", "unrelated rewrite")
    git(repo, "update-ref", "refs/heads/main", orphan)


class TestBaseRefIsLocalBranch:
    def test_review_rejects_tag_main_when_branch_main_rewritten(self, plan_repo, evidence,
                                                                tmp_path):
        _rewrite_main_unrelated_with_tag(plan_repo)
        bindir, env = _fake_codex(tmp_path, _result(plan_repo))
        r = _cli(_target_args(plan_repo, evidence), env_extra=env, path_prefix=bindir)
        assert r.returncode == 1, r.stdout + r.stderr
        assert not (tmp_path / "cwd.txt").exists()
        assert not (evidence / "demo").exists()


def _untrack_and_ignore(repo, rel):
    """rel을 commit에서 빼고 .gitignore에 넣는다 — 작업트리 파일은 남아 git status에 안 보인다."""
    git(repo, "rm", "-q", "--cached", rel)
    with open(repo / ".gitignore", "a", encoding="utf-8") as f:
        f.write(rel + "\n")
    git(repo, "commit", "-qam", "chore: ignore %s" % rel)


def _hidden_index_mutation(repo):
    """tracked index.json을 skip-worktree로 숨기고 mutable 필드만 바꾼다(manifest hash 불변)."""
    git(repo, "update-index", "--skip-worktree", "phases/demo/index.json")
    p = repo / "phases/demo/index.json"
    d = json.loads(p.read_text(encoding="utf-8"))
    d["created_at"] = "uncommitted"
    p.write_text(json.dumps(d), encoding="utf-8")


PLAN_INPUT_EVASIONS = {
    "ignored-step": lambda r: _untrack_and_ignore(r, "phases/demo/step1.md"),
    "ignored-design": lambda r: _untrack_and_ignore(
        r, "docs/superpowers/specs/2026-11-22-demo-design.md"),
    "ignored-index": lambda r: _untrack_and_ignore(r, "phases/demo/index.json"),
    "skip-worktree-index": _hidden_index_mutation,
}


class TestPlanInputsCommitted:
    @pytest.mark.parametrize("evade", sorted(PLAN_INPUT_EVASIONS))
    def test_review_rejects_uncommitted_plan_inputs(self, plan_repo, evidence, tmp_path,
                                                     evade):
        PLAN_INPUT_EVASIONS[evade](plan_repo)
        assert git(plan_repo, "status", "--porcelain", "--untracked-files=all") == ""
        bindir, env = _fake_codex(tmp_path, _result(plan_repo))
        r = _cli(_target_args(plan_repo, evidence), env_extra=env, path_prefix=bindir)
        assert r.returncode == 1, r.stdout + r.stderr
        assert not (tmp_path / "cwd.txt").exists()
        assert not (evidence / "demo/plan-reviews/latest.json").exists()


@pytest.fixture
def harness_dest(_cli_harness_root):
    import shutil
    d = CLI_HARNESS_ROOT / ".harness" / ("harness-nested-%d" % os.getpid())
    shutil.rmtree(d, ignore_errors=True)
    d.mkdir(parents=True)
    yield d
    subprocess.run(["chmod", "-R", "u+w", str(d)], capture_output=True)
    shutil.rmtree(d, ignore_errors=True)


class TestNestedEvidenceSymlinks:
    @pytest.mark.parametrize("component", ["demo", "demo/plan-reviews"])
    @pytest.mark.parametrize("into", ["target", "harness"])
    def test_review_rejects_nested_symlink(self, plan_repo, evidence, tmp_path, harness_dest,
                                           component, into):
        if into == "target":
            dest = plan_repo / ".harness" / "redirect"
            dest.mkdir(parents=True)
        else:
            dest = harness_dest
        link = evidence / component
        link.parent.mkdir(parents=True, exist_ok=True)
        link.symlink_to(dest, target_is_directory=True)
        bindir, env = _fake_codex(tmp_path, _result(plan_repo))
        r = _cli(_target_args(plan_repo, evidence), env_extra=env, path_prefix=bindir)
        assert r.returncode == 1, r.stdout + r.stderr
        assert not (tmp_path / "cwd.txt").exists()
        assert list(dest.iterdir()) == []


FAKE_CODEX_PLANT_TMP = textwrap.dedent("""\
    #!/bin/sh
    # 실제 spawn 가짜 codex: 하네스(부모 PID)의 latest.json.tmp-<pid> 자리에 symlink를 심는다.
    mkdir -p "$PLANT_DIR"
    ln -s "$PLANT_DEST" "$PLANT_DIR/latest.json.tmp-$PPID"
    cat > /dev/null
    cat "$RESULT_FILE"
""")


def _fstate(p):
    st = os.lstat(str(p))
    return (stat.S_IMODE(st.st_mode), Path(p).read_bytes())


class TestLatestPointerTempRedirect:
    """3차: latest.json.tmp-<pid>가 기존 symlink면 따라가거나 교체하지 않는다."""

    @pytest.mark.parametrize("into", ["target", "harness"])
    def test_review_refuses_preexisting_tmp_symlink(self, plan_repo, evidence, tmp_path,
                                                     harness_dest, into):
        if into == "target":
            dest = plan_repo / "phases/demo/index.json"
        else:
            dest = harness_dest / "protected.json"
            dest.write_bytes(b'{"protected": true}\n')
        os.chmod(str(dest), 0o640)
        before = _fstate(dest)
        bindir, env = _fake_codex(tmp_path, _result(plan_repo))
        (bindir / "codex").write_text(FAKE_CODEX_PLANT_TMP, encoding="utf-8")
        pdir = evidence / "demo/plan-reviews"
        env.update(PLANT_DIR=str(pdir), PLANT_DEST=str(dest))
        r = _cli(_target_args(plan_repo, evidence), env_extra=env, path_prefix=bindir)
        assert r.returncode == 2, r.stdout + r.stderr
        assert _fstate(dest) == before
        links = [p for p in pdir.iterdir() if p.name.startswith("latest.json.tmp-")]
        assert len(links) == 1 and links[0].is_symlink()
        assert os.readlink(str(links[0])) == str(dest)
        assert not os.path.lexists(str(pdir / "latest.json"))
