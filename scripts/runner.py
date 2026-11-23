#!/usr/bin/env python3
"""외부 runner 계약 — sandbox-exec profile 생성, launch descriptor, control hash, git ref 불변.

이 파일은 하네스 repo의 **source**다. 실제 실행 전 운영자가 Astra-reviewed exact SHA의
runner·manifest 코드를 repo 밖 runner home(`<RH>/scripts`)으로 복제(export)하고 hash를
고정한다. runner home도 하네스 설치 root다 — 자기 `<RH>/.harness/policy.json`(+선택
`policy.local.json`)만 읽는다. 구현 Claude는 이 외부 runner·profile·evidence를 쓸 수 없다.

Usage: ./.venv/bin/python scripts/harness.py runner <command>
  prepare --task T --evidence-dir E --approval-sha S --output-dir O --descriptor-out D
          승인 검증 → sandbox profile·launch descriptor를 read-only로 생성
  probe   --descriptor D      허용 source write 성공 / 계획·control·.git·evidence 거부를 실측
  verify-final --descriptor D tested SHA = reviewed SHA = 현재 HEAD, clean tree 확인

3.9에서도 파싱되어야 한다 — 3.10+ 문법 금지.
"""
import argparse
import hashlib
import json
import os
import re
import stat
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import runtime  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
SANDBOX_EXEC = "/usr/bin/sandbox-exec"
CONTROL_PATHS = ("CLAUDE.md", ".claude", ".codex", "scripts", "pytest.ini", ".gitignore",
                 ".gitattributes", ".python-version")
# 구현 Claude가 쓰면 안 되는 clone 내부 경로(명시 deny — deny default 위에 이중 방어)
PROTECTED_CLONE = (".git", "phases", "scripts", ".claude", ".codex", ".harness", ".venv",
                   "docs/superpowers/specs")
PROTECTED_CLONE_FILES = ("CLAUDE.md", ".gitignore", ".gitattributes", "pytest.ini",
                         ".python-version")
DESCRIPTOR_KEYS = ("version", "task", "repoRoot", "branch", "baseBranch", "evidenceDir",
                   "approvalRecordSha", "sandboxProfile", "sandboxProfileSha", "outputDir",
                   "controlSha", "controlPin", "controlPinSha", "manifestCodeSha",
                   "metadataPaths", "allowedPaths", "createdAt")
_SAFE_PATH = re.compile(r"[^\"\\\n\r()]+")


class RunnerError(Exception):
    pass


def _extra_protected():
    """policy.local.json의 호스트 전용 보호 경로(원본 템플릿 checkout 등). 기본은 없음."""
    try:
        return [Path(p) for p in runtime.extra_protected_paths()]
    except runtime.PolicyError as e:
        raise RunnerError("policy.local 오류: %s" % e)


def _branch_issue(branch):
    """descriptor branch가 policy의 feat/<ISSUE>/<slug> 패턴이면 issue, 아니면 None."""
    try:
        return runtime.policy().feature_branch_issue(branch)
    except runtime.PolicyError as e:
        raise RunnerError("policy 오류: %s" % e)


def _sha_bytes(b):
    return hashlib.sha256(b).hexdigest()


def write_read_only(path, text):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    data = text.encode("utf-8") if isinstance(text, str) else text
    if path.exists():
        path.chmod(0o644)
    tmp = path.with_name(path.name + ".tmp-%d" % os.getpid())
    tmp.write_bytes(data)
    os.chmod(tmp, 0o444)
    os.replace(tmp, path)
    return _sha_bytes(data)


def _real(p):
    return Path(os.path.realpath(str(p)))


def _inside(child, parent):
    c, p = _real(child), _real(parent)
    return c == p or p in c.parents


def _q(path):
    s = str(path)
    if not _SAFE_PATH.fullmatch(s):
        raise RunnerError("sandbox profile에 넣을 수 없는 경로 문자: %r" % s)
    return '"%s"' % s


def default_metadata_paths(home=None):
    """Claude 인증·session/cache에 필요한 최소 쓰기 경로. 목록은 evidence에 남긴다."""
    home = Path(home or Path.home())
    claude = home / ".claude"
    # /private/tmp 같은 공용 임시 경로는 주지 않는다 — 임시 파일은 TMPDIR=<output>/tmp.
    return [str(claude / d) for d in ("projects", "todos", "shell-snapshots", "statsig",
                                      "session-env", "debug", "file-history", "telemetry")] + [
        str(home / ".claude.json"), str(home / ".claude.json.backup"),
        str(home / "Library" / "Caches" / "claude-cli-nodejs")]


def _overlaps(a, b):
    return _inside(a, b) or _inside(b, a)


