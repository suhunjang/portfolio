"""A. Python >=3.10 repo-local 실행 환경과 고정 실행기(harness.py) 계약."""
import os
import subprocess
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent))
import runtime  # noqa: E402
import bootstrap_venv as bv  # noqa: E402

REPO = Path(__file__).resolve().parent.parent
HARNESS = REPO / "scripts" / "harness.py"
VENV_PY = REPO / ".venv" / "bin" / "python"
SYSTEM_PY39 = Path("/usr/bin/python3")


def _version_of(py):
    r = subprocess.run([str(py), "-c", "import sys;print('%d %d' % sys.version_info[:2])"],
                       capture_output=True, text=True, timeout=30)
    return tuple(int(x) for x in r.stdout.split())


class TestCheckRuntime:
    def test_rejects_python_39(self):
        errs = runtime.check_runtime(version_info=(3, 9, 6), prefix=REPO / ".venv", root=REPO)
        assert any("3.10" in e for e in errs)

    def test_accepts_repo_venv_314(self):
        assert runtime.check_runtime(version_info=(3, 14, 9), prefix=REPO / ".venv",
                                     root=REPO) == []

    def test_rejects_non_repo_interpreter(self, tmp_path):
        errs = runtime.check_runtime(version_info=(3, 14, 9), prefix=tmp_path, root=REPO)
        assert any(".venv" in e for e in errs)

    def test_current_test_process_is_valid(self):
        """테스트 자체가 ./.venv/bin/python 으로 돈다 — 운영 경로와 같다."""
        assert runtime.check_runtime() == []

    def test_require_runtime_exits_on_error(self, monkeypatch):
        monkeypatch.setattr(runtime, "check_runtime", lambda **k: ["bad"])
        with pytest.raises(SystemExit) as e:
            runtime.require_runtime()
        assert e.value.code == 1

    def test_evidence_records_base_interpreter_and_version(self):
        ev = runtime.runtime_evidence()
        assert ev["version"].startswith("3.")
        assert ev["executable"] and ev["baseExecutable"] and ev["prefix"]


class TestReviewPolicy:
    def test_requires_explicit_codex_and_astra(self):
        assert runtime.review_policy_errors({}) != []
        assert runtime.review_policy_errors({"HARNESS_REVIEW_BACKEND": "codex"}) != []
        assert runtime.review_policy_errors(
            {"HARNESS_REVIEW_BACKEND": "claude", "HARNESS_REVIEW_MODEL": "gpt-6-astra"}) != []
        assert runtime.review_policy_errors(
            {"HARNESS_REVIEW_BACKEND": "codex", "HARNESS_REVIEW_MODEL": "gpt-5"}) != []
        assert runtime.review_policy_errors(
            {"HARNESS_REVIEW_BACKEND": "codex", "HARNESS_REVIEW_MODEL": "gpt-6-astra"}) == []

    def test_rejects_no_git_env(self):
        env = {"HARNESS_REVIEW_BACKEND": "codex", "HARNESS_REVIEW_MODEL": "gpt-6-astra",
               "HARNESS_NO_GIT": "1"}
        assert any("HARNESS_NO_GIT" in e for e in runtime.review_policy_errors(env))

    def test_rejects_non_claude_impl(self):
        env = {"HARNESS_REVIEW_BACKEND": "codex", "HARNESS_REVIEW_MODEL": "gpt-6-astra",
               "HARNESS_IMPL_BACKEND": "codex"}
        assert runtime.review_policy_errors(env) != []

    def test_review_model_comes_from_policy_file(self, monkeypatch, tmp_path):
        """리뷰 model은 .harness/policy.json 값이다 — env도 그 값과 같아야 한다."""
        (tmp_path / ".harness").mkdir()
        (tmp_path / ".harness" / "policy.json").write_bytes(_policy_bytes(reviewModel="gpt-x"))
        monkeypatch.setattr(runtime, "policy", lambda: runtime.load_repo_policy(tmp_path))
        env = {"HARNESS_REVIEW_BACKEND": "codex", "HARNESS_REVIEW_MODEL": "gpt-x"}
        assert runtime.review_policy_errors(env) == []
        assert runtime.review_model() == "gpt-x"
        assert runtime.review_policy_errors(dict(env, HARNESS_REVIEW_MODEL="gpt-6-astra")) != []

    def test_missing_policy_file_fails_closed(self, monkeypatch, tmp_path):
        monkeypatch.setattr(runtime, "policy", lambda: runtime.load_repo_policy(tmp_path))
        env = {"HARNESS_REVIEW_BACKEND": "codex", "HARNESS_REVIEW_MODEL": "gpt-6-astra"}
        errs = runtime.review_policy_errors(env)
        assert errs and any("policy" in e for e in errs)


