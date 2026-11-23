#!/usr/bin/env python3
"""하네스 배포 설치기 — harness-manifest.json 기반으로 target Git 프로젝트를 materialize한다.

Usage: ./.venv/bin/python scripts/harness.py init --target <T> [mode] ...

3.9에서도 파싱되어야 한다 — 3.10+ 문법 금지.
"""
import fcntl
import hashlib
import json
import os
import re
import signal
import stat
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

# 설치기 경로(init --check·--dry-run)는 target·distribution에 어떤 파일도 남기지 않는다 —
# 하네스 모듈 import가 scripts/__pycache__를 쓰지 않게 한다.
sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parent))
import runtime  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
MANIFEST_NAME = "harness-manifest.json"
MANIFEST_SCHEMA = 1
OWNERSHIPS = ("managed", "seed", "merge-required")
# installer 자신이 쓰는 경로 — manifest 항목이 차지할 수 없다.
RESERVED_PATHS = (".harness/install-state.json", ".harness/install.lock",
                  ".harness/policy.local.json")
RESERVED_DIRS = (".harness/transactions/", ".harness/runtime/")
# installer 자신(harness.py init이 import하는 모듈). update 때 마지막에 써서, 중간 크래시 뒤에도
# target installer가 가능한 한 옛 버전 그대로 남게 한다(복구는 distribution installer로도 가능).
INSTALLER_FILES = ("scripts/harness.py", "scripts/project_init.py", "scripts/runtime.py")
EXIT_OK, EXIT_ERROR, EXIT_USAGE, EXIT_RECOVERY, EXIT_MERGE, EXIT_BUSY = 0, 1, 2, 3, 4, 5
EXIT_INTERRUPTED = 130
STATE_REL = ".harness/install-state.json"
LOCK_REL = ".harness/install.lock"
TX_REL = ".harness/transactions"
STATE_SCHEMA = 1
TX_SCHEMA = 2         # 2: ownerIno(owner.lock inode) 기록 + dirs/ 생성 증거 marker


class InstallError(Exception):
    """설치기 오류. exit_code·kind는 CLI 종료코드와 JSON 보고에 쓴다."""
    exit_code = EXIT_ERROR
    kind = "error"

    def __init__(self, message, details=None):
        Exception.__init__(self, message)
        self.details = list(details or [])


class LockBusy(InstallError):
    exit_code = EXIT_BUSY
    kind = "busy"


class LockLost(InstallError):
    """획득 뒤 lock 경로가 우리가 쥔 inode를 더 이상 가리키지 않음(교체·삭제). flock은 경로 교체를 막지
    못하므로(새 inode에 두 번째 holder가 생길 수 있다) 매 전이·쓰기 직전에 재확인하고 잃으면 멈춘다."""
    exit_code = EXIT_BUSY
    kind = "lock-lost"


class RecoveryRequired(InstallError):
    exit_code = EXIT_RECOVERY
    kind = "recovery-required"


class Conflict(InstallError):
    exit_code = EXIT_MERGE
    kind = "conflict"


class RecoveryConflict(InstallError):
    exit_code = EXIT_RECOVERY
    kind = "recovery-conflict"


# 테스트가 실제 프로세스 안에서 중단·실패를 주입하는 지점(운영 입력이 아니다 — env·CLI로 켤 수 없음).
_fault_hook = None


def _fault(point, index=None, path=None):
    if _fault_hook is not None:
        _fault_hook(point, index, path)


def sha256(data):
    return hashlib.sha256(data).hexdigest()


# --- 경로·manifest -------------------------------------------------------------------

_COMPONENT_RE = re.compile(r"[^\x00-\x1f\x7f/\\]+")


def check_rel(path, what="경로"):
    """manifest·state의 상대경로 검증: 절대경로·..·.·빈 구성요소·backslash·.git 거부."""
    if not isinstance(path, str) or not path or len(path) > 512:
        raise InstallError("%s 형식 오류: %r" % (what, path))
    if path.startswith("/") or "\\" in path:
        raise InstallError("%s는 '/' 구분 상대경로여야 함: %r" % (what, path))
    for part in path.split("/"):
        if part in ("", ".", "..") or not _COMPONENT_RE.fullmatch(part):
            raise InstallError("%s에 허용하지 않는 구성요소: %r" % (what, path))
        if part.lower() == ".git":
            raise InstallError("%s가 .git 내부를 가리킴: %r" % (what, path))
    return path


def _reserved(path):
    low = path.lower()
    return low in RESERVED_PATHS or any(low.startswith(d) for d in RESERVED_DIRS)


VALIDATOR_KEYS = {"contains": ("required",), "lines": ("required",),
                  "claude-settings": ("allow", "deny", "hooks")}


def _str_list(v, what, allow_empty=False):
    if not isinstance(v, list) or (not v and not allow_empty) or not all(
            isinstance(x, str) and x for x in v):
        raise InstallError("%s는 비어 있지 않은 문자열 목록이어야 함" % what)
    return v


def _check_validator(v, path):
    if not isinstance(v, dict) or v.get("kind") not in VALIDATOR_KEYS:
        raise InstallError("%s: 알 수 없는 validator: %r" % (path, v))
    want = {"kind"} | set(VALIDATOR_KEYS[v["kind"]])
    if set(v) != want:
        raise InstallError("%s: validator key 불일치: %s" % (path, sorted(v)))
    if v["kind"] in ("contains", "lines"):
        _str_list(v["required"], "%s validator required" % path)
    else:
        _str_list(v["allow"], "%s validator allow" % path, allow_empty=True)
        _str_list(v["deny"], "%s validator deny" % path, allow_empty=True)
        if not isinstance(v["hooks"], list) or not all(
                isinstance(h, dict) and set(h) == {"event", "matcher", "command"}
                and all(isinstance(h[k], str) for k in h) for h in v["hooks"]):
            raise InstallError("%s: hooks validator 형식 오류" % path)


class Entry(object):
    def __init__(self, path, ownership, source, profiles, requirements_version=None,
                 validators=(), moved_from=None):
        self.path = path
        self.ownership = ownership
        self.source = source
        self.profiles = tuple(profiles)
        self.requirements_version = requirements_version
        self.validators = list(validators)
        self.moved_from = moved_from


class Manifest(object):
    def __init__(self, data, obj, entries):
        self.data = data
        self.sha = sha256(data)
        self.name = obj["distribution"]["name"]
        self.version = obj["distribution"]["version"]
        self.profiles = tuple(obj["profiles"])
        self.entries = entries
        self.source_only = tuple(obj["sourceOnly"])
        self.by_path = dict((e.path, e) for e in entries)


ENTRY_KEYS = ("path", "ownership", "source", "profiles", "requirementsVersion", "validators",
              "movedFrom")


def _load_entry(raw, profiles):
    if not isinstance(raw, dict) or not set(raw) <= set(ENTRY_KEYS) or "path" not in raw:
        raise InstallError("manifest entry 형식 오류: %r" % (raw,))
    path = check_rel(raw["path"], "manifest path")
    if _reserved(path):
        raise InstallError("installer 예약 경로는 manifest에 둘 수 없음: %s" % path)
    own = raw.get("ownership")
    if own not in OWNERSHIPS:
        raise InstallError("%s: 알 수 없는 ownership %r" % (path, own))
    prof = raw.get("profiles", list(profiles))
    if (not isinstance(prof, list) or not prof or len(set(prof)) != len(prof)
            or not set(prof) <= set(profiles)):
        raise InstallError("%s: profiles 오류 %r (선언: %s)" % (path, prof, list(profiles)))
    rv, validators, moved = raw.get("requirementsVersion"), raw.get("validators"), None
    if own == "managed":
        if "source" in raw or rv is not None or validators is not None:
            raise InstallError("%s: managed는 source·requirementsVersion·validators가 없다" % path)
        if set(prof) != set(profiles):
            raise InstallError("%s: managed는 모든 profile에 있어야 함(설치된 파일만으로 "
                               "profile 확장)" % path)
        source = path
        if "movedFrom" in raw:
            moved = check_rel(raw["movedFrom"], "%s movedFrom" % path)
    else:
        if "movedFrom" in raw:
            raise InstallError("%s: movedFrom은 managed만 쓸 수 있음" % path)
        source = check_rel(raw.get("source"), "%s source" % path)
        if own == "seed":
            if rv is not None or validators is not None:
                raise InstallError("%s: seed에는 requirementsVersion·validators가 없다" % path)
        else:
            if type(rv) is not int or rv < 1:
                raise InstallError("%s: merge-required는 requirementsVersion(>=1)이 필수" % path)
            if not isinstance(validators, list) or not validators:
                raise InstallError("%s: merge-required는 validators가 필수" % path)
            for v in validators:
                _check_validator(v, path)
    return Entry(path, own, source, prof, rv, validators or (), moved)


def load_manifest(data):
    """manifest bytes → Manifest. 형식·소유권 규칙을 어기면 InstallError(설치 전 전체 거부)."""
    obj = runtime.strict_json_loads(data, "manifest", InstallError)
    if not isinstance(obj, dict) or set(obj) != {"schemaVersion", "distribution", "profiles",
                                                 "entries", "sourceOnly"}:
        raise InstallError("manifest 최상위 key 불일치")
    if type(obj["schemaVersion"]) is not int or obj["schemaVersion"] != MANIFEST_SCHEMA:
        raise InstallError("지원하지 않는 manifest schemaVersion: %r — 더 새 installer로 실행하라"
                           % (obj["schemaVersion"],))
    dist = obj["distribution"]
    if (not isinstance(dist, dict) or set(dist) != {"name", "version"}
            or not isinstance(dist["name"], str)
            or not re.fullmatch(r"[a-z0-9][a-z0-9._-]{0,63}", dist["name"])
            or not isinstance(dist["version"], str)
            or not re.fullmatch(r"[0-9]+\.[0-9]+\.[0-9]+", dist["version"])):
        raise InstallError("manifest distribution(name·version) 형식 오류")
    profiles = obj["profiles"]
    if (not isinstance(profiles, list) or not profiles or len(set(profiles)) != len(profiles)
            or not all(isinstance(p, str) and re.fullmatch(r"[a-z][a-z0-9-]{0,31}", p)
                       for p in profiles)):
        raise InstallError("manifest profiles 형식 오류")
    if not isinstance(obj["entries"], list) or not obj["entries"]:
        raise InstallError("manifest entries가 비어 있음")
    entries = [_load_entry(raw, profiles) for raw in obj["entries"]]
    seen = {}
    for e in entries:
        key = e.path.lower()
        if key in seen:
            raise InstallError("manifest 경로 중복(대소문자 무시): %s / %s" % (seen[key], e.path))
        seen[key] = e.path
    managed = set(e.path for e in entries if e.ownership == "managed")
    for e in entries:
        if e.ownership != "managed" and e.source not in managed:
            raise InstallError("%s: source %s가 managed 항목이 아님(설치된 템플릿만 쓴다)"
                               % (e.path, e.source))
        if e.moved_from is not None and e.moved_from.lower() in seen:
            raise InstallError("%s: movedFrom %s가 현재 manifest 경로와 겹침"
                               % (e.path, e.moved_from))
    source_only = obj["sourceOnly"]
    if not isinstance(source_only, list):
        raise InstallError("manifest sourceOnly는 목록이어야 함")
    so_seen = set()
    for p in source_only:
        check_rel(p, "sourceOnly")
        if p.lower() in so_seen:
            raise InstallError("sourceOnly 중복: %s" % p)
        so_seen.add(p.lower())
    if so_seen & set(m.lower() for m in managed):
        raise InstallError("sourceOnly가 managed 경로와 겹침")
    return Manifest(data, obj, entries)