def _existing_ancestor(p):
    p = Path(p)
    while not p.exists() and p != p.parent:
        p = p.parent
    return p


def _in_git_repo(p):
    anc = _existing_ancestor(p)
    r = subprocess.run(["git", "-C", str(anc if anc.is_dir() else anc.parent), "rev-parse",
                        "--show-toplevel"], capture_output=True, text=True)
    return r.returncode == 0


def _contains_git_repo(p, limit=20000):
    n = 0
    for dirpath, dirnames, filenames in os.walk(str(p)):
        if ".git" in dirnames or ".git" in filenames:
            return True
        n += 1
        if n > limit:
            return True  # 너무 큰 디렉터리는 전용 출력 디렉터리가 아니다 — fail closed
    return False


def _check_output_root(out, clone, protected):
    """B2: 출력(쓰기) root는 clone·보호 경로와 어느 방향으로도 겹치면 안 되고,
    다른 git repo 안에 있거나 repo를 품어서도 안 된다(sibling repo 쓰기 차단)."""
    if _overlaps(out, clone):
        raise RunnerError("output dir가 clone과 겹침(안/조상): %s" % out)
    for p in protected:
        if _overlaps(out, p):
            raise RunnerError("output dir가 보호 경로와 겹침: %s ↔ %s" % (out, p))
    if _in_git_repo(out):
        raise RunnerError("output dir가 다른 git repo 안에 있음: %s" % out)
    if Path(out).exists() and _contains_git_repo(out):
        raise RunnerError("output dir 아래에 git repo가 있음: %s" % out)


def _check_metadata_path(m, clone, protected, home=None):
    """Claude 인증·session metadata만 허용: ~/.claude/<dir>, ~/.claude.json*, Caches/claude-cli-nodejs."""
    home = Path(home or Path.home())
    mp = Path(m)
    allowed_roots = [home / ".claude"]
    allowed_exact = [home / ".claude.json", home / ".claude.json.backup",
                     home / "Library" / "Caches" / "claude-cli-nodejs"]
    ok = (any(str(mp).startswith(str(r) + "/") for r in allowed_roots)
          or any(mp == e for e in allowed_exact))
    if not ok:
        raise RunnerError("허용되지 않은 metadata 쓰기 경로: %s" % m)
    if _overlaps(mp, clone) or any(_overlaps(mp, p) for p in protected):
        raise RunnerError("metadata 경로가 clone/보호 경로와 겹침: %s" % m)


# --- B3: 에이전트가 쓸 수 있는 저장소(output dir)에 대한 신뢰 I/O --------------
# 하네스(sandbox 밖)는 에이전트가 만든 경로를 **따라가지 않는다**: 디렉터리 fd 기준(openat),
# O_NOFOLLOW, regular file·nlink==1만, 크기 제한. 신뢰 출력은 에이전트가 못 쓰는 evidence에 쓴다.

AGENT_FILE_MAX = 1 << 20
_AGENT_NAME = re.compile(r"[A-Za-z0-9][A-Za-z0-9._-]{0,127}")


def _check_agent_name(name):
    if not isinstance(name, str) or not _AGENT_NAME.fullmatch(name) or name in (".", ".."):
        raise RunnerError("에이전트 저장소 이름이 안전하지 않음: %r" % (name,))


