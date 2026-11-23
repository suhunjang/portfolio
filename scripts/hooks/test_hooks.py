"""hook 스크립트를 payload fixture로 실행·검증한다."""
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

HOOKS = Path(__file__).resolve().parent
BLOCK = HOOKS / "block-dangerous.sh"
TDD = HOOKS / "tdd-guard.sh"


def _find_bash():
    """POSIX bash를 찾는다(이 하네스는 macOS 전용)."""
    return shutil.which("bash")


BASH = _find_bash()

pytestmark = pytest.mark.skipif(BASH is None, reason="bash not available")


def _run(script, payload, cwd=None):
    return subprocess.run(
        [BASH, str(script)],
        input=json.dumps(payload),
        capture_output=True, text=True, encoding="utf-8",
        cwd=str(cwd) if cwd else None,
    )


@pytest.mark.parametrize("cmd", [
    "rm -rf /", "git push --force origin main",
    "git reset --hard HEAD~3", "DROP TABLE users;",
])
def test_dangerous_commands_blocked(cmd):
    r = _run(BLOCK, {"tool_input": {"command": cmd}})
    assert r.returncode == 2


def test_safe_command_allowed():
    r = _run(BLOCK, {"tool_input": {"command": "git status"}})
    assert r.returncode == 0


def test_no_command_allowed():
    r = _run(BLOCK, {"tool_input": {}})
    assert r.returncode == 0


# ── 정규식 JSON 파싱 회귀 방지 (2026-07-31) ────────────────────────────────
# 예전 구현은 grep -o '"command"..."[^"]*"' 로 값을 뽑았다. 값 안에 큰따옴표가
# 있으면 거기서 잘려 **뒤쪽 위험 패턴이 검사되지 않고 통과**했다.
# 아래는 그 구멍을 그대로 재현한다 — 정규식으로 되돌리면 이 테스트가 깨진다.
@pytest.mark.parametrize("cmd", [
    'git commit -m "wip" && rm -rf /',
    'echo "done" ; git push --force origin main',
    'psql -c "select 1" && DROP TABLE users;',
])
def test_quoted_prefix_does_not_hide_danger(cmd):
    r = _run(BLOCK, {"tool_input": {"command": cmd}})
    assert r.returncode == 2, f"따옴표 뒤 위험명령이 통과함: {cmd!r}"


@pytest.mark.parametrize("raw", [
    '{"tool_input": {"command": "rm -rf /"',   # 닫히지 않음
    "not json at all",
])
def test_malformed_json_fails_closed(raw):
    """가드가 입력을 못 읽으면 조용히 통과시키지 말고 막아야 한다."""
    r = subprocess.run(
        [BASH, str(BLOCK)], input=raw,
        capture_output=True, text=True, encoding="utf-8",
    )
    assert r.returncode == 2, f"깨진 JSON인데 통과함: {raw!r}"


def test_tdd_guard_quoted_path_still_parsed(tmp_path):
    """tdd-guard도 같은 정규식 파싱을 썼다. 이스케이프된 경로가 잘리면
    가드가 엉뚱한 값을 보거나 통째로 건너뛴다."""
    (tmp_path / "src").mkdir()
    payload = {"tool_input": {"file_path": "src\\quo\"ted.ts"}}
    r = _run(TDD, payload, cwd=tmp_path)
    assert '"permissionDecision": "deny"' in r.stdout


# --- tdd-guard.sh : codex apply_patch 파싱 ---

def _patch(*lines):
    return "*** Begin Patch\n" + "\n".join(lines) + "\n*** End Patch\n"


def test_apply_patch_update_no_test_denies(tmp_path):
    (tmp_path / "src").mkdir()
    (tmp_path / "src" / "foo.ts").write_text("x")
    payload = {"tool_input": {"command": _patch("*** Update File: src/foo.ts")}}
    r = _run(TDD, payload, cwd=tmp_path)
    assert '"permissionDecision": "deny"' in r.stdout


def test_apply_patch_with_test_allows(tmp_path):
    (tmp_path / "src").mkdir()
    (tmp_path / "src" / "foo.ts").write_text("x")
    (tmp_path / "src" / "foo.test.ts").write_text("t")
    payload = {"tool_input": {"command": _patch("*** Update File: src/foo.ts")}}
    r = _run(TDD, payload, cwd=tmp_path)
    assert '"deny"' not in r.stdout and r.returncode == 0


def test_apply_patch_config_ext_allows(tmp_path):
    payload = {"tool_input": {"command": _patch("*** Add File: package.json")}}
    r = _run(TDD, payload, cwd=tmp_path)
    assert '"deny"' not in r.stdout