def select_entries(manifest, profile):
    if profile not in manifest.profiles:
        raise InstallError("알 수 없는 profile %r (허용: %s)"
                           % (profile, ", ".join(manifest.profiles)))
    return [e for e in manifest.entries if profile in e.profiles]


def validate_merge_file(entry, data):
    """merge-required 파일이 manifest validator(필수 marker·줄·hook/permission)를 만족하는가.
    문제 목록을 돌려준다(빈 목록 = 통과)."""
    problems = []
    try:
        text = data.decode("utf-8")
    except UnicodeDecodeError:
        return ["%s: UTF-8 텍스트가 아님" % entry.path]
    for v in entry.validators:
        if v["kind"] == "contains":
            problems += ["%s: 필수 marker 없음: %s" % (entry.path, s)
                         for s in v["required"] if s not in text]
        elif v["kind"] == "lines":
            lines = set(line.strip() for line in text.splitlines())
            problems += ["%s: 필수 줄 없음: %s" % (entry.path, s)
                         for s in v["required"] if s.strip() not in lines]
        else:
            problems += _claude_settings_problems(entry.path, data, v)
    return problems


def build_parser():
    import argparse
    p = argparse.ArgumentParser(
        prog="harness.py init",
        description="하네스 배포 설치기 — manifest 기반 init·check·update·recover")
    p.add_argument("--target", required=True, help="독립 Git root인 target 프로젝트")
    p.add_argument("--profile", help="base | ui (최초 설치 기본 base, 확장은 base→ui)")
    p.add_argument("--check", action="store_true", help="read-only 무결성 검증")
    p.add_argument("--dry-run", action="store_true", help="생성·교체·conflict 목록만 출력")
    p.add_argument("--adopt-merged", action="append", default=[], metavar="PATH",
                   help="수동 병합한 merge-required 파일을 validator 통과 시 adopted로 기록")
    p.add_argument("--update", action="store_true", help="새 distribution으로 갱신")
    p.add_argument("--from-distribution", metavar="DIR",
                   help="--update에 필수: 새 하네스 checkout(clean exact commit)")
    p.add_argument("--accept-managed-removal", action="append", default=[], metavar="PATH",
                   help="unchanged managed 파일의 remove/move를 경로별로 수락")
    p.add_argument("--adopt-managed", action="append", default=[], metavar="PATH",
                   help="seed/adopted→managed 전환: 현재 bytes가 새 source와 exact 같을 때만")
    p.add_argument("--recover", action="store_true", help="중단된 transaction 복구")
    p.add_argument("--transaction", metavar="ID", help="--recover 대상 transaction id")
    return p


# --- 파일시스템 안전 I/O -------------------------------------------------------------

class Snap(object):
    """target 경로 하나의 관측 상태. sha가 None이면 없음."""

    def __init__(self, sha=None, data=None, executable=False):
        self.sha = sha
        self.data = data
        self.executable = executable

    @property
    def absent(self):
        return self.sha is None


def _open_regular(path, what):
    """O_NOFOLLOW로 열어 regular·nlink 1을 확인하고 bytes를 돌려준다."""
    try:
        fd = os.open(str(path), os.O_RDONLY | os.O_NOFOLLOW)
    except OSError as e:
        raise InstallError("%s 열기 실패(symlink 등): %s" % (what, e))
    try:
        st = os.fstat(fd)
        if not stat.S_ISREG(st.st_mode) or st.st_nlink != 1:
            raise InstallError("%s는 regular file(nlink 1)이어야 함: %s" % (what, path))
        chunks = []
        while True:
            b = os.read(fd, 1 << 16)
            if not b:
                break
            chunks.append(b)
        return b"".join(chunks), bool(st.st_mode & 0o111)
    finally:
        os.close(fd)


def _real_parent_chain(root, rel):
    """root/rel의 상위 디렉터리 사슬을 root부터 symlink 없이 확인한다. 상위가 없으면 False(그 아래에는
    아무것도 없다), symlink·비디렉터리면 InstallError(경로 탈출·링크 공격 거부). inspect(쓰기·복원
    재검증)와 recover 임시 파일 정리가 같은 보장을 쓴다."""
    cur = Path(root)
    for part in rel.split("/")[:-1]:
        cur = cur / part
        try:
            st = os.lstat(str(cur))
        except FileNotFoundError:
            return False
        if stat.S_ISLNK(st.st_mode) or not stat.S_ISDIR(st.st_mode):
            raise InstallError("경로 상위가 실제 디렉터리가 아님(symlink 등): %s" % rel)
    return True


def inspect(root, rel):
    """root/rel을 symlink 없이 따라가며 관측한다. 상위 symlink·비디렉터리·대상 symlink·
    hardlink·디렉터리는 InstallError(경로 탈출·링크 공격 거부)."""
    check_rel(rel)
    if not _real_parent_chain(root, rel):
        return Snap()
    p = Path(root) / rel
    try:
        st = os.lstat(str(p))
    except FileNotFoundError:
        return Snap()
    if stat.S_ISLNK(st.st_mode):
        raise InstallError("대상이 symlink임: %s" % rel)
    if not stat.S_ISREG(st.st_mode):
        raise InstallError("대상이 regular file이 아님: %s" % rel)
    if st.st_nlink != 1:
        raise InstallError("대상이 hardlink임(nlink=%d): %s" % (st.st_nlink, rel))
    data, exe = _open_regular(p, rel)
    return Snap(sha256(data), data, exe)


def _fsync_dir(path):
    fd = os.open(str(path), os.O_RDONLY)
    try:
        os.fsync(fd)
    finally:
        os.close(fd)


def _write_new_file(path, data, executable=False):
    """새 파일을 O_EXCL|O_NOFOLLOW로 만든다(기존 경로·링크를 따라가지 않는다)."""
    fd = os.open(str(path), os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW,
                 0o755 if executable else 0o644)
    try:
        view = memoryview(data)
        while view:
            n = os.write(fd, view)
            view = view[n:]
        os.fsync(fd)
    finally:
        os.close(fd)


def _git(cwd, *args):
    # --no-optional-locks: status 등이 index를 refresh하며 쓰지 않게(설치 원본·target read-only)
    return subprocess.run(["git", "--no-optional-locks"] + list(args), cwd=str(cwd),
                          capture_output=True, text=True)


def _git_blob_sha1(data):
    return hashlib.sha1(b"blob %d\0" % len(data) + data).hexdigest()


def _real_dir(path, what):
    raw = Path(path)
    if raw.is_symlink() or not raw.is_dir():
        raise InstallError("%s가 실제 디렉터리가 아님: %s" % (what, raw))
    return raw.resolve()


def check_target_root(target):
    """target = 존재하는 독립 Git root(toplevel·자기 .git 디렉터리). main/detached 여부는 무관."""
    real = _real_dir(target, "target")
    top = _git(real, "rev-parse", "--show-toplevel")
    if top.returncode != 0 or Path(top.stdout.strip()).resolve() != real:
        raise InstallError("target이 Git toplevel이 아님: %s" % real)
    dot = real / ".git"
    gd = _git(real, "rev-parse", "--absolute-git-dir").stdout.strip()
    common = _git(real, "rev-parse", "--git-common-dir").stdout.strip()
    if (dot.is_symlink() or not dot.is_dir() or not gd or Path(gd).resolve() != dot.resolve()
            or not common or (real / common).resolve() != dot.resolve()):
        raise InstallError("target이 독립 Git root가 아님(linked worktree·submodule·공유 .git): %s"
                           % real)
    return real


def _not_nested(a, b, what):
    if a == b or a in b.parents or b in a.parents:
        raise InstallError("%s: target과 distribution이 같거나 서로 안에 있음" % what)


# --- distribution(설치 원본) -----------------------------------------------------------

class Distribution(object):
    def __init__(self, root, manifest, commit, payload):
        self.root = root
        self.manifest = manifest
        self.commit = commit
        self.payload = payload          # managed 경로 → (bytes, executable)

    def source(self, entry):
        return self.payload[entry.source]


def load_git_distribution(root):
    """설치 원본 checkout: clean·exact commit이고 모든 payload bytes가 그 commit의 blob과 같아야 한다."""
    root = _real_dir(root, "distribution")
    top = _git(root, "rev-parse", "--show-toplevel")
    if top.returncode != 0 or Path(top.stdout.strip()).resolve() != root:
        raise InstallError("distribution이 git checkout root가 아님: %s" % root)
    head = _git(root, "rev-parse", "--verify", "-q", "HEAD^{commit}").stdout.strip()
    if not re.fullmatch(r"[0-9a-f]{40}", head):
        raise InstallError("distribution HEAD commit이 없음: %s" % root)
    st = _git(root, "status", "--porcelain", "--untracked-files=all")
    if st.returncode != 0 or st.stdout.strip():
        raise InstallError("distribution checkout이 clean하지 않음 — exact commit만 설치한다: %s"
                           % root, details=st.stdout.splitlines()[:20])
    mdata = inspect(root, MANIFEST_NAME)
    if mdata.absent:
        raise InstallError("distribution에 %s 없음" % MANIFEST_NAME)
    manifest = load_manifest(mdata.data)
    paths = sorted(e.path for e in manifest.entries if e.ownership == "managed")
    # 검사한 commit을 고정한다 — HEAD 이름이 아니라 위에서 확인한 exact SHA로 읽는다.
    ls = subprocess.run(["git", "--no-optional-locks", "ls-tree", "-r", "-z", "--full-tree",
                         head, "--"] + paths, cwd=str(root), capture_output=True)
    tree = {}
    for rec in ls.stdout.split(b"\0"):
        if rec:
            meta, path = rec.split(b"\t", 1)
            mode, _typ, blob = meta.decode("ascii").split(" ")
            tree[path.decode("utf-8")] = (mode, blob)
    payload = {}
    for rel in paths:
        if rel not in tree or tree[rel][0] not in ("100644", "100755"):
            raise InstallError("distribution payload가 commit에 regular file로 없음: %s" % rel)
        snap = inspect(root, rel)
        if snap.absent or _git_blob_sha1(snap.data) != tree[rel][1]:
            raise InstallError("distribution payload bytes가 commit과 다름: %s" % rel)
        payload[rel] = (snap.data, tree[rel][0] == "100755")
    return Distribution(root, manifest, head, payload)


