"""배포 계약 — manifest 소유권 분류·템플릿·배포 파일(런타임·테스트)의 프로젝트·호스트 중립성.

target 프로젝트에도 배포되는 회귀 테스트다. target에서는 **설치된** manifest·템플릿으로 같은
계약을 검증한다(source checkout·원본 저장소·git 이력에 의존하지 않는다).
"""
import json
import re
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent))
import project_init as pi  # noqa: E402
import runtime  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
MANIFEST = ROOT / "harness-manifest.json"
PROFILES = ("base", "ui")


def _manifest():
    return pi.load_manifest(MANIFEST.read_bytes())


def _entry(path, ownership="managed", **kw):
    e = {"path": path, "ownership": ownership}
    e.update(kw)
    return e


def _mk(entries, **over):
    """최소 유효 manifest + 변형. 로더 거부 규칙 단위 테스트용."""
    base_entries = [
        _entry("harness-manifest.json"),
        _entry("scripts/project_init.py"),
        _entry("templates/project/docs/PRD.md"),
        _entry("docs/PRD.md", "seed", source="templates/project/docs/PRD.md", profiles=["base"]),
    ]
    m = {"schemaVersion": 1, "distribution": {"name": "demo-harness", "version": "1.0.0"},
         "profiles": ["base"], "entries": base_entries + list(entries), "sourceOnly": []}
    m.update(over)
    return json.dumps(m).encode("utf-8")


class TestManifestLoaderRejects:
    """manifest 형식 오류는 설치 전 전부 거부한다(fail closed)."""

    def test_minimal_manifest_loads(self):
        m = pi.load_manifest(_mk([]))
        assert m.version == "1.0.0" and m.profiles == ("base",)

    @pytest.mark.parametrize("entries", [
        [_entry("scripts/project_init.py")],                         # 경로 중복
        [_entry("Scripts/Project_Init.py")],                         # 대소문자만 다른 중복
        [_entry(".git/config")],                                     # .git 내부
        [_entry("sub/.GIT/hooks/pre-commit")],
        [_entry("/etc/passwd")],                                     # 절대경로
        [_entry("scripts/../x.py")],                                 # ..
        [_entry("scripts\\x.py")],                                   # backslash
        [_entry("scripts//x.py")],
        [_entry("x.py", "owned-by-me")],                             # 알 수 없는 ownership
        [_entry("CLAUDE.md", "merge-required",
                source="templates/project/docs/PRD.md")],            # validator·rv 없음
        [_entry("docs/X.md", "seed", source="templates/missing.md")],  # source가 managed 아님
        [_entry(".harness/install-state.json")],                     # installer 예약 경로
        [_entry(".harness/transactions/x")],
        [_entry("x.py", profiles=["ui"])],                           # 선언 안 된 profile
        [_entry("x.py", source="y.py")],                             # managed는 source 없음
    ])
    def test_invalid_entries_rejected(self, entries):
        with pytest.raises(pi.InstallError):
            pi.load_manifest(_mk(entries))

    def test_duplicate_json_key_rejected(self):
        data = _mk([]).replace(b'"schemaVersion": 1', b'"schemaVersion": 1, "schemaVersion": 1')
        with pytest.raises(pi.InstallError):
            pi.load_manifest(data)

    def test_managed_must_be_in_every_profile(self):
        """profile 확장은 설치된 파일만 쓴다 — managed는 모든 profile에 있어야 한다."""
        with pytest.raises(pi.InstallError):
            pi.load_manifest(_mk([_entry("x.py", profiles=["base"])], profiles=["base", "ui"]))

    def test_source_only_must_not_overlap_managed(self):
        with pytest.raises(pi.InstallError):
            pi.load_manifest(_mk([], sourceOnly=["scripts/project_init.py"]))

    def test_unknown_validator_kind_rejected(self):
        e = _entry("CLAUDE.md", "merge-required", source="templates/project/docs/PRD.md",
                   requirementsVersion=1, validators=[{"kind": "eval", "code": "1"}])
        with pytest.raises(pi.InstallError):
            pi.load_manifest(_mk([e]))


