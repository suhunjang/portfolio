"""배포 설치기 — public CLI(subprocess)로 실제 init·check·dry-run·adopt·확장·update·recover.

target 프로젝트에도 배포되는 회귀 테스트다. 픽스처 distribution은 **이 하네스 root의 manifest가
가리키는 managed 파일만** 복사해 만든 clean git checkout이다(source checkout의 다른 파일·원본
저장소·git 이력에 의존하지 않는다). 설치·검증은 항상 실제 프로세스로 띄운다.
"""
import hashlib
import json
import os
import shutil
import signal
import subprocess
import sys
import textwrap
import time
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent))
import project_init as pi  # noqa: E402
from conftest import git  # noqa: E402

SCRIPTS = Path(__file__).resolve().parent
ROOT = SCRIPTS.parent
VENV = ROOT / ".venv"
VENV_PY = VENV / "bin" / "python"
STATE = ".harness/install-state.json"


def _sha(data):
    return hashlib.sha256(data).hexdigest()


def _manifest(root):
    return pi.load_manifest((Path(root) / "harness-manifest.json").read_bytes())


def make_dist(base, name="dist-v1", mutate=None, message="harness v1"):
    """manifest의 모든 managed source만 복사한 clean distribution checkout(+ .venv symlink)."""
    d = Path(base) / name
    for e in _manifest(ROOT).entries:
        if e.ownership == "managed":
            dst = d / e.path
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(str(ROOT / e.path), str(dst))
    (d / ".gitignore").write_text(".venv\n__pycache__/\n", encoding="utf-8")
    if mutate:
        mutate(d)
    git(d, "init", "-q", "-b", "main")
    git(d, "config", "user.email", "t@example.com")
    git(d, "config", "user.name", "T")
    git(d, "config", "commit.gpgsign", "false")
    git(d, "add", "-A")
    git(d, "commit", "-q", "-m", message)
    (d / ".venv").symlink_to(VENV)
    return d


def make_target(base, name="target", files=None):
    """독립 Git root target. files: {rel: bytes|str} 선재 파일(커밋됨)."""
    t = Path(base) / name
    t.mkdir(parents=True)
    git(t, "init", "-q", "-b", "main")
    git(t, "config", "user.email", "t@example.com")
    git(t, "config", "user.name", "T")
    git(t, "config", "commit.gpgsign", "false")
    (t / "README.md").write_text("target project\n", encoding="utf-8")
    for rel, data in (files or {}).items():
        p = t / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_bytes(data.encode("utf-8") if isinstance(data, str) else data)
    git(t, "add", "-A")
    git(t, "commit", "-q", "-m", "init")
    return t


def link_venv(target):
    """target에 설치된 installer를 같은 interpreter로 띄우기 위한 .venv(테스트 전용)."""
    if not os.path.lexists(str(target / ".venv")):
        (target / ".venv").symlink_to(VENV)


def run_init(installer_root, *args):
    return subprocess.run([str(VENV_PY), str(Path(installer_root) / "scripts" / "harness.py"),
                           "init"] + [str(a) for a in args],
                          capture_output=True, text=True, encoding="utf-8", timeout=300)


def tree(root):
    """.git·.venv를 뺀 전체 파일 트리(경로 → (종류, sha256|링크)). 읽기 전용 검증용."""
    out = {}
    root = Path(root)
    for dirpath, dirnames, filenames in os.walk(str(root)):
        rel_dir = Path(dirpath).relative_to(root)
        dirnames[:] = [d for d in dirnames if not (rel_dir == Path(".") and d in (".git", ".venv"))]
        for name in list(dirnames) + filenames:
            p = Path(dirpath) / name
            rel = (rel_dir / name).as_posix()
            if rel in (".venv",):
                continue
            if p.is_symlink():
                out[rel] = ("link", os.readlink(str(p)))
            elif p.is_dir():
                out[rel] = ("dir", None)
            else:
                out[rel] = ("file", _sha(p.read_bytes()))
    return out


def state(target):
    return json.loads((Path(target) / STATE).read_text(encoding="utf-8"))


# 배포 회귀 테스트는 **설치된 manifest에서** 필요한 사실을 도출한다 — 하네스가 새 버전으로 update돼
# 분류(어떤 파일이 managed인지·requirementsVersion)가 바뀌어도 설치기 동작을 계속 검증한다.
# (원본 분류 자체의 고정은 test_distribution_contract.py가 맡는다.)
BASE_MANIFEST = _manifest(ROOT)
_MANAGED = sorted(e.path for e in BASE_MANIFEST.entries if e.ownership == "managed")
ROOT_MANAGED = next(x for x in _MANAGED if "/" not in x and x != "harness-manifest.json")
_CLAUDE_MANAGED = [x for x in _MANAGED if x.startswith(".claude/")]


def rv(path):
    """설치된 manifest의 merge-required requirementsVersion."""
    return BASE_MANIFEST.by_path[path].requirements_version


V1 = BASE_MANIFEST.version                                  # 설치된(기반) 배포 버전
_maj, _min, _pat = (int(x) for x in V1.split("."))
V2 = "%d.%d.0" % (_maj, _min + 1)                            # 테스트 update 배포 버전


class TestFreshInit:
    def test_base_profile_materializes_and_records_state(self, tmp_path):
        dist = make_dist(tmp_path)
        tgt = make_target(tmp_path)
        r = run_init(dist, "--target", tgt, "--profile", "base")
        assert r.returncode == 0, r.stdout + r.stderr
        m = _manifest(dist)
        for e in pi.select_entries(m, "base"):
            assert (tgt / e.path).is_file(), e.path
            src = (dist / e.source).read_bytes()
            if e.ownership == "managed":
                assert (tgt / e.path).read_bytes() == src
        assert not (tgt / "docs/UI_GUIDE.md").exists()
        assert (tgt / "docs/PRD.md").read_bytes() == (
            dist / "templates/project/docs/PRD.md").read_bytes()
        st = state(tgt)
        assert st["profile"] == "base"
        assert st["distributionVersion"] == m.version
        assert st["manifestHash"] == _sha((dist / "harness-manifest.json").read_bytes())
        assert st["sourceCommit"] == git(dist, "rev-parse", "HEAD")
        h = _sha((dist / "scripts/runtime.py").read_bytes())
        assert st["files"]["scripts/runtime.py"] == {
            "ownership": "managed", "sourceHash": h, "installedHash": h}
        assert st["files"]["docs/PRD.md"]["ownership"] == "seed"
        assert st["files"]["docs/PRD.md"]["status"] == "created"
        assert st["files"]["CLAUDE.md"]["status"] == "created"
        assert st["files"]["CLAUDE.md"]["requirementsVersion"] == rv("CLAUDE.md")
        assert git(dist, "status", "--porcelain") == ""   # source distribution 불변


@pytest.fixture
def installed(tmp_path):
    """base로 설치된 target(+ target 자신의 installer를 띄울 .venv)."""
    dist = make_dist(tmp_path)
    tgt = make_target(tmp_path)
    r = run_init(dist, "--target", tgt, "--profile", "base")
    assert r.returncode == 0, r.stdout + r.stderr
    link_venv(tgt)
    return dist, tgt


class TestCheck:
    def test_check_passes_from_installed_installer_and_is_read_only(self, installed):
        _, tgt = installed
        before = tree(tgt)
        r = run_init(tgt, "--target", tgt, "--check")
        assert r.returncode == 0, r.stdout + r.stderr
        out = json.loads(r.stdout)
        assert out["ok"] is True and out["mode"] == "check" and out["profile"] == "base"
        assert tree(tgt) == before


class TestDryRun:
    def test_dry_run_lists_plan_and_writes_nothing(self, tmp_path):
        dist = make_dist(tmp_path)
        tgt = make_target(tmp_path)
        before, dist_before = tree(tgt), tree(dist)
        r = run_init(dist, "--target", tgt, "--profile", "ui", "--dry-run")
        assert r.returncode == 0, r.stdout + r.stderr
        out = json.loads(r.stdout)
        planned = {a["path"]: a["op"] for a in out["actions"]}
        assert planned["scripts/runtime.py"] == "create"
        assert planned["docs/UI_GUIDE.md"] == "create" and planned["CLAUDE.md"] == "create"
        assert out["dryRun"] is True and out["conflicts"] == [] and out["mergeNeeded"] == []
        assert tree(tgt) == before and not (tgt / ".harness").exists()
        assert tree(dist) == dist_before

    def test_dry_run_reports_conflicts_without_writing(self, tmp_path):
        dist = make_dist(tmp_path)
        tgt = make_target(tmp_path, files={"CLAUDE.md": "# mine\n", ROOT_MANAGED: "# mine\n"})
        before = tree(tgt)
        r = run_init(dist, "--target", tgt, "--dry-run")
        assert r.returncode == 4, r.stdout + r.stderr
        out = json.loads(r.stdout)
        assert any(ROOT_MANAGED in c for c in out["conflicts"])
        assert any("CLAUDE.md" in m for m in out["mergeNeeded"])
        assert tree(tgt) == before


class TestInstalledTargetInit:
    def test_rerun_is_idempotent_and_keeps_user_seed(self, installed):
        _, tgt = installed
        (tgt / "docs/PRD.md").write_text("# PRD: 내 프로젝트\n\n## 목표\n실제 목표\n",
                                         encoding="utf-8")
        before = tree(tgt)
        r = run_init(tgt, "--target", tgt)
        assert r.returncode == 0, r.stdout + r.stderr
        out = json.loads(r.stdout)
        assert out["actions"] == [] and out["changed"] is False
        assert tree(tgt) == before
        assert run_init(tgt, "--target", tgt, "--check").returncode == 0

    def test_locally_modified_managed_is_conflict_and_check_fails(self, installed):
        _, tgt = installed
        p = tgt / ROOT_MANAGED
        p.write_bytes(p.read_bytes() + b"# local tweak\n")
        before = tree(tgt)
        r = run_init(tgt, "--target", tgt, "--profile", "base")
        assert r.returncode == 4, r.stdout + r.stderr
        assert ROOT_MANAGED in r.stdout
        assert tree(tgt) == before
        c = run_init(tgt, "--target", tgt, "--check")
        assert c.returncode == 1
        assert any(ROOT_MANAGED in x for x in json.loads(c.stdout)["problems"])


def _harness_block(dist):
    t = (dist / "templates/project/CLAUDE.md.template").read_text(encoding="utf-8")
    return t[t.index("<!-- harness:begin -->"):]


class TestMergeRequired:
    def test_existing_claude_md_blocks_whole_init_without_writes(self, tmp_path):
        dist = make_dist(tmp_path)
        tgt = make_target(tmp_path, files={"CLAUDE.md": "# 우리 프로젝트 규칙\n"})
        before = tree(tgt)
        r = run_init(dist, "--target", tgt, "--profile", "base")
        assert r.returncode == 4, r.stdout + r.stderr
        assert any("CLAUDE.md" in m for m in json.loads(r.stdout)["mergeNeeded"])
        assert tree(tgt) == before and not (tgt / ".harness").exists()

    def test_adopt_after_manual_merge_records_adopted(self, tmp_path):
        dist = make_dist(tmp_path)
        mine = "# 우리 프로젝트 규칙\n\n- 프로젝트 고유 규칙\n\n"
        tgt = make_target(tmp_path, files={"CLAUDE.md": mine})
        merged = mine + _harness_block(dist)
        (tgt / "CLAUDE.md").write_text(merged, encoding="utf-8")
        r = run_init(dist, "--target", tgt, "--profile", "base", "--adopt-merged", "CLAUDE.md")
        assert r.returncode == 0, r.stdout + r.stderr
        assert (tgt / "CLAUDE.md").read_text(encoding="utf-8") == merged   # 사용자 bytes 보존
        rec = state(tgt)["files"]["CLAUDE.md"]
        assert rec == {"ownership": "merge-required", "status": "adopted",
                       "hash": _sha(merged.encode("utf-8")),
                       "requirementsVersion": rv("CLAUDE.md")}

    def test_adopt_rejected_when_validator_fails(self, tmp_path):
        dist = make_dist(tmp_path)
        bad = "# 규칙\n" + _harness_block(dist).replace("<!-- harness:end -->", "")
        tgt = make_target(tmp_path, files={"CLAUDE.md": bad})
        before = tree(tgt)
        r = run_init(dist, "--target", tgt, "--adopt-merged", "CLAUDE.md")
        assert r.returncode == 4, r.stdout + r.stderr
        assert any("harness:end" in m for m in json.loads(r.stdout)["mergeNeeded"])
        assert tree(tgt) == before

    def test_adopt_flag_for_non_merge_path_is_error(self, tmp_path):
        dist = make_dist(tmp_path)
        tgt = make_target(tmp_path)
        before = tree(tgt)
        r = run_init(dist, "--target", tgt, "--adopt-merged", "docs/PRD.md")
        assert r.returncode == 1, r.stdout + r.stderr
        assert tree(tgt) == before