def load_installed_distribution(target, st):
    """설치된 target 자신을 원본으로 쓴다(check·profile 확장·adopt·recover — source checkout 불필요).
    설치된 manifest와 모든 managed 파일(템플릿 포함)이 state의 hash와 같아야 한다."""
    msnap = inspect(target, MANIFEST_NAME)
    if msnap.absent or msnap.sha != st["manifestHash"]:
        raise InstallError("설치된 manifest가 state의 manifestHash와 다름 — 버전 변경은 --update로만")
    manifest = load_manifest(msnap.data)
    payload, bad = {}, []
    for e in manifest.entries:
        if e.ownership != "managed":
            continue
        rec = st["files"].get(e.path)
        snap = inspect(target, e.path)
        if (rec is None or rec["ownership"] != "managed" or snap.absent
                or snap.sha != rec["installedHash"]):
            bad.append(e.path)
            continue
        payload[e.path] = (snap.data, snap.executable)
    if bad:
        raise Conflict("설치된 managed 파일이 state hash와 다름(로컬 수정·누락) — 되돌리거나 "
                       "--update --from-distribution으로 갱신", details=bad)
    return Distribution(target, manifest, st["sourceCommit"], payload)


# --- install state ---------------------------------------------------------------------

STATE_KEYS = ("schemaVersion", "distributionName", "distributionVersion", "sourceCommit",
              "manifestHash", "profile", "files", "updatedAt", "stateHash")


def _canonical(obj):
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def serialize_state(obj):
    """stateHash(자기 hash)를 붙여 publish할 bytes를 만든다."""
    body = dict((k, v) for k, v in obj.items() if k != "stateHash")
    body["stateHash"] = sha256(_canonical(body))
    return (json.dumps(body, indent=2, sort_keys=True, ensure_ascii=False) + "\n").encode("utf-8")


def _now():
    return datetime.now(timezone.utc).isoformat()


_HEX64 = re.compile(r"[0-9a-f]{64}")
STATE_FILE_KEYS = {"managed": ("ownership", "sourceHash", "installedHash"),
                   "seed": ("ownership", "status", "hash"),
                   "merge-required": ("ownership", "status", "hash", "requirementsVersion")}
STATE_STATUS = {"seed": ("created", "preexisting"), "merge-required": ("created", "adopted")}


def parse_state(data):
    """install-state bytes → dict. 중복 key·자기 hash 불일치·경로/ownership 오류는 거부."""
    obj = runtime.strict_json_loads(data, "install-state", InstallError)
    if not isinstance(obj, dict) or set(obj) != set(STATE_KEYS):
        raise InstallError("install-state key 불일치")
    if type(obj["schemaVersion"]) is not int or obj["schemaVersion"] != STATE_SCHEMA:
        raise InstallError("지원하지 않는 install-state schemaVersion: %r" % obj["schemaVersion"])
    body = dict((k, v) for k, v in obj.items() if k != "stateHash")
    try:
        canonical = _canonical(body)
    except (UnicodeError, ValueError) as e:
        raise InstallError("install-state 인코딩 오류(손상·변조): %s" % e)
    if obj["stateHash"] != sha256(canonical):
        raise InstallError("install-state 자체 hash 불일치(변조·손상)")
    if not re.fullmatch(r"[0-9a-f]{40}", str(obj["sourceCommit"])) or not _HEX64.fullmatch(
            str(obj["manifestHash"])) or not isinstance(obj["profile"], str):
        raise InstallError("install-state sourceCommit·manifestHash·profile 형식 오류")
    files = obj["files"]
    if not isinstance(files, dict):
        raise InstallError("install-state files 형식 오류")
    seen = set()
    for rel, rec in files.items():
        check_rel(rel, "install-state 경로")
        if _reserved(rel) or rel.lower() in seen:
            raise InstallError("install-state 경로 중복·예약 경로: %s" % rel)
        seen.add(rel.lower())
        own = rec.get("ownership") if isinstance(rec, dict) else None
        if own not in STATE_FILE_KEYS or set(rec) != set(STATE_FILE_KEYS[own]):
            raise InstallError("install-state 항목 형식 오류(알 수 없는 ownership 등): %s" % rel)
        for k in ("sourceHash", "installedHash", "hash"):
            if k in rec and not _HEX64.fullmatch(str(rec[k])):
                raise InstallError("install-state hash 형식 오류: %s" % rel)
        if own in STATE_STATUS and rec["status"] not in STATE_STATUS[own]:
            raise InstallError("install-state status 오류: %s" % rel)
        if own == "merge-required" and (type(rec["requirementsVersion"]) is not int
                                        or rec["requirementsVersion"] < 1):
            raise InstallError("install-state requirementsVersion 오류: %s" % rel)
    return obj


def load_state(target):
    """(state dict|None, Snap). 없으면 None."""
    snap = inspect(target, STATE_REL)
    if snap.absent:
        return None, snap
    return parse_state(snap.data), snap


def incomplete_transactions(target):
    """prepared marker는 있는데 committed·rolled-back이 없는 transaction id 목록."""
    d = target / TX_REL
    if not os.path.lexists(str(d)):
        return []
    st = os.lstat(str(d))
    if stat.S_ISLNK(st.st_mode) or not stat.S_ISDIR(st.st_mode):
        raise InstallError("transactions가 실제 디렉터리가 아님")
    out = []
    for child in sorted(os.listdir(str(d))):
        c = d / child
        if os.path.lexists(str(c / "prepared")) and not os.path.lexists(str(c / "committed")) \
                and not os.path.lexists(str(c / "rolled-back")):
            out.append(child)
    return out


def _require_no_incomplete(target):
    pending = incomplete_transactions(target)
    if pending:
        raise RecoveryRequired(
            "중단된 transaction이 있음 — 자동 진행하지 않는다. 먼저 recover: "
            "harness.py init --target %s --recover --transaction %s" % (target, pending[0]),
            details=pending)


# --- transaction -----------------------------------------------------------------------

class Action(object):
    def __init__(self, path, op, old_sha, new_sha, new_data=None, executable=False, label=None,
                 old_data=None, old_executable=False):
        self.path = path
        self.op = op                    # create | replace | remove
        self.old_sha = old_sha
        self.new_sha = new_sha
        self.new_data = new_data
        self.old_data = old_data
        self.executable = executable
        self.old_executable = old_executable
        self.label = label or op


TX_OWNER = "owner.lock"


class OwnerLock(object):
    """transaction 소유 표시 `<transaction>/owner.lock`(regular file)의 flock과 경로 동일성.

    - 실행 중인 installer는 prepare에서 O_CREAT|O_EXCL로 만들어 transaction이 끝날 때까지 쥐고, 그 inode
      번호를 intent의 `ownerIno`로 기록한다(prepared hash가 덮는다). 매 project 쓰기·commit point 전에
      경로가 아직 그 inode인지 verify()한다 — 교체되면 다른 실행이 소유를 가장할 수 있으므로 멈춘다.
    - recover는 기존 파일만 열어(만들지 않음) non-blocking flock을 잡고, 획득 직후 경로 동일성과
      `ownerIno` 일치를 확인한 뒤에만 진행하며, settle 동안에도 매 복원 전에 verify()한다. 살아 있는
      소유자가 쥐고 있으면 busy, 경로가 교체돼 기록된 inode가 아니면 소유자 생존을 판정할 수 없으므로
      recovery-conflict로 멈춘다(fail closed). owner.lock은 어느 쪽도 지우지 않는다(교체 inode 보존)."""

    def __init__(self, d):
        self.path = d / TX_OWNER
        self.fd = None
        self.ino = None

    def acquire(self, create):
        flags = os.O_RDWR | os.O_NOFOLLOW | ((os.O_CREAT | os.O_EXCL) if create else 0)
        try:
            fd = os.open(str(self.path), flags, 0o644)
        except FileNotFoundError:
            raise RecoveryConflict("transaction에 %s가 없음 — 소유 installer의 생존을 판정할 수 없어 "
                                   "진행하지 않는다(수동 확인)" % TX_OWNER,
                                   details=[self.path.parent.name])
        except OSError as e:
            raise InstallError("transaction %s를 열 수 없음(symlink 등): %s" % (TX_OWNER, e))
        ok = False
        try:
            st = os.fstat(fd)
            if not stat.S_ISREG(st.st_mode) or st.st_nlink != 1:
                raise InstallError("transaction %s가 regular file이 아님" % TX_OWNER)
            try:
                fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
            except (BlockingIOError, OSError):
                raise LockBusy("transaction %s를 실행 중인 installer가 아직 살아 있음 — 다른 실행은 "
                               "확정·rollback하지 않는다" % self.path.parent.name)
            self.fd = fd
            self.verify()                   # 열기와 flock 사이에 경로가 바뀌었으면 멈춘다
            ok = True
        finally:
            if not ok:
                self.fd = None
                os.close(fd)
        self.ino = st.st_ino
        return st.st_ino

    def owns_path(self):
        if self.fd is None:
            return False
        try:
            now = os.lstat(str(self.path))
        except (FileNotFoundError, NotADirectoryError):
            return False
        held = os.fstat(self.fd)
        return (now.st_ino, now.st_dev) == (held.st_ino, held.st_dev)

    def verify(self):
        if not self.owns_path():
            raise LockLost("transaction %s 경로가 이 실행이 쥔 inode를 더 이상 가리키지 않음(교체·삭제) — "
                           "다른 실행이 소유를 가장할 수 있어 멈춘다(fail closed)" % TX_OWNER)

    def check_recorded(self, ino):
        """recover: 잡은 owner.lock이 transaction이 기록한 inode인가. 아니면 경로가 교체된 것이다 —
        진짜 소유자가 살아 있는지 알 수 없으므로 진행하지 않는다."""
        if self.ino != ino:
            raise RecoveryConflict("transaction %s가 intent에 기록된 inode가 아님(경로 교체) — 소유 "
                                   "installer의 생존을 판정할 수 없어 복구하지 않는다(수동 확인)" % TX_OWNER,
                                   details=[self.path.parent.name])

    def release(self):
        if self.fd is not None:
            os.close(self.fd)
            self.fd = None


def _tx_id():
    """시간순으로 정렬되는 id(마이크로초) + 충돌 방지 난수."""
    return "%s-%s" % (datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ"),
                      os.urandom(4).hex())


def _ensure_harness_dir(target):
    d = target / ".harness"
    try:
        st = os.lstat(str(d))
    except FileNotFoundError:
        return None
    if stat.S_ISLNK(st.st_mode) or not stat.S_ISDIR(st.st_mode):
        raise InstallError(".harness가 실제 디렉터리가 아님(symlink 등): %s" % d)
    return d


def _mkdir_real(path):
    try:
        os.mkdir(str(path))
    except FileExistsError:
        pass
    st = os.lstat(str(path))
    if stat.S_ISLNK(st.st_mode) or not stat.S_ISDIR(st.st_mode):
        raise InstallError("디렉터리가 아님(symlink 등): %s" % path)


def _missing_dirs(target, rel):
    out = []
    parts = rel.split("/")[:-1]
    for i in range(1, len(parts) + 1):
        d = "/".join(parts[:i])
        if not os.path.lexists(str(target / d)):
            out.append(d)
    return out