class TestLauncherSpawn:
    """실제 프로세스를 띄워 확인한다 — mock으로는 3.9 거부를 증명할 수 없다."""

    @pytest.mark.skipif(not SYSTEM_PY39.exists() or _version_of(SYSTEM_PY39) >= (3, 10),
                        reason="시스템 python3 3.9가 없음")
    def test_system_python39_fails_immediately(self):
        r = subprocess.run([str(SYSTEM_PY39), str(HARNESS), "check"],
                           capture_output=True, text=True, timeout=60, cwd=REPO)
        assert r.returncode == 1
        assert "3.10" in (r.stdout + r.stderr)

    @pytest.mark.skipif(not SYSTEM_PY39.exists() or _version_of(SYSTEM_PY39) >= (3, 10),
                        reason="시스템 python3 3.9가 없음")
    @pytest.mark.parametrize("script", ["execute.py", "review_plan.py", "plan_session.py",
                                        "approval.py", "runner.py", "project_init.py"])
    def test_direct_entry_with_python39_fails_before_work(self, script):
        r = subprocess.run([str(SYSTEM_PY39), str(REPO / "scripts" / script), "x"],
                           capture_output=True, text=True, timeout=60, cwd=REPO)
        assert r.returncode != 0
        assert "3.10" in (r.stdout + r.stderr)

    def test_base_interpreter_outside_venv_rejected(self):
        # 호스트 절대경로 상수 대신 현재 .venv를 만든 base interpreter를 쓴다.
        base = Path(getattr(sys, "_base_executable", "") or "/nonexistent")
        if not base.exists() or sys.prefix == sys.base_prefix:
            pytest.skip("venv 밖 base interpreter를 찾을 수 없음")
        r = subprocess.run([str(base), str(HARNESS), "check"],
                           capture_output=True, text=True, timeout=60, cwd=REPO)
        assert r.returncode == 1
        assert ".venv" in (r.stdout + r.stderr)

    def test_repo_venv_passes(self):
        r = subprocess.run([str(VENV_PY), str(HARNESS), "check"],
                           capture_output=True, text=True, timeout=60, cwd=REPO)
        assert r.returncode == 0, r.stdout + r.stderr
        assert "3.14" in r.stdout

    def test_unknown_command_rejected(self):
        r = subprocess.run([str(VENV_PY), str(HARNESS), "sdd"],
                           capture_output=True, text=True, timeout=60, cwd=REPO)
        assert r.returncode == 2

    def test_dispatches_to_subcommand(self):
        r = subprocess.run([str(VENV_PY), str(HARNESS), "plan-session", "--help"],
                           capture_output=True, text=True, timeout=60, cwd=REPO)
        assert r.returncode == 0
        assert "record-agreement" in r.stdout

    def test_init_dispatches_to_installer(self):
        """harness.py init → project_init.py(배포 설치기)."""
        r = subprocess.run([str(VENV_PY), str(HARNESS), "init", "--help"],
                           capture_output=True, text=True, timeout=60, cwd=REPO)
        assert r.returncode == 0, r.stdout + r.stderr
        for flag in ("--target", "--profile", "--check", "--dry-run", "--update",
                     "--from-distribution", "--adopt-merged", "--recover"):
            assert flag in r.stdout

    def test_check_reports_policy_status(self, tmp_path):
        """check는 하네스 root의 .harness/policy.json 상태를 보고하고 틀리면 실패한다."""
        import json as _json
        from conftest import make_harness_root, write_policy
        root = make_harness_root(tmp_path)
        r = subprocess.run([str(VENV_PY), str(root / "scripts/harness.py"), "check"],
                           capture_output=True, text=True, timeout=60)
        assert r.returncode == 0, r.stdout + r.stderr
        assert _json.loads(r.stdout)["policy"]["status"] == "ok"
        write_policy(root, {"schemaVersion": 1})
        r = subprocess.run([str(VENV_PY), str(root / "scripts/harness.py"), "check"],
                           capture_output=True, text=True, timeout=60)
        assert r.returncode == 1
        assert _json.loads(r.stdout)["policy"]["status"] == "invalid"
        (root / ".harness/policy.json").unlink()
        r = subprocess.run([str(VENV_PY), str(root / "scripts/harness.py"), "check"],
                           capture_output=True, text=True, timeout=60)
        assert r.returncode == 0 and "policy" in r.stderr
        assert _json.loads(r.stdout)["policy"]["status"] == "missing"