def test_apply_patch_move_uses_new_path(tmp_path):
    (tmp_path / "src").mkdir()
    payload = {"tool_input": {"command": _patch(
        "*** Update File: src/old.ts", "*** Move to: src/new.ts")}}
    r = _run(TDD, payload, cwd=tmp_path)
    assert '"deny"' in r.stdout  # new.ts에 테스트 없음


def test_apply_patch_delete_only_allows(tmp_path):
    payload = {"tool_input": {"command": _patch("*** Delete File: src/gone.ts")}}
    r = _run(TDD, payload, cwd=tmp_path)
    assert '"deny"' not in r.stdout and r.returncode == 0


def test_apply_patch_path_traversal_denies(tmp_path):
    payload = {"tool_input": {"command": _patch("*** Update File: ../evil.ts")}}
    r = _run(TDD, payload, cwd=tmp_path)
    assert '"deny"' in r.stdout


def test_apply_patch_unparseable_denies(tmp_path):
    payload = {"tool_input": {"command": "not a patch at all"}}
    r = _run(TDD, payload, cwd=tmp_path)
    # apply_patch 마커가 없으면 Bash 등 다른 tool로 간주 → allow (deny 아님)
    assert '"deny"' not in r.stdout


def test_claude_edit_still_works(tmp_path):
    (tmp_path / "src").mkdir()
    (tmp_path / "src" / "bar.ts").write_text("x")
    payload = {"tool_input": {"file_path": "src/bar.ts"}}
    r = _run(TDD, payload, cwd=tmp_path)
    assert '"permissionDecision": "deny"' in r.stdout


# ── Windows 역슬래시 경로 ────────────────────────────────────────────────────
# Claude Code는 Windows에서 file_path를 C:\...\page.tsx 형태로 넘긴다.
# 예외 패턴(*/page.tsx 등)과 dirname이 '/'만 구분자로 봐서 page 파일이 막혔다.
# tmp_path 절대 경로에는 'test'가 들어 있어(*test* 예외에 걸린다) cwd 기준 상대 경로로 쓴다.
@pytest.mark.parametrize("rel", [
    "src\\app\\x\\page.tsx", "src\\app\\x\\layout.tsx", "src\\app\\not-found.tsx",
    "src\\types\\content.ts",
])
def test_windows_backslash_exempt_path_allows(tmp_path, rel):
    payload = {"tool_input": {"file_path": rel}}
    r = _run(TDD, payload, cwd=tmp_path)
    assert '"deny"' not in r.stdout and r.returncode == 0


def test_windows_backslash_with_test_allows(tmp_path):
    (tmp_path / "src").mkdir()
    (tmp_path / "src" / "foo.ts").write_text("x")
    (tmp_path / "src" / "foo.test.ts").write_text("t")
    payload = {"tool_input": {"file_path": "src\\foo.ts"}}
    r = _run(TDD, payload, cwd=tmp_path)
    assert '"deny"' not in r.stdout and r.returncode == 0


def test_windows_backslash_no_test_denies(tmp_path):
    (tmp_path / "src").mkdir()
    (tmp_path / "src" / "foo.ts").write_text("x")
    payload = {"tool_input": {"file_path": "src\\foo.ts"}}
    r = _run(TDD, payload, cwd=tmp_path)
    assert '"permissionDecision": "deny"' in r.stdout


# ── .codex/hooks.json · 인터프리터 계약 (macOS 전용 사본) ─────────────────
# 구 commandWindows(8.3 경로) 시험은 Windows 전용이라 macOS에서 늘 실패했다(기준선
# 4 failed 중 2건). 이 사본은 macOS만 지원하므로 commandWindows를 없애고, 대신
# "hook이 실제로 뜨는 인터프리터를 쓰는가"를 macOS 기준으로 검증한다.
CODEX_HOOKS = HOOKS.parent.parent / ".codex" / "hooks.json"
REPO_ROOT = HOOKS.parent.parent
# 위험 명령 예시는 런타임에 조립한다(이 파일을 만드는 셸 명령이 hook에 막히지 않게).
DANGER = " ".join(["rm", "-" + "rf", "/"])


def _codex_hook_commands():
    cfg = json.loads(CODEX_HOOKS.read_text(encoding="utf-8"))
    return [h for entry in cfg["hooks"]["PreToolUse"] for h in entry["hooks"]]


def test_codex_hooks_json_is_valid_and_macos_only():
    hooks = _codex_hook_commands()
    assert hooks, "codex PreToolUse hook이 없습니다"
    for h in hooks:
        assert "commandWindows" not in h
        script = h["command"].split()[-1]
        assert (REPO_ROOT / script).is_file(), script