class Transaction(object):
    """다중 파일 쓰기: backup·의도·prepared marker를 먼저 완성한 뒤 적용, state publish가 commit point."""

    def __init__(self, target, operation, actions, observed, prev_state, new_state_bytes, lock):
        self.target = target
        self.lock = lock                # TargetLock — 매 쓰기·commit point 직전 경로 동일성 재확인
        self.id = _tx_id()
        self.dir = target / TX_REL / self.id
        self.operation = operation
        self.actions = actions
        self.observed = observed        # 경로 → preflight에서 본 sha(None=없음)
        self.prev_state = prev_state    # Snap
        self.new_state = new_state_bytes
        dirs = []
        for a in actions:
            if a.op != "remove":
                for d in _missing_dirs(target, a.path):
                    if d not in dirs:
                        dirs.append(d)
        self.create_dirs = sorted(dirs, key=lambda d: (d.count("/"), d))
        self.made_dirs = {}             # createDirs 색인 → 이 실행이 mkdir로 만든 inode(메모리 증거)

    def prepare(self):
        hd = _ensure_harness_dir(self.target)
        if hd is None:
            raise InstallError(".harness 디렉터리 없음(lock 전 준비 실패)")
        _mkdir_real(self.target / TX_REL)
        os.mkdir(str(self.dir))
        self.owner = OwnerLock(self.dir)
        owner_ino = self.owner.acquire(create=True)     # transaction 끝까지 쥔다(inode는 intent에 기록)
        for sub in ("old", "new", "dirs"):     # dirs/: 디렉터리 생성 증거 marker(쓰기 중 기록)
            os.mkdir(str(self.dir / sub))
        recs = []
        for i, a in enumerate(self.actions):
            if a.op in ("replace", "remove"):
                _write_new_file(self.dir / "old" / str(i), a.old_data, a.old_executable)
            if a.op in ("create", "replace"):
                _write_new_file(self.dir / "new" / str(i), a.new_data, a.executable)
            recs.append({"path": a.path, "op": a.op, "oldSha": a.old_sha, "newSha": a.new_sha,
                         "executable": a.executable, "oldExecutable": a.old_executable,
                         "label": a.label})
        if not self.prev_state.absent:
            _write_new_file(self.dir / "prev-state.json", self.prev_state.data)
        _write_new_file(self.dir / "new-state.json", self.new_state)
        intent = {"schemaVersion": TX_SCHEMA, "id": self.id, "operation": self.operation,
                  "createdAt": _now(), "actions": recs, "createDirs": self.create_dirs,
                  "observed": self.observed, "prevStateSha": self.prev_state.sha,
                  "newStateSha": sha256(self.new_state), "ownerIno": owner_ino}
        data = (json.dumps(intent, indent=2, sort_keys=True, ensure_ascii=False) + "\n").encode(
            "utf-8")
        _write_new_file(self.dir / "intent.json", data)
        for sub in ("old", "new", "dirs"):
            _fsync_dir(self.dir / sub)
        _fsync_dir(self.dir)
        _write_new_file(self.dir / "prepared", (sha256(data) + "\n").encode("ascii"))
        _fsync_dir(self.dir)
        _fsync_dir(self.target / TX_REL)
        self.intent = intent

    def _tmp_name(self, rel):
        p = self.target / rel
        return p.with_name(".%s.harness-tmp-%s" % (p.name, self.id))

    def _verify(self, applied):
        """각 write 직전: preflight가 본 모든 경로를 다시 본다(외부 변경이면 중단)."""
        done = dict((a.path, a.new_sha) for a in self.actions[:applied])
        for rel, seen in sorted(self.observed.items()):
            want = done[rel] if rel in done else seen
            try:
                cur = inspect(self.target, rel).sha
            except InstallError as e:
                raise InstallError("preflight 뒤 경로가 바뀜: %s (%s)" % (rel, e))
            if cur != want:
                raise InstallError("preflight 뒤 외부 변경 감지: %s" % rel)
        cur_state = inspect(self.target, STATE_REL).sha
        if cur_state != self.prev_state.sha:
            raise InstallError("preflight 뒤 install-state가 바뀜")

    def _make_dir(self, k, rel):
        """createDirs[k]를 만든다. mkdir가 **이 실행에서 성공했을 때만** 그 inode를 증거로 남긴다
        (메모리 + `dirs/<k>` marker). 그 사이 외부가 만든 디렉터리는 증거가 없으므로 rollback이 지우지 않는다."""
        p = self.target / rel
        try:
            os.mkdir(str(p))
        except FileExistsError:
            _mkdir_real(p)              # 외부가 만든 디렉터리: 실제 디렉터리인지만 확인(소유 아님)
            return
        st = os.lstat(str(p))
        if stat.S_ISLNK(st.st_mode) or not stat.S_ISDIR(st.st_mode):
            raise InstallError("디렉터리가 아님(symlink 등): %s" % p)
        self.made_dirs[k] = st.st_ino
        _write_new_file(self.dir / "dirs" / str(k), ("%d\n" % st.st_ino).encode("ascii"))
        _fsync_dir(self.dir / "dirs")

    def _write(self, a):
        for k, d in enumerate(self.create_dirs):
            if a.path.startswith(d + "/") and not os.path.lexists(str(self.target / d)):
                self._make_dir(k, d)
        p = self.target / a.path
        tmp = self._tmp_name(a.path)
        _write_new_file(tmp, a.new_data, a.executable)
        if a.op == "create":
            try:
                os.link(str(tmp), str(p))       # 없을 때만 만든다(그 사이 생긴 파일을 덮지 않음)
            except FileExistsError:
                os.unlink(str(tmp))
                raise InstallError("생성 직전에 외부에서 파일이 생김: %s" % a.path)
            os.unlink(str(tmp))
        else:
            os.replace(str(tmp), str(p))
        _fsync_dir(p.parent)

    def apply(self):
        self.applied, self.in_flight = 0, None
        for i, a in enumerate(self.actions):
            _fault("before-write", i, a.path)
            self._verify(i)
            self._hold()                    # lock을 잃었으면 이 경로를 쓰지 않는다
            self.in_flight = i              # 재검증을 통과해 이 경로를 쓰기 시작한다
            if a.op == "remove":
                os.unlink(str(self.target / a.path))
                _fsync_dir((self.target / a.path).parent)
            else:
                self._write(a)
            self.applied, self.in_flight = i + 1, None
            _fault("after-write", i, a.path)
        _fault("before-state")
        self._verify(len(self.actions))
        self._hold()                        # commit point 직전: lock을 잃은 실행은 publish하지 않는다
        tmp = self.target / ".harness" / (".install-state.json.tmp-%s" % self.id)
        _write_new_file(tmp, self.new_state)
        os.replace(str(tmp), str(self.target / STATE_REL))     # commit point
        _fsync_dir(self.target / ".harness")
        _fault("after-state")
        _write_new_file(self.dir / "committed", b"committed\n")
        _fsync_dir(self.dir)

    def run(self):
        """prepare → apply. 실패·SIGINT면 commit point(state hash)로 판정해 확정하거나 rollback한다."""
        self.lock.verify()                  # preflight → prepare 전이
        self.owner = None
        try:
            return self._run()
        finally:
            if self.owner is not None:      # 확정·rollback이 끝난 뒤에야 owner lock을 놓는다
                self.owner.release()

    def _hold(self):
        """매 project 쓰기·삭제·commit point 직전: target lock과 owner.lock이 아직 이 실행의 inode인가."""
        self.lock.verify()
        self.owner.verify()

    def _run(self):
        self.prepare()
        self.applied, self.in_flight = 0, None
        try:
            self.apply()
        except BaseException as exc:
            with _signals_ignored():
                try:
                    outcome = settle(self.target, self.id, applied=self.applied,
                                     in_flight=self.in_flight, made_dirs=self.made_dirs)
                except Exception as e2:   # InstallError·OSError 모두 — transaction은 미완료로 남는다
                    raise RecoveryRequired(
                        "자동 rollback 실패 — 수동 확인 뒤 harness.py init --target %s --recover "
                        "--transaction %s" % (self.target, self.id),
                        details=[str(e2)] + list(getattr(e2, "details", [])))
            if outcome == "committed":
                return "committed"
            note = "transaction %s rollback 완료(이전 bytes·state 복원)" % self.id
            if isinstance(exc, InstallError):
                exc.details.append(note)
                raise
            if isinstance(exc, Exception):
                raise InstallError("설치 중 실패 — %s: %s" % (note, exc))
            exc.rolled_back = note
            raise
        return "committed"


class _signals_ignored(object):
    """rollback·복구 중에는 SIGINT·SIGTERM으로 다시 끊기지 않게 한다(main thread만)."""

    def __enter__(self):
        self.saved = []
        for s in (signal.SIGINT, signal.SIGTERM):
            try:
                self.saved.append((s, signal.signal(s, signal.SIG_IGN)))
            except ValueError:
                pass
        return self

    def __exit__(self, *exc):
        for s, h in self.saved:
            signal.signal(s, h)
        return False


TX_ID_RE = re.compile(r"[0-9]{8}T[0-9]{12}Z-[0-9a-f]{8}")


def _check_tx_id(txid):
    if not isinstance(txid, str) or not TX_ID_RE.fullmatch(txid):
        raise InstallError("transaction id 형식 오류: %r" % (txid,))


def _tx_dir(target, txid):
    _check_tx_id(txid)
    d = target / TX_REL / txid
    try:
        st = os.lstat(str(d))
    except FileNotFoundError:
        raise InstallError("transaction 없음: %s" % txid)
    if stat.S_ISLNK(st.st_mode) or not stat.S_ISDIR(st.st_mode):
        raise InstallError("transaction 디렉터리가 실제 디렉터리가 아님: %s" % txid)
    return d


def _sha_or_none(v):
    return v is None or (isinstance(v, str) and bool(_HEX64.fullmatch(v)))


TX_KEYS = frozenset(["schemaVersion", "id", "operation", "createdAt", "actions", "createDirs",
                     "observed", "prevStateSha", "newStateSha", "ownerIno"])
TX_ACTION_KEYS = frozenset(["path", "op", "oldSha", "newSha", "executable", "oldExecutable",
                            "label"])
TX_OP_HASHES = {"create": (False, True), "replace": (True, True), "remove": (True, False)}


def _tx_path(rel, what):
    check_rel(rel, what)
    if _reserved(rel) or _reserved(rel + "/"):
        raise InstallError("%s가 installer 예약 경로를 가리킴: %r" % (what, rel))
    return rel