def _open_agent_dir(d):
    """경로 전체에 symlink가 없고 마지막 구성요소도 따라가지 않는 디렉터리 fd."""
    p = os.path.abspath(str(d))
    if os.path.realpath(p) != p:
        raise RunnerError("에이전트 저장소 경로에 symlink가 있음: %s" % p)
    try:
        return os.open(p, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
    except OSError as e:
        raise RunnerError("에이전트 저장소를 열 수 없음(%s): %s" % (e.strerror, p))


def read_agent_file(d, name, max_bytes=AGENT_FILE_MAX):
    """에이전트가 남긴 결과 파일을 읽는다. 없으면 None. symlink·hardlink·특수 파일·초과 크기는 거부."""
    _check_agent_name(name)
    dfd = _open_agent_dir(d)
    try:
        try:
            fd = os.open(name, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK, dir_fd=dfd)
        except FileNotFoundError:
            return None
        except OSError as e:
            raise RunnerError("결과 파일을 안전하게 열 수 없음(symlink 등, %s): %s" % (e.strerror, name))
        try:
            st = os.fstat(fd)
            if not stat.S_ISREG(st.st_mode):
                raise RunnerError("결과 파일이 regular file이 아님: %s" % name)
            if st.st_nlink != 1:
                raise RunnerError("결과 파일이 hardlink임(nlink=%d): %s" % (st.st_nlink, name))
            if st.st_size > max_bytes:
                raise RunnerError("결과 파일이 너무 큼: %s" % name)
            data = os.read(fd, max_bytes + 1)
            if len(data) > max_bytes:
                raise RunnerError("결과 파일이 너무 큼: %s" % name)
            return data
        finally:
            os.close(fd)
    finally:
        os.close(dfd)


def remove_agent_entry(d, name):
    """이름 하나를 따라가지 않고 지운다(symlink·hardlink는 링크만, 디렉터리는 fd 기반 rmtree)."""
    import shutil
    _check_agent_name(name)
    dfd = _open_agent_dir(d)
    try:
        try:
            st = os.stat(name, dir_fd=dfd, follow_symlinks=False)
        except FileNotFoundError:
            return
        if stat.S_ISDIR(st.st_mode):
            if not shutil.rmtree.avoids_symlink_attacks:
                raise RunnerError("이 플랫폼의 rmtree는 symlink 공격에 안전하지 않음")
            shutil.rmtree(name, dir_fd=dfd)
        else:
            os.unlink(name, dir_fd=dfd)
    finally:
        os.close(dfd)


def fresh_agent_dir(d, name):
    """에이전트용 하위 디렉터리를 새로 만든다. 기존 항목(symlink·파일·디렉터리)은 따라가지 않고
    제거한다. 다시 바뀌어 만들 수 없으면 실패한다(fail closed)."""
    remove_agent_entry(d, name)
    dfd = _open_agent_dir(d)
    try:
        try:
            os.mkdir(name, 0o700, dir_fd=dfd)
        except FileExistsError:
            raise RunnerError("에이전트 디렉터리가 경쟁적으로 교체됨: %s" % name)
        st = os.stat(name, dir_fd=dfd, follow_symlinks=False)
        if not stat.S_ISDIR(st.st_mode):
            raise RunnerError("에이전트 디렉터리 생성 확인 실패: %s" % name)
    finally:
        os.close(dfd)
    return Path(d) / name


def build_profile(clone_root, allowed_paths, output_dir, protected, metadata_paths):
    import plan_manifest as pm
    clone = _real(clone_root)
    out = _real(output_dir)
    err = pm._allowed_paths_error(list(allowed_paths))
    if err:
        raise RunnerError(err)
    extra = _extra_protected()
    _check_output_root(out, clone, list(protected) + extra)
    for m in metadata_paths:
        _check_metadata_path(m, clone, list(protected) + extra)
    allow = []
    for a in allowed_paths:
        if a.endswith("/"):
            allow.append("(subpath %s)" % _q(clone / a.rstrip("/")))
        else:
            allow.append("(literal %s)" % _q(clone / a))
    allow.append("(subpath %s)" % _q(out))
    meta = []
    for m in metadata_paths:
        mp = Path(m)
        meta.append("(subpath %s)" % _q(_real(mp) if mp.exists() else mp))
    denies = [clone / p for p in PROTECTED_CLONE] + [clone / f for f in PROTECTED_CLONE_FILES]
    denies += [_real(p) for p in protected] + [_real(p) for p in extra]
    lines = [
        "(version 1)",
        "(deny default)",
        ";; 실행·IPC·읽기는 허용, 쓰기는 allowlist만",
        "(allow process-exec) (allow process-fork) (allow process-info*) (allow signal)",
        "(allow sysctl-read) (allow mach-lookup) (allow ipc-posix-shm*) (allow ipc-posix-sem*)",
        "(allow iokit-open) (allow network*) (allow file-read*) (allow file-ioctl)",
        "(allow file-map-executable) (allow pseudo-tty) (allow system-socket)",
        "(allow user-preference-read)",
        '(allow file-write* (literal "/dev/null") (literal "/dev/tty") (regex #"^/dev/fd/")'
        ' (regex #"^/dev/ttys"))',
        ";; 승인된 source/test allowlist + 임시 출력",
        "(allow file-write* %s)" % " ".join(allow),
    ]
    if meta:
        lines += [";; Claude 인증·session 최소 metadata", "(allow file-write* %s)" % " ".join(meta)]
    lines.append(";; 보호 경로 — 나중 규칙이 우선한다")
    for d in denies:
        lines.append("(deny file-write* (subpath %s))" % _q(d))
    return "\n".join(lines) + "\n"


def wrap_argv(profile_path, argv):
    return [SANDBOX_EXEC, "-f", str(profile_path)] + list(argv)


def probe(profile_path, allowed, denied):
    """실제 sandboxed write 시도. 허용 경로 성공·거부 경로 실패여야 ok."""
    def attempt(target):
        target = Path(target)
        existed = target.exists()
        r = subprocess.run(wrap_argv(profile_path, ["/bin/sh", "-c", 'echo probe > "$1"', "sh",
                                                    str(target)]),
                           capture_output=True, text=True)
        wrote = r.returncode == 0
        if wrote and not existed:
            try:
                target.unlink()
            except OSError:
                pass
        return {"path": str(target), "wrote": wrote}
    res = {"allowed": [attempt(p) for p in allowed], "denied": [attempt(p) for p in denied]}
    res["ok"] = (all(r["wrote"] for r in res["allowed"])
                 and not any(r["wrote"] for r in res["denied"]))
    return res


def control_sha(root):
    """repo 내부 제어 파일(scripts/.claude/.codex/CLAUDE.md 등)의 hash."""
    root = Path(root)
    entries = []
    for top in CONTROL_PATHS:
        p = root / top
        if not os.path.lexists(p):
            continue
        paths = [p] if not p.is_dir() or p.is_symlink() else sorted(
            x for x in p.rglob("*") if "__pycache__" not in x.parts
            and not x.name.endswith(".pyc") and x.name != ".cross-review-state")
        for x in paths:
            st = os.lstat(x)
            rel = x.relative_to(root).as_posix()
            if stat.S_ISDIR(st.st_mode):
                continue
            if stat.S_ISLNK(st.st_mode):
                entries.append([rel, "symlink", os.readlink(x)])
            else:
                entries.append([rel, "file", _sha_bytes(x.read_bytes())])
    return _sha_bytes(json.dumps(sorted(entries), ensure_ascii=False).encode("utf-8"))


def _git(repo, *args):
    return subprocess.run(["git"] + list(args), cwd=str(repo), capture_output=True, text=True,
                          encoding="utf-8")


def git_fingerprint(repo, feature_ref):
    """feature ref를 제외한 git metadata(HEAD·config·hooks·다른 ref) 지문."""
    gd = _git(repo, "rev-parse", "--absolute-git-dir")
    if gd.returncode != 0:
        raise RunnerError("git dir 확인 실패: %s" % gd.stderr.strip())
    gdir = Path(gd.stdout.strip())
    head = (gdir / "HEAD").read_bytes() if (gdir / "HEAD").exists() else b""
    config = (gdir / "config").read_bytes() if (gdir / "config").exists() else b""
    hooks = []
    if (gdir / "hooks").is_dir():
        for h in sorted((gdir / "hooks").iterdir()):
            if h.is_file():
                hooks.append([h.name, _sha_bytes(h.read_bytes())])
    refs = _git(repo, "for-each-ref", "--format=%(refname) %(objectname)")
    if refs.returncode != 0:
        raise RunnerError("ref 목록 실패")
    other = sorted(l for l in refs.stdout.splitlines() if l.split(" ")[0] != feature_ref)
    return {"HEAD": _sha_bytes(head), "config": _sha_bytes(config),
            "hooks": _sha_bytes(json.dumps(hooks).encode()),
            "refs": _sha_bytes("\n".join(other).encode())}


def build_descriptor(task, repo_root, branch, base_branch, evidence_dir, approval_record_sha,
                     sandbox_profile, output_dir, metadata_paths=(), allowed_paths=(),
                     control_pin=None, control_pin_sha=None, control=None):
    import plan_manifest as pm
    return {
        "version": 2, "task": task, "repoRoot": str(_real(repo_root)), "branch": branch,
        "baseBranch": base_branch, "evidenceDir": str(_real(evidence_dir)),
        "approvalRecordSha": approval_record_sha, "sandboxProfile": str(_real(sandbox_profile)),
        "sandboxProfileSha": _sha_bytes(Path(sandbox_profile).read_bytes()),
        "outputDir": str(_real(output_dir)),
        "controlSha": control if control is not None else control_sha(repo_root),
        "controlPin": str(_real(control_pin)) if control_pin else None,
        "controlPinSha": control_pin_sha,
        "manifestCodeSha": pm.code_sha(), "metadataPaths": list(metadata_paths),
        "allowedPaths": list(allowed_paths),
        "createdAt": datetime.now(timezone.utc).isoformat(),
    }


def _read_only_regular(path, what, repo):
    p = Path(path)
    try:
        st = os.lstat(p)
    except OSError:
        raise RunnerError("%s 없음: %s" % (what, p))
    if not stat.S_ISREG(st.st_mode):
        raise RunnerError("%s가 regular file이 아님(symlink 등): %s" % (what, p))
    if st.st_mode & 0o222:
        raise RunnerError("%s가 read-only가 아님: %s" % (what, p))
    if _inside(p, repo):
        raise RunnerError("%s가 repo 안에 있음 — 외부 runner 경로여야 함: %s" % (what, p))
    return p.read_bytes()


# --- M2: reviewed commit에 고정된 control·runner 코드 pin ---------------------

RUNNER_FILES = ("runtime.py", "plan_manifest.py", "review_plan.py", "approval.py", "runner.py",
                "execute.py", "plan_session.py")
PIN_KEYS = ("version", "reviewedCommit", "controlSha", "harnessCommit", "runnerCodeSha",
            "runnerFiles", "createdAt")
REQUIRED_BASE = "main"
TICKET_MAX_AGE = 600


def _git_bytes(repo, *args):
    r = subprocess.run(["git"] + list(args), cwd=str(repo), capture_output=True)
    if r.returncode != 0:
        raise RunnerError("git %s 실패: %s" % (args[0], r.stderr.decode("utf-8", "replace")[:200]))
    return r.stdout


def _runner_entries(read):
    entries = []
    for name in RUNNER_FILES:
        data = read(name)
        if data is None:
            raise RunnerError("runner 파일 없음: %s" % name)
        entries.append([name, _sha_bytes(data)])
    return _sha_bytes(json.dumps(entries).encode("utf-8"))


def runner_code_sha(scripts_dir):
    """실행 중인 runner 코드(외부 runner home의 scripts/)의 hash."""
    d = Path(scripts_dir)

    def read(name):
        p = d / name
        return p.read_bytes() if p.is_file() and not p.is_symlink() else None
    return _runner_entries(read)


def runner_code_sha_at_commit(harness_repo, commit):
    def read(name):
        try:
            return _git_bytes(harness_repo, "show", "%s:scripts/%s" % (commit, name))
        except RunnerError:
            return None
    return _runner_entries(read)


def control_sha_at_commit(repo, commit):
    """reviewed commit의 git object로 control hash를 계산한다(작업 트리 아님).
    control_sha(worktree)와 같은 형식 — 둘이 같아야 실행할 수 있다."""
    out = _git_bytes(repo, "ls-tree", "-r", "-z", "--full-tree", commit, "--",
                     *CONTROL_PATHS)
    entries = []
    for rec in out.split(b"\0"):
        if not rec:
            continue
        meta, path = rec.split(b"\t", 1)
        mode, _typ, obj = meta.decode().split(" ")
        rel = path.decode("utf-8")
        parts = rel.split("/")
        if "__pycache__" in parts or rel.endswith(".pyc") or parts[-1] == ".cross-review-state":
            continue
        blob = _git_bytes(repo, "cat-file", "blob", obj)
        if mode == "120000":
            entries.append([rel, "symlink", blob.decode("utf-8")])
        else:
            entries.append([rel, "file", _sha_bytes(blob)])
    return _sha_bytes(json.dumps(sorted(entries), ensure_ascii=False).encode("utf-8"))


def export_runner(harness_repo, commit, dest):
    """Astra-reviewed harness commit의 runner 코드를 외부 runner home으로 그대로 복제한다."""
    dest = Path(dest)
    if dest.exists() and any(dest.iterdir()):
        raise RunnerError("export 대상이 비어 있지 않음: %s" % dest)
    dest.mkdir(parents=True, exist_ok=True)
    for name in RUNNER_FILES:
        data = _git_bytes(harness_repo, "show", "%s:scripts/%s" % (commit, name))
        (dest / name).write_bytes(data)
        os.chmod(dest / name, 0o444)
    return runner_code_sha(dest)


def pin_control(clone, reviewed_commit, harness_repo, harness_commit, out):
    """control pin: clone의 reviewed commit control hash + harness reviewed commit runner hash."""
    if _inside(out, clone):
        raise RunnerError("control pin은 clone 밖에 둔다: %s" % out)
    commit = _git_bytes(clone, "rev-parse", "--verify", reviewed_commit + "^{commit}")
    hcommit = _git_bytes(harness_repo, "rev-parse", "--verify", harness_commit + "^{commit}")
    pin = {"version": 1, "reviewedCommit": commit.decode().strip(),
           "controlSha": control_sha_at_commit(clone, reviewed_commit),
           "harnessCommit": hcommit.decode().strip(),
           "runnerCodeSha": runner_code_sha_at_commit(harness_repo, harness_commit),
           "runnerFiles": list(RUNNER_FILES),
           "createdAt": datetime.now(timezone.utc).isoformat()}
    write_read_only(out, json.dumps(pin, indent=2))
    return pin


def load_pin(path, repo):
    data = _read_only_regular(path, "control pin", repo)
    try:
        pin = json.loads(data.decode("utf-8"))
    except ValueError:
        raise RunnerError("control pin JSON 오류")
    if not isinstance(pin, dict) or set(pin) != set(PIN_KEYS):
        raise RunnerError("control pin 키 불일치")
    return pin, _sha_bytes(data)


def _verify_pin(pin, repo, runner_dir):
    if control_sha(repo) != pin["controlSha"]:
        raise RunnerError("clone control 파일이 reviewed commit %s의 pin과 다름"
                          % pin["reviewedCommit"][:10])
    if runner_code_sha(runner_dir) != pin["runnerCodeSha"]:
        raise RunnerError("runner 코드(%s)가 reviewed harness commit %s의 pin과 다름"
                          % (runner_dir, pin["harnessCommit"][:10]))


def load_descriptor(path, repo_root, runner_dir=None):
    """외부 runner가 만든 read-only descriptor + reviewed pin을 독립 검증한다."""
    import plan_manifest as pm
    if not path:
        raise RunnerError("launch descriptor 없음 — execute는 외부 runner로만 실행한다 "
                          "(HARNESS_LAUNCH_DESCRIPTOR)")
    repo = _real(repo_root)
    data = _read_only_regular(path, "launch descriptor", repo)
    try:
        d = json.loads(data.decode("utf-8"))
    except ValueError:
        raise RunnerError("descriptor JSON 오류")
    if not isinstance(d, dict) or set(d) != set(DESCRIPTOR_KEYS):
        raise RunnerError("descriptor 키 불일치")
    if d["version"] != 2 or Path(d["repoRoot"]) != repo:
        raise RunnerError("descriptor repoRoot가 현재 repo와 다름")
    if (d["baseBranch"] != REQUIRED_BASE or d["branch"] == REQUIRED_BASE
            or _branch_issue(d["branch"]) is None):
        raise RunnerError("descriptor branch/base가 승인 패턴이 아님(main 금지)")
    if not re.fullmatch(r"[0-9a-f]{64}", str(d["approvalRecordSha"])):
        raise RunnerError("approvalRecordSha 형식 오류")
    for k in ("evidenceDir", "outputDir"):
        p = Path(d[k])
        if not p.is_dir() or p.is_symlink() or _inside(p, repo):
            raise RunnerError("%s가 repo 밖의 실제 디렉터리가 아님: %s" % (k, p))
    if _overlaps(d["outputDir"], d["evidenceDir"]):
        raise RunnerError("outputDir가 evidence와 겹침")
    _check_output_root(Path(d["outputDir"]), repo, [Path(d["evidenceDir"])])
    prof = _read_only_regular(d["sandboxProfile"], "sandbox profile", repo)
    if _sha_bytes(prof) != d["sandboxProfileSha"]:
        raise RunnerError("sandbox profile hash 불일치")
    if b"(deny default)" not in prof:
        raise RunnerError("sandbox profile이 deny-default가 아님")
    if not d["controlPin"]:
        raise RunnerError("control pin 없음 — reviewed commit에 고정되지 않은 descriptor")
    pin, pin_sha = load_pin(d["controlPin"], repo)
    if pin_sha != d["controlPinSha"] or pin["controlSha"] != d["controlSha"]:
        raise RunnerError("control pin이 descriptor와 다름")
    _verify_pin(pin, repo, Path(runner_dir) if runner_dir else Path(__file__).resolve().parent)
    if d["manifestCodeSha"] != pm.code_sha():
        raise RunnerError("plan_manifest 코드 hash 불일치")
    return d


def verify_final(repo, final_path):
    data = json.loads(Path(final_path).read_text(encoding="utf-8"))
    tested, reviewed = data.get("testedSha"), data.get("reviewedSha")
    head = _git(repo, "rev-parse", "HEAD").stdout.strip()
    if not tested or tested != reviewed:
        raise RunnerError("tested SHA(%s) ≠ reviewed SHA(%s)" % (tested, reviewed))
    if head != reviewed:
        raise RunnerError("현재 HEAD(%s)가 리뷰된 SHA가 아님 — push 거부" % head[:10])
    st = _git(repo, "status", "--porcelain", "--untracked-files=all")
    if st.returncode != 0 or st.stdout.strip():
        raise RunnerError("작업 트리가 clean하지 않음 — push 거부")
    return head


def prepare(task, evidence_dir, approval_sha, output_dir, descriptor_out, control_pin=None,
            repo=ROOT):
    import approval as ap
    repo = _real(repo)
    if not control_pin:
        raise RunnerError("--control-pin(reviewed commit pin) 필수")
    pin, pin_sha = load_pin(control_pin, repo)
    _verify_pin(pin, repo, Path(__file__).resolve().parent)
    try:
        v = ap.verify_approval(evidence_dir, task, repo, approval_sha, first_run=False)
    except ap.ApprovalError as e:
        raise RunnerError(str(e))
    branch = v.record["branch"]
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    meta = default_metadata_paths()
    prof_text = build_profile(repo, v.snapshot.index["allowedPaths"], output_dir,
                              protected=[evidence_dir, Path(descriptor_out), Path(control_pin),
                                         Path(__file__).resolve().parent],
                              metadata_paths=meta)
    prof = Path(evidence_dir) / task / "runner" / "sandbox.sb"
    write_read_only(prof, prof_text)
    d = build_descriptor(task, repo, branch, v.record["baseBranch"], evidence_dir, approval_sha,
                         prof, output_dir, metadata_paths=meta,
                         allowed_paths=v.snapshot.index["allowedPaths"],
                         control_pin=control_pin, control_pin_sha=pin_sha,
                         control=pin["controlSha"])
    write_read_only(descriptor_out, json.dumps(d, indent=2, ensure_ascii=False))
    return d


# --- M2: 외부 실행 supervisor + 1회용 launch ticket ---------------------------

def _tickets_dir(d):
    return Path(d["evidenceDir"]) / d["task"] / "runner" / "tickets"


def write_ticket(d, descriptor_path):
    import time as _t
    tdir = _tickets_dir(d)
    tdir.mkdir(parents=True, exist_ok=True)
    nonce = os.urandom(16).hex()
    path = tdir / ("%s.json" % nonce)
    write_read_only(path, json.dumps({
        "descriptorSha": _sha_bytes(Path(descriptor_path).read_bytes()),
        "approvalRecordSha": d["approvalRecordSha"], "controlPinSha": d["controlPinSha"],
        "createdEpoch": _t.time()}))
    return path


def consume_ticket(ticket_path, descriptor_path, d):
    """execute.py: supervisor가 방금 발급한 ticket만 1회 받는다."""
    import time as _t
    if not ticket_path:
        raise RunnerError("launch ticket 없음 — execute는 runner launch(supervisor)로만 실행한다")
    t = Path(ticket_path)
    data = _read_only_regular(t, "launch ticket", Path(d["repoRoot"]))
    if _real(t).parent != _real(_tickets_dir(d)):
        raise RunnerError("launch ticket 위치가 evidence tickets 디렉터리가 아님")
    tk = json.loads(data.decode("utf-8"))
    if (tk.get("descriptorSha") != _sha_bytes(Path(descriptor_path).read_bytes())
            or tk.get("approvalRecordSha") != d["approvalRecordSha"]
            or tk.get("controlPinSha") != d["controlPinSha"]):
        raise RunnerError("launch ticket이 descriptor와 다름")
    if not (0 <= _t.time() - float(tk.get("createdEpoch", 0)) <= TICKET_MAX_AGE):
        raise RunnerError("launch ticket 만료")
    try:
        fd = os.open(str(t) + ".consumed", os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o444)
        os.close(fd)
    except FileExistsError:
        raise RunnerError("launch ticket 재사용 거부")


def launch(descriptor_path, repo_root, base="main", spawn=None, runner_dir=None):
    """외부 supervisor: pin·descriptor·승인·branch·정책을 독립 검증한 뒤 **자기(pinned)**
    execute.py를 띄우고, 끝난 뒤 git 불변식과 final 결속을 다시 확인한다."""
    import approval as ap
    runner_dir = Path(runner_dir) if runner_dir else Path(__file__).resolve().parent
    repo = _real(repo_root)
    errors = runtime.review_policy_errors()
    if base != REQUIRED_BASE:
        errors.append("--base는 %s만 허용(현재 %r)" % (REQUIRED_BASE, base))
    if errors:
        for e in errors:
            print("ERROR: " + e, file=sys.stderr)
        return 1
    try:
        d = load_descriptor(descriptor_path, repo, runner_dir=runner_dir)
        ev, task, sha = d["evidenceDir"], d["task"], d["approvalRecordSha"]
        first = ap.is_first_run(ev, task, sha)
        v = ap.verify_approval(ev, task, repo, sha, first_run=first)
        ap.is_first_run(ev, task, sha, plan_commit=v.record["planCommitSha"])
        if v.record["branch"] != d["branch"]:
            raise RunnerError("descriptor branch가 승인 branch와 다름")
        feature_ref = "refs/heads/" + d["branch"]
        before = git_fingerprint(repo, feature_ref)
        ticket = write_ticket(d, descriptor_path)
    except (RunnerError, ap.ApprovalError, OSError, ValueError) as e:
        print("ERROR: supervisor 사전 검증 실패 — %s" % e, file=sys.stderr)
        return 1
    argv = [sys.executable, str(runner_dir / "execute.py"), task, "--repo-root", str(repo),
            "--base", base]
    env = dict(os.environ, HARNESS_LAUNCH_DESCRIPTOR=str(descriptor_path),
               HARNESS_LAUNCH_TICKET=str(ticket))
    rc = spawn(argv, env) if spawn else subprocess.call(argv, env=env)
    final = Path(ev) / task / "final.json"
    try:
        if git_fingerprint(repo, feature_ref) != before:
            raise RunnerError("실행 중 feature ref 밖 git metadata(main·다른 ref·config·hooks) 변경")
        if _git(repo, "symbolic-ref", "--short", "-q", "HEAD").stdout.strip() != d["branch"]:
            raise RunnerError("실행 중 branch가 바뀜")
        if rc == 0:
            verify_final(repo, final)
    except (RunnerError, OSError, ValueError) as e:
        if final.exists():
            final.chmod(0o644)
            os.replace(final, final.with_name("final.rejected.json"))
        write_read_only(Path(ev) / task / "runner" / ("violation-%d.json" % os.getpid()),
                        json.dumps({"reason": str(e), "childExit": rc}))
        print("ERROR: supervisor 사후 검증 실패 — %s" % e, file=sys.stderr)
        return 3
    return rc


def main(argv=None):
    runtime.require_runtime()
    p = argparse.ArgumentParser(description="외부 runner 계약·실행 supervisor")
    sub = p.add_subparsers(dest="cmd", required=True)
    pn = sub.add_parser("pin-control")
    for a in ("--clone", "--reviewed-commit", "--harness-repo", "--harness-commit", "--out"):
        pn.add_argument(a, required=True)
    exp = sub.add_parser("export")
    for a in ("--harness-repo", "--commit", "--dest"):
        exp.add_argument(a, required=True)
    pr = sub.add_parser("prepare")
    for a in ("--task", "--evidence-dir", "--approval-sha", "--output-dir", "--descriptor-out",
              "--control-pin"):
        pr.add_argument(a, required=True)
    pr.add_argument("--repo-root", default=str(ROOT), help="독립 clone root")
    la = sub.add_parser("launch")
    la.add_argument("--descriptor", required=True)
    la.add_argument("--repo-root", required=True, help="독립 clone root")
    la.add_argument("--base", default=REQUIRED_BASE)
    pb = sub.add_parser("probe")
    pb.add_argument("--descriptor", required=True)
    pb.add_argument("--repo-root", default=str(ROOT), help="독립 clone root")
    vf = sub.add_parser("verify-final")
    vf.add_argument("--descriptor", required=True)
    vf.add_argument("--repo-root", default=str(ROOT), help="독립 clone root")
    args = p.parse_args(argv)
    try:
        if args.cmd == "pin-control":
            out = pin_control(args.clone, args.reviewed_commit, args.harness_repo,
                              args.harness_commit, args.out)
        elif args.cmd == "export":
            out = {"runnerCodeSha": export_runner(args.harness_repo, args.commit, args.dest)}
        elif args.cmd == "prepare":
            out = prepare(args.task, args.evidence_dir, args.approval_sha, args.output_dir,
                          args.descriptor_out, control_pin=args.control_pin,
                          repo=args.repo_root)
        elif args.cmd == "launch":
            return launch(args.descriptor, args.repo_root, base=args.base)
        elif args.cmd == "probe":
            d = load_descriptor(args.descriptor, args.repo_root)
            repo = Path(d["repoRoot"])
            allowed = [Path(d["outputDir"]) / ".sandbox-probe"] + [
                repo / a / ".sandbox-probe" for a in d["allowedPaths"]
                if a.endswith("/") and (repo / a).is_dir()]
            tag = "harness-probe-%d" % os.getpid()
            denied = [repo / p / ".sandbox-probe" for p in PROTECTED_CLONE] + [
                repo / ".sandbox-probe", repo.parent / tag,
                Path(d["evidenceDir"]) / ".sandbox-probe",
                Path("/private/tmp") / tag, Path.home() / ("." + tag)] + [
                p / ".sandbox-probe" for p in _extra_protected()]
            out = probe(d["sandboxProfile"], allowed, denied)
            write_read_only(Path(d["evidenceDir"]) / d["task"] / "runner" / "probe.json",
                            json.dumps(out, indent=2))
            if not out["ok"]:
                print(json.dumps(out, indent=2))
                return 1
        else:
            d = load_descriptor(args.descriptor, args.repo_root)
            out = {"head": verify_final(d["repoRoot"],
                                        Path(d["evidenceDir"]) / d["task"] / "final.json")}
    except RunnerError as e:
        print("ERROR: %s" % e, file=sys.stderr)
        return 1
    print(json.dumps(out, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