class TestDistributionManifest:
    def test_manifest_is_valid(self):
        m = _manifest()
        assert m.profiles == PROFILES
        assert m.name and re.fullmatch(r"[0-9]+\.[0-9]+\.[0-9]+", m.version)

    def test_every_entry_source_present_as_regular_file(self):
        for e in _manifest().entries:
            p = ROOT / e.source
            assert p.is_file() and not p.is_symlink(), e.source

    def test_installer_is_self_contained(self):
        """target이 설치된 manifest·템플릿·installer만으로 check·profile 확장·recover를 한다."""
        managed = {e.path for e in _manifest().entries if e.ownership == "managed"}
        need = {"harness-manifest.json", "scripts/project_init.py", "scripts/harness.py",
                "scripts/runtime.py", "scripts/bootstrap_venv.py"}
        assert need <= managed
        for e in _manifest().entries:
            if e.ownership != "managed":
                assert e.source in managed and e.source.startswith("templates/project/")

    def test_plan_ownership_classes(self):
        by = {}
        for e in _manifest().entries:
            by.setdefault(e.ownership, set()).add(e.path)
        assert by["seed"] == {"docs/PRD.md", "docs/UI_GUIDE.md", "phases/index.json",
                              ".harness/policy.json"}
        assert by["merge-required"] == {".claude/settings.json", "CLAUDE.md", ".gitignore"}
        assert {".claude/commands/harness.md", ".claude/commands/review.md",
                ".claude/skills/cross-review/SKILL.md", ".codex/hooks.json", ".gitattributes",
                "pytest.ini", ".python-version", "scripts/hooks/block-dangerous.sh",
                "scripts/hooks/cross-review-nudge.sh", "scripts/hooks/tdd-guard.sh",
                "scripts/hooks/test_hooks.py"} <= by["managed"]

    def test_business_and_history_assets_absent(self):
        text = MANIFEST.read_text(encoding="utf-8")
        # 금지어는 조합해 만든다 — 배포되는 이 테스트 자신이 원본 업무 자산 이름을 싣지 않게.
        biz = "b" + "bg"
        for s in ("plugins/%s-package-register" % biz, "%s-hospital-tools" % biz, ".claude-plugin",
                  "docs/superpowers/plans", "docs/superpowers/specs/2026-07"):
            assert s not in text, s


class TestProfiles:
    def test_base_selects_prd_only(self):
        seeds = {e.path for e in pi.select_entries(_manifest(), "base") if e.ownership == "seed"}
        assert "docs/PRD.md" in seeds and "docs/UI_GUIDE.md" not in seeds

    def test_ui_adds_ui_guide(self):
        seeds = {e.path for e in pi.select_entries(_manifest(), "ui") if e.ownership == "seed"}
        assert {"docs/PRD.md", "docs/UI_GUIDE.md"} <= seeds

    def test_unknown_profile_rejected(self):
        with pytest.raises(pi.InstallError):
            pi.select_entries(_manifest(), "mobile")


class TestTemplates:
    def _t(self, rel):
        return (ROOT / "templates/project" / rel).read_text(encoding="utf-8")

    def test_prd_sections_and_placeholders(self):
        t = self._t("docs/PRD.md")
        for s in ("# PRD: {프로젝트명}", "## 목표", "## 사용자", "## 핵심 기능", "## MVP 제외 사항",
                  "## 디자인"):
            assert s in t
        assert len(re.findall(r"\{[^{}\n]+\}", t)) >= 8

    def test_ui_guide_sections_and_placeholders(self):
        t = self._t("docs/UI_GUIDE.md")
        for s in ("## 프로젝트 원칙", "## 보편 원칙 (7가지)", "### 5. 접근성 (Accessibility)",
                  "## AI 슬롭 안티패턴", "## 색상", "## 컴포넌트", "## 레이아웃", "## 타이포그래피"):
            assert s in t
        assert "{원칙 1" in t and "4.5:1" in t

    def test_policy_template_is_valid_and_unfilled(self):
        pol = runtime.parse_policy((ROOT / "templates/project/.harness/policy.json").read_bytes())
        assert pol.approver_user_ids == () and pol.approval_thread_ids == ()
        assert pol.issue_scoped_threads == {}
        assert (pol.impl_backend, pol.review_backend) == ("claude", "codex")

    def test_phases_index_template(self):
        assert json.loads(self._t("phases/index.json")) == {"phases": []}

    def test_merge_templates_satisfy_own_validators(self):
        for e in _manifest().entries:
            if e.ownership == "merge-required":
                assert pi.validate_merge_file(e, (ROOT / e.source).read_bytes()) == [], e.path

    @pytest.mark.parametrize("path,mutate", [
        ("CLAUDE.md", lambda b: b.replace(b"<!-- harness:end -->", b"")),
        (".gitignore", lambda b: b.replace(b"/.harness/transactions/\n", b"")),
        (".claude/settings.json", lambda b: b.replace(b"block-dangerous.sh", b"noop.sh")),
        (".claude/settings.json", lambda b: b.replace(b'"Bash(git push:*)",', b"")),
        (".claude/settings.json", lambda b: b + b"{"),
    ])
    def test_validators_reject_missing_requirements(self, path, mutate):
        e = {x.path: x for x in _manifest().entries}[path]
        assert pi.validate_merge_file(e, mutate((ROOT / e.source).read_bytes())) != []