def load_transaction(target, txid):
    """prepared marker·intent·backup hash를 검증해 (intent, old bytes{i}, dir)를 돌려준다.

    intent는 엄격히 읽는다(모호하면 아무것도 건드리지 않고 거부 — fail closed): 최상위·action 키 정확히,
    schemaVersion·operation, op별 hash 유무(create: old 없음·new 있음 / replace: 둘 다 / remove: old만),
    action oldSha == preflight 관측(observed), 경로 중복(대소문자 무시)·installer 예약 경로 거부,
    old/·new/ backup 기록은 action이 요구하는 색인과 정확히 같은 집합(여분·누락·잘못된 항목 거부),
    createDirs는 create/replace 경로의 상위 디렉터리만, prev/new state backup hash 일치."""
    d = _tx_dir(target, txid)
    snap_i = inspect(d, "intent.json")
    snap_p = inspect(d, "prepared")
    if snap_i.absent or snap_p.absent:
        raise InstallError("prepared transaction이 아님(준비 미완료): %s" % txid)
    if snap_p.data.decode("ascii", "replace").strip() != snap_i.sha:
        raise InstallError("prepared marker가 intent와 맞지 않음(손상): %s" % txid)
    intent = runtime.strict_json_loads(snap_i.data, "transaction intent", InstallError)

    def bad(why):
        return InstallError("transaction intent 형식 오류(%s) — 복구하지 않는다: %s" % (why, txid))

    if not isinstance(intent, dict) or set(intent) != TX_KEYS:
        raise bad("최상위 키가 %s와 다름" % sorted(TX_KEYS))
    if type(intent["schemaVersion"]) is not int or intent["schemaVersion"] != TX_SCHEMA:
        raise bad("schemaVersion")
    if intent["id"] != txid:
        raise bad("id")
    if intent["operation"] not in ("init", "update"):
        raise bad("operation")
    if not isinstance(intent["createdAt"], str):
        raise bad("createdAt")
    if type(intent["ownerIno"]) is not int or intent["ownerIno"] <= 0:
        raise bad("ownerIno")
    if not _sha_or_none(intent["prevStateSha"]) or intent["newStateSha"] is None \
            or not _sha_or_none(intent["newStateSha"]):
        raise bad("state hash")
    observed = intent["observed"]
    if not isinstance(observed, dict):
        raise bad("observed")
    folded = set()
    for rel, seen in observed.items():
        _tx_path(rel, "transaction observed")
        if not _sha_or_none(seen) or rel.casefold() in folded:
            raise bad("observed 항목")
        folded.add(rel.casefold())
    acts = intent["actions"]
    if not isinstance(acts, list):
        raise bad("actions")
    olds, paths, want_old, want_new = {}, set(), set(), set()
    for i, a in enumerate(acts):
        if not isinstance(a, dict) or set(a) != TX_ACTION_KEYS:
            raise bad("action 키가 %s와 다름" % sorted(TX_ACTION_KEYS))
        if a["op"] not in TX_OP_HASHES:
            raise bad("action op")
        rel = _tx_path(a["path"], "transaction path")
        if rel.casefold() in paths:
            raise bad("action 경로 중복(대소문자 무시): %s" % rel)
        paths.add(rel.casefold())
        has_old, has_new = TX_OP_HASHES[a["op"]]
        for key, want in (("oldSha", has_old), ("newSha", has_new)):
            v = a[key]
            if (v is not None) != want or not _sha_or_none(v):
                raise bad("op/hash 불일치: %s %s %s" % (rel, a["op"], key))
        if type(a["executable"]) is not bool or type(a["oldExecutable"]) is not bool \
                or not isinstance(a["label"], str) or not a["label"]:
            raise bad("action 속성")
        if rel not in observed or observed[rel] != a["oldSha"]:
            raise bad("action oldSha가 preflight 관측과 다름: %s" % rel)
        if has_old:
            want_old.add(i)
        if has_new:
            want_new.add(i)
    # backup 기록은 action이 요구하는 것과 정확히 같은 집합이어야 한다 — intent에서 action을 지우고 prepared
    # hash를 다시 맞춘 변조·손상은 남은(orphan) 기록으로 드러난다. target을 건드리기 전에 확인한다.
    _check_backup_records(d, "old", want_old, txid)
    _check_backup_records(d, "new", want_new, txid)
    for i, a in enumerate(acts):
        if i in want_old:
            b = inspect(d, "old/%d" % i)
            if b.absent or b.sha != a["oldSha"]:
                raise InstallError("backup(old/%d) hash가 intent와 다름: %s" % (i, a["path"]))
            olds[i] = b.data
        if i in want_new:
            b = inspect(d, "new/%d" % i)
            if b.absent or b.sha != a["newSha"]:
                raise InstallError("backup(new/%d) hash가 intent와 다름: %s" % (i, a["path"]))
    writes = [a["path"] for a in acts if a["op"] != "remove"]
    dirs = intent["createDirs"]
    if not isinstance(dirs, list):
        raise bad("createDirs")
    seen_dirs = set()
    for rel in dirs:
        _tx_path(rel, "transaction createDirs")
        if rel.casefold() in seen_dirs or not any(w.startswith(rel + "/") for w in writes):
            raise bad("createDirs 항목이 중복이거나 쓰기 경로의 상위가 아님: %s" % rel)
        seen_dirs.add(rel.casefold())
    ps = inspect(d, "prev-state.json")
    if (intent["prevStateSha"] is None) != ps.absent or (
            not ps.absent and ps.sha != intent["prevStateSha"]):
        raise InstallError("prev-state backup이 intent와 다름: %s" % txid)
    ns = inspect(d, "new-state.json")
    if ns.absent or ns.sha != intent["newStateSha"]:
        raise InstallError("new-state backup hash 불일치: %s" % txid)
    return intent, olds, d, _load_dir_marks(d, intent, txid)


_BACKUP_NAME = re.compile(r"0|[1-9][0-9]*")


def _check_backup_records(d, sub, expected, txid):
    """`old/`·`new/`에는 action이 요구하는 색인(expected)의 regular file(nlink 1)만 **정확히** 있어야 한다.
    여분(orphan)·누락·숫자가 아닌 이름·앞자리 0(색인 별칭)·symlink·디렉터리 항목은 모호한 기록이므로
    거부한다(fail closed). 이름은 ASCII 10진수만 받으므로 대소문자·유니코드 숫자 별칭도 생기지 않는다."""
    sd = d / sub
    try:
        st = os.lstat(str(sd))
    except FileNotFoundError:
        raise InstallError("transaction backup 기록(%s/) 없음 — 복구하지 않는다: %s" % (sub, txid))
    if stat.S_ISLNK(st.st_mode) or not stat.S_ISDIR(st.st_mode):
        raise InstallError("transaction backup 기록(%s/)이 실제 디렉터리가 아님 — 복구하지 않는다: %s"
                           % (sub, txid))
    found, wrong = set(), []
    for name in os.listdir(str(sd)):
        if not _BACKUP_NAME.fullmatch(name):
            wrong.append(name)
            continue
        est = os.lstat(str(sd / name))
        if stat.S_ISLNK(est.st_mode) or not stat.S_ISREG(est.st_mode) or est.st_nlink != 1:
            wrong.append(name)
            continue
        found.add(int(name))
    extra, missing = sorted(found - expected), sorted(expected - found)
    if wrong or extra or missing:
        raise InstallError("transaction backup 기록(%s/)이 action과 정확히 맞지 않음 — 여분 %s, 누락 %s, "
                           "잘못된 항목 %s: 복구하지 않는다(%s)" % (sub, extra, missing, sorted(wrong), txid))


_DIR_MARK_NAME = re.compile(r"0|[1-9][0-9]*")
_DIR_MARK_BODY = re.compile(r"[1-9][0-9]*\n")


def _load_dir_marks(d, intent, txid):
    """`dirs/<k>` marker(이 transaction이 mkdir로 만든 createDirs[k]의 inode)를 엄격히 읽는다 — 이름은
    createDirs 색인, 내용은 inode 숫자 한 줄, regular file(nlink 1). 모호하면 복구하지 않는다(fail closed)."""
    dd = d / "dirs"
    try:
        st = os.lstat(str(dd))
    except FileNotFoundError:
        raise InstallError("transaction dirs/ 없음(손상) — 복구하지 않는다: %s" % txid)
    if stat.S_ISLNK(st.st_mode) or not stat.S_ISDIR(st.st_mode):
        raise InstallError("transaction dirs/가 실제 디렉터리가 아님: %s" % txid)
    marks = {}
    for name in sorted(os.listdir(str(dd))):
        if not _DIR_MARK_NAME.fullmatch(name) or int(name) >= len(intent["createDirs"]):
            raise InstallError("transaction dirs/ marker 이름이 createDirs 색인이 아님(%s) — 복구하지 "
                               "않는다: %s" % (name, txid))
        try:
            snap = inspect(dd, name)
        except InstallError as e:
            raise InstallError("transaction dirs/%s marker가 regular file이 아님(%s): %s" % (name, e, txid))
        text = snap.data.decode("ascii", "replace")
        if not _DIR_MARK_BODY.fullmatch(text):
            raise InstallError("transaction dirs/%s marker 형식 오류 — 복구하지 않는다: %s" % (name, txid))
        marks[int(name)] = int(text)
    return marks


def _restore_file(target, rel, data, executable, txid):
    p = target / rel
    tmp = p.with_name(".%s.harness-restore-%s" % (p.name, txid))
    if os.path.lexists(str(tmp)):
        os.unlink(str(tmp))
    _write_new_file(tmp, data, executable)
    os.replace(str(tmp), str(p))
    _fsync_dir(p.parent)


def _cleanup_tmp(target, intent, txid):
    """중단된 쓰기가 남긴 이 transaction의 임시 파일(정규 파일만)을 지운다. 쓰기·복원과 같은 경로 보장:
    **어느 것도 지우기 전에** 모든 후보의 상위 사슬이 target 안의 symlink 없는 실제 디렉터리인지 확인하고,
    아니면 아무것도 지우지 않고 recovery-conflict로 멈춘다(상위 symlink를 따라 target 밖을 지우지 않는다)."""
    rels = []
    for a in intent["actions"]:
        head, _, name = a["path"].rpartition("/")
        for kind in ("tmp", "restore"):
            tmp = ".%s.harness-%s-%s" % (name, kind, txid)
            rels.append("%s/%s" % (head, tmp) if head else tmp)
    rels.append(".harness/.install-state.json.tmp-%s" % txid)
    present = []
    for rel in rels:
        try:
            if _real_parent_chain(target, rel):
                present.append(target / rel)
        except InstallError as e:
            raise RecoveryConflict("recovery-conflict: 임시 파일 정리 경로의 상위가 target 안의 실제 "
                                   "디렉터리가 아님(symlink 등) — 아무것도 지우지 않는다",
                                   details=[str(e)])
    for p in present:
        try:
            st = os.lstat(str(p))
        except (FileNotFoundError, NotADirectoryError):
            continue
        if stat.S_ISREG(st.st_mode):
            os.unlink(str(p))