def _policy(**over):
    """범용 정책 fixture(.harness/policy.json 스키마). 값은 테스트용 가짜 ID다."""
    base = {
        "schemaVersion": 1, "issueKeyPattern": "PROJ-[0-9]+",
        "approverUserIds": ["91111"],
        "approvalThreadIds": ["92222"],
        "issueScopedThreads": {"93333": "PROJ-7"},
        "implBackend": "claude", "reviewBackend": "codex", "reviewModel": "gpt-6-astra",
        "pythonMinVersion": "3.10", "pythonRecommendedVersion": "3.14.9",
    }
    base.update(over)
    return base


def _policy_bytes(**over):
    import json
    return json.dumps(_policy(**over)).encode("utf-8")


class TestPolicyParse:
    """project/local policy는 .harness/policy.json이 유일한 입력 — strict 스키마."""

    def test_valid_policy_exposes_fields(self):
        pol = runtime.parse_policy(_policy_bytes())
        assert pol.issue_key_pattern == "PROJ-[0-9]+"
        assert pol.approver_user_ids == ("91111",)
        assert pol.approval_thread_ids == ("92222",)
        assert pol.issue_scoped_threads == {"93333": "PROJ-7"}
        assert (pol.impl_backend, pol.review_backend, pol.review_model) == (
            "claude", "codex", "gpt-6-astra")
        assert pol.python_min_version == (3, 10)
        assert pol.python_recommended_version == (3, 14, 9)

    def test_duplicate_json_key_rejected(self):
        data = _policy_bytes().replace(
            b'"reviewModel": "gpt-6-astra"',
            b'"reviewModel": "gpt-6-astra", "reviewModel": "other-model"')
        with pytest.raises(runtime.PolicyError, match="중복"):
            runtime.parse_policy(data)

    @pytest.mark.parametrize("mutate", [
        lambda p: p.update(discordBotToken="x"),          # 알 수 없는 key(secret 자리)
        lambda p: p.pop("reviewModel"),                    # 필수 key 누락
        lambda p: p.update(schemaVersion=2),
        lambda p: p.update(schemaVersion=True),
    ])
    def test_schema_keys_exact(self, mutate):
        import json
        p = _policy()
        mutate(p)
        with pytest.raises(runtime.PolicyError):
            runtime.parse_policy(json.dumps(p).encode("utf-8"))

    @pytest.mark.parametrize("over", [
        {"approverUserIds": ["sk-ant-api03-abcdefghijklmnop"]},   # secret 의심 값
        {"approvalThreadIds": ["ghp_abcdefghijklmnopqrstuvwxyz0123"]},
        {"approverUserIds": "91111"},                 # list 아님
        {"approverUserIds": ["a b"]},                               # ID 형식
        {"approverUserIds": ["91111", "91111"]},  # 중복
        {"issueKeyPattern": ""},
        {"issueKeyPattern": "[A-Z]*"},                              # 빈 문자열과 일치
        {"issueKeyPattern": "(?P<issue>PROJ)-[0-9]+"},              # named group 충돌
        {"issueKeyPattern": "PROJ-[0-9+"},                          # 정규식 오류
        {"issueKeyPattern": "(?i)PROJ-[0-9]+"},                     # inline flag(3.10에선 전체 본문에 전파)
        {"issueKeyPattern": "(?=PROJ)PROJ-[0-9]+"},                 # lookaround 등 (?…) 구문 금지
        {"issueScopedThreads": {"93333": "OTHER-1"}},  # pattern 불일치
        {"issueScopedThreads": {"92222": "PROJ-7"}},   # 전역 thread와 겹침
        {"implBackend": "codex"},
        {"reviewBackend": "claude"},
        {"reviewModel": "gpt 6"},
        {"pythonMinVersion": "3.9"},
        {"pythonMinVersion": "3"},
        {"pythonRecommendedVersion": "3.10"},
        {"pythonRecommendedVersion": "3.9.6"},
    ])
    def test_invalid_values_rejected(self, over):
        with pytest.raises(runtime.PolicyError):
            runtime.parse_policy(_policy_bytes(**over))


