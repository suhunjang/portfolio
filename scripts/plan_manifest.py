"""단일 canonical plan manifest — plan review·approval·execute가 **모두** 이 함수를 쓴다.

hash 대상:
  - 확정 설계 문서 1개(index.json `designDoc`, docs/superpowers/specs/ 아래)
  - phases/<task>/index.json의 불변 필드(project, phase, baseBranch, reviewExclude,
    designDoc, allowedPaths, testCommand)와 각 step의 step·name
  - index에 열거된 모든 stepN.md의 경로·종류·bytes
제외(단, 허용 필드 schema로 제한): status·summary·timestamp·error·reviewBaseSha.

모든 계획 파일은 regular file이어야 한다 — symlink·hardlink·symlink 상위 디렉터리 거부.
3.9에서도 파싱되어야 한다(launcher가 명확히 거부하기 위해) — 3.10+ 문법 금지.
"""
import hashlib
import json
import os
import re
import stat
from pathlib import Path

VERSION = 1
SPECS_PREFIX = "docs/superpowers/specs/"
IMMUTABLE_TOP = ("project", "phase", "baseBranch", "reviewExclude", "designDoc",
                 "allowedPaths", "testCommand")
REQUIRED_TOP = ("project", "phase", "baseBranch", "designDoc", "allowedPaths", "testCommand",
                "steps")
MUTABLE_TOP = ("status", "review_reason", "review_at", "created_at", "completed_at",
               "reviewBaseSha")
STEP_MUTABLE = ("status", "summary", "started_at", "completed_at", "failed_at", "blocked_at",
                "error_message", "blocked_reason")
STEP_STATUSES = ("pending", "completed", "error", "blocked")
PHASE_STATUSES = ("pending", "completed", "error", "blocked", "needs-review")
# 구현 에이전트가 절대 쓸 수 없는 경로(allowedPaths가 덮으면 거부).
PROTECTED_PREFIXES = (".git/", "phases/", "scripts/", ".claude/", ".codex/", ".harness/",
                      ".venv/", SPECS_PREFIX)
PROTECTED_FILES = ("CLAUDE.md", ".gitignore", ".gitattributes", "pytest.ini",
                   ".python-version")
_TASK_RE = re.compile(r"[A-Za-z0-9][A-Za-z0-9._-]*")
_STEP_FILE_RE = re.compile(r"step(\d+)\.md")
_STEPLIKE_RE = re.compile(r"step.*\.md", re.IGNORECASE)
_KEBAB = re.compile(r"[a-z0-9]+(-[a-z0-9]+)*")
_SHA40 = re.compile(r"[0-9a-f]{40}")


class ManifestError(Exception):
    pass


class Manifest:
    def __init__(self, manifest, canonical, files):
        self.manifest = manifest
        self.canonical = canonical
        self.files = files  # rel -> bytes
        self.sha = hashlib.sha256(canonical).hexdigest()

    def read(self, rel):
        if rel not in self.files:
            raise ManifestError("manifest에 없는 파일: %s" % rel)
        return self.files[rel]

    @property
    def index(self):
        return self.manifest["index"]


def code_sha():
    return hashlib.sha256(Path(__file__).read_bytes()).hexdigest()


def canonical_bytes(obj):
    return json.dumps(obj, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=False).encode("utf-8")


def _safe_rel(rel):
    if not isinstance(rel, str) or not rel or rel.startswith("/") or "\\" in rel:
        return False
    parts = rel.rstrip("/").split("/")
    return all(p not in ("", ".", "..") for p in parts)


def path_allowed(rel, allowed):
    """rel(파일 경로)이 allowedPaths 안인가. 'dir/'는 하위 전체, 그 외는 정확히 그 파일."""
    for a in allowed:
        if a.endswith("/"):
            if rel.startswith(a):
                return True
        elif rel == a:
            return True
    return False


def _allowed_paths_error(allowed):
    if not isinstance(allowed, list) or not allowed:
        return "allowedPaths는 비어 있지 않은 목록이어야 함"
    for a in allowed:
        if not _safe_rel(a):
            return "allowedPaths 항목이 안전한 상대경로가 아님: %r" % (a,)
        probe = a if a.endswith("/") else a + "/"
        for p in PROTECTED_PREFIXES:
            # 보호 경로를 포함하거나(상위) 보호 경로 안이면(하위) 거부
            if p.startswith(probe) or probe.startswith(p):
                return "allowedPaths가 보호 경로 %s와 겹침: %r" % (p, a)
        for f in PROTECTED_FILES:
            if a == f or (a.endswith("/") and f.startswith(a)):
                return "allowedPaths가 보호 파일 %s와 겹침: %r" % (f, a)
    return None