def settle(target, txid, applied=None, in_flight=None, guard=None, owner=None, made_dirs=None):
    """중단·실패한 transaction 확정. commit point = state publish:
    - 현재 state hash == newStateSha → 완료로 판정, committed marker만 보완(rollback 안 함)
    - 현재 state hash == prevStateSha → 자기 변경(현재 hash == new)만 old bytes로 rollback
    - applied=None(크래시 뒤 recover, 진행 정도 모름): 어떤 파일이든 제3의 hash면
      recovery-conflict — 아무것도 덮어쓰지 않는다.
    - applied=k(같은 프로세스 안 실패): installer가 쓴 앞의 k개와 쓰던 중이던 in_flight만 대상이다.
      그중 제3의 hash가 있으면 recovery-conflict. 아직 쓰지 않은 경로는 hash가 무엇이든(새 bytes와
      같더라도) 외부 변경이므로 건드리지 않고 보존한다.
    - applied=0·in_flight=None(같은 프로세스가 첫 project 쓰기 전에 멈춤): 되돌릴 자기 bytes가 없다 —
      state가 이전·새 state 어느 쪽도 아니어도(그 사이 외부·다른 실행의 변경) 판정·복원 없이 닫는다.
    - guard(recover: target lock·owner.lock verify): 매 복원·삭제·marker 기록 직전 호출 — lock을 잃으면
      거기서 멈추고 transaction은 미완료로 남는다(다시 recover).
    - owner(recover가 잡은 OwnerLock): intent의 ownerIno와 같은 inode여야 진행한다(교체면 fail closed).
    - 디렉터리 정리: 이 transaction이 만들었다는 **증거**(mkdir 직후 기록한 `dirs/<k>` inode marker, 같은
      프로세스면 메모리 기록)가 있고, 지금 그 경로가 같은 inode의 빈 실제 디렉터리일 때만 rmdir한다.
      intent의 createDirs에 있다는 주장만으로는 지우지 않는다."""
    def hold():
        if guard is not None:
            guard()

    d = _tx_dir(target, txid)
    for marker in ("committed", "rolled-back"):
        if os.path.lexists(str(d / marker)):
            return marker
    intent, olds, d, marks = load_transaction(target, txid)
    if owner is not None:
        owner.check_recorded(intent["ownerIno"])
    if applied == 0 and in_flight is None:
        _cleanup_tmp(target, intent, txid)
        _write_new_file(d / "rolled-back", b"rolled-back (nothing written)\n")
        _fsync_dir(d)
        return "rolled-back"
    hold()
    _cleanup_tmp(target, intent, txid)
    cur_state = inspect(target, STATE_REL).sha
    if cur_state == intent["newStateSha"]:
        hold()
        _write_new_file(d / "committed", b"committed (recovered)\n")
        _fsync_dir(d)
        return "committed"
    if cur_state != intent["prevStateSha"]:
        raise RecoveryConflict("install-state가 transaction의 이전·새 state 어느 쪽도 아님 — "
                               "덮어쓰지 않는다(수동 확인)", details=[txid])
    def ours(i):
        return applied is None or i < applied or i == in_flight

    conflicts = []
    for i, a in enumerate(intent["actions"]):
        if not ours(i):
            continue
        try:
            cur = inspect(target, a["path"]).sha
        except InstallError as e:
            conflicts.append(str(e))
            continue
        if cur not in (a["oldSha"], a["newSha"]):
            conflicts.append("%s: transaction 밖에서 바뀜(제3의 hash) — 덮어쓰지 않는다" % a["path"])
    if conflicts:
        raise RecoveryConflict("recovery-conflict: 중단 뒤 사용자가 바꾼 파일이 있음", details=conflicts)
    _fault("settle")
    for i in reversed(range(len(intent["actions"]))):
        a = intent["actions"][i]
        if not ours(i):
            continue                    # installer가 쓰지 않은 경로 — 외부 변경 보존
        cur = inspect(target, a["path"]).sha
        if cur == a["oldSha"] or cur != a["newSha"]:
            continue
        hold()                          # 매 복원·삭제 직전 lock 동일성
        if a["oldSha"] is None:
            os.unlink(str(target / a["path"]))
            _fsync_dir((target / a["path"]).parent)
        else:
            _restore_file(target, a["path"], olds[i], bool(a.get("oldExecutable")), txid)
    owned = dict(marks)
    owned.update(made_dirs or {})
    for k in sorted(owned, key=lambda k: -intent["createDirs"][k].count("/")):
        p = target / intent["createDirs"][k]
        try:
            st = os.lstat(str(p))
        except FileNotFoundError:
            continue
        if (stat.S_ISDIR(st.st_mode) and not stat.S_ISLNK(st.st_mode) and st.st_ino == owned[k]
                and not os.listdir(str(p))):
            hold()
            os.rmdir(str(p))
    hold()
    _write_new_file(d / "rolled-back", b"rolled-back\n")
    _fsync_dir(d)
    return "rolled-back"


# --- lock ------------------------------------------------------------------------------

class TargetLock(object):
    """target 단위 non-blocking 배타 lock(`.harness/install.lock`, regular file).

    프로토콜(모든 init·update·check·recover·dry-run 공통):
    - lock 파일이 없으면 만든다(새 clone·미설치 target 포함). preflight부터 끝까지 쥔다.
    - flock 뒤 경로가 같은 inode인지 재확인한다 — 다르면(교체) busy, 사라졌으면(앞 holder의 정리)
      처음부터 다시 잡는다. `.harness`가 정리로 사라져 open이 ENOENT여도 다시 시도한다.
    - flock은 경로 교체를 막지 못한다(unlink-proof 아님): 획득 뒤 lock 파일이 지워지거나 바뀌면 다른
      실행이 새 inode를 잡을 수 있다. 그래서 holder는 매 전이·project 쓰기/삭제·commit point 직전에
      verify()로 경로가 아직 자기 inode인지 확인하고, 아니면 LockLost로 멈춘다(확인과 syscall 사이의
      짧은 창은 남는다 — 문서화된 잔여 위험).
    - "이번 실행이 만든"은 O_CREAT|O_EXCL 생성 성공으로만 판정한다(이미 있으면 만들지 않는 별도 open).
    - 정리(unlink)는 이번 실행이 만든 inode만: read-only(check·dry-run·시작 전 recover)는 설치 여부와
      무관하게, 쓰는 모드는 미설치 target(install-state 없음)에서만. rename-확인-unlink로 교체 inode와
      원래 있던 lock은 지우지 않는다. 설치된 target의 lock(gitignore)은 쓰는 모드가 남긴다."""

    ATTEMPTS = 5

    def __init__(self, target):
        self.target = target
        self.fd = None
        self.created_dir = False
        self.created_file = False

    def _open(self, lp):
        """(fd, stat, created). 이번 실행이 O_CREAT|O_EXCL로 **원자적으로 만든** 경우에만 created=True —
        이미 있으면 만들지 않는 별도 경로로 기존 파일만 연다. 존재 확인과 생성 사이의 경쟁으로 남이 만든
        inode를 자기 것으로 주장(→ 정리에서 삭제)하지 않는다."""
        _fault("lock-open")
        try:
            fd = os.open(str(lp), os.O_RDWR | os.O_NOFOLLOW | os.O_CREAT | os.O_EXCL, 0o644)
            created = True
        except FileExistsError:
            try:
                fd = os.open(str(lp), os.O_RDWR | os.O_NOFOLLOW)      # 기존 파일만(만들지 않음)
            except FileNotFoundError:
                return None, None, False       # 그 사이 앞 holder가 정리하고 떠났다 — 재시도
            except OSError as e:
                raise InstallError("install.lock을 열 수 없음(symlink 등): %s" % e)
            created = False
        except FileNotFoundError:
            return None, None, False           # .harness가 다른 실행의 정리로 사라짐 — 재시도
        except OSError as e:
            raise InstallError("install.lock을 열 수 없음(symlink 등): %s" % e)
        st = os.fstat(fd)
        if not stat.S_ISREG(st.st_mode) or st.st_nlink != 1:
            os.close(fd)
            raise InstallError("install.lock이 regular file이 아님")
        return fd, st, created

    def acquire(self, create=True):
        """lock을 잡는다(없으면 만든다). 다른 installer가 쥐고 있으면 LockBusy."""
        lp = self.target / LOCK_REL
        for _ in range(self.ATTEMPTS):
            if _ensure_harness_dir(self.target) is None:
                try:
                    os.mkdir(str(self.target / ".harness"))
                    self.created_dir = True
                except FileExistsError:
                    pass
                if _ensure_harness_dir(self.target) is None:
                    continue
            fd, st, created = self._open(lp)
            if fd is None:
                continue
            _fault("lock-opened")
            try:
                fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
            except (BlockingIOError, OSError):
                os.close(fd)
                raise LockBusy("다른 installer가 이 target에서 실행 중 — 쓰지 않고 종료한다")
            try:
                now = os.lstat(str(lp))
            except (FileNotFoundError, NotADirectoryError):
                now = None
            if now is None:
                os.close(fd)                   # 앞 holder가 정리하고 떠났다 — 새로 잡는다
                continue
            if (now.st_ino, now.st_dev) != (st.st_ino, st.st_dev):
                os.close(fd)
                raise LockBusy("install.lock이 획득 중 바뀜(다른 installer) — 쓰지 않고 종료한다")
            self.fd = fd
            self.created_file = created     # O_EXCL로 만든 inode만 — 정리 대상
            return True
        raise LockBusy("install.lock을 안정적으로 잡지 못함(다른 installer와 경쟁) — 다시 실행")

    def owns_path(self):
        """lock 경로가 지금도 우리가 쥔 inode를 가리키는가(교체·삭제되지 않았는가)."""
        if self.fd is None:
            return False
        try:
            now = os.lstat(str(self.target / LOCK_REL))
        except (FileNotFoundError, NotADirectoryError):
            return False
        held = os.fstat(self.fd)
        return (now.st_ino, now.st_dev) == (held.st_ino, held.st_dev)

    def verify(self):
        """preflight→apply 전이·매 project 쓰기/삭제·state publish 직전 호출: 경로가 아직 우리 inode인가.
        아니면 LockLost — 호출자는 더 쓰지 않고 자기가 쓴 bytes만 되돌린다(교체 inode는 건드리지 않음)."""
        if not self.owns_path():
            raise LockLost("install.lock이 이 실행이 쥔 inode를 더 이상 가리키지 않음(교체·삭제) — "
                           "다른 installer가 새 lock을 쥐었을 수 있어 더 쓰지 않고 멈춘다(fail closed)")

    def _unlink_own(self):
        """경로가 우리 inode일 때만 지운다. 확인과 unlink 사이에 경로가 교체돼도 남의 inode를 지우지
        않도록, 먼저 이 실행 전용 이름으로 rename한 뒤 그 이름의 inode를 확인한다 — 우리 것이면 지우고,
        남의 것이면 같은 inode를 제자리에 되돌린다(그 사이 또 생긴 파일은 덮지 않는다)."""
        lp = self.target / LOCK_REL
        grave = lp.with_name(".install.lock.release-%d-%s" % (os.getpid(), os.urandom(4).hex()))
        try:
            os.rename(str(lp), str(grave))
        except (FileNotFoundError, NotADirectoryError):
            return False
        g = os.lstat(str(grave))
        held = os.fstat(self.fd)
        if (g.st_ino, g.st_dev) == (held.st_ino, held.st_dev):
            os.unlink(str(grave))
            return True
        try:
            if stat.S_ISDIR(g.st_mode):
                os.rename(str(grave), str(lp))
            elif os.link in os.supports_follow_symlinks:
                os.link(str(grave), str(lp), follow_symlinks=False)
                os.unlink(str(grave))
            else:
                os.link(str(grave), str(lp))
                os.unlink(str(grave))
        except OSError as e:
            print("WARNING: release 중 install.lock이 교체됨 — 옮겨진 다른 lock을 %s에 남긴다(수동 "
                  "확인): %s" % (grave, e), file=sys.stderr)
        return False

    def release(self, cleanup=False, read_only=False):
        """lock을 놓는다. 정리(unlink)는 **이번 실행이 만든 inode**이고 경로가 아직 그 inode일 때만
        한다 — 원래 있던 lock·교체된 inode는 절대 지우지 않는다(_unlink_own: rename-확인-unlink).
        read_only(check·dry-run·복구 시작 전 끝난 recover)는 설치 여부와 무관하게 정리해 target을
        byte-identical로 남기고, 그 밖의 모드는 미설치 target(install-state 없음)에서만 정리한다.
        lock을 쥔 채 unlink한 뒤 close한다."""
        if self.fd is None:
            return
        try:
            remove = self.created_file and (
                read_only or (cleanup and not os.path.lexists(str(self.target / STATE_REL))))
            if remove and self.owns_path():
                _fault("lock-release")
                if self._unlink_own() and self.created_dir:
                    try:
                        os.rmdir(str(self.target / ".harness"))
                    except OSError:
                        pass
        finally:
            os.close(self.fd)
            self.fd = None