class TestPolicyFile:
    """하네스 root의 .harness/policy.json만 읽는다(regular file, symlink·hardlink 거부)."""

    def _write(self, root, data=None):
        (root / ".harness").mkdir(exist_ok=True)
        p = root / ".harness" / "policy.json"
        p.write_bytes(data if data is not None else _policy_bytes())
        return p

    def test_reads_harness_policy_json(self, tmp_path):
        self._write(tmp_path)
        assert runtime.read_policy(tmp_path).review_model == "gpt-6-astra"

    def test_missing_policy_is_error(self, tmp_path):
        with pytest.raises(runtime.PolicyError, match="policy.json"):
            runtime.read_policy(tmp_path)

    @pytest.mark.parametrize("kind", ["symlink", "hardlink", "symlink-dir"])
    def test_non_regular_policy_rejected(self, tmp_path, kind):
        real = tmp_path / "elsewhere"
        real.mkdir()
        (real / "policy.json").write_bytes(_policy_bytes())
        root = tmp_path / "root"
        root.mkdir()
        if kind == "symlink-dir":
            (root / ".harness").symlink_to(real)
        else:
            (root / ".harness").mkdir()
            if kind == "symlink":
                (root / ".harness" / "policy.json").symlink_to(real / "policy.json")
            else:
                os.link(real / "policy.json", root / ".harness" / "policy.json")
        with pytest.raises(runtime.PolicyError):
            runtime.read_policy(root)


class TestLocalPolicy:
    """호스트 전용 값(승인 interpreter 절대경로·추가 보호 경로)은 배포하지 않는
    .harness/policy.local.json에만 둔다. 없으면 빈 정책."""

    def _write(self, root, obj):
        import json
        (root / ".harness").mkdir(exist_ok=True)
        (root / ".harness" / "policy.local.json").write_text(json.dumps(obj), encoding="utf-8")

    def test_missing_is_empty(self, tmp_path):
        assert runtime.read_local_policy(tmp_path) == {}

    def test_valid_local_policy(self, tmp_path):
        self._write(tmp_path, {"schemaVersion": 1, "approvedBaseInterpreter": "/opt/py/bin/python3",
                               "extraProtectedPaths": ["/srv/original-template"]})
        loc = runtime.read_local_policy(tmp_path)
        assert loc["approvedBaseInterpreter"] == "/opt/py/bin/python3"
        assert loc["extraProtectedPaths"] == ["/srv/original-template"]

    @pytest.mark.parametrize("obj", [
        {"schemaVersion": 1, "approvedBaseInterpreter": "python3"},           # 상대경로
        {"schemaVersion": 1, "extraProtectedPaths": ["relative/dir"]},
        {"schemaVersion": 1, "extraProtectedPaths": "/srv/x"},
        {"schemaVersion": 1, "apiToken": "x"},                                  # 임의 key
        {"approvedBaseInterpreter": "/opt/py/bin/python3"},                     # schemaVersion 누락
        {"schemaVersion": 1, "extraProtectedPaths": ["/srv/ghp_abcdefghijklmnopqrstu"]},
    ])
    def test_invalid_local_policy_rejected(self, tmp_path, obj):
        self._write(tmp_path, obj)
        with pytest.raises(runtime.PolicyError):
            runtime.read_local_policy(tmp_path)