# --- 배포 런타임·템플릿에 프로젝트 전용 값·호스트 경로가 없는가 --------------------------------

def _j(*parts):
    """금지 패턴은 조각을 이어 만든다 — 배포되는 이 테스트 자신이 금지 값을 싣지 않게."""
    return "".join(parts)


# 배포되는 모든 파일(managed: 런타임·hook·command·템플릿·manifest·회귀 테스트·conftest)에 없어야 하는 값.
# 특정 운영 조직의 값·이름은 source-only(docs/examples·감사/문서 테스트)에만 둔다.
FORBIDDEN = [
    (re.compile(_j("(?i)h", "oo-?[0-9]+")), "HOO 식별자(issue key·식별자 이름 포함)"),
    (re.compile(r"(?<![0-9])[0-9]{17,20}(?![0-9])"), "Discord 크기 ID(17~20자리)"),
    (re.compile(_j("/", "Users/|/", "Volumes/|/home/[a-z]")), "호스트 절대경로"),
    (re.compile(_j(r"\.", "hermes|hoon", "labs/", "work")), "호스트 전용 경로·source checkout"),
    (re.compile(_j("harness_fram", "work|tri", "up")), "원본 저장소·업무 경로"),
    (re.compile(_j("(?i)b", "bg")), "원본 업무 자산"),
    (re.compile(_j("(?i)hoon", r"[\s_.-]*", "labs")), "운영 조직 브랜딩(대소문자 무시)"),
]
RUNTIME_FORBIDDEN = FORBIDDEN


def _managed_paths():
    return [e.path for e in _manifest().entries if e.ownership == "managed"]


def _distributed_runtime_files():
    """managed 중 테스트가 아닌 배포 런타임 + 템플릿(설치되는 모든 bytes의 원본)."""
    out = []
    for rel in _managed_paths():
        name = Path(rel).name
        if name.startswith("test_") or name == "conftest.py":
            continue
        out.append(rel)
    return out


def _scan(paths, patterns):
    hits = []
    for rel in paths:
        text = (ROOT / rel).read_text(encoding="utf-8", errors="replace")
        for rx, what in patterns:
            for m in rx.finditer(text):
                hits.append("%s:%d: %s %r" % (rel, text.count("\n", 0, m.start()) + 1, what,
                                              m.group(0)))
    return hits


def test_distributed_runtime_has_no_project_ids_or_host_paths():
    assert _scan(_distributed_runtime_files(), RUNTIME_FORBIDDEN) == []


def test_distributed_tests_carry_no_real_operator_ids():
    """배포되는 회귀 테스트·fixture도 실제 운영 Discord ID·호스트 경로를 싣지 않는다."""
    real_ids = re.compile(r"(?<![0-9])1[0-9]{17,19}(?![0-9])")
    host_values = (_j("/", "Users/", "hoon"), _j("/", "Volumes/", "P9"), _j(".", "hermes/"))
    hits = []
    for rel in _managed_paths():
        text = (ROOT / rel).read_text(encoding="utf-8", errors="replace")
        for m in real_ids.finditer(text):
            hits.append("%s: %s" % (rel, m.group(0)))
        for s in host_values:
            if s in text:
                hits.append("%s: %s" % (rel, s))
    assert hits == []


def test_all_managed_files_are_project_and_host_neutral():
    """manifest가 target에 설치하는 **모든** 파일(테스트·conftest 포함)은 HOO 식별자·Discord 크기 ID·
    호스트 절대경로·source checkout·원본 저장소·원본 업무 자산 값이 없는 중립 bytes여야 한다."""
    assert _scan(_managed_paths(), FORBIDDEN) == []