# --- 계획(preflight) -------------------------------------------------------------------

class Plan(object):
    def __init__(self):
        self.actions = []
        self.observed = {}
        self.files = {}
        self.conflicts = []
        self.merge_needed = []
        self.needs_acceptance = []
        self.ownership_changes = []

    @property
    def blocked(self):
        return bool(self.conflicts or self.merge_needed or self.needs_acceptance)


def plan_install(target, dist, profile, prev_files, opts):
    """target 현재 상태 + (이전 state) + distribution → 행동 목록. 쓰기 없음."""
    pl = Plan()
    adopt = set(check_rel(x, "--adopt-merged") for x in getattr(opts, "adopt_merged", []) or [])
    accept = set(check_rel(x, "--accept-managed-removal")
                 for x in getattr(opts, "accept_managed_removal", []) or [])
    adopt_managed = set(check_rel(x, "--adopt-managed")
                        for x in getattr(opts, "adopt_managed", []) or [])
    used, used_accept, used_adopt_managed = set(), set(), set()

    def snap(rel):
        if rel not in pl.observed:
            pl.observed[rel] = inspect(target, rel)
        return pl.observed[rel]

    for e in sorted(select_entries(dist.manifest, profile), key=lambda x: x.path):
        cur = snap(e.path)
        data, exe = dist.source(e)
        src_sha = sha256(data)
        prev = prev_files.get(e.path)
        if prev is not None and prev["ownership"] != e.ownership:
            pl.ownership_changes.append({"path": e.path, "from": prev["ownership"],
                                         "to": e.ownership})
        if e.ownership == "managed":
            pl.files[e.path] = {"ownership": "managed", "sourceHash": src_sha,
                                "installedHash": src_sha}
            if prev is not None and prev["ownership"] == "managed":
                if cur.absent or cur.sha != prev["installedHash"]:
                    pl.conflicts.append("%s: 사용자가 수정·삭제한 managed 파일(설치 hash와 다름)"
                                        % e.path)
                elif cur.sha != src_sha:
                    pl.actions.append(Action(e.path, "replace", cur.sha, src_sha, data, exe,
                                             "replace", old_data=cur.data,
                                             old_executable=cur.executable))
            elif prev is not None:
                # seed/adopted → managed: 자동 금지. 수동 병합 뒤 --adopt-managed + exact source hash.
                if e.path in adopt_managed:
                    used_adopt_managed.add(e.path)
                    if cur.absent or cur.sha != src_sha:
                        pl.merge_needed.append(
                            "%s: --adopt-managed 거부 — 현재 bytes가 새 source와 exact 같지 않음"
                            % e.path)
                else:
                    pl.merge_needed.append(
                        "%s: %s→managed 전환은 자동으로 하지 않는다 — 새 source bytes로 수동 병합한 뒤 "
                        "--adopt-managed %s" % (e.path, prev["ownership"], e.path))
            elif cur.absent:
                pl.actions.append(Action(e.path, "create", None, src_sha, data, exe, "add"))
            elif cur.sha != src_sha:
                pl.conflicts.append("%s: managed 경로에 다른 파일이 있음(덮어쓰지 않음)" % e.path)
        elif e.ownership == "seed":
            if prev is not None and prev["ownership"] == "managed":
                # managed → seed: 현재 bytes가 이전 managed hash와 같을 때만 파일을 남긴 채 관리 중단
                if cur.absent or cur.sha != prev["installedHash"]:
                    pl.conflicts.append("%s: managed→seed 전환 — 현재 bytes가 이전 managed hash와 "
                                        "다름(로컬 수정·누락)" % e.path)
                else:
                    pl.files[e.path] = {"ownership": "seed", "status": "preexisting",
                                        "hash": cur.sha}
            elif cur.absent:
                pl.files[e.path] = {"ownership": "seed", "status": "created", "hash": src_sha}
                pl.actions.append(Action(e.path, "create", None, src_sha, data, exe, "seed"))
            elif prev is not None and prev["ownership"] == "seed":
                pl.files[e.path] = dict(prev)       # 사용자 수정은 허용·절대 덮지 않음
            else:
                pl.files[e.path] = {"ownership": "seed", "status": "preexisting",
                                    "hash": cur.sha}
        else:
            rv = e.requirements_version
            if prev is not None and prev["ownership"] == "managed":
                if cur.absent or cur.sha != prev["installedHash"]:
                    pl.conflicts.append("%s: managed→merge-required 전환 — 현재 bytes가 이전 "
                                        "managed hash와 다름" % e.path)
                else:
                    problems = validate_merge_file(e, cur.data)
                    if problems:
                        pl.merge_needed += problems
                    else:
                        pl.files[e.path] = {"ownership": "merge-required", "status": "adopted",
                                            "hash": cur.sha, "requirementsVersion": rv}
            elif cur.absent:
                pl.files[e.path] = {"ownership": "merge-required", "status": "created",
                                    "hash": src_sha, "requirementsVersion": rv}
                pl.actions.append(Action(e.path, "create", None, src_sha, data, exe, "merge"))
            else:
                problems = validate_merge_file(e, cur.data)
                if e.path in adopt:
                    used.add(e.path)
                    if problems:
                        pl.merge_needed += ["--adopt-merged 거부 — %s" % x for x in problems]
                    else:
                        pl.files[e.path] = {"ownership": "merge-required", "status": "adopted",
                                            "hash": cur.sha, "requirementsVersion": rv}
                elif (prev is not None and prev["ownership"] == "merge-required"
                      and prev["requirementsVersion"] == rv and not problems):
                    pl.files[e.path] = dict(prev)
                else:
                    pl.merge_needed.append(
                        "%s: 기존 파일이 있음 — 템플릿 %s의 하네스 블록을 수동 병합한 뒤 "
                        "--adopt-merged %s" % (e.path, e.source, e.path))
                    pl.merge_needed += problems
    # 이전 state에는 있고 새 manifest(profile)에는 없는 경로: remove 또는 move(movedFrom)
    entries = select_entries(dist.manifest, profile)
    new_paths = set(e.path for e in entries)
    moved_to = dict((e.moved_from, e.path) for e in entries if e.moved_from)
    for rel in sorted(prev_files):
        if rel in new_paths:
            continue
        old = prev_files[rel]
        cur = snap(rel)
        label = "move" if rel in moved_to else "remove"
        if old["ownership"] == "managed":
            if rel not in accept:
                pl.needs_acceptance.append(rel)
                continue
            used_accept.add(rel)
            if cur.absent:
                continue
            if cur.sha != old["installedHash"]:
                pl.conflicts.append("%s: 수정된 managed 파일은 %s 수락이 있어도 지우지 않는다"
                                    % (rel, label))
            else:
                pl.actions.append(Action(rel, "remove", cur.sha, None, None, cur.executable,
                                         label, old_data=cur.data,
                                         old_executable=cur.executable))
        else:
            if rel in accept:
                used_accept.add(rel)        # 인식하되 사용자 소유 bytes 삭제에는 쓰지 않는다
            if not cur.absent:
                pl.merge_needed.append(
                    "%s: %s 파일의 %s는 installer가 하지 않는다(사용자 소유 bytes, managed 제거 수락 "
                    "적용 안 됨) — 직접 옮기거나 지운 뒤 다시 실행"
                    % (rel, old["ownership"], "이동" if label == "move" else "제거"))
    pl.actions.sort(key=lambda a: a.path in INSTALLER_FILES)     # stable: installer 파일만 뒤로
    unused = sorted(adopt - used)
    if unused:
        raise InstallError("--adopt-merged 대상이 이 profile의 merge-required 기존 파일이 아님: %s"
                           % ", ".join(unused))
    unused = sorted(adopt_managed - used_adopt_managed)
    if unused:
        raise InstallError("--adopt-managed 대상이 이번 update의 seed/adopted→managed 전환이 아님: %s"
                           % ", ".join(unused))
    unused = sorted(accept - used_accept)
    if unused:
        raise InstallError("--accept-managed-removal 대상이 이번 update의 managed remove/move가 "
                           "아님: %s" % ", ".join(unused))
    return pl


# --- 실행 ------------------------------------------------------------------------------

def _report(**kw):
    print(json.dumps(kw, indent=2, ensure_ascii=False))


def _plan_report(pl):
    return {"actions": [{"path": a.path, "op": a.op, "label": a.label} for a in pl.actions],
            "ownershipChanges": pl.ownership_changes,
            "conflicts": pl.conflicts, "mergeNeeded": pl.merge_needed,
            "needsAcceptance": pl.needs_acceptance}


def run_init(args):
    target = check_target_root(args.target)
    lock = TargetLock(target)
    locked = lock.acquire()          # dry-run·미설치 target도 preflight부터 lock을 쥔다
    prepared = False
    try:
        _fault("after-lock")
        _require_no_incomplete(target)
        st, st_snap = load_state(target)
        if st is None:
            profile = args.profile or "base"
            dist = load_git_distribution(ROOT)
            _not_nested(target, dist.root, "init")
            prev_files = {}
        else:
            # 설치된 target: 설치된 manifest·템플릿만 쓴다(source checkout 불필요).
            profile = args.profile or st["profile"]
            dist = load_installed_distribution(target, st)
            prev_files = st["files"]
            if profile != st["profile"]:
                # profile 확장(예: base→ui)만 허용 — 기존 항목을 모두 포함해야 한다.
                new_paths = set(e.path for e in select_entries(dist.manifest, profile))
                if not set(prev_files) <= new_paths:
                    raise InstallError("profile 축소(%s→%s)는 지원하지 않음 — 확장만 가능"
                                       % (st["profile"], profile))
        pl = plan_install(target, dist, profile, prev_files, args)
        lock.verify()                   # preflight 결과를 보고·적용하기 전: lock을 잃었으면 fail closed
        if args.dry_run or pl.blocked:
            _report(ok=not pl.blocked, mode="init", dryRun=args.dry_run, target=str(target),
                    profile=profile, **_plan_report(pl))
            return EXIT_MERGE if pl.blocked else EXIT_OK
        if (st is not None and not pl.actions and pl.files == st["files"]
                and profile == st["profile"]):
            _report(ok=True, mode="init", target=str(target), profile=profile, changed=False,
                    message="변경 없음", **_plan_report(pl))
            return EXIT_OK
        prepared = True     # 이 뒤 실패는 transaction evidence를 남긴다(lock·.harness 정리 안 함)
        return _publish(target, "init", dist, profile, pl, st_snap, lock)
    finally:
        if locked:
            lock.release(cleanup=not prepared, read_only=args.dry_run)