class TestProfileExpansion:
    def test_base_to_ui_adds_only_ui_seed_and_keeps_user_files(self, tmp_path):
        dist = make_dist(tmp_path)
        tgt = make_target(tmp_path, files={"CLAUDE.md": "# 우리 규칙\n\n" + _harness_block(dist)})
        r = run_init(dist, "--target", tgt, "--adopt-merged", "CLAUDE.md")
        assert r.returncode == 0, r.stdout + r.stderr
        link_venv(tgt)
        (tgt / "docs/PRD.md").write_text("# PRD: 수정됨\n", encoding="utf-8")
        keep = {p: (tgt / p).read_bytes() for p in ("docs/PRD.md", "CLAUDE.md")}
        r = run_init(tgt, "--target", tgt, "--profile", "ui")
        assert r.returncode == 0, r.stdout + r.stderr
        assert [a["path"] for a in json.loads(r.stdout)["actions"]] == ["docs/UI_GUIDE.md"]
        assert (tgt / "docs/UI_GUIDE.md").read_bytes() == (
            tgt / "templates/project/docs/UI_GUIDE.md").read_bytes()
        assert {p: (tgt / p).read_bytes() for p in keep} == keep
        st = state(tgt)
        assert st["profile"] == "ui" and st["files"]["CLAUDE.md"]["status"] == "adopted"
        assert run_init(tgt, "--target", tgt, "--check").returncode == 0

    def test_profile_shrink_rejected(self, installed):
        _, tgt = installed
        assert run_init(tgt, "--target", tgt, "--profile", "ui").returncode == 0
        before = tree(tgt)
        r = run_init(tgt, "--target", tgt, "--profile", "base")
        assert r.returncode == 1, r.stdout + r.stderr
        assert tree(tgt) == before


class TestPathSafety:
    @pytest.mark.parametrize("attack", ["symlink-file", "hardlink-file", "symlink-parent",
                                        "symlink-harness"])
    def test_links_and_escapes_rejected_without_writes(self, tmp_path, attack):
        dist = make_dist(tmp_path)
        outside = tmp_path / "outside"
        outside.mkdir()
        (outside / "victim.md").write_text("victim\n", encoding="utf-8")
        tgt = make_target(tmp_path)
        if attack in ("symlink-file", "hardlink-file"):
            (tgt / "docs").mkdir()
            if attack == "symlink-file":
                (tgt / "docs/PRD.md").symlink_to(outside / "victim.md")
            else:
                os.link(str(outside / "victim.md"), str(tgt / "docs/PRD.md"))
        elif attack == "symlink-parent":
            (tgt / "scripts").symlink_to(outside, target_is_directory=True)
        else:
            (tgt / ".harness").symlink_to(outside, target_is_directory=True)
        before, out_before = tree(tgt), tree(outside)
        r = run_init(dist, "--target", tgt)
        assert r.returncode == 1, r.stdout + r.stderr
        assert tree(tgt) == before and tree(outside) == out_before


class TestTargetAndDistribution:
    def test_target_must_be_independent_git_root(self, tmp_path):
        dist = make_dist(tmp_path)
        tgt = make_target(tmp_path)
        (tgt / "sub").mkdir()
        wt = tmp_path / "linked-wt"
        git(tgt, "worktree", "add", "-q", "-b", "wt", str(wt))
        plain = tmp_path / "plain"
        plain.mkdir()
        for bad in (tgt / "sub", wt, plain):
            before = tree(bad)
            r = run_init(dist, "--target", bad)
            assert r.returncode == 1, (bad, r.stdout + r.stderr)
            assert tree(bad) == before

    def test_dirty_or_self_distribution_rejected(self, tmp_path):
        dist = make_dist(tmp_path)
        tgt = make_target(tmp_path)
        r = run_init(dist, "--target", dist)
        assert r.returncode == 1, r.stdout + r.stderr
        (dist / "scripts/runtime.py").write_bytes((dist / "scripts/runtime.py").read_bytes()
                                                  + b"# uncommitted\n")
        before = tree(tgt)
        r = run_init(dist, "--target", tgt)
        assert r.returncode == 1 and "clean" in r.stdout + r.stderr
        assert tree(tgt) == before


class TestTargetIndependence:
    def test_target_runs_check_and_expansion_without_distribution(self, installed, tmp_path):
        dist, tgt = installed
        dist.rename(tmp_path / "dist-moved-away")      # source/distribution 접근 불가
        r = run_init(tgt, "--target", tgt, "--check")
        assert r.returncode == 0, r.stdout + r.stderr
        r = run_init(tgt, "--target", tgt, "--profile", "ui")
        assert r.returncode == 0, r.stdout + r.stderr
        assert (tgt / "docs/UI_GUIDE.md").is_file()
        assert run_init(tgt, "--target", tgt, "--check").returncode == 0


def _rewrite_state(tgt, mutate, rehash=True):
    """테스트용: state를 고친 뒤 (선택적으로) 자기 hash를 다시 계산해 쓴다."""
    p = tgt / STATE
    obj = json.loads(p.read_text(encoding="utf-8"))
    mutate(obj)
    if rehash:
        p.write_bytes(pi.serialize_state(obj))
    else:
        p.write_text(json.dumps(obj, indent=2, sort_keys=True), encoding="utf-8")


class TestCheckDetects:
    def test_missing_seed_is_error(self, installed):
        _, tgt = installed
        (tgt / "docs/PRD.md").unlink()
        r = run_init(tgt, "--target", tgt, "--check")
        assert r.returncode == 1 and "docs/PRD.md" in r.stdout

    def test_broken_merge_file_is_merge_needed(self, installed):
        _, tgt = installed
        p = tgt / "CLAUDE.md"
        p.write_text(p.read_text(encoding="utf-8").replace("<!-- harness:end -->", ""),
                     encoding="utf-8")
        r = run_init(tgt, "--target", tgt, "--check")
        assert r.returncode == 4 and "harness:end" in r.stdout

    def test_outdated_requirements_version_is_merge_needed(self, installed):
        _, tgt = installed
        _rewrite_state(tgt, lambda o: o["files"][".gitignore"].update(
            requirementsVersion=rv(".gitignore") + 1))
        r = run_init(tgt, "--target", tgt, "--check")
        assert r.returncode == 4 and "requirementsVersion" in r.stdout

    def test_invalid_policy_seed_is_error(self, installed):
        _, tgt = installed
        (tgt / ".harness/policy.json").write_text('{"schemaVersion": 1}', encoding="utf-8")
        r = run_init(tgt, "--target", tgt, "--check")
        assert r.returncode == 1 and "policy" in r.stdout

    @pytest.mark.parametrize("tamper", ["hash", "dupkey", "ownership", "abs-path"])
    def test_tampered_state_is_rejected(self, installed, tamper):
        _, tgt = installed
        p = tgt / STATE
        if tamper == "hash":
            _rewrite_state(tgt, lambda o: o.update(profile="ui"), rehash=False)
        elif tamper == "dupkey":
            p.write_bytes(p.read_bytes().replace(b'"profile": "base"',
                                                 b'"profile": "base", "profile": "ui"'))
        elif tamper == "ownership":
            _rewrite_state(tgt, lambda o: o["files"]["docs/PRD.md"].update(ownership="owner"))
        else:
            _rewrite_state(tgt, lambda o: o["files"].update(
                {"/etc/passwd": {"ownership": "seed", "status": "created", "hash": "0" * 64}}))
        before = tree(tgt)
        for args in (("--check",), ("--profile", "ui")):
            r = run_init(tgt, "--target", tgt, *args)
            assert r.returncode == 1, (tamper, args, r.stdout + r.stderr)
        assert tree(tgt) == before


class TestParseState:
    """state 파서 자체(1차 방어): 자기 hash·중복 key·ownership·경로를 직접 거부한다."""

    def _valid(self):
        return pi.serialize_state({
            "schemaVersion": 1, "distributionName": "x", "distributionVersion": "1.0.0",
            "sourceCommit": "a" * 40, "manifestHash": "b" * 64, "profile": "base",
            "updatedAt": "2026-11-23T00:00:00+00:00",
            "files": {"docs/PRD.md": {"ownership": "seed", "status": "created", "hash": "c" * 64}}})

    def test_valid_round_trip(self):
        assert pi.parse_state(self._valid())["profile"] == "base"

    @pytest.mark.parametrize("mutate", [
        lambda b: b.replace(b'"profile": "base"', b'"profile": "ui"'),             # 자기 hash
        lambda b: b.replace(b'"profile": "base"', b'"profile": "base", "profile": "base"'),
        lambda b: pi.serialize_state(dict(json.loads(b), files={"docs/PRD.md": {
            "ownership": "owner", "status": "created", "hash": "c" * 64}})),
        lambda b: pi.serialize_state(dict(json.loads(b), files={"/etc/passwd": {
            "ownership": "seed", "status": "created", "hash": "c" * 64}})),
        lambda b: pi.serialize_state(dict(json.loads(b), files={".git/config": {
            "ownership": "seed", "status": "created", "hash": "c" * 64}})),
        lambda b: pi.serialize_state(dict(json.loads(b), files={
            "docs/PRD.md": {"ownership": "seed", "status": "created", "hash": "c" * 64},
            "docs/prd.md": {"ownership": "seed", "status": "created", "hash": "c" * 64}})),
    ])
    def test_rejects_tampered_or_invalid(self, mutate):
        with pytest.raises(pi.InstallError):
            pi.parse_state(mutate(self._valid()))


