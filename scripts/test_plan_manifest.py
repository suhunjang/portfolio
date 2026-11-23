"""단일 canonical plan manifest 계약 (plan review·approval·execute 공용)."""
import json
import os
import stat
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent))
import plan_manifest as pm  # noqa: E402
from conftest import DESIGN, make_plan  # noqa: E402


@pytest.fixture
def root(tmp_path):
    make_plan(tmp_path)
    return tmp_path


def _index(root, task="demo"):
    return root / "phases" / task / "index.json"


def _edit_index(root, fn, task="demo"):
    p = _index(root, task)
    data = json.loads(p.read_text(encoding="utf-8"))
    fn(data)
    p.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


class TestHashStability:
    def test_same_input_same_hash(self, root):
        assert pm.build_manifest(root, "demo").sha == pm.build_manifest(root, "demo").sha

    def test_hash_is_sha256_hex(self, root):
        sha = pm.build_manifest(root, "demo").sha
        assert len(sha) == 64 and int(sha, 16) >= 0

    def test_mutable_execution_fields_excluded(self, root):
        before = pm.build_manifest(root, "demo").sha

        def mutate(d):
            d["status"] = "needs-review"
            d["created_at"] = "2026-11-22T00:00:00+0900"
            d["reviewBaseSha"] = "a" * 40
            d["steps"][0].update(status="completed", summary="done",
                                 started_at="t", completed_at="t")
            d["steps"][1].update(status="error", error_message="boom", failed_at="t")
        _edit_index(root, mutate)
        assert pm.build_manifest(root, "demo").sha == before

    def test_json_formatting_does_not_change_hash(self, root):
        before = pm.build_manifest(root, "demo").sha
        data = json.loads(_index(root).read_text(encoding="utf-8"))
        _index(root).write_text(json.dumps(data), encoding="utf-8")
        assert pm.build_manifest(root, "demo").sha == before

    @pytest.mark.parametrize("field,value", [
        ("project", "Other"), ("phase", "other"), ("baseBranch", "develop"),
        ("reviewExclude", [{"glob": "x/*", "reason": "r"}]),
        ("allowedPaths", ["src/", "tests/", "lib/"]),
        ("testCommand", ["true"]),
    ])
    def test_immutable_field_change_changes_hash(self, root, field, value):
        before = pm.build_manifest(root, "demo").sha
        _edit_index(root, lambda d: d.__setitem__(field, value))
        assert pm.build_manifest(root, "demo").sha != before

    def test_step_name_change_changes_hash(self, root):
        before = pm.build_manifest(root, "demo").sha
        _edit_index(root, lambda d: d["steps"][0].__setitem__("name", "renamed"))
        assert pm.build_manifest(root, "demo").sha != before

    def test_one_byte_step_change_changes_hash(self, root):
        before = pm.build_manifest(root, "demo").sha
        p = root / "phases/demo/step1.md"
        p.write_bytes(p.read_bytes() + b" ")
        assert pm.build_manifest(root, "demo").sha != before

    def test_design_doc_change_changes_hash(self, root):
        before = pm.build_manifest(root, "demo").sha
        (root / DESIGN).write_text("changed", encoding="utf-8")
        assert pm.build_manifest(root, "demo").sha != before

    def test_manifest_contains_design_and_steps_sorted(self, root):
        m = pm.build_manifest(root, "demo")
        paths = [f["path"] for f in m.manifest["files"]]
        assert paths == sorted(paths)
        assert DESIGN in paths and "phases/demo/step0.md" in paths