def _publish(target, operation, dist, profile, pl, st_snap, lock, extra_report=None):
    """계획을 transaction으로 적용한다(prepare → 적용 → state publish(commit point) → committed)."""
    new_state = serialize_state({
        "schemaVersion": STATE_SCHEMA, "distributionName": dist.manifest.name,
        "distributionVersion": dist.manifest.version, "sourceCommit": dist.commit,
        "manifestHash": dist.manifest.sha, "profile": profile, "files": pl.files,
        "updatedAt": _now()})
    tx = Transaction(target, operation, pl.actions,
                     dict((k, v.sha) for k, v in pl.observed.items()), st_snap, new_state, lock)
    tx.run()
    rep = dict(ok=True, mode=operation, target=str(target), profile=profile, changed=True,
               transaction=tx.id, distributionVersion=dist.manifest.version, **_plan_report(pl))
    rep.update(extra_report or {})
    _report(**rep)
    return EXIT_OK


def run_update(args):
    """--update --from-distribution D: 새 distribution(clean exact commit)과 이전 state를 비교해 갱신."""
    if not args.from_distribution:
        raise InstallError("--update에는 --from-distribution <새 하네스 checkout>이 필수")
    target = check_target_root(args.target)
    lock = TargetLock(target)
    lock.acquire()                  # 전제(state 존재)도 lock 안에서 읽는다 — 새 clone·미설치 target 포함
    prepared = False
    try:
        _fault("after-lock")
        if not os.path.lexists(str(target / STATE_REL)):
            raise InstallError("설치 state 없음(%s) — update 전에 init" % STATE_REL)
        _require_no_incomplete(target)
        st, st_snap = load_state(target)
        if st is None:
            raise InstallError("install-state 없음 — update할 수 없음(먼저 init)")
        msnap = inspect(target, MANIFEST_NAME)
        if msnap.absent or msnap.sha != st["manifestHash"]:
            raise InstallError("manifestHash 불일치 — 설치된 manifest가 state와 다름")
        dist = load_git_distribution(args.from_distribution)
        _not_nested(target, dist.root, "update")
        profile = st["profile"]
        if args.profile and args.profile != profile:
            raise InstallError("--update는 설치 profile(%s)을 바꾸지 않는다" % profile)
        pl = plan_install(target, dist, profile, st["files"], args)
        lock.verify()
        if args.dry_run or pl.blocked:
            _report(ok=not pl.blocked, mode="update", dryRun=args.dry_run, target=str(target),
                    profile=profile, fromVersion=st["distributionVersion"],
                    toVersion=dist.manifest.version, **_plan_report(pl))
            return EXIT_MERGE if pl.blocked else EXIT_OK
        if (not pl.actions and pl.files == st["files"]
                and dist.manifest.sha == st["manifestHash"] and dist.commit == st["sourceCommit"]):
            _report(ok=True, mode="update", target=str(target), profile=profile, changed=False,
                    message="변경 없음", **_plan_report(pl))
            return EXIT_OK
        prepared = True     # 이 뒤 실패는 transaction evidence를 남긴다
        return _publish(target, "update", dist, profile, pl, st_snap, lock,
                        {"fromVersion": st["distributionVersion"]})
    finally:
        lock.release(cleanup=not prepared, read_only=args.dry_run)


def run_recover(args):
    """recover --transaction <id>: backup manifest·hash를 검증한 뒤 commit point로 확정·rollback."""
    if not args.transaction:
        raise InstallError("--recover에는 --transaction <id>가 필수")
    _check_tx_id(args.transaction)               # 문자열 형식만 — target은 lock 안에서 읽는다
    target = check_target_root(args.target)
    lock = TargetLock(target)
    lock.acquire()
    started = False
    try:
        _fault("after-lock")
        owner = OwnerLock(_tx_dir(target, args.transaction))
        owner.acquire(create=False)

        def guard():
            lock.verify()
            owner.verify()

        try:
            guard()
            started = True
            with _signals_ignored():
                outcome = settle(target, args.transaction, guard=guard, owner=owner)
        finally:
            owner.release()
        _report(ok=True, mode="recover", target=str(target), transaction=args.transaction,
                outcome=outcome,
                next="./.venv/bin/python scripts/harness.py init --target %s --check" % target)
        print("복구 완료(%s) — 이제 --check를 실행하라" % outcome, file=sys.stderr)
        return EXIT_OK
    finally:
        lock.release(read_only=not started)     # 복구 시작 전 실패면 이번에 만든 lock만 지운다


def run_check(args):
    """read-only: 설치 state·manifest hash·managed hash·seed 존재·merge validator·policy."""
    target = check_target_root(args.target)
    lock = TargetLock(target)
    locked = lock.acquire()          # read-only지만 lock은 쥔다(없으면 만든다 — 새 clone)
    try:
        _fault("after-lock")
        _require_no_incomplete(target)
        st, _ = load_state(target)
        if st is None:
            raise InstallError("설치 state 없음(%s) — 먼저 init" % STATE_REL)
        problems, merge = [], []
        msnap = inspect(target, MANIFEST_NAME)
        if msnap.absent or msnap.sha != st["manifestHash"]:
            raise InstallError("설치된 manifest가 state의 manifestHash와 다름")
        manifest = load_manifest(msnap.data)
        entries = dict((e.path, e) for e in select_entries(manifest, st["profile"]))
        if set(entries) != set(st["files"]):
            problems.append("state 항목과 manifest profile 항목이 다름: 누락 %s / 초과 %s"
                            % (sorted(set(entries) - set(st["files"])),
                               sorted(set(st["files"]) - set(entries))))
        for rel in sorted(set(entries) & set(st["files"])):
            e, rec = entries[rel], st["files"][rel]
            if rec["ownership"] != e.ownership:
                problems.append("%s: ownership 불일치(state %s ≠ manifest %s)"
                                % (rel, rec["ownership"], e.ownership))
                continue
            try:
                cur = inspect(target, rel)
            except InstallError as ex:
                problems.append(str(ex))
                continue
            if e.ownership == "managed":
                if cur.absent:
                    problems.append("%s: managed 파일 누락" % rel)
                elif cur.sha != rec["installedHash"]:
                    problems.append("%s: managed 파일이 설치 hash와 다름(로컬 수정)" % rel)
            elif cur.absent:
                problems.append("%s: %s 파일 누락" % (rel, e.ownership))
            elif e.ownership == "merge-required":
                merge += validate_merge_file(e, cur.data)
                if rec["requirementsVersion"] != e.requirements_version:
                    merge.append("%s: requirementsVersion %d ≠ manifest %d — 수동 병합 후 "
                                 "--adopt-merged" % (rel, rec["requirementsVersion"],
                                                     e.requirements_version))
        if runtime.POLICY_REL in entries:
            try:
                runtime.read_policy(target)
            except runtime.PolicyError as ex:
                problems.append("policy 오류: %s" % ex)
        ok = not problems and not merge
        lock.verify()                   # 검사 도중 lock을 잃었으면 결과를 믿지 않는다(fail closed)
        _report(ok=ok, mode="check", target=str(target), profile=st["profile"],
                distributionVersion=st["distributionVersion"], sourceCommit=st["sourceCommit"],
                problems=problems, mergeNeeded=merge)
        if problems:
            return EXIT_ERROR
        return EXIT_MERGE if merge else EXIT_OK
    finally:
        if locked:
            lock.release(read_only=True)  # 이번에 만든 lock inode만 지워 byte-identical로 남긴다


class Terminated(BaseException):
    pass


def _on_sigterm(signum, frame):
    raise Terminated()


def main(argv=None):
    runtime.require_runtime()
    args = build_parser().parse_args(argv)
    signal.signal(signal.SIGTERM, _on_sigterm)
    try:
        if args.recover:
            return run_recover(args)
        if args.transaction:
            raise InstallError("--transaction은 --recover와 함께 쓴다")
        if args.check:
            return run_check(args)
        if args.update:
            return run_update(args)
        if args.from_distribution:
            raise InstallError("--from-distribution은 --update에서만 쓴다")
        return run_init(args)
    except InstallError as e:
        _report(ok=False, kind=e.kind, error=str(e), details=e.details)
        print("ERROR: %s" % e, file=sys.stderr)
        return e.exit_code
    except (OSError, ValueError) as e:
        # 권한·디스크·git 실행 실패 등: traceback 대신 보고(쓰기 중이었다면 transaction이 이미 처리)
        _report(ok=False, kind="error", error="%s: %s" % (type(e).__name__, e), details=[])
        print("ERROR: %s: %s" % (type(e).__name__, e), file=sys.stderr)
        return EXIT_ERROR
    except (KeyboardInterrupt, Terminated) as e:
        note = getattr(e, "rolled_back", "")
        _report(ok=False, kind="interrupted", error="중단됨", details=[note] if note else [])
        print("ERROR: 중단됨 %s" % note, file=sys.stderr)
        return EXIT_INTERRUPTED


def _claude_settings_problems(path, data, v):
    try:
        obj = runtime.strict_json_loads(data, path, InstallError)
    except InstallError as e:
        return [str(e)]
    if not isinstance(obj, dict):
        return ["%s: JSON 객체가 아님" % path]
    perms = obj.get("permissions") if isinstance(obj.get("permissions"), dict) else {}
    problems = []
    for key in ("allow", "deny"):
        have = perms.get(key) if isinstance(perms.get(key), list) else []
        problems += ["%s: permissions.%s 누락: %s" % (path, key, s)
                     for s in v[key] if s not in have]
    hooks = obj.get("hooks") if isinstance(obj.get("hooks"), dict) else {}
    for h in v["hooks"]:
        groups = hooks.get(h["event"]) if isinstance(hooks.get(h["event"]), list) else []
        found = any(
            isinstance(g, dict) and g.get("matcher") == h["matcher"]
            and isinstance(g.get("hooks"), list)
            and any(isinstance(x, dict) and x.get("type") == "command"
                    and x.get("command") == h["command"] for x in g["hooks"])
            for g in groups)
        if not found:
            problems.append("%s: hook 누락: %s[%s] %s" % (path, h["event"], h["matcher"],
                                                         h["command"]))
    return problems


if __name__ == "__main__":
    sys.exit(main())
