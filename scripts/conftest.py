"""공용 fixture — 승인 가능한 최소 계획을 가진 임시 git repo + 테스트용 project policy."""
import json
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent))

DESIGN = "docs/superpowers/specs/2026-11-22-demo-design.md"
SCRIPTS_DIR = Path(__file__).resolve().parent

# 테스트용 project policy fixture. 실제 운영 ID가 아니다(짧은 가짜 숫자 ID·DEMO issue key).
# 운영 policy(.harness/policy.json)는 테스트가 읽지 않는다 — in-process는 아래 autouse
# fixture가, subprocess는 make_harness_root()가 이 값을 쓴다.
FIXTURE_APPROVER = "20001"
FIXTURE_THREAD = "10002"
FIXTURE_SCOPED_THREAD = "10081"   # DEMO-81 issue 전용 thread
FIXTURE_POLICY = {
    "schemaVersion": 1,
    "issueKeyPattern": "DEMO-[0-9]+",
    "approverUserIds": [FIXTURE_APPROVER],
    "approvalThreadIds": [FIXTURE_THREAD],
    "issueScopedThreads": {FIXTURE_SCOPED_THREAD: "DEMO-81"},
    "implBackend": "claude",
    "reviewBackend": "codex",
    "reviewModel": "gpt-6-astra",
    "pythonMinVersion": "3.10",
    "pythonRecommendedVersion": "3.14.9",
}


def write_policy(root, policy=None):
    """<root>/.harness/policy.json에 policy를 쓴다."""
    d = Path(root) / ".harness"
    d.mkdir(parents=True, exist_ok=True)
    (d / "policy.json").write_text(json.dumps(policy or FIXTURE_POLICY, indent=2),
                                   encoding="utf-8")
    return d / "policy.json"


def make_harness_root(base, policy=None, name="harness-root"):
    """subprocess 테스트용 하네스 설치 root: scripts 복사본 + .venv symlink + fixture policy.

    운영 경로와 같이 `<root>/.venv/bin/python <root>/scripts/...`로 띄우면 그 root의
    `.harness/policy.json`만 읽는다(테스트가 실제 운영 policy에 의존하지 않게)."""
    root = Path(base) / name
    (root / "scripts").mkdir(parents=True)
    for p in SCRIPTS_DIR.glob("*.py"):
        shutil.copy2(str(p), str(root / "scripts" / p.name))
    (root / ".venv").symlink_to(SCRIPTS_DIR.parent / ".venv")
    write_policy(root, policy)
    return root


@pytest.fixture(autouse=True)
def _fixture_policy(monkeypatch):
    """in-process 테스트는 하네스 root의 실제 policy·policy.local 대신 fixture를 쓴다."""
    import runtime
    pol = runtime.parse_policy(json.dumps(FIXTURE_POLICY).encode("utf-8"))
    monkeypatch.setattr(runtime, "policy", lambda: pol)
    monkeypatch.setattr(runtime, "local_policy", lambda: {})
    return pol


def git(repo, *args, check=True):
    r = subprocess.run(["git", *args], cwd=str(repo), capture_output=True, text=True,
                       encoding="utf-8")
    if check and r.returncode != 0:
        raise AssertionError(f"git {args} failed: {r.stderr}")
    return r.stdout.strip()


def make_plan(root, task="demo", steps=2, **index_extra):
    """docs/phases 계획 파일을 쓴다(커밋하지 않음)."""
    root = Path(root)
    (root / "docs/superpowers/specs").mkdir(parents=True, exist_ok=True)
    (root / DESIGN).write_text("# Demo design\n\n한글 설계 본문\n", encoding="utf-8")
    d = root / "phases" / task
    d.mkdir(parents=True, exist_ok=True)
    index = {
        "project": "Demo", "phase": task, "baseBranch": "main",
        "designDoc": DESIGN,
        "allowedPaths": ["src/", "tests/"],
        "testCommand": ["python3", "-c", "print('tests ok')"],
        "steps": [{"step": i, "name": f"part-{i}", "status": "pending"} for i in range(steps)],
    }
    index.update(index_extra)
    (d / "index.json").write_text(json.dumps(index, indent=2, ensure_ascii=False),
                                  encoding="utf-8")
    for i in range(steps):
        (d / f"step{i}.md").write_text(f"# Step {i}\n\n작업 {i}\n", encoding="utf-8")
    return d


@pytest.fixture
def plan_repo(tmp_path):
    """main에 초기 커밋, feature 브랜치에 계획 커밋이 있는 repo."""
    repo = tmp_path / "repo"
    repo.mkdir()
    git(repo, "init", "-q", "-b", "main")
    git(repo, "config", "user.email", "t@example.com")
    git(repo, "config", "user.name", "T")
    git(repo, "config", "commit.gpgsign", "false")
    (repo / "README.md").write_text("x\n", encoding="utf-8")
    (repo / ".gitignore").write_text(".harness/\n", encoding="utf-8")
    git(repo, "add", "-A")
    git(repo, "commit", "-q", "-m", "init")
    git(repo, "checkout", "-q", "-b", "feat/DEMO-74/demo")
    make_plan(repo)
    git(repo, "add", "-A")
    git(repo, "commit", "-q", "-m", "docs: plan")
    return repo