class TestRejects:
    def _raises(self, root, task="demo"):
        with pytest.raises(pm.ManifestError):
            pm.build_manifest(root, task)

    def test_missing_step_file(self, root):
        (root / "phases/demo/step1.md").unlink()
        self._raises(root)

    def test_extra_step_file(self, root):
        (root / "phases/demo/step2.md").write_text("x", encoding="utf-8")
        self._raises(root)

    def test_duplicate_numbered_alias(self, root):
        (root / "phases/demo/step01.md").write_text("x", encoding="utf-8")
        self._raises(root)

    def test_non_consecutive_numbers(self, root):
        _edit_index(root, lambda d: d["steps"][1].__setitem__("step", 2))
        self._raises(root)

    def test_symlink_step(self, root):
        p = root / "phases/demo/step1.md"
        target = root / "elsewhere.md"
        target.write_text("# Step 1\n", encoding="utf-8")
        p.unlink()
        p.symlink_to(target)
        self._raises(root)

    def test_symlink_design(self, root):
        p = root / DESIGN
        target = root / "other.md"
        target.write_bytes(p.read_bytes())
        p.unlink()
        p.symlink_to(target)
        self._raises(root)

    def test_hardlink_step(self, root):
        os.link(root / "phases/demo/step0.md", root / "hard.md")
        self._raises(root)

    def test_symlinked_parent_dir(self, root, tmp_path_factory):
        real = tmp_path_factory.mktemp("real")
        task_dir = root / "phases/demo"
        for p in task_dir.iterdir():
            (real / p.name).write_bytes(p.read_bytes())
        for p in list(task_dir.iterdir()):
            p.unlink()
        task_dir.rmdir()
        task_dir.symlink_to(real, target_is_directory=True)
        self._raises(root)

    def test_index_symlink(self, root):
        p = _index(root)
        target = root / "idx.json"
        target.write_bytes(p.read_bytes())
        p.unlink()
        p.symlink_to(target)
        self._raises(root)

    @pytest.mark.parametrize("field", ["project", "phase", "baseBranch", "designDoc",
                                       "allowedPaths", "testCommand"])
    def test_missing_required_field(self, root, field):
        _edit_index(root, lambda d: d.pop(field))
        self._raises(root)

    def test_unknown_top_field(self, root):
        _edit_index(root, lambda d: d.__setitem__("sneaky", 1))
        self._raises(root)

    def test_unknown_step_field(self, root):
        _edit_index(root, lambda d: d["steps"][0].__setitem__("prompt", "override"))
        self._raises(root)

    def test_bad_status(self, root):
        _edit_index(root, lambda d: d["steps"][0].__setitem__("status", "skipped"))
        self._raises(root)

    def test_design_outside_specs(self, root):
        _edit_index(root, lambda d: d.__setitem__("designDoc", "README.md"))
        self._raises(root)

    @pytest.mark.parametrize("bad", [["phases/"], ["scripts/"], [".git/"], [".claude/"],
                                     [".codex/"], ["CLAUDE.md"], ["../x/"], ["/abs/"],
                                     ["docs/superpowers/specs/"], [".harness/"], ["."],
                                     [], ["src/../phases/"]])
    def test_allowed_paths_cannot_cover_protected(self, root, bad):
        _edit_index(root, lambda d: d.__setitem__("allowedPaths", bad))
        self._raises(root)

    @pytest.mark.parametrize("task", ["..", ".", "a/b", "", "../demo"])
    def test_bad_task_names(self, root, task):
        self._raises(root, task)

    def test_empty_steps(self, root):
        _edit_index(root, lambda d: d.__setitem__("steps", []))
        for i in range(2):
            (root / f"phases/demo/step{i}.md").unlink()
        self._raises(root)

    def test_bad_review_base_sha_type(self, root):
        _edit_index(root, lambda d: d.__setitem__("reviewBaseSha", "main"))
        self._raises(root)