def read_regular(root, rel):
    """root/rel을 regular file로만 읽는다. 상위 디렉터리 symlink·hardlink 거부."""
    if not _safe_rel(rel):
        raise ManifestError("안전하지 않은 경로: %r" % (rel,))
    root = Path(root)
    cur = root
    parts = rel.split("/")
    for part in parts[:-1]:
        cur = cur / part
        try:
            st = os.lstat(cur)
        except OSError:
            raise ManifestError("디렉터리 없음: %s" % cur.relative_to(root))
        if not stat.S_ISDIR(st.st_mode):
            raise ManifestError("디렉터리가 아님(symlink 등): %s" % cur.relative_to(root))
    path = root / rel
    try:
        st = os.lstat(path)
    except OSError:
        raise ManifestError("파일 없음: %s" % rel)
    if not stat.S_ISREG(st.st_mode):
        raise ManifestError("regular file이 아님(symlink 등): %s" % rel)
    if st.st_nlink != 1:
        raise ManifestError("hardlink 파일 거부(nlink=%d): %s" % (st.st_nlink, rel))
    fd = os.open(str(path), os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0))
    try:
        with os.fdopen(fd, "rb") as f:
            data = f.read()
    except OSError as e:
        raise ManifestError("읽기 실패 %s: %s" % (rel, e))
    return data


def validate_index(index, task):
    """index.json schema 검증. 오류 시 ManifestError."""
    if not isinstance(index, dict):
        raise ManifestError("index.json이 객체가 아님")
    unknown = set(index) - set(IMMUTABLE_TOP) - set(MUTABLE_TOP) - {"steps"}
    if unknown:
        raise ManifestError("index.json에 허용되지 않은 필드: %s" % sorted(unknown))
    for k in REQUIRED_TOP:
        if k not in index:
            raise ManifestError("index.json 필수 필드 없음: %s" % k)
    for k in ("project", "phase", "baseBranch"):
        if not isinstance(index[k], str) or not index[k].strip():
            raise ManifestError("%s는 비어 있지 않은 문자열이어야 함" % k)
    design = index["designDoc"]
    if not (_safe_rel(design) and design.startswith(SPECS_PREFIX) and design.endswith(".md")):
        raise ManifestError("designDoc은 %s*.md 여야 함: %r" % (SPECS_PREFIX, design))
    err = _allowed_paths_error(index["allowedPaths"])
    if err:
        raise ManifestError(err)
    tc = index["testCommand"]
    if not (isinstance(tc, list) and tc and all(isinstance(x, str) and x for x in tc)):
        raise ManifestError("testCommand는 비어 있지 않은 문자열 argv 목록이어야 함")
    rex = index.get("reviewExclude", [])
    if not isinstance(rex, list) or not all(
            isinstance(r, dict) and set(r) == {"glob", "reason"}
            and isinstance(r["glob"], str) and r["glob"].strip()
            and isinstance(r["reason"], str) and r["reason"].strip() for r in rex):
        raise ManifestError("reviewExclude 형식 오류(glob·reason 필수)")
    if "status" in index and index["status"] not in PHASE_STATUSES:
        raise ManifestError("phase status 값 오류: %r" % (index["status"],))
    for k in ("review_reason", "review_at", "created_at", "completed_at"):
        if k in index and not isinstance(index[k], str):
            raise ManifestError("%s는 문자열이어야 함" % k)
    if "reviewBaseSha" in index and not (
            isinstance(index["reviewBaseSha"], str) and _SHA40.fullmatch(index["reviewBaseSha"])):
        raise ManifestError("reviewBaseSha는 40자 hex여야 함")
    steps = index["steps"]
    if not isinstance(steps, list) or not steps:
        raise ManifestError("steps가 비어 있음")
    for i, s in enumerate(steps):
        if not isinstance(s, dict):
            raise ManifestError("step %d가 객체가 아님" % i)
        bad = set(s) - {"step", "name"} - set(STEP_MUTABLE)
        if bad:
            raise ManifestError("step %d에 허용되지 않은 필드: %s" % (i, sorted(bad)))
        if type(s.get("step")) is not int or s["step"] != i:
            raise ManifestError("step 번호는 0부터 연속이어야 함(위치 %d: %r)" % (i, s.get("step")))
        if not isinstance(s.get("name"), str) or not _KEBAB.fullmatch(s["name"]):
            raise ManifestError("step %d name이 kebab-case가 아님" % i)
        if s.get("status", "pending") not in STEP_STATUSES:
            raise ManifestError("step %d status 값 오류: %r" % (i, s.get("status")))
        for k in STEP_MUTABLE:
            if k != "status" and k in s and not isinstance(s[k], str):
                raise ManifestError("step %d %s는 문자열이어야 함" % (i, k))


def _check_task(task):
    if not isinstance(task, str) or not _TASK_RE.fullmatch(task) or task in (".", ".."):
        raise ManifestError("task 이름이 안전하지 않음: %r" % (task,))