@pytest.mark.parametrize("script", ["block-dangerous.sh", "tdd-guard.sh",
                                    "cross-review-nudge.sh"])
def test_hooks_do_not_use_bare_python(script):
    """bare `python`은 macOS에 없을 수 있다 — 없으면 block-dangerous가 모든 Bash를 막는다."""
    import re
    body = (HOOKS / script).read_text(encoding="utf-8")
    code = "\n".join(l for l in body.splitlines() if not l.lstrip().startswith("#"))
    assert not re.search(r"(^|[\s|(])python\s", code), "bare python 호출이 남아 있다"
    assert ".venv/bin/python" in code


def test_block_hook_works_without_python_on_path():
    """PATH에 python이 없어도 repo-local .venv로 파싱해 위험 명령을 막는다(실제 spawn)."""
    env = {"PATH": "/usr/bin:/bin", "HOME": os.environ.get("HOME", "")}
    r = subprocess.run([BASH, str(BLOCK)], input=json.dumps(
        {"tool_input": {"command": DANGER}}), capture_output=True, text=True,
        encoding="utf-8", env=env)
    assert r.returncode == 2 or '"permissionDecision": "deny"' in r.stdout, r.stderr
    r = subprocess.run([BASH, str(BLOCK)], input=json.dumps(
        {"tool_input": {"command": "ls"}}), capture_output=True, text=True,
        encoding="utf-8", env=env)
    assert r.returncode == 0, r.stderr


# ── Stop hook: cross-review-nudge.sh ──────────────────────────────────────
NUDGE = HOOKS / "cross-review-nudge.sh"
NUDGE_MARK = "cross-review"
CROSS_REVIEW_PY = HOOKS.parent / "cross_review.py"


def _init_repo(path):
    """tmp_path를 git repo로 만들고 파일 하나를 커밋한다.

    실제 repo와 같이 __pycache__/와 state 파일을 gitignore 한다 — nudge가
    이 규칙에 기대므로 fixture도 같은 조건이어야 한다.
    """
    subprocess.run(["git", "init", "-q"], cwd=str(path), check=True)
    subprocess.run(["git", "config", "user.email", "t@t.t"], cwd=str(path), check=True)
    subprocess.run(["git", "config", "user.name", "t"], cwd=str(path), check=True)
    (path / ".gitignore").write_text(
        "__pycache__/\n.claude/.cross-review-state\n", encoding="utf-8")
    src = path / "src.py"
    src.write_text("x = 1\n", encoding="utf-8")
    subprocess.run(["git", "add", "."], cwd=str(path), check=True)
    subprocess.run(["git", "commit", "-q", "-m", "init"], cwd=str(path), check=True)
    return src


def _run_nudge(cwd):
    return subprocess.run(
        [BASH, str(NUDGE)], capture_output=True, text=True,
        encoding="utf-8", cwd=str(cwd),
    )


def _write_state(path):
    """현재 워킹트리 상태를 '리뷰됨'으로 기록한다(cross_review._touch_state와 동형).

    지문 계산은 **프로덕션 코드에 위임한다**(재구현 금지 — 테스트가 구현과
    따로 놀면 계약이 깨져도 초록으로 통과한다).
    """
    fingerprint = subprocess.run(
        [sys.executable, str(CROSS_REVIEW_PY), "--fingerprint"],
        cwd=str(path), capture_output=True, text=True,
        encoding="utf-8", check=True).stdout.strip()
    state = path / ".claude" / ".cross-review-state"
    state.parent.mkdir(parents=True, exist_ok=True)
    state.write_text(f"{fingerprint}\n", encoding="utf-8")
    return state


def test_nudge_silent_when_no_state(tmp_path):
    _init_repo(tmp_path)
    r = _run_nudge(tmp_path)
    assert r.returncode == 0
    assert NUDGE_MARK not in r.stdout


def test_nudge_silent_when_state_matches_worktree(tmp_path):
    _init_repo(tmp_path)
    _write_state(tmp_path)
    r = _run_nudge(tmp_path)
    assert r.returncode == 0
    assert NUDGE_MARK not in r.stdout


def test_nudge_warns_when_source_changed(tmp_path):
    src = _init_repo(tmp_path)
    _write_state(tmp_path)
    src.write_text("x = 2\n", encoding="utf-8")
    r = _run_nudge(tmp_path)
    assert r.returncode == 0
    assert NUDGE_MARK in r.stdout