class TestSnapshot:
    def test_snapshot_round_trip(self, root, tmp_path_factory):
        dest = tmp_path_factory.mktemp("ev") / "snap"
        m = pm.build_manifest(root, "demo")
        pm.write_snapshot(m, dest)
        snap = pm.load_snapshot(dest, m.sha)
        assert snap.read("phases/demo/step0.md") == (root / "phases/demo/step0.md").read_bytes()
        assert snap.sha == m.sha

    def test_snapshot_is_read_only(self, root, tmp_path_factory):
        dest = tmp_path_factory.mktemp("ev") / "snap"
        m = pm.build_manifest(root, "demo")
        pm.write_snapshot(m, dest)
        for p in dest.rglob("*"):
            assert not (p.stat().st_mode & 0o222), p

    def test_snapshot_tamper_detected(self, root, tmp_path_factory):
        dest = tmp_path_factory.mktemp("ev") / "snap"
        m = pm.build_manifest(root, "demo")
        pm.write_snapshot(m, dest)
        f = dest / "files" / "phases/demo/step0.md"
        f.chmod(0o644)
        f.write_text("tampered", encoding="utf-8")
        with pytest.raises(pm.ManifestError):
            pm.load_snapshot(dest, m.sha)

    def test_snapshot_wrong_sha(self, root, tmp_path_factory):
        dest = tmp_path_factory.mktemp("ev") / "snap"
        m = pm.build_manifest(root, "demo")
        pm.write_snapshot(m, dest)
        with pytest.raises(pm.ManifestError):
            pm.load_snapshot(dest, "0" * 64)

    def test_snapshot_ignores_later_worktree_change(self, root, tmp_path_factory):
        """승인 후 worktree 계획을 바꿨다가 복원해도 snapshot 내용은 그대로."""
        dest = tmp_path_factory.mktemp("ev") / "snap"
        m = pm.build_manifest(root, "demo")
        pm.write_snapshot(m, dest)
        (root / "phases/demo/step0.md").write_text("evil", encoding="utf-8")
        snap = pm.load_snapshot(dest, m.sha)
        assert b"evil" not in snap.read("phases/demo/step0.md")

    def test_existing_different_snapshot_rejected(self, root, tmp_path_factory):
        dest = tmp_path_factory.mktemp("ev") / "snap"
        pm.write_snapshot(pm.build_manifest(root, "demo"), dest)
        (root / "phases/demo/step0.md").write_text("v2", encoding="utf-8")
        with pytest.raises(pm.ManifestError):
            pm.write_snapshot(pm.build_manifest(root, "demo"), dest)


class TestVerifyAndCodeSha:
    def test_verify_matches(self, root):
        sha = pm.build_manifest(root, "demo").sha
        pm.verify_matches(root, "demo", sha)
        (root / "phases/demo/step0.md").write_text("drift", encoding="utf-8")
        with pytest.raises(pm.ManifestError):
            pm.verify_matches(root, "demo", sha)

    def test_code_sha_is_file_hash(self):
        import hashlib
        src = Path(pm.__file__).read_bytes()
        assert pm.code_sha() == hashlib.sha256(src).hexdigest()

    def test_allowed_path_predicate(self):
        allowed = ["src/", "tests/", "README.md"]
        assert pm.path_allowed("src/a/b.py", allowed)
        assert pm.path_allowed("README.md", allowed)
        assert not pm.path_allowed("README.md.bak", allowed)
        assert not pm.path_allowed("srcx/a.py", allowed)
        assert not pm.path_allowed("phases/demo/step0.md", allowed)


class TestLegacyRegressions:
    """구 review_plan 무결성 시험(_validate_task·IndexFileMatch)을 manifest 계약으로 옮긴 것."""

    def test_missing_phase_rejected(self, root):
        with pytest.raises(pm.ManifestError):
            pm.build_manifest(root, "9-nope")

    def test_phases_root_index_rejected(self, root):
        (root / "phases" / "index.json").write_text('{"phases": []}', encoding="utf-8")
        with pytest.raises(pm.ManifestError):
            pm.build_manifest(root, ".")

    def test_two_digit_step_files_ok(self, tmp_path):
        """숫자로 비교한다 — 문자열 정렬이면 step10이 step2 앞에 선다."""
        make_plan(tmp_path, steps=11)
        m = pm.build_manifest(tmp_path, "demo")
        assert "phases/demo/step10.md" in m.files
        assert [s["step"] for s in m.index["steps"]] == list(range(11))