class TestBootstrapVenv:
    """승인 base = bootstrap을 실행한 interpreter(sys.executable)의 기록 또는
    policy.local.json의 exact pin. 최소/권장 버전은 policy(.harness/policy.json)."""

    BASE = "/opt/py-3.14.9/bin/python3"

    def _cfg(self, root, home, version, record=True):
        venv = root / ".venv"
        (venv / "bin").mkdir(parents=True)
        (venv / "bin" / "python").write_text("", encoding="utf-8")
        (venv / "pyvenv.cfg").write_text(
            f"home = {home}\nversion = {version}\n", encoding="utf-8")
        (root / ".python-version").write_text("3.14.9\n", encoding="utf-8")
        if record:
            bv.write_record(root, home + "/python3")

    def _pin(self, root, base):
        import json
        (root / ".harness").mkdir(exist_ok=True)
        (root / ".harness" / "policy.local.json").write_text(
            json.dumps({"schemaVersion": 1, "approvedBaseInterpreter": base}), encoding="utf-8")

    def test_check_accepts_approved_interpreter(self, tmp_path):
        """bootstrap이 기록한 interpreter로 만든 .venv는 통과."""
        self._cfg(tmp_path, str(Path(self.BASE).parent), "3.14.9")
        assert bv.check(tmp_path) == []

    def test_check_accepts_local_exact_pin(self, tmp_path):
        """운영자가 policy.local.json으로 exact interpreter를 고정한 경우."""
        self._cfg(tmp_path, str(Path(self.BASE).parent), "3.14.9", record=False)
        self._pin(tmp_path, self.BASE)
        assert bv.check(tmp_path) == []

    def test_check_rejects_other_home(self, tmp_path):
        self._cfg(tmp_path, "/usr/bin", "3.14.9", record=False)
        self._pin(tmp_path, self.BASE)
        assert bv.check(tmp_path) != []

    def test_check_rejects_venv_recreated_after_record(self, tmp_path):
        self._cfg(tmp_path, str(Path(self.BASE).parent), "3.14.9")
        (tmp_path / ".venv" / "pyvenv.cfg").write_text("home = /usr/bin\nversion = 3.14.9\n",
                                                        encoding="utf-8")
        assert bv.check(tmp_path) != []

    def test_check_rejects_unrecorded_unpinned_venv(self, tmp_path):
        self._cfg(tmp_path, str(Path(self.BASE).parent), "3.14.9", record=False)
        assert any("bootstrap" in e for e in bv.check(tmp_path))

    def test_check_rejects_version_mismatch(self, tmp_path):
        self._cfg(tmp_path, str(Path(self.BASE).parent), "3.9.6")
        assert bv.check(tmp_path) != []

    def test_policy_min_and_recommended_versions(self, tmp_path):
        (tmp_path / ".harness").mkdir()
        (tmp_path / ".harness" / "policy.json").write_bytes(
            _policy_bytes(pythonMinVersion="3.12", pythonRecommendedVersion="3.14.9"))
        self._cfg(tmp_path, "/opt/py-3.13/bin", "3.13.2")
        errors, warnings = bv.check_report(tmp_path)
        assert errors == [] and any("3.14.9" in w for w in warnings)
        (tmp_path / ".venv" / "pyvenv.cfg").write_text(
            "home = /opt/py-3.13/bin\nversion = 3.11.9\n", encoding="utf-8")
        bv.write_record(tmp_path, "/opt/py-3.13/bin/python3")
        assert any("3.12" in e for e in bv.check(tmp_path))

    def test_check_rejects_missing_venv(self, tmp_path):
        assert bv.check(tmp_path) != []

    def test_real_repo_venv_is_approved(self):
        assert bv.check(REPO) == []

    def test_plan_lists_commands_without_running(self, tmp_path):
        cmds = bv.plan_commands(tmp_path)
        assert cmds[0][:3] == [sys.executable, "-m", "venv"]
        assert any("pytest" in c for c in cmds[1])
        assert not (tmp_path / ".venv").exists()

    def test_plan_uses_local_pin(self, tmp_path):
        self._pin(tmp_path, self.BASE)
        assert bv.plan_commands(tmp_path)[0][0] == self.BASE

    def test_no_host_interpreter_constant(self):
        assert not hasattr(runtime, "APPROVED_BASE_INTERPRETER")

    @pytest.mark.skipif(not SYSTEM_PY39.exists() or _version_of(SYSTEM_PY39) >= (3, 10),
                        reason="시스템 python3 3.9가 없음")
    def test_create_refuses_old_base_without_creating(self, tmp_path):
        """실제 spawn: 3.9 base로는 .venv를 만들지 않는다."""
        self._pin(tmp_path, str(SYSTEM_PY39))
        assert bv.create(tmp_path) == 1
        assert not (tmp_path / ".venv").exists()


class TestBootstrapCleanErrors:
    def test_plan_with_invalid_local_policy_is_clean_error(self, tmp_path):
        from conftest import make_harness_root
        root = make_harness_root(tmp_path)
        (root / ".harness" / "policy.local.json").write_text('{"schemaVersion": 1, "x": 1}',
                                                              encoding="utf-8")
        r = subprocess.run([str(VENV_PY), str(root / "scripts/bootstrap_venv.py"), "--plan"],
                           capture_output=True, text=True, timeout=60)
        assert r.returncode == 1 and "Traceback" not in r.stderr, r.stdout + r.stderr
        assert "ERROR" in r.stderr