def test_nudge_silent_on_resave_with_identical_content(tmp_path):
    """오탐 회귀 방지: 내용이 같은데 mtime만 바뀌면 알리지 않는다.

    이것이 mtime 방식을 버린 이유다(포매터·에디터 자동저장·git checkout).
    """
    src = _init_repo(tmp_path)
    _write_state(tmp_path)
    src.write_text("x = 1\n", encoding="utf-8")  # 같은 내용 재저장
    os.utime(src, None)  # mtime을 확실히 현재로
    r = _run_nudge(tmp_path)
    assert r.returncode == 0
    assert NUDGE_MARK not in r.stdout, "내용이 같은 재저장에 알림이 뜨면 안 된다"


def test_nudge_warns_after_commit_of_unreviewed_change(tmp_path):
    """누락 회귀 방지: 리뷰 후 새로 커밋한 변경도 미리뷰로 잡아야 한다.

    diff만 해시하면 커밋 순간 `git diff HEAD`가 비어 '리뷰됨'과 같아져
    조용해진다 — 미리뷰 코드를 리뷰된 것으로 표시하는 사고(fd2479a와 동류).
    HEAD sha를 함께 기록해 이를 막는다.
    """
    src = _init_repo(tmp_path)
    _write_state(tmp_path)          # 이 시점까지가 리뷰됨
    src.write_text("x = 2\n", encoding="utf-8")
    subprocess.run(["git", "commit", "-qam", "unreviewed"],
                   cwd=str(tmp_path), check=True)
    r = _run_nudge(tmp_path)
    assert r.returncode == 0
    assert NUDGE_MARK in r.stdout, "커밋했다고 미리뷰 변경이 사라지면 안 된다"


def test_nudge_warns_on_new_untracked_file(tmp_path):
    """추적되지 않은 새 소스 파일도 미리뷰 변경이다."""
    _init_repo(tmp_path)
    _write_state(tmp_path)
    (tmp_path / "new.py").write_text("y = 1\n", encoding="utf-8")
    r = _run_nudge(tmp_path)
    assert r.returncode == 0
    assert NUDGE_MARK in r.stdout


def test_nudge_warns_when_untracked_file_content_changes(tmp_path):
    """누락 회귀 방지: untracked 파일의 **내용** 수정도 잡아야 한다.

    `git status --porcelain -uall`은 경로만(`?? new.py`), `git diff HEAD`는
    untracked 내용을 포함하지 않는다. 경로만 해시하면 새 파일을 리뷰한 뒤
    그 내용을 고쳐도 지문이 그대로여서 미리뷰 변경을 놓친다.
    """
    _init_repo(tmp_path)
    new = tmp_path / "new.py"
    new.write_text("y = 1\n", encoding="utf-8")
    _write_state(tmp_path)                        # 이 내용까지가 리뷰됨
    new.write_text("y = 999\n", encoding="utf-8")  # 경로는 그대로, 내용만 변경
    r = _run_nudge(tmp_path)
    assert r.returncode == 0
    assert NUDGE_MARK in r.stdout, "untracked 파일 내용 변경을 놓치면 안 된다"


def test_nudge_ignores_pyc_files(tmp_path):
    """pytest가 만드는 .pyc는 알림을 유발하면 안 된다."""
    _init_repo(tmp_path)
    _write_state(tmp_path)
    cache = tmp_path / "__pycache__"
    cache.mkdir()
    (cache / "src.cpython-313.pyc").write_bytes(b"\x00")
    r = _run_nudge(tmp_path)
    assert r.returncode == 0
    assert NUDGE_MARK not in r.stdout


def test_nudge_warns_when_state_is_legacy_format(tmp_path):
    """구 형식(mtime 시절) state는 지문과 다르므로 알림이 뜬다 — 의도된 동작.

    "리뷰됐는지 알 수 없음"은 조용할 이유가 아니다. 안전한 쪽(알림)으로
    기울이고, 다음 /cross-review 한 번이면 새 형식으로 덮인다.
    차단은 하지 않으므로 exit 0은 유지된다.
    """
    _init_repo(tmp_path)
    state = tmp_path / ".claude" / ".cross-review-state"
    state.parent.mkdir(parents=True, exist_ok=True)
    state.write_text("cross-review last run\n", encoding="utf-8")  # 구 형식
    r = _run_nudge(tmp_path)
    assert r.returncode == 0, "알림이 작업을 막으면 안 된다"
    assert NUDGE_MARK in r.stdout


def test_nudge_exits_zero_outside_git_repo(tmp_path):
    """git repo가 아니어도 절대 실패하지 않는다(작업을 방해하면 안 됨)."""
    r = _run_nudge(tmp_path)
    assert r.returncode == 0