def edit_manifest(d, fn):
    p = Path(d) / "harness-manifest.json"
    obj = json.loads(p.read_text(encoding="utf-8"))
    fn(obj)
    p.write_text(json.dumps(obj, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def _bump(m, version=V2):
    m["distribution"]["version"] = version


def _v2_basic(d):
    """v2: managed 1개 교체·managed 1개 추가·seed 템플릿 변경(target seed는 그대로여야 함)."""
    p = d / "scripts/runtime.py"
    p.write_bytes(p.read_bytes() + b"\n# harness v2\n")
    (d / "templates/project/docs/PRD.md").write_text("# PRD v2 템플릿\n", encoding="utf-8")
    (d / "scripts/hooks/extra-check.sh").write_text("#!/bin/bash\nexit 0\n", encoding="utf-8")
    edit_manifest(d, lambda m: (_bump(m), m["entries"].append(
        {"path": "scripts/hooks/extra-check.sh", "ownership": "managed"})))


def update(tgt, dist2, *extra):
    return run_init(tgt, "--target", tgt, "--update", "--from-distribution", dist2, *extra)


class TestUpdate:
    def test_v1_to_v2_replaces_unchanged_managed_and_adds(self, installed, tmp_path):
        _, tgt = installed
        dist2 = make_dist(tmp_path, "dist-v2", mutate=_v2_basic, message="harness v2")
        prd = (tgt / "docs/PRD.md").read_bytes()
        r = update(tgt, dist2)
        assert r.returncode == 0, r.stdout + r.stderr
        ops = {a["path"]: a["op"] for a in json.loads(r.stdout)["actions"]}
        assert ops["scripts/runtime.py"] == "replace"
        assert ops["harness-manifest.json"] == "replace"
        assert ops["templates/project/docs/PRD.md"] == "replace"
        assert ops["scripts/hooks/extra-check.sh"] == "create"
        assert "docs/PRD.md" not in ops
        for rel in ("scripts/runtime.py", "scripts/hooks/extra-check.sh", "harness-manifest.json"):
            assert (tgt / rel).read_bytes() == (dist2 / rel).read_bytes()
        assert (tgt / "docs/PRD.md").read_bytes() == prd
        st = state(tgt)
        assert st["distributionVersion"] == V2
        assert st["sourceCommit"] == git(dist2, "rev-parse", "HEAD")
        assert st["manifestHash"] == _sha((dist2 / "harness-manifest.json").read_bytes())
        assert run_init(tgt, "--target", tgt, "--check").returncode == 0

    @pytest.mark.parametrize("damage,code", [
        ("modified-managed", 4), ("missing-state", 1), ("tampered-state", 1),
        ("dupkey-state", 1), ("manifest-hash", 1)])
    def test_preflight_failures_keep_target_byte_identical(self, installed, tmp_path, damage,
                                                            code):
        _, tgt = installed
        dist2 = make_dist(tmp_path, "dist-v2", mutate=_v2_basic, message="harness v2")
        st = tgt / STATE
        if damage == "modified-managed":
            p = tgt / "scripts/runtime.py"
            p.write_bytes(p.read_bytes() + b"# mine\n")
        elif damage == "missing-state":
            st.unlink()
        elif damage == "tampered-state":
            st.write_bytes(st.read_bytes().replace(b'"profile": "base"', b'"profile": "ui"'))
        elif damage == "dupkey-state":
            st.write_bytes(st.read_bytes().replace(b'"profile": "base"',
                                                   b'"profile": "base", "profile": "base"'))
        else:
            # state를 유효하게 다시 쓰되 manifestHash만 다른 값으로(자기 hash는 맞춤)
            _rewrite_state(tgt, lambda o: o.update(manifestHash="f" * 64))
        before = tree(tgt)
        r = update(tgt, dist2)
        assert r.returncode == code, (damage, r.stdout + r.stderr)
        assert tree(tgt) == before


REMOVED, MOVED_FROM = _CLAUDE_MANAGED[-2], _CLAUDE_MANAGED[-1]
MOVED_TO = MOVED_FROM.replace(".claude/", ".claude/moved-v2/", 1)


def _v2_remove_move(d):
    (d / REMOVED).unlink()
    (d / MOVED_TO).parent.mkdir(parents=True)
    (d / MOVED_FROM).rename(d / MOVED_TO)
    try:
        (d / MOVED_FROM).parent.rmdir()
    except OSError:
        pass                                        # 다른 파일이 남은 디렉터리

    def fn(m):
        _bump(m)
        m["entries"] = [e for e in m["entries"] if e["path"] not in (REMOVED, MOVED_FROM)]
        m["entries"].append({"path": MOVED_TO, "ownership": "managed", "movedFrom": MOVED_FROM})
    edit_manifest(d, fn)


class TestUpdateRemovalAndMove:
    def test_managed_remove_and_move_need_per_path_acceptance(self, installed, tmp_path):
        _, tgt = installed
        dist2 = make_dist(tmp_path, "dist-v2", mutate=_v2_remove_move)
        before = tree(tgt)
        r = update(tgt, dist2)
        assert r.returncode == 4, r.stdout + r.stderr
        assert set(json.loads(r.stdout)["needsAcceptance"]) == {REMOVED, MOVED_FROM}
        r = update(tgt, dist2, "--accept-managed-removal", REMOVED)
        assert r.returncode == 4 and tree(tgt) == before
        removed_bytes = (tgt / REMOVED).read_bytes()
        r = update(tgt, dist2, "--accept-managed-removal", REMOVED,
                   "--accept-managed-removal", MOVED_FROM)
        assert r.returncode == 0, r.stdout + r.stderr
        out = json.loads(r.stdout)
        labels = {a["path"]: a["label"] for a in out["actions"]}
        assert labels[REMOVED] == "remove" and labels[MOVED_FROM] == "move"
        assert not (tgt / REMOVED).exists() and not (tgt / MOVED_FROM).exists()
        assert (tgt / MOVED_TO).read_bytes() == (dist2 / MOVED_TO).read_bytes()
        backups = [p.read_bytes() for p in (tgt / ".harness/transactions" / out["transaction"]
                                            / "old").iterdir()]
        assert removed_bytes in backups                      # 삭제 전 backup
        assert run_init(tgt, "--target", tgt, "--check").returncode == 0

    def test_modified_managed_not_removed_even_if_accepted(self, installed, tmp_path):
        _, tgt = installed
        dist2 = make_dist(tmp_path, "dist-v2", mutate=_v2_remove_move)
        (tgt / REMOVED).write_text("내가 고친 명령\n", encoding="utf-8")
        before = tree(tgt)
        r = update(tgt, dist2, "--accept-managed-removal", REMOVED,
                   "--accept-managed-removal", MOVED_FROM)
        assert r.returncode == 4 and REMOVED in r.stdout
        assert tree(tgt) == before


def _v2_ownership(d):
    """v2: ROOT_MANAGED managed→seed(템플릿 managed 추가), phases/index.json seed→managed."""
    tpl = "templates/project/%s.seed-template" % ROOT_MANAGED.lstrip(".")
    (d / tpl).write_bytes((d / ROOT_MANAGED).read_bytes())
    (d / "phases").mkdir()
    (d / "phases/index.json").write_bytes((d / "templates/project/phases/index.json").read_bytes())

    def fn(m):
        _bump(m)
        m["entries"] = [e for e in m["entries"] if e["path"] not in (ROOT_MANAGED,
                                                                       "phases/index.json")]
        m["entries"] += [{"path": tpl, "ownership": "managed"},
                         {"path": ROOT_MANAGED, "ownership": "seed", "source": tpl},
                         {"path": "phases/index.json", "ownership": "managed"}]
        # source tree의 phases/index.json은 이제 managed payload다(sourceOnly에서 뺀다)
        m["sourceOnly"] = [x for x in m["sourceOnly"] if x != "phases/index.json"]
    edit_manifest(d, fn)


def _v2_drop_seed(d):
    edit_manifest(d, lambda m: (_bump(m), m.__setitem__("entries", [
        e for e in m["entries"] if e["path"] != "docs/PRD.md"])))


class TestOwnershipChange:
    def test_managed_to_seed_and_seed_to_managed(self, installed, tmp_path):
        _, tgt = installed
        dist2 = make_dist(tmp_path, "dist-v2", mutate=_v2_ownership)
        ini = (tgt / ROOT_MANAGED).read_bytes()
        before = tree(tgt)
        r = update(tgt, dist2)                                  # seed→managed는 자동 금지
        assert r.returncode == 4 and "phases/index.json" in r.stdout
        assert tree(tgt) == before
        r = update(tgt, dist2, "--adopt-managed", "phases/index.json")
        assert r.returncode == 0, r.stdout + r.stderr
        st = state(tgt)
        assert st["files"][ROOT_MANAGED]["ownership"] == "seed"
        assert (tgt / ROOT_MANAGED).read_bytes() == ini        # 파일은 그대로, 관리만 중단
        assert st["files"]["phases/index.json"]["ownership"] == "managed"
        assert run_init(tgt, "--target", tgt, "--check").returncode == 0

    def test_modified_managed_to_seed_is_conflict(self, installed, tmp_path):
        _, tgt = installed
        dist2 = make_dist(tmp_path, "dist-v2", mutate=_v2_ownership)
        (tgt / ROOT_MANAGED).write_text("# mine\n", encoding="utf-8")
        before = tree(tgt)
        r = update(tgt, dist2, "--adopt-managed", "phases/index.json")
        assert r.returncode == 4 and ROOT_MANAGED in r.stdout
        assert tree(tgt) == before

    def test_seed_to_managed_needs_exact_source_bytes(self, installed, tmp_path):
        _, tgt = installed
        dist2 = make_dist(tmp_path, "dist-v2", mutate=_v2_ownership)
        (tgt / "phases/index.json").write_text('{"phases": [{"dir": "x"}]}\n', encoding="utf-8")
        before = tree(tgt)
        r = update(tgt, dist2, "--adopt-managed", "phases/index.json")
        assert r.returncode == 4 and "phases/index.json" in r.stdout
        assert tree(tgt) == before

    def test_seed_removal_never_deletes_user_bytes(self, installed, tmp_path):
        _, tgt = installed
        dist2 = make_dist(tmp_path, "dist-v2", mutate=_v2_drop_seed)
        (tgt / "docs/PRD.md").write_text("# 내 PRD\n", encoding="utf-8")
        before = tree(tgt)
        for extra in ((), ("--accept-managed-removal", "docs/PRD.md")):
            r = update(tgt, dist2, *extra)
            assert r.returncode == 4, r.stdout + r.stderr
            assert "docs/PRD.md" in json.loads(r.stdout)["mergeNeeded"][0]
            assert tree(tgt) == before
        (tgt / "docs/PRD.md").unlink()                          # 사용자가 직접 치운 뒤에만 진행
        r = update(tgt, dist2)
        assert r.returncode == 0, r.stdout + r.stderr
        assert "docs/PRD.md" not in state(tgt)["files"]


NEW_MARKER = "<!-- harness:test-only-new-requirement -->"   # 어떤 배포본에도 없는 marker
NEW_HOOK = {"event": "PostToolUse", "matcher": "Bash",
            "command": "bash \"$CLAUDE_PROJECT_DIR/scripts/hooks/cross-review-nudge.sh\""}


def _add_hook(obj):
    obj["hooks"].setdefault(NEW_HOOK["event"], []).append(
        {"matcher": NEW_HOOK["matcher"], "hooks": [{"type": "command",
                                                    "command": NEW_HOOK["command"]}]})


def _v2_requirements(d):
    tpl = d / "templates/project/CLAUDE.md.template"
    tpl.write_text(tpl.read_text(encoding="utf-8").replace(
        "<!-- harness:end -->", NEW_MARKER + "\n<!-- harness:end -->"), encoding="utf-8")
    s = d / "templates/project/claude-settings.json.template"
    obj = json.loads(s.read_text(encoding="utf-8"))
    _add_hook(obj)
    s.write_text(json.dumps(obj, indent=2) + "\n", encoding="utf-8")

    def fn(m):
        _bump(m)
        for e in m["entries"]:
            if e["path"] == "CLAUDE.md":
                e["requirementsVersion"] = rv("CLAUDE.md") + 1
                e["validators"][0]["required"].append(NEW_MARKER)
            if e["path"] == ".claude/settings.json":
                e["requirementsVersion"] = rv(".claude/settings.json") + 1
                e["validators"][0]["hooks"].append(dict(NEW_HOOK))
    edit_manifest(d, fn)


class TestRequirementsVersion:
    ADOPT = ("--adopt-merged", "CLAUDE.md", "--adopt-merged", ".claude/settings.json")

    def test_rv_bump_blocks_update_until_manual_merge_and_readopt(self, installed, tmp_path):
        _, tgt = installed
        dist2 = make_dist(tmp_path, "dist-v2", mutate=_v2_requirements)
        before = tree(tgt)
        r = update(tgt, dist2)
        assert r.returncode == 4, r.stdout + r.stderr
        need = " ".join(json.loads(r.stdout)["mergeNeeded"])
        assert "CLAUDE.md" in need and ".claude/settings.json" in need
        r = update(tgt, dist2, *self.ADOPT)                     # 병합 없이 adopt → 거부
        assert r.returncode == 4 and tree(tgt) == before
        assert state(tgt)["distributionVersion"] == V1
        # 사용자가 새 marker·hook을 수동 병합
        c = tgt / "CLAUDE.md"
        c.write_text(c.read_text(encoding="utf-8").replace(
            "<!-- harness:end -->", NEW_MARKER + "\n<!-- harness:end -->"), encoding="utf-8")
        s = tgt / ".claude/settings.json"
        obj = json.loads(s.read_text(encoding="utf-8"))
        _add_hook(obj)
        s.write_text(json.dumps(obj, indent=2) + "\n", encoding="utf-8")
        merged = tree(tgt)
        r = update(tgt, dist2)                                  # validator 통과해도 rv↑면 재-adopt 필요
        assert r.returncode == 4 and tree(tgt) == merged
        r = update(tgt, dist2, *self.ADOPT)
        assert r.returncode == 0, r.stdout + r.stderr
        st = state(tgt)
        assert st["distributionVersion"] == V2
        for p in ("CLAUDE.md", ".claude/settings.json"):
            assert st["files"][p]["requirementsVersion"] == rv(p) + 1
            assert st["files"][p]["status"] == "adopted"
        assert run_init(tgt, "--target", tgt, "--check").returncode == 0


# --- transaction 장애 주입 ----------------------------------------------------------------
# 실제 프로세스에서 installer main을 띄우고, 테스트 전용 module hook(pi._fault_hook)으로 지정 지점에서
# 예외·강제 종료(os._exit)·SIGINT·일시 정지·외부 변경을 일으킨다. env·CLI로는 켤 수 없다.
DRIVER = textwrap.dedent('''
    import json, os, signal, sys, time
    sys.dont_write_bytecode = True   # 실제 CLI 경로와 같게: target에 .pyc를 남기지 않음
    sys.path.insert(0, sys.argv[1])
    import project_init as pi
    specs = json.loads(sys.argv[2])
    specs = specs if isinstance(specs, list) else [specs]
    def hook(point, index=None, path=None):
        for spec in specs:
            if point == spec["point"] and ("index" not in spec or index == spec["index"]):
                act_on(spec, index)
    def act_on(spec, index):
        act = spec["action"]
        point = spec["point"]
        if act == "raise":
            raise OSError("injected fault at %s %s" % (point, index))
        if act == "exit":
            os._exit(137)
        if act == "sigint":
            os.kill(os.getpid(), signal.SIGINT)
            time.sleep(5)
        if act == "pause":
            open(spec["ready"], "w").close()
            deadline = time.time() + 60
            while not os.path.exists(spec["go"]) and time.time() < deadline:
                time.sleep(0.05)
        if act == "tamper":
            with open(spec["file"], "ab") as f:
                f.write(b"external change\\n")
        if act == "create":              # 경쟁자: 경로에 남의 파일을 원자적으로 만든다(한 번만)
            if not os.path.lexists(spec["file"]):
                with open(spec["file"], "x") as f:
                    f.write(spec.get("content", ""))
        if act == "replace-owner":       # 실행 중인 미완료 transaction의 owner.lock 경로 교체
            from pathlib import Path as _P
            for txid in pi.incomplete_transactions(_P(spec["target"])):
                o = _P(spec["target"]) / ".harness/transactions" / txid / "owner.lock"
                o.unlink()
                o.write_text(spec.get("content", ""))
        if act == "replace-lock":
            os.unlink(spec["file"])
            with open(spec["file"], "w") as f:
                f.write(spec.get("content", ""))
        if act == "copy":
            os.makedirs(os.path.dirname(spec["dst"]), exist_ok=True)
            with open(spec["src"], "rb") as s, open(spec["dst"], "wb") as d:
                d.write(s.read())
    pi._fault_hook = hook
    sys.exit(pi.main(sys.argv[3:]))
''')


def run_fault(installer_root, spec, *args, wait=True):
    argv = [str(VENV_PY), "-c", DRIVER, str(Path(installer_root) / "scripts"),
            json.dumps(spec)] + [str(a) for a in args]
    if not wait:
        return subprocess.Popen(argv, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    return subprocess.run(argv, capture_output=True, text=True, timeout=300)


def tree_ex_tx(root):
    """transaction evidence(.harness/transactions/**)를 뺀 tree — rollback 결과 비교용."""
    return dict((k, v) for k, v in tree(root).items()
                if not (k == ".harness/transactions" or k.startswith(".harness/transactions/")))


def tx_dirs(tgt):
    d = tgt / ".harness/transactions"
    return sorted(d.iterdir()) if d.exists() else []


class TestTransactionFaults:
    def test_nth_write_failure_rolls_back_to_byte_identical(self, installed, tmp_path):
        _, tgt = installed
        dist2 = make_dist(tmp_path, "dist-v2", mutate=_v2_basic)
        before = tree_ex_tx(tgt)
        r = run_fault(tgt, {"point": "before-write", "index": 2, "action": "raise"},
                      "--target", tgt, "--update", "--from-distribution", dist2)
        assert r.returncode == 1, r.stdout + r.stderr
        assert "rollback" in r.stdout + r.stderr
        assert tree_ex_tx(tgt) == before
        rolled = [d for d in tx_dirs(tgt) if (d / "rolled-back").exists()]
        assert len(rolled) == 1 and not (rolled[0] / "committed").exists()
        assert pi.incomplete_transactions(tgt) == []
        assert run_init(tgt, "--target", tgt, "--check").returncode == 0


def _pending_id(tgt):
    ids = pi.incomplete_transactions(tgt)
    assert len(ids) == 1, ids
    return ids[0]


class TestCrashRecovery:
    def _crash(self, installed, tmp_path, spec):
        _, tgt = installed
        dist2 = make_dist(tmp_path, "dist-v2", mutate=_v2_basic)
        before = tree_ex_tx(tgt)
        r = run_fault(tgt, spec, "--target", tgt, "--update", "--from-distribution", dist2)
        assert r.returncode == 137, r.stdout + r.stderr          # 강제 종료(정리 없음)
        return tgt, dist2, before

    @pytest.mark.parametrize("spec", [
        {"point": "after-write", "index": 1, "action": "exit"},
        {"point": "before-state", "action": "exit"},
    ])
    def test_crash_before_commit_point_requires_recover_then_rolls_back(self, installed,
                                                                       tmp_path, spec):
        tgt, dist2, before = self._crash(installed, tmp_path, spec)
        txid = _pending_id(tgt)
        mid = tree(tgt)
        for args in (("--check",), ("--profile", "base"), ("--update", "--from-distribution",
                                                          dist2)):
            r = run_init(tgt, "--target", tgt, *args)
            assert r.returncode == 3 and txid in r.stdout, (args, r.stdout + r.stderr)
            assert tree(tgt) == mid                                # 자동 진행·쓰기 없음
        r = run_init(tgt, "--target", tgt, "--recover", "--transaction", txid)
        assert r.returncode == 0, r.stdout + r.stderr
        assert json.loads(r.stdout)["outcome"] == "rolled-back"
        assert tree_ex_tx(tgt) == before
        assert run_init(tgt, "--target", tgt, "--check").returncode == 0

    def test_crash_after_state_publish_is_completed_not_rolled_back(self, installed, tmp_path):
        tgt, dist2, _ = self._crash(installed, tmp_path, {"point": "after-state",
                                                          "action": "exit"})
        txid = _pending_id(tgt)
        assert state(tgt)["distributionVersion"] == V2      # commit point 통과
        r = run_init(tgt, "--target", tgt, "--recover", "--transaction", txid)
        assert r.returncode == 0, r.stdout + r.stderr
        assert json.loads(r.stdout)["outcome"] == "committed"
        assert (tgt / "scripts/runtime.py").read_bytes() == (dist2 / "scripts/runtime.py").read_bytes()
        assert run_init(tgt, "--target", tgt, "--check").returncode == 0


class TestInterruptsConflictsAndConcurrency:
    def test_sigint_during_apply_rolls_back(self, installed, tmp_path):
        _, tgt = installed
        dist2 = make_dist(tmp_path, "dist-v2", mutate=_v2_basic)
        before = tree_ex_tx(tgt)
        r = run_fault(tgt, {"point": "after-write", "index": 1, "action": "sigint"},
                      "--target", tgt, "--update", "--from-distribution", dist2)
        assert r.returncode == 130, r.stdout + r.stderr
        assert tree_ex_tx(tgt) == before
        assert pi.incomplete_transactions(tgt) == []

    def test_user_edit_after_crash_is_recovery_conflict(self, installed, tmp_path):
        _, tgt = installed
        dist2 = make_dist(tmp_path, "dist-v2", mutate=_v2_basic)
        r = run_fault(tgt, {"point": "after-write", "index": 2, "action": "exit"},
                      "--target", tgt, "--update", "--from-distribution", dist2)
        assert r.returncode == 137
        txid = _pending_id(tgt)
        p = tgt / "scripts/runtime.py"                       # 이미 새 bytes로 바뀐 파일
        p.write_bytes(p.read_bytes() + b"# user edit after crash\n")
        mid = tree(tgt)
        r = run_init(tgt, "--target", tgt, "--recover", "--transaction", txid)
        assert r.returncode == 3, r.stdout + r.stderr
        assert json.loads(r.stdout)["kind"] == "recovery-conflict"
        assert "scripts/runtime.py" in r.stdout
        assert tree(tgt) == mid                              # 아무것도 덮지 않음
        assert pi.incomplete_transactions(tgt) == [txid]

    def test_concurrent_installer_gets_busy_and_writes_nothing(self, installed, tmp_path):
        _, tgt = installed
        dist2 = make_dist(tmp_path, "dist-v2", mutate=_v2_basic)
        ready, go = tmp_path / "ready", tmp_path / "go"
        a = run_fault(tgt, {"point": "before-write", "index": 0, "action": "pause",
                            "ready": str(ready), "go": str(go)},
                      "--target", tgt, "--update", "--from-distribution", dist2, wait=False)
        try:
            deadline = time.time() + 60
            while not ready.exists() and time.time() < deadline:
                time.sleep(0.05)
            assert ready.exists(), "installer A가 lock 뒤 정지 지점에 오지 않음"
            mid = tree(tgt)
            for args in (("--update", "--from-distribution", dist2), ("--profile", "ui"),
                         ("--check",)):
                b = run_init(tgt, "--target", tgt, *args)
                assert b.returncode == 5, (args, b.stdout + b.stderr)
                assert tree(tgt) == mid
        finally:
            go.write_text("go", encoding="utf-8")
            out, err = a.communicate(timeout=120)
        assert a.returncode == 0, out + err
        assert state(tgt)["distributionVersion"] == V2

    def test_external_change_after_preflight_blocks_write(self, installed, tmp_path):
        _, tgt = installed
        dist2 = make_dist(tmp_path, "dist-v2", mutate=_v2_basic)
        before = tree_ex_tx(tgt)
        victim = tgt / "scripts/runtime.py"                   # 나중(index 2)에 교체될 파일
        r = run_fault(tgt, {"point": "after-write", "index": 0, "action": "tamper",
                            "file": str(victim)},
                      "--target", tgt, "--update", "--from-distribution", dist2)
        assert r.returncode == 1, r.stdout + r.stderr
        assert "scripts/runtime.py" in r.stdout + r.stderr
        after = tree_ex_tx(tgt)
        changed = sorted(k for k in set(before) | set(after) if before.get(k) != after.get(k))
        assert changed == ["scripts/runtime.py"]             # 자기 변경은 rollback
        assert victim.read_bytes().endswith(b"external change\n")   # 외부 변경은 보존

    def test_initial_init_failure_removes_only_own_creations(self, tmp_path):
        dist = make_dist(tmp_path)
        tgt = make_target(tmp_path, files={"docs/notes.md": "선재 문서\n",
                                           "src/app.py": "print('app')\n"})
        before = tree(tgt)
        r = run_fault(dist, {"point": "before-write", "index": 5, "action": "raise"},
                      "--target", tgt, "--profile", "base")
        assert r.returncode == 1, r.stdout + r.stderr
        after = tree(tgt)
        extra = sorted(k for k in after if k not in before)
        assert all(k == ".harness" or k == ".harness/install.lock"
                   or k.startswith(".harness/transactions") for k in extra), extra
        assert all(after.get(k) == v for k, v in before.items())      # 선재 파일 보존
        assert not (tgt / STATE).exists()


def _v2_everything(d):
    _v2_basic(d)
    _v2_remove_move(d)
    _v2_ownership(d)


class TestUpdateDryRun:
    def test_dry_run_classifies_every_change_without_writing(self, installed, tmp_path):
        _, tgt = installed
        dist2 = make_dist(tmp_path, "dist-v2", mutate=_v2_everything)
        before = tree(tgt)
        r = update(tgt, dist2, "--dry-run", "--accept-managed-removal", REMOVED,
                   "--accept-managed-removal", MOVED_FROM, "--adopt-managed", "phases/index.json")
        assert r.returncode == 0, r.stdout + r.stderr
        out = json.loads(r.stdout)
        labels = {a["path"]: a["label"] for a in out["actions"]}
        assert labels["scripts/hooks/extra-check.sh"] == "add"
        assert labels["scripts/runtime.py"] == "replace"
        assert labels[REMOVED] == "remove" and labels[MOVED_FROM] == "move"
        assert labels[MOVED_TO] == "add"
        changes = {c["path"]: (c["from"], c["to"]) for c in out["ownershipChanges"]}
        assert changes == {ROOT_MANAGED: ("managed", "seed"),
                           "phases/index.json": ("seed", "managed")}
        assert out["dryRun"] is True and tree(tgt) == before


class TestEdgesAndCli:
    def test_identical_preexisting_managed_is_adopted_without_write(self, tmp_path):
        dist = make_dist(tmp_path)
        same = (dist / ROOT_MANAGED).read_bytes()
        tgt = make_target(tmp_path, files={ROOT_MANAGED: same})
        r = run_init(dist, "--target", tgt)
        assert r.returncode == 0, r.stdout + r.stderr
        assert ROOT_MANAGED not in [a["path"] for a in json.loads(r.stdout)["actions"]]
        assert state(tgt)["files"][ROOT_MANAGED]["ownership"] == "managed"

    def test_invalid_mode_combinations_and_noop_update(self, installed):
        dist, tgt = installed
        before = tree(tgt)
        for args in (("--from-distribution", dist), ("--transaction", "x"),
                     ("--update", "--from-distribution", dist, "--profile", "ui"),
                     ("--update",)):
            r = run_init(tgt, "--target", tgt, *args)
            assert r.returncode == 1, (args, r.stdout + r.stderr)
            assert tree(tgt) == before
        r = update(tgt, dist)                                   # 같은 distribution
        assert r.returncode == 0, r.stdout + r.stderr
        assert json.loads(r.stdout)["changed"] is False and tree(tgt) == before


def _commit_all(repo, msg):
    git(repo, "add", "-A", "--", ".", ":!.venv")
    git(repo, "commit", "-q", "-m", msg)


class TestFreshCloneOfInstalledTarget:
    """install-state.json은 커밋되고 install.lock은 gitignore — 새 clone에서도 update·recover가 돼야 한다."""

    def test_clone_without_lock_can_update_and_noop_init_keeps_lock(self, installed, tmp_path):
        _, tgt = installed
        _commit_all(tgt, "chore: install harness")
        clone = tmp_path / "clone"
        git(tmp_path, "clone", "-q", str(tgt), str(clone))
        link_venv(clone)
        assert (clone / STATE).exists() and not (clone / ".harness/install.lock").exists()
        r = run_init(clone, "--target", clone)
        assert r.returncode == 0 and json.loads(r.stdout)["changed"] is False, r.stdout + r.stderr
        assert (clone / ".harness/install.lock").is_file()          # 이미 설치된 target의 lock은 지우지 않음
        dist2 = make_dist(tmp_path, "dist-v2", mutate=_v2_basic)
        (clone / ".harness/install.lock").unlink()                  # 다시 lock 없는 clone 상태
        r = update(clone, dist2)
        assert r.returncode == 0, r.stdout + r.stderr
        assert state(clone)["distributionVersion"] == V2

    def test_recover_works_when_lock_file_missing(self, installed, tmp_path):
        _, tgt = installed
        dist2 = make_dist(tmp_path, "dist-v2", mutate=_v2_basic)
        before = tree_ex_tx(tgt)
        r = run_fault(tgt, {"point": "after-write", "index": 1, "action": "exit"},
                      "--target", tgt, "--update", "--from-distribution", dist2)
        assert r.returncode == 137
        txid = _pending_id(tgt)
        (tgt / ".harness/install.lock").unlink()
        r = run_init(tgt, "--target", tgt, "--recover", "--transaction", txid)
        assert r.returncode == 0, r.stdout + r.stderr
        assert tree_ex_tx(tgt) == dict(before, **{".harness/install.lock": before.get(
            ".harness/install.lock")})


class TestRollbackScope:
    """같은 프로세스 rollback은 installer가 실제로 쓴(또는 쓰던) 경로만 되돌린다 — 아직 쓰지 않은
    경로에 외부가 같은 bytes를 써 넣었어도 그 변경은 보존한다."""

    def test_update_rollback_keeps_identical_external_write(self, installed, tmp_path):
        _, tgt = installed
        dist2 = make_dist(tmp_path, "dist-v2", mutate=_v2_basic)
        manifest_v1 = (tgt / "harness-manifest.json").read_bytes()
        ext = (dist2 / "scripts/runtime.py").read_bytes()
        r = run_fault(tgt, {"point": "before-write", "index": 1, "action": "copy",
                            "src": str(dist2 / "scripts/runtime.py"),
                            "dst": str(tgt / "scripts/runtime.py")},
                      "--target", tgt, "--update", "--from-distribution", dist2)
        assert r.returncode == 1, r.stdout + r.stderr
        assert (tgt / "scripts/runtime.py").read_bytes() == ext          # 외부 변경 보존
        assert (tgt / "harness-manifest.json").read_bytes() == manifest_v1  # 자기 변경 rollback
        assert pi.incomplete_transactions(tgt) == []

    def test_init_rollback_keeps_identical_external_create(self, tmp_path):
        dist = make_dist(tmp_path)
        tgt = make_target(tmp_path)
        tpl = dist / "templates/project/docs/PRD.md"
        r = run_fault(dist, {"point": "before-write", "index": 1, "action": "copy",
                             "src": str(tpl), "dst": str(tgt / "docs/PRD.md")},
                      "--target", tgt, "--profile", "base")
        assert r.returncode == 1, r.stdout + r.stderr
        assert (tgt / "docs/PRD.md").read_bytes() == tpl.read_bytes()      # 외부 생성 보존
        assert not (tgt / ".claude/commands/harness.md").exists()          # 자기 생성물은 제거


class TestLockIdentity:
    def test_lock_file_replaced_during_acquire_is_busy(self, installed, monkeypatch):
        """open과 flock 사이에 lock 파일이 교체되면(다른 installer의 정리·재생성) 옛 inode의 lock을
        믿지 않는다 — 두 installer가 동시에 lock을 가진다고 착각하지 않게."""
        _, tgt = installed
        lock = tgt / ".harness/install.lock"

        def hook(point, index=None, path=None):
            if point == "lock-opened":
                lock.unlink()
                lock.write_text("", encoding="utf-8")
        monkeypatch.setattr(pi, "_fault_hook", hook)
        with pytest.raises(pi.LockBusy):
            pi.TargetLock(tgt).acquire(create=True)


class TestDistributionReadOnly:
    def test_preflight_does_not_rewrite_distribution_git_index(self, tmp_path):
        """--dry-run·init preflight는 distribution에 아무것도 쓰지 않는다(.git/index 포함)."""
        dist = make_dist(tmp_path)
        tgt = make_target(tmp_path)
        p = dist / "scripts/runtime.py"
        st = p.stat()
        os.utime(str(p), (st.st_atime, st.st_mtime + 5))    # 내용은 같고 stat만 바뀜
        idx = (dist / ".git/index").read_bytes()
        r = run_init(dist, "--target", tgt, "--dry-run")
        assert r.returncode == 0, r.stdout + r.stderr
        assert (dist / ".git/index").read_bytes() == idx


class TestCleanErrors:
    """실패는 traceback이 아니라 JSON 보고 + 종료코드로 끝난다(fail closed는 그대로)."""

    def test_state_with_lone_surrogate_is_clean_error(self, installed):
        _, tgt = installed
        p = tgt / STATE
        p.write_bytes(p.read_bytes().replace(b'"profile": "base"', b'"profile": "\\udc80"'))
        r = run_init(tgt, "--target", tgt, "--check")
        assert r.returncode == 1 and "Traceback" not in r.stderr, r.stdout + r.stderr
        assert json.loads(r.stdout)["ok"] is False

    def test_unwritable_target_is_clean_error(self, tmp_path):
        dist = make_dist(tmp_path)
        tgt = make_target(tmp_path)
        before = tree(tgt)
        os.chmod(str(tgt), 0o555)
        try:
            r = run_init(dist, "--target", tgt)
        finally:
            os.chmod(str(tgt), 0o755)
        assert r.returncode == 1 and "Traceback" not in r.stderr, r.stdout + r.stderr
        assert json.loads(r.stdout)["ok"] is False
        assert tree(tgt) == before

    def test_rollback_failure_becomes_recovery_required(self, installed, tmp_path):
        _, tgt = installed
        dist2 = make_dist(tmp_path, "dist-v2", mutate=_v2_basic)
        r = run_fault(tgt, [{"point": "before-write", "index": 2, "action": "raise"},
                            {"point": "settle", "action": "raise"}],
                      "--target", tgt, "--update", "--from-distribution", dist2)
        assert r.returncode == 3 and "Traceback" not in r.stderr, r.stdout + r.stderr
        out = json.loads(r.stdout)
        assert out["kind"] == "recovery-required" and "--recover" in out["error"]
        assert len(pi.incomplete_transactions(tgt)) == 1        # fail closed: recover만 허용


INSTALLER_FILES = {"scripts/harness.py", "scripts/project_init.py", "scripts/runtime.py"}


def _v2_installer(d):
    _v2_basic(d)
    for rel in ("scripts/project_init.py", "scripts/harness.py"):
        (d / rel).write_bytes((d / rel).read_bytes() + b"\n# harness v2\n")


class TestInstallerSafeOrdering:
    def test_installer_files_are_written_last(self, installed, tmp_path):
        """크래시가 나도 target의 installer가 앞쪽 쓰기 동안 옛 버전 그대로 남도록 installer 파일은 마지막."""
        _, tgt = installed
        dist2 = make_dist(tmp_path, "dist-v2", mutate=_v2_installer)
        r = update(tgt, dist2, "--dry-run")
        assert r.returncode == 0, r.stdout + r.stderr
        paths = [a["path"] for a in json.loads(r.stdout)["actions"]]
        k = min(paths.index(p) for p in INSTALLER_FILES)
        assert set(paths[k:]) == INSTALLER_FILES

    def test_recover_with_distribution_installer(self, installed, tmp_path):
        """target installer가 섞여 못 쓰게 됐을 때를 대비해 distribution checkout의 installer로도
        같은 transaction을 복구할 수 있다(transaction 기록은 자기완결)."""
        _, tgt = installed
        dist2 = make_dist(tmp_path, "dist-v2", mutate=_v2_installer)
        before = tree_ex_tx(tgt)
        r = run_fault(tgt, {"point": "after-write", "index": 1, "action": "exit"},
                      "--target", tgt, "--update", "--from-distribution", dist2)
        assert r.returncode == 137
        txid = _pending_id(tgt)
        r = run_init(dist2, "--target", tgt, "--recover", "--transaction", txid)
        assert r.returncode == 0, r.stdout + r.stderr
        assert json.loads(r.stdout)["outcome"] == "rolled-back"
        assert tree_ex_tx(tgt) == before


def _start_paused(installer_root, tmp_path, *args):
    """installer를 lock 단계 직후(after-lock)에서 멈춘 실제 프로세스로 띄운다."""
    ready, go = tmp_path / "paused.ready", tmp_path / "paused.go"
    proc = run_fault(installer_root, {"point": "after-lock", "action": "pause",
                                      "ready": str(ready), "go": str(go)}, *args, wait=False)
    deadline = time.time() + 60
    while not ready.exists() and time.time() < deadline and proc.poll() is None:
        time.sleep(0.05)
    assert ready.exists(), "installer가 after-lock 지점에 오지 않음: %r" % (proc.poll(),)
    return proc, go


def _finish(proc, go):
    go.write_text("go", encoding="utf-8")
    out, err = proc.communicate(timeout=120)
    return proc.returncode, out, err


class TestLockForReadOnlyModes:
    """check·dry-run도 preflight부터 끝날 때까지 target lock을 잡는다 — lock 파일이 아직 없는
    새 clone·미설치 target에서도(계획 4.3: 모든 init/update/check/recover)."""

    def _fresh_clone(self, installed, tmp_path):
        _, tgt = installed
        _commit_all(tgt, "chore: install harness")
        clone = tmp_path / "clone"
        git(tmp_path, "clone", "-q", str(tgt), str(clone))
        link_venv(clone)
        assert not (clone / ".harness/install.lock").exists()
        return clone

    def test_fresh_clone_check_holds_lock_against_concurrent_installer(self, installed,
                                                                       tmp_path):
        clone = self._fresh_clone(installed, tmp_path)
        proc, go = _start_paused(clone, tmp_path, "--target", clone, "--check")
        try:
            mid = tree(clone)
            r = run_init(clone, "--target", clone, "--profile", "ui")
            assert r.returncode == 5, r.stdout + r.stderr          # check가 lock을 쥐고 있다
            assert tree(clone) == mid
        finally:
            rc, out, err = _finish(proc, go)
        assert rc == 0, out + err
        assert not (clone / "docs/UI_GUIDE.md").exists()

    def test_fresh_clone_check_busy_when_installer_holds_lock(self, installed, tmp_path):
        clone = self._fresh_clone(installed, tmp_path)
        proc, go = _start_paused(clone, tmp_path, "--target", clone, "--profile", "ui")
        try:
            r = run_init(clone, "--target", clone, "--check")
            assert r.returncode == 5, r.stdout + r.stderr
        finally:
            rc, out, err = _finish(proc, go)
        assert rc == 0, out + err

    def test_fresh_target_dry_run_holds_lock_against_concurrent_init(self, tmp_path):
        dist = make_dist(tmp_path)
        tgt = make_target(tmp_path)
        before = tree(tgt)
        proc, go = _start_paused(dist, tmp_path, "--target", tgt, "--profile", "base",
                                 "--dry-run")
        try:
            mid = tree(tgt)
            r = run_init(dist, "--target", tgt, "--profile", "base")
            assert r.returncode == 5, r.stdout + r.stderr          # dry-run이 lock을 쥐고 있다
            assert tree(tgt) == mid
        finally:
            rc, out, err = _finish(proc, go)
        assert rc == 0, out + err
        assert tree(tgt) == before                                  # dry-run은 흔적을 남기지 않음

    def test_fresh_target_dry_run_busy_when_init_holds_lock(self, tmp_path):
        dist = make_dist(tmp_path)
        tgt = make_target(tmp_path)
        proc, go = _start_paused(dist, tmp_path, "--target", tgt, "--profile", "base")
        try:
            r = run_init(dist, "--target", tgt, "--profile", "base", "--dry-run")
            assert r.returncode == 5, r.stdout + r.stderr
        finally:
            rc, out, err = _finish(proc, go)
        assert rc == 0, out + err

    def test_lock_cleaned_up_by_finished_holder_is_reacquired(self, tmp_path, monkeypatch):
        """open과 flock 사이에 앞 holder가 lock·.harness를 정리하고 떠나면 옛 inode를 믿지 않고
        새 lock을 다시 만들어 잡는다(정리 경쟁에서 두 installer가 동시에 진행하지 않게)."""
        tgt = make_target(tmp_path)
        lock = tgt / ".harness/install.lock"
        fired = []

        def hook(point, index=None, path=None):
            if point == "lock-opened" and not fired:
                fired.append(1)
                lock.unlink()
                os.rmdir(str(tgt / ".harness"))
        monkeypatch.setattr(pi, "_fault_hook", hook)
        lk = pi.TargetLock(tgt)
        assert lk.acquire() is True and fired
        assert os.lstat(str(lock)).st_ino == os.fstat(lk.fd).st_ino   # 경로의 현재 inode를 쥠
        lk.release(cleanup=True)
        assert not (tgt / ".harness").exists()                         # 미설치 target — 흔적 없음


def _fresh_clone(installed, tmp_path, name="clone"):
    """설치 결과를 커밋한 target의 새 clone(gitignore된 install.lock 없음) + 자기 .venv."""
    _, tgt = installed
    if git(tgt, "status", "--porcelain", "--", ".", ":!.venv"):
        _commit_all(tgt, "chore: install harness")
    clone = tmp_path / name
    git(tmp_path, "clone", "-q", str(tgt), str(clone))
    link_venv(clone)
    assert not (clone / ".harness/install.lock").exists()
    return clone


class TestReadOnlyByteIdentity:
    """check·dry-run은 target lock을 쥐어 직렬화하되, 끝나면 target을 byte-identical로 남긴다 —
    이번 실행이 만든 lock inode만 지우고, 원래 있던 lock은 지우지 않는다(계획 4.3·Task 3)."""

    def test_installed_fresh_clone_check_leaves_target_byte_identical(self, installed,
                                                                      tmp_path):
        clone = _fresh_clone(installed, tmp_path)
        before = tree(clone)
        r = run_init(clone, "--target", clone, "--check")
        assert r.returncode == 0, r.stdout + r.stderr
        assert tree(clone) == before

    def test_installed_fresh_clone_update_dry_run_leaves_target_byte_identical(
            self, installed, tmp_path):
        clone = _fresh_clone(installed, tmp_path)
        dist2 = make_dist(tmp_path, "dist-v2", mutate=_v2_basic)
        before = tree(clone)
        r = update(clone, dist2, "--dry-run")
        assert r.returncode == 0, r.stdout + r.stderr
        assert json.loads(r.stdout)["dryRun"] is True
        assert tree(clone) == before

    def test_installed_fresh_clone_init_dry_run_leaves_target_byte_identical(self, installed,
                                                                             tmp_path):
        clone = _fresh_clone(installed, tmp_path)
        before = tree(clone)
        r = run_init(clone, "--target", clone, "--profile", "ui", "--dry-run")
        assert r.returncode == 0, r.stdout + r.stderr
        assert tree(clone) == before

    def test_update_dry_run_serializes_and_then_leaves_no_trace(self, installed, tmp_path):
        clone = _fresh_clone(installed, tmp_path)
        dist2 = make_dist(tmp_path, "dist-v2", mutate=_v2_basic)
        before = tree(clone)
        proc, go = _start_paused(clone, tmp_path, "--target", clone, "--update",
                                 "--from-distribution", dist2, "--dry-run")
        try:
            mid = tree(clone)
            r = run_init(clone, "--target", clone, "--profile", "ui")
            assert r.returncode == 5, r.stdout + r.stderr          # dry-run이 lock을 쥐고 있다
            assert tree(clone) == mid
        finally:
            rc, out, err = _finish(proc, go)
        assert rc == 0, out + err
        assert tree(clone) == before

    def test_preexisting_lock_survives_read_only_modes(self, installed, tmp_path):
        _, tgt = installed
        lock = tgt / ".harness/install.lock"
        ino = os.lstat(str(lock)).st_ino
        dist2 = make_dist(tmp_path, "dist-v2", mutate=_v2_basic)
        for args in (("--check",), ("--profile", "ui", "--dry-run"),
                     ("--update", "--from-distribution", dist2, "--dry-run")):
            r = run_init(tgt, "--target", tgt, *args)
            assert r.returncode == 0, (args, r.stdout + r.stderr)
            assert os.lstat(str(lock)).st_ino == ino                # 원래 lock inode 그대로


def _replace_lock(target, content="replacement\n"):
    lock = Path(target) / ".harness/install.lock"
    lock.unlink()
    lock.write_text(content, encoding="utf-8")
    return lock


class TestLockIdentityAfterAcquire:
    """획득 뒤 lock 경로가 교체되면 Unix flock은 새 inode의 두 번째 holder를 막지 못한다 — 첫 holder는
    preflight→apply의 매 전이·매 쓰기·commit point 직전에 경로 동일성을 다시 확인해 fail closed로 멈추고,
    교체 inode는 절대 지우지 않는다."""

    def test_probe_second_holder_on_replacement_and_first_detects_loss(self, installed):
        _, tgt = installed
        a = pi.TargetLock(tgt)
        a.acquire()
        lock = _replace_lock(tgt)
        b = pi.TargetLock(tgt)
        assert b.acquire() is True               # 새 inode에 두 번째 holder — Unix가 막지 못함
        with pytest.raises(pi.LockLost):
            a.verify()
        b.verify()
        a.release(cleanup=True, read_only=True)
        b.release()
        assert lock.read_text(encoding="utf-8") == "replacement\n"   # 교체 inode 보존

    @pytest.mark.parametrize("point", [{"point": "after-lock"},
                                       {"point": "before-write", "index": 0},
                                       {"point": "before-state"}])
    def test_update_aborts_without_project_writes_when_lock_replaced(self, installed, tmp_path,
                                                                     point):
        _, tgt = installed
        dist2 = make_dist(tmp_path, "dist-v2", mutate=_v2_basic)
        before = tree_ex_tx(tgt)
        spec = dict(point, action="replace-lock", file=str(tgt / ".harness/install.lock"),
                    content="replacement\n")
        r = run_fault(tgt, spec, "--target", tgt, "--update", "--from-distribution", dist2)
        assert r.returncode == 5, r.stdout + r.stderr
        assert json.loads(r.stdout)["kind"] == "lock-lost"
        after = tree_ex_tx(tgt)
        assert after.pop(".harness/install.lock")[1] == _sha(b"replacement\n")   # 교체 inode 보존
        before.pop(".harness/install.lock")
        assert after == before                                  # project 내용·state 그대로
        assert pi.incomplete_transactions(tgt) == []

    def test_stale_holder_cannot_commit_and_new_holder_cannot_write(self, installed, tmp_path):
        _, tgt = installed
        dist2 = make_dist(tmp_path, "dist-v2", mutate=_v2_basic)
        before = tree_ex_tx(tgt)
        ready, go = tmp_path / "a.ready", tmp_path / "a.go"
        a = run_fault(tgt, {"point": "before-write", "index": 0, "action": "pause",
                            "ready": str(ready), "go": str(go)},
                      "--target", tgt, "--update", "--from-distribution", dist2, wait=False)
        try:
            deadline = time.time() + 60
            while not ready.exists() and time.time() < deadline:
                time.sleep(0.05)
            assert ready.exists()
            _replace_lock(tgt)
            b = update(tgt, dist2)                  # 새 inode의 lock은 잡지만…
            assert b.returncode == 3, b.stdout + b.stderr     # …A의 prepared transaction이 쓰기 전에 막는다
        finally:
            go.write_text("go", encoding="utf-8")
            out, err = a.communicate(timeout=120)
        assert a.returncode == 5 and json.loads(out)["kind"] == "lock-lost", out + err
        after = tree_ex_tx(tgt)
        after.pop(".harness/install.lock")
        before.pop(".harness/install.lock")
        assert after == before
        assert pi.incomplete_transactions(tgt) == []

    def test_check_fails_closed_and_keeps_replacement(self, installed, tmp_path):
        clone = _fresh_clone(installed, tmp_path)        # check가 lock을 만드는 경우
        proc, go = _start_paused(clone, tmp_path, "--target", clone, "--check")
        lock = _replace_lock(clone)
        rc, out, err = _finish(proc, go)
        assert rc == 5 and json.loads(out)["kind"] == "lock-lost", out + err
        assert lock.read_text(encoding="utf-8") == "replacement\n"   # 자기 inode가 아니면 지우지 않음


class TestStaleHolderCannotRace:
    """lock 경로가 교체돼 두 번째 holder가 생겨도: 살아 있는 첫 holder의 transaction을 두 번째가 확정·
    rollback하지 못하고(transaction owner lock), recover도 매 복원 직전 lock 동일성을 재확인하며,
    아무것도 쓰기 전 멈춘 transaction은 target을 recovery-required로 막지 않는다. release는 확인과
    unlink 사이에 생긴 교체 inode도 지우지 않는다."""

    def test_recover_refuses_transaction_owned_by_live_installer(self, installed, tmp_path):
        _, tgt = installed
        dist2 = make_dist(tmp_path, "dist-v2", mutate=_v2_basic)
        before = tree_ex_tx(tgt)
        ready, go = tmp_path / "a.ready", tmp_path / "a.go"
        a = run_fault(tgt, {"point": "after-write", "index": 0, "action": "pause",
                            "ready": str(ready), "go": str(go)},
                      "--target", tgt, "--update", "--from-distribution", dist2, wait=False)
        try:
            deadline = time.time() + 60
            while not ready.exists() and time.time() < deadline:
                time.sleep(0.05)
            assert ready.exists()
            txid = _pending_id(tgt)
            _replace_lock(tgt)
            mid = tree(tgt)
            b = run_init(tgt, "--target", tgt, "--recover", "--transaction", txid)
            assert b.returncode == 5, b.stdout + b.stderr
            assert json.loads(b.stdout)["kind"] == "busy"
            assert tree(tgt) == mid                        # 살아 있는 A의 transaction을 건드리지 않음
            assert pi.incomplete_transactions(tgt) == [txid]
        finally:
            go.write_text("go", encoding="utf-8")
            out, err = a.communicate(timeout=120)
        assert a.returncode == 5 and json.loads(out)["kind"] == "lock-lost", out + err
        after = tree_ex_tx(tgt)
        after.pop(".harness/install.lock")
        before.pop(".harness/install.lock")
        assert after == before                             # A는 자기가 쓴 bytes만 되돌림
        assert pi.incomplete_transactions(tgt) == []

    def test_abort_before_first_write_never_leaves_blocking_transaction(self, installed, tmp_path):
        _, tgt = installed
        dist2 = make_dist(tmp_path, "dist-v2", mutate=_v2_basic)
        before = tree_ex_tx(tgt)
        r = run_fault(tgt, {"point": "before-write", "index": 0, "action": "tamper",
                            "file": str(tgt / STATE)},
                      "--target", tgt, "--update", "--from-distribution", dist2)
        assert r.returncode == 1, r.stdout + r.stderr
        assert json.loads(r.stdout)["kind"] == "error"
        assert pi.incomplete_transactions(tgt) == []       # 쓴 것이 없으니 recover 대상도 없다
        after = tree_ex_tx(tgt)
        changed = sorted(k for k in set(before) | set(after) if before.get(k) != after.get(k))
        assert changed == [STATE]                          # 외부 변경만 남고 installer는 쓰지 않음

    def test_recover_stops_when_lock_identity_lost_then_resumes(self, installed, tmp_path):
        _, tgt = installed
        dist2 = make_dist(tmp_path, "dist-v2", mutate=_v2_basic)
        before = tree_ex_tx(tgt)
        r = run_fault(tgt, {"point": "after-write", "index": 1, "action": "exit"},
                      "--target", tgt, "--update", "--from-distribution", dist2)
        assert r.returncode == 137
        txid = _pending_id(tgt)
        lock = tgt / ".harness/install.lock"
        mid = tree_ex_tx(tgt)
        mid.pop(".harness/install.lock")
        r = run_fault(tgt, {"point": "settle", "action": "replace-lock", "file": str(lock),
                            "content": "replacement\n"},
                      "--target", tgt, "--recover", "--transaction", txid)
        assert r.returncode == 5 and json.loads(r.stdout)["kind"] == "lock-lost", r.stdout + r.stderr
        now = tree_ex_tx(tgt)
        assert now.pop(".harness/install.lock")[1] == _sha(b"replacement\n")
        assert now == mid                                  # 복원을 시작하지 않음
        assert pi.incomplete_transactions(tgt) == [txid]   # 다시 recover할 수 있다
        r = run_init(tgt, "--target", tgt, "--recover", "--transaction", txid)
        assert r.returncode == 0 and json.loads(r.stdout)["outcome"] == "rolled-back", r.stdout
        after = tree_ex_tx(tgt)
        after.pop(".harness/install.lock")
        before.pop(".harness/install.lock")
        assert after == before

    def test_release_never_unlinks_replacement_appearing_during_release(self, tmp_path,
                                                                       monkeypatch):
        tgt = make_target(tmp_path)
        lk = pi.TargetLock(tgt)
        assert lk.acquire() is True                        # 이 실행이 lock(·.harness)을 만들었다
        lock = tgt / ".harness/install.lock"
        seen = {}

        def hook(point, index=None, path=None):
            if point == "lock-release" and not seen:       # 확인 직후·unlink 직전 교체
                _replace_lock(tgt, "late\n")
                seen["ino"] = os.lstat(str(lock)).st_ino

        monkeypatch.setattr(pi, "_fault_hook", hook)
        lk.release(read_only=True)
        assert seen, "release가 정리 단계에 오지 않음"
        assert lock.read_text(encoding="utf-8") == "late\n"
        assert os.lstat(str(lock)).st_ino == seen["ino"]   # 같은 inode가 제자리에
        assert sorted(p.name for p in (tgt / ".harness").iterdir()) == ["install.lock"]


FAKE_TX = "20260101T000000000000Z-deadbeef"


class TestLockBeforePreflight:
    """update의 state 존재 확인·recover의 transaction 존재 확인도 target lock을 잡은 뒤에 읽는다 —
    다른 installer가 쥐고 있으면 판단 없이 busy, 전제 실패면 이번에 만든 lock만 지워 흔적이 없다."""

    def test_update_reads_install_state_only_under_lock(self, tmp_path):
        dist = make_dist(tmp_path)
        dist2 = make_dist(tmp_path, "dist-v2", mutate=_v2_basic)
        tgt = make_target(tmp_path)
        before = tree(tgt)
        proc, go = _start_paused(dist, tmp_path, "--target", tgt, "--profile", "base", "--dry-run")
        try:
            b = run_init(dist, "--target", tgt, "--update", "--from-distribution", dist2)
            assert b.returncode == 5 and json.loads(b.stdout)["kind"] == "busy", b.stdout + b.stderr
        finally:
            rc, out, err = _finish(proc, go)
        assert rc == 0, out + err
        r = run_init(dist, "--target", tgt, "--update", "--from-distribution", dist2)
        assert r.returncode == 1 and "init" in json.loads(r.stdout)["error"], r.stdout + r.stderr
        assert tree(tgt) == before                         # lock·.harness를 만들었다면 지웠다

    def test_recover_reads_transaction_only_under_lock(self, installed, tmp_path):
        clone = _fresh_clone(installed, tmp_path)          # lock 파일 없는 설치된 clone
        before = tree(clone)
        proc, go = _start_paused(clone, tmp_path, "--target", clone, "--check")
        try:
            b = run_init(clone, "--target", clone, "--recover", "--transaction", FAKE_TX)
            assert b.returncode == 5 and json.loads(b.stdout)["kind"] == "busy", b.stdout + b.stderr
        finally:
            rc, out, err = _finish(proc, go)
        assert rc == 0, out + err
        r = run_init(clone, "--target", clone, "--recover", "--transaction", FAKE_TX)
        assert r.returncode == 1 and "transaction 없음" in r.stdout, r.stdout + r.stderr
        assert tree(clone) == before                       # 만든 lock만 지웠다


def _tamper_intent(tgt, txid, mutate):
    """intent.json을 바꾸고 prepared marker도 새 intent hash로 맞춘다(marker 대조만으로는 못 잡는 변조)."""
    d = Path(tgt) / ".harness/transactions" / txid
    intent = json.loads((d / "intent.json").read_text(encoding="utf-8"))
    mutate(intent, d)
    data = (json.dumps(intent, indent=2, sort_keys=True, ensure_ascii=False) + "\n").encode("utf-8")
    for name, content in (("intent.json", data), ("prepared", (_sha(data) + "\n").encode("ascii"))):
        f = d / name
        os.chmod(str(f), 0o644)
        f.write_bytes(content)


def _dup_action(intent, d, path_of=lambda p: p):
    a = dict(intent["actions"][1])
    a["path"] = path_of(a["path"])
    n = len(intent["actions"])
    for sub in ("old", "new"):
        if (d / sub / "1").exists():
            (d / sub / str(n)).write_bytes((d / sub / "1").read_bytes())
    intent["actions"].append(a)


def _reserved_action(intent, d):
    a = intent["actions"][0]
    a.update(path=".harness/install.lock", op="replace", oldSha=_sha(b""))
    os.chmod(str(d / "old" / "0"), 0o644)
    (d / "old" / "0").write_bytes(b"")
    intent["observed"][".harness/install.lock"] = _sha(b"")


TAMPERS = {
    "owner-ino-type": ("ownerIno", lambda i, d: i.update(ownerIno="1")),
    "extra-top-key": ("최상위", lambda i, d: i.update(extra=1)),
    "missing-top-key": ("최상위", lambda i, d: i.pop("observed")),
    "schema": ("schemaVersion", lambda i, d: i.update(schemaVersion=99)),
    "operation": ("operation", lambda i, d: i.update(operation="deploy")),
    "extra-action-key": ("action 키", lambda i, d: i["actions"][0].update(mode="0644")),
    "dup-path": ("중복", _dup_action),
    "dup-path-case": ("중복", lambda i, d: _dup_action(i, d, str.upper)),
    "reserved-path": ("예약", _reserved_action),
    "op-hash": ("op/hash", lambda i, d: i["actions"][0].update(op="create")),
    "createdirs-unrelated": ("createDirs", lambda i, d: i["createDirs"].append("user-empty")),
    "observed-type": ("observed", lambda i, d: i.update(observed=[])),
    "observed-mismatch": ("관측", lambda i, d: i["observed"].update(
        {i["actions"][0]["path"]: "0" * 64})),
}


class TestRecoveryIntentStrict:
    """recover는 intent를 엄격히 읽는다 — 최상위·action 키 정확히, schema·operation, op별 hash 유무,
    preflight 관측과 oldSha 일치, 경로 중복(대소문자 무시)·installer 예약 경로·무관한 createDirs 거부.
    prepared marker까지 맞춘 변조도 모호하면 아무것도 건드리지 않고 거부한다(fail closed)."""

    @pytest.mark.parametrize("name", sorted(TAMPERS))
    def test_tampered_intent_is_refused_without_touching_target(self, installed, tmp_path, name):
        _, tgt = installed
        dist2 = make_dist(tmp_path, "dist-v2", mutate=_v2_basic)
        r = run_fault(tgt, {"point": "after-write", "index": 1, "action": "exit"},
                      "--target", tgt, "--update", "--from-distribution", dist2)
        assert r.returncode == 137
        txid = _pending_id(tgt)
        (tgt / "user-empty").mkdir()                       # 사용자의 빈 디렉터리
        why, mutate = TAMPERS[name]
        _tamper_intent(tgt, txid, mutate)
        mid = tree(tgt)
        r = run_init(tgt, "--target", tgt, "--recover", "--transaction", txid)
        assert r.returncode == 1 and "Traceback" not in r.stderr, r.stdout + r.stderr
        out = json.loads(r.stdout)
        assert out["kind"] == "error" and why in out["error"], out
        assert tree(tgt) == mid                            # 복원·정리·marker 아무것도 없음
        assert pi.incomplete_transactions(tgt) == [txid]

    def test_untampered_init_transaction_still_recovers(self, tmp_path):
        """엄격 파싱의 회귀 guard: operation init·prevStateSha 없음·createDirs가 있는 정상 intent는 복구된다."""
        dist = make_dist(tmp_path)
        tgt = make_target(tmp_path)
        before = tree(tgt)
        r = run_fault(dist, {"point": "after-write", "index": 1, "action": "exit"},
                      "--target", tgt, "--profile", "base")
        assert r.returncode == 137
        txid = _pending_id(tgt)
        intent = json.loads((tgt / ".harness/transactions" / txid / "intent.json").read_text(
            encoding="utf-8"))
        assert intent["operation"] == "init" and intent["prevStateSha"] is None
        assert intent["createDirs"]
        r = run_init(dist, "--target", tgt, "--recover", "--transaction", txid)
        assert r.returncode == 0 and json.loads(r.stdout)["outcome"] == "rolled-back", r.stdout
        after = tree(tgt)
        assert all(after.get(k) == v for k, v in before.items())
        assert all(k.startswith(".harness") for k in set(after) - set(before))
        assert not (tgt / STATE).exists()


class TestAtomicLockOwnership:
    """lock 파일 소유는 O_CREAT|O_EXCL로 원자적으로 판정한다 — 존재 확인과 열기 사이에 경쟁자가 만든
    파일을 자기 것으로 주장해 read-only 정리에서 지우지 않는다(남의 inode는 내용·inode 그대로)."""

    def test_probe_foreign_lock_created_right_before_open_is_not_claimed(self, tmp_path,
                                                                        monkeypatch):
        tgt = make_target(tmp_path)
        lock = tgt / ".harness/install.lock"
        seen = {}

        def hook(point, index=None, path=None):
            if point == "lock-open" and not seen:
                with open(str(lock), "x") as f:
                    f.write("foreign\n")
                seen["ino"] = os.lstat(str(lock)).st_ino

        monkeypatch.setattr(pi, "_fault_hook", hook)
        lk = pi.TargetLock(tgt)
        assert lk.acquire() is True
        assert seen, "acquire가 lock-open 지점에 오지 않음"
        lk.release(read_only=True)
        assert lock.read_text(encoding="utf-8") == "foreign\n"
        assert os.lstat(str(lock)).st_ino == seen["ino"]

    @pytest.mark.parametrize("mode", ["check", "update-dry-run"])
    def test_read_only_run_keeps_foreign_lock_created_during_race(self, installed, tmp_path,
                                                                 mode):
        clone = _fresh_clone(installed, tmp_path)          # lock 파일 없는 설치된 clone
        dist2 = make_dist(tmp_path, "dist-v2", mutate=_v2_basic)
        args = (["--check"] if mode == "check"
                else ["--update", "--from-distribution", dist2, "--dry-run"])
        lock = clone / ".harness/install.lock"
        before = tree(clone)
        r = run_fault(clone, {"point": "lock-open", "action": "create", "file": str(lock),
                              "content": "foreign\n"}, "--target", clone, *args)
        assert r.returncode == 0, r.stdout + r.stderr
        after = tree(clone)
        assert after.pop(".harness/install.lock") == ("file", _sha(b"foreign\n"))   # 남의 inode 보존
        assert after == before


def _owner_lock(tgt, txid):
    return Path(tgt) / ".harness/transactions" / txid / "owner.lock"


class TestOwnerLockIdentity:
    """transaction owner.lock도 flock만으로는 경로 교체를 막지 못한다 — 소유자는 매 쓰기·commit point 전에
    owner.lock 경로 동일성을 재확인하고, intent가 owner.lock inode(ownerIno)를 기록해 recover는 기록된
    inode를 잡았을 때만 진행한다(교체면 소유자 생존을 판정할 수 없어 fail closed). 교체 inode는 보존한다."""

    def test_probe_owner_lock_replaced_after_acquire(self, tmp_path):
        d = tmp_path / "tx"
        d.mkdir()
        a = pi.OwnerLock(d)
        a.acquire(create=True)
        own = d / "owner.lock"
        own.unlink()
        own.write_text("replacement\n", encoding="utf-8")
        b = pi.OwnerLock(d)
        b.acquire(create=False)                            # 새 inode는 잡힌다 — Unix가 막지 못함
        with pytest.raises(pi.LockLost):
            a.verify()
        b.verify()
        a.release()
        b.release()
        assert own.read_text(encoding="utf-8") == "replacement\n"

    def test_live_installer_stops_when_its_owner_lock_is_replaced(self, installed, tmp_path):
        _, tgt = installed
        dist2 = make_dist(tmp_path, "dist-v2", mutate=_v2_basic)
        before = tree_ex_tx(tgt)
        r = run_fault(tgt, {"point": "before-write", "index": 0, "action": "replace-owner",
                            "target": str(tgt), "content": "replacement\n"},
                      "--target", tgt, "--update", "--from-distribution", dist2)
        assert r.returncode == 5 and json.loads(r.stdout)["kind"] == "lock-lost", r.stdout + r.stderr
        assert tree_ex_tx(tgt) == before                   # project 쓰기 없음
        assert pi.incomplete_transactions(tgt) == []
        txd = tx_dirs(tgt)[-1]                             # 가장 새 transaction(이번 update)
        assert (txd / "owner.lock").read_text(encoding="utf-8") == "replacement\n"

    def test_second_holder_recover_fails_closed_when_both_locks_replaced(self, installed,
                                                                         tmp_path):
        _, tgt = installed
        dist2 = make_dist(tmp_path, "dist-v2", mutate=_v2_basic)
        before = tree_ex_tx(tgt)
        ready, go = tmp_path / "a.ready", tmp_path / "a.go"
        a = run_fault(tgt, {"point": "after-write", "index": 0, "action": "pause",
                            "ready": str(ready), "go": str(go)},
                      "--target", tgt, "--update", "--from-distribution", dist2, wait=False)
        try:
            deadline = time.time() + 60
            while not ready.exists() and time.time() < deadline:
                time.sleep(0.05)
            assert ready.exists()
            txid = _pending_id(tgt)
            _replace_lock(tgt)
            own = _owner_lock(tgt, txid)
            own.unlink()
            own.write_text("replacement\n", encoding="utf-8")
            mid = tree(tgt)
            b = run_init(tgt, "--target", tgt, "--recover", "--transaction", txid)
            assert b.returncode == 3, b.stdout + b.stderr
            assert json.loads(b.stdout)["kind"] == "recovery-conflict"
            assert tree(tgt) == mid                        # 살아 있는 A의 transaction을 건드리지 않음
            assert pi.incomplete_transactions(tgt) == [txid]
        finally:
            go.write_text("go", encoding="utf-8")
            out, err = a.communicate(timeout=120)
        assert a.returncode == 5 and json.loads(out)["kind"] == "lock-lost", out + err
        after = tree_ex_tx(tgt)
        after.pop(".harness/install.lock")
        before.pop(".harness/install.lock")
        assert after == before                             # A는 자기 쓰기만 되돌림
        assert pi.incomplete_transactions(tgt) == []
        assert own.read_text(encoding="utf-8") == "replacement\n"

    def test_owner_lock_replaced_during_recover_stops_then_fails_closed(self, installed,
                                                                        tmp_path):
        _, tgt = installed
        dist2 = make_dist(tmp_path, "dist-v2", mutate=_v2_basic)
        r = run_fault(tgt, {"point": "after-write", "index": 1, "action": "exit"},
                      "--target", tgt, "--update", "--from-distribution", dist2)
        assert r.returncode == 137
        txid = _pending_id(tgt)
        own = _owner_lock(tgt, txid)
        rel = own.relative_to(tgt).as_posix()
        mid = tree(tgt)
        r = run_fault(tgt, {"point": "settle", "action": "replace-lock", "file": str(own),
                            "content": "replacement\n"},
                      "--target", tgt, "--recover", "--transaction", txid)
        assert r.returncode == 5 and json.loads(r.stdout)["kind"] == "lock-lost", r.stdout + r.stderr
        now = tree(tgt)
        assert now.pop(rel) == ("file", _sha(b"replacement\n"))   # 교체 inode 보존
        mid.pop(rel)
        assert now == mid                                  # 복원을 시작하지 않음
        assert pi.incomplete_transactions(tgt) == [txid]
        frozen = tree(tgt)
        r = run_init(tgt, "--target", tgt, "--recover", "--transaction", txid)
        assert r.returncode == 3 and json.loads(r.stdout)["kind"] == "recovery-conflict", r.stdout
        assert tree(tgt) == frozen                         # 기록된 inode가 아니면 진행하지 않음
        assert pi.incomplete_transactions(tgt) == [txid]


def _init_crash_with_user_empty_dir(tmp_path):
    """미설치 target에 사용자의 빈 `docs/`가 있고 init이 그 안에 `docs/PRD.md`를 만든 뒤 commit point 직전 크래시."""
    dist = make_dist(tmp_path)
    tgt = make_target(tmp_path)
    (tgt / "docs").mkdir()
    before = tree(tgt)
    r = run_fault(dist, {"point": "before-state", "action": "exit"},
                  "--target", tgt, "--profile", "base")
    assert r.returncode == 137, r.stdout + r.stderr
    return dist, tgt, before, _pending_id(tgt)


class TestRollbackDirectoryOwnership:
    """rollback의 디렉터리 정리는 이 transaction이 **만들었다는 증거**(mkdir 직후 기록한 inode marker)가 있는
    디렉터리만 지운다 — intent의 createDirs 주장만으로는 지우지 않는다(prepared hash까지 맞춘 변조 포함)."""

    def test_tampered_createdirs_cannot_remove_preexisting_empty_ancestor(self, tmp_path):
        dist, tgt, before, txid = _init_crash_with_user_empty_dir(tmp_path)
        _tamper_intent(tgt, txid, lambda i, d: i["createDirs"].append("docs"))
        r = run_init(dist, "--target", tgt, "--recover", "--transaction", txid)
        assert r.returncode == 0 and json.loads(r.stdout)["outcome"] == "rolled-back", r.stdout + r.stderr
        after = tree(tgt)
        assert after.get("docs") == ("dir", None)                   # 사용자의 빈 디렉터리 보존
        assert all(after.get(k) == v for k, v in before.items())
        assert all(k.startswith(".harness") for k in set(after) - set(before))   # 자기 디렉터리는 제거

    def test_forged_marker_with_other_inode_does_not_remove_directory(self, tmp_path):
        dist, tgt, before, txid = _init_crash_with_user_empty_dir(tmp_path)

        def forge(i, d):
            i["createDirs"].append("docs")
            (d / "dirs").mkdir(exist_ok=True)
            k = len(i["createDirs"]) - 1
            (d / "dirs" / str(k)).write_text("%d\n" % (os.lstat(str(tgt / "docs")).st_ino + 7),
                                             encoding="ascii")

        _tamper_intent(tgt, txid, forge)
        r = run_init(dist, "--target", tgt, "--recover", "--transaction", txid)
        assert r.returncode == 0 and json.loads(r.stdout)["outcome"] == "rolled-back", r.stdout + r.stderr
        after = tree(tgt)
        assert after.get("docs") == ("dir", None)
        assert all(after.get(k) == v for k, v in before.items())

    @pytest.mark.parametrize("bad", ["garbage", "unknown-index", "symlink", "directory",
                                     "leading-zero"])
    def test_malformed_dir_marker_is_refused(self, tmp_path, bad):
        dist, tgt, before, txid = _init_crash_with_user_empty_dir(tmp_path)
        dd = tgt / ".harness/transactions" / txid / "dirs"
        dd.mkdir(exist_ok=True)
        if bad == "garbage":
            (dd / "0").write_text("not-an-inode\n", encoding="ascii")
        elif bad == "unknown-index":
            (dd / "999").write_text("12345\n", encoding="ascii")
        elif bad == "directory":
            (dd / "1").unlink()
            (dd / "1").mkdir()
        elif bad == "leading-zero":
            (dd / "01").write_text("12345\n", encoding="ascii")
        else:
            if (dd / "0").exists():
                (dd / "0").unlink()
            (dd / "0").symlink_to("/etc/hosts")
        mid = tree(tgt)
        r = run_init(dist, "--target", tgt, "--recover", "--transaction", txid)
        assert r.returncode == 1 and "Traceback" not in r.stderr, r.stdout + r.stderr
        out = json.loads(r.stdout)
        assert out["kind"] == "error" and "dirs/" in out["error"], out
        assert tree(tgt) == mid
        assert pi.incomplete_transactions(tgt) == [txid]


def _update_crash_before_state(installed, tmp_path):
    """update가 모든 action을 적용한 뒤 commit point(state publish) 직전에 강제 종료된 target."""
    _, tgt = installed
    dist2 = make_dist(tmp_path, "dist-v2", mutate=_v2_basic)
    r = run_fault(tgt, {"point": "before-state", "action": "exit"},
                  "--target", tgt, "--update", "--from-distribution", dist2)
    assert r.returncode == 137, r.stdout + r.stderr
    return tgt, _pending_id(tgt)


def _drop_final_action(i, d):
    i["actions"].pop()              # 적용된 마지막 action을 intent에서 지운다 — backup 기록은 orphan으로 남는다


def _extra_backup(sub, name=None, kind="file"):
    def mutate(i, d):
        p = d / sub / (name if name is not None else str(len(i["actions"])))
        if kind == "file":
            p.write_bytes(b"orphan\n")
        elif kind == "dir":
            p.mkdir()
        else:
            p.symlink_to("/etc/hosts")
    return mutate


def _missing_backup(sub):
    def mutate(i, d):
        want = ("replace", "remove") if sub == "old" else ("create", "replace")
        k = next(n for n, a in enumerate(i["actions"]) if a["op"] in want)
        (d / sub / str(k)).unlink()
    return mutate


BACKUP_TAMPERS = {
    "drop-final-applied-action": _drop_final_action,
    "orphan-old": _extra_backup("old"),
    "orphan-new": _extra_backup("new"),
    "non-numeric": _extra_backup("old", "notes.txt"),
    "leading-zero": _extra_backup("new", "01"),
    "extra-dir": _extra_backup("old", kind="dir"),
    "extra-symlink": _extra_backup("new", kind="symlink"),
    "missing-old": _missing_backup("old"),
    "missing-new": _missing_backup("new"),
}


class TestTransactionBackupRecords:
    """old/·new/ backup 기록은 action이 요구하는 색인과 **정확히** 같아야 한다 — 여분(orphan)·누락·숫자가 아닌
    이름·앞자리 0·symlink·디렉터리 항목이 있으면 target을 건드리기 전에 거부한다(fail closed). 적용된 마지막
    action을 intent에서 지우고 prepared hash를 다시 맞춰도 남은 backup 기록으로 들킨다."""

    @pytest.mark.parametrize("name", sorted(BACKUP_TAMPERS))
    def test_backup_records_must_match_actions_exactly(self, installed, tmp_path, name):
        tgt, txid = _update_crash_before_state(installed, tmp_path)
        _tamper_intent(tgt, txid, BACKUP_TAMPERS[name])
        mid = tree(tgt)
        r = run_init(tgt, "--target", tgt, "--recover", "--transaction", txid)
        assert r.returncode == 1 and "Traceback" not in r.stderr, r.stdout + r.stderr
        out = json.loads(r.stdout)
        assert out["kind"] == "error" and "backup 기록" in out["error"], out
        assert tree(tgt) == mid                            # target·install-state·transaction 그대로
        assert pi.incomplete_transactions(tgt) == [txid]


class TestRecoveryCleanupContainment:
    """recover의 임시 파일 정리도 쓰기·복원과 같은 경로 보장을 따른다 — 정리 후보의 상위 사슬에 symlink·
    비디렉터리가 있으면 **아무것도 지우기 전에** recovery-conflict로 멈춘다(상위 symlink를 따라 target 밖
    파일을 지우지 않는다). 정상 상위의 남은 임시 파일은 그대로 정리한다."""

    def _crash(self, installed, tmp_path):
        _, tgt = installed
        dist2 = make_dist(tmp_path, "dist-v2", mutate=_v2_basic)
        before = tree_ex_tx(tgt)
        r = run_fault(tgt, {"point": "after-write", "index": 1, "action": "exit"},
                      "--target", tgt, "--update", "--from-distribution", dist2)
        assert r.returncode == 137, r.stdout + r.stderr
        return tgt, dist2, before, _pending_id(tgt)

    def test_symlinked_parent_never_lets_cleanup_unlink_outside_target(self, installed,
                                                                       tmp_path):
        tgt, dist2, _, txid = self._crash(installed, tmp_path)
        outside = tmp_path / "outside"
        outside.mkdir()
        victim = outside / (".runtime.py.harness-tmp-%s" % txid)
        victim.write_text("victim\n", encoding="utf-8")
        shutil.move(str(tgt / "scripts"), str(tmp_path / "scripts-moved"))
        os.symlink(str(outside), str(tgt / "scripts"))    # 중단 뒤 target/scripts → target 밖
        before_in, before_out = tree(tgt), tree(outside)
        r = run_init(dist2, "--target", tgt, "--recover", "--transaction", txid)
        assert r.returncode == 3 and json.loads(r.stdout)["kind"] == "recovery-conflict", \
            r.stdout + r.stderr                           # symlink 충돌로 거부된다
        assert victim.read_text(encoding="utf-8") == "victim\n"   # …그 전에 target 밖을 지우지 않는다
        assert tree(outside) == before_out
        assert tree(tgt) == before_in                     # target 안도 그대로
        assert pi.incomplete_transactions(tgt) == [txid]

    def test_normal_leftover_temp_files_are_still_cleaned(self, installed, tmp_path):
        tgt, _, before, txid = self._crash(installed, tmp_path)
        leftovers = [tgt / "scripts" / (".runtime.py.harness-tmp-%s" % txid),
                     tgt / "scripts" / (".runtime.py.harness-restore-%s" % txid),
                     tgt / ".harness" / (".install-state.json.tmp-%s" % txid)]
        for p in leftovers:
            p.write_text("partial\n", encoding="utf-8")
        r = run_init(tgt, "--target", tgt, "--recover", "--transaction", txid)
        assert r.returncode == 0 and json.loads(r.stdout)["outcome"] == "rolled-back", \
            r.stdout + r.stderr
        assert not any(os.path.lexists(str(p)) for p in leftovers)
        assert tree_ex_tx(tgt) == before