def build_manifest(root, task):
    _check_task(task)
    root = Path(root)
    task_dir = "phases/%s" % task
    index_rel = task_dir + "/index.json"
    raw = read_regular(root, index_rel)
    try:
        index = json.loads(raw.decode("utf-8"))
    except (ValueError, UnicodeDecodeError) as e:
        raise ManifestError("index.json 파싱 실패: %s" % e)
    validate_index(index, task)
    n = len(index["steps"])
    listed = {"step%d.md" % i for i in range(n)}
    for entry in os.listdir(root / task_dir):
        if _STEPLIKE_RE.fullmatch(entry) and entry not in listed:
            raise ManifestError("index에 없는 step 파일: %s/%s" % (task_dir, entry))
    files = {}
    for i in range(n):
        rel = "%s/step%d.md" % (task_dir, i)
        files[rel] = read_regular(root, rel)
    files[index["designDoc"]] = read_regular(root, index["designDoc"])
    immutable = {k: index.get(k, [] if k == "reviewExclude" else None) for k in IMMUTABLE_TOP}
    immutable["steps"] = [{"step": s["step"], "name": s["name"]} for s in index["steps"]]
    manifest = {
        "version": VERSION,
        "task": task,
        "index": immutable,
        "files": [{"path": rel, "type": "regular", "size": len(files[rel]),
                   "sha256": hashlib.sha256(files[rel]).hexdigest()}
                  for rel in sorted(files)],
    }
    return Manifest(manifest, canonical_bytes(manifest), files)


def verify_matches(root, task, expected_sha):
    m = build_manifest(root, task)
    if m.sha != expected_sha:
        raise ManifestError("계획 manifest hash 불일치: 현재 %s ≠ 승인 %s" % (m.sha, expected_sha))
    return m


def _make_read_only(dest):
    for dirpath, dirnames, filenames in os.walk(str(dest), topdown=False):
        for f in filenames:
            os.chmod(os.path.join(dirpath, f), 0o444)
        os.chmod(dirpath, 0o555)


def _require_real_dir(path):
    """path 자체를 lstat해 실제 디렉터리만 허용한다(symlink·비디렉터리 거부)."""
    try:
        st = os.lstat(str(path))
    except OSError as e:
        raise ManifestError("snapshot 디렉터리 확인 실패 %s: %s" % (path, e))
    if not stat.S_ISDIR(st.st_mode):
        raise ManifestError("snapshot 경로가 실제 디렉터리가 아님(symlink 등): %s" % path)


def staging_path(dest):
    """write_snapshot의 staging 디렉터리(결정적 이름 — 경계 검사 대상)."""
    dest = Path(dest)
    return dest.parent / (dest.name + ".staging")


def write_snapshot(m, dest):
    """manifest와 원문을 dest에 read-only로 복제한다. 이미 있으면 동일해야 한다.

    dest와 staging은 symlink를 따르지 않는다. staging은 배타적으로 만들며, 이미 있으면
    (symlink 포함) 거부한다 — 중단된 이전 시도의 잔재는 운영자가 확인 후 지운다."""
    dest = Path(dest)
    if os.path.lexists(str(dest)):
        _require_real_dir(dest)
        return load_snapshot(dest, m.sha)  # 다르면 ManifestError
    _require_real_dir(dest.parent)
    tmp = staging_path(dest)
    try:
        os.mkdir(str(tmp), 0o700)
    except FileExistsError:
        raise ManifestError("snapshot staging 경로가 이미 있음(symlink 등): %s" % tmp)
    os.mkdir(str(tmp / "files"), 0o700)
    with open(str(tmp / "manifest.json"), "xb") as f:
        f.write(m.canonical)
    for rel, data in m.files.items():
        if not _safe_rel(rel):
            raise ManifestError("안전하지 않은 경로: %r" % (rel,))
        p = tmp / "files" / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        with open(str(p), "xb") as f:
            f.write(data)
    _make_read_only(tmp)
    os.rename(str(tmp), str(dest))
    return load_snapshot(dest, m.sha)


def load_snapshot(dest, expected_sha):
    dest = Path(dest)
    _require_real_dir(dest)
    _require_real_dir(dest / "files")
    try:
        canonical = read_regular(dest, "manifest.json")
    except ManifestError as e:
        raise ManifestError("snapshot manifest 읽기 실패: %s" % e)
    if hashlib.sha256(canonical).hexdigest() != expected_sha:
        raise ManifestError("snapshot manifest hash 불일치")
    manifest = json.loads(canonical.decode("utf-8"))
    files = {}
    for f in manifest["files"]:
        data = read_regular(dest / "files", f["path"])
        if hashlib.sha256(data).hexdigest() != f["sha256"] or len(data) != f["size"]:
            raise ManifestError("snapshot 파일 변조: %s" % f["path"])
        files[f["path"]] = data
    return Manifest(manifest, canonical, files)
