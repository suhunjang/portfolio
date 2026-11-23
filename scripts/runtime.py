"""공통 실행 환경 검증 — Python 버전·repo-local .venv·리뷰 정책·project/local policy.

project/local policy(승인자·승인 thread·issue key 규칙·리뷰 backend/model·Python 버전)는
하네스 root의 `.harness/policy.json` 하나만 입력이다. 코드에 ID·경로를 하드코딩하지 않는다.

이 파일은 Python 3.9에서도 **파싱**되어야 한다(3.9로 실행됐을 때 SyntaxError가
아니라 명확한 거부 메시지를 내기 위해서). 3.10+ 전용 문법을 쓰지 마라.
"""
import json
import os
import re
import sys
from pathlib import Path

MIN_VERSION = (3, 10)
REPO_ROOT = Path(__file__).resolve().parent.parent

# 지원하는 backend(이 코드가 실제로 띄우는 CLI). 리뷰 model 등 값은 policy가 정한다.
REQUIRED_IMPL_BACKEND = "claude"
REQUIRED_REVIEW_BACKEND = "codex"


def check_runtime(version_info=None, prefix=None, root=None):
    """오류 목록을 돌려준다. 비어 있으면 통과."""
    version_info = tuple(version_info if version_info is not None else sys.version_info)
    prefix = Path(prefix if prefix is not None else sys.prefix)
    root = Path(root if root is not None else REPO_ROOT)
    errors = []
    if version_info[:2] < MIN_VERSION:
        errors.append(
            "Python >=3.10 필요 — 현재 %s. ./.venv/bin/python 으로 실행하라."
            % ".".join(str(x) for x in version_info[:3]))
    try:
        same = prefix.resolve() == (root / ".venv").resolve()
    except OSError:
        same = False
    if not same:
        errors.append(
            "repo-local .venv 인터프리터가 아님(prefix=%s). "
            "./.venv/bin/python scripts/harness.py ... 로 실행하라." % prefix)
    return errors


def require_runtime():
    errors = check_runtime()
    if errors:
        for e in errors:
            print("ERROR: " + e, file=sys.stderr)
        sys.exit(1)


def runtime_evidence():
    return {
        "executable": sys.executable,
        "baseExecutable": getattr(sys, "_base_executable", sys.executable),
        "prefix": sys.prefix,
        "version": ".".join(str(x) for x in sys.version_info[:3]),
    }


def review_policy_errors(env=None):
    """policy(.harness/policy.json)의 구현·리뷰 backend/model을 env에 **명시**해야 한다.
    폴백·NO_GIT 금지. policy가 없거나 틀리면 그것도 오류다(fail closed)."""
    env = os.environ if env is None else env
    errors = []
    try:
        pol = policy()
    except PolicyError as e:
        pol = None
        errors.append(str(e))
    review = env.get("HARNESS_REVIEW_BACKEND", "").strip()
    model = env.get("HARNESS_REVIEW_MODEL", "").strip()
    impl = env.get("HARNESS_IMPL_BACKEND", "").strip() or REQUIRED_IMPL_BACKEND
    if pol is not None:
        if review != pol.review_backend:
            errors.append("HARNESS_REVIEW_BACKEND=%s 를 명시해야 함(현재 %r) — 폴백 없음"
                          % (pol.review_backend, review))
        if model != pol.review_model:
            errors.append("HARNESS_REVIEW_MODEL=%s 를 명시해야 함(현재 %r)"
                          % (pol.review_model, model))
        if impl != pol.impl_backend:
            errors.append("HARNESS_IMPL_BACKEND는 %s만 허용(현재 %r)" % (pol.impl_backend, impl))
    if "HARNESS_NO_GIT" in env:
        errors.append("HARNESS_NO_GIT 는 이 하네스에서 지원하지 않음 — 제거하라")
    return errors


def require_review_policy():
    errors = review_policy_errors()
    if errors:
        for e in errors:
            print("ERROR: " + e, file=sys.stderr)
        sys.exit(1)


# --- project/local policy (.harness/policy.json) -------------------------------------

class PolicyError(Exception):
    pass


def _version_tuple(text):
    return tuple(int(x) for x in text.split("."))


class Policy(object):
    """검증된 project policy. 값은 읽기 전용으로 쓴다."""

    def __init__(self, data):
        self.data = data
        self.issue_key_pattern = data["issueKeyPattern"]
        self.approver_user_ids = tuple(data["approverUserIds"])
        self.approval_thread_ids = tuple(data["approvalThreadIds"])
        self.issue_scoped_threads = dict(data["issueScopedThreads"])
        self.impl_backend = data["implBackend"]
        self.review_backend = data["reviewBackend"]
        self.review_model = data["reviewModel"]
        self.python_min_version = _version_tuple(data["pythonMinVersion"])
        self.python_recommended_version = _version_tuple(data["pythonRecommendedVersion"])
        self.issue_re, self.body_re, self.branch_re = compile_issue_regexes(
            self.issue_key_pattern)

    def issue_matches(self, issue):
        """issue key가 정책 정규식과 안전 문자 규칙을 모두 만족하는가."""
        return (isinstance(issue, str) and bool(self.issue_re.fullmatch(issue))
                and bool(_ISSUE_SAFE_RE.fullmatch(issue)))

    def thread_authorized(self, thread_id, issue):
        """전역 승인 thread는 모든 issue, issue-scoped thread는 지정 issue만."""
        if not isinstance(thread_id, str) or not isinstance(issue, str):
            return False
        if thread_id in self.approval_thread_ids:
            return True
        return self.issue_scoped_threads.get(thread_id) == issue

    def feature_branch_issue(self, branch):
        """`feat/<issue>/<slug>` branch면 issue를, 아니면 None."""
        m = self.branch_re.fullmatch(branch) if isinstance(branch, str) else None
        if not m or not self.issue_matches(m.group("issue")):
            return None
        return m.group("issue")


def _reject_duplicate_keys(pairs):
    out = {}
    for k, v in pairs:
        if k in out:
            raise ValueError("중복 JSON key: %r" % k)
        out[k] = v
    return out


def _reject_constant(name):
    raise ValueError("허용하지 않는 JSON 상수: %s" % name)


def strict_json_loads(data, what, error=ValueError):
    """UTF-8 JSON을 strict하게 읽는다: 중복 key·NaN/Infinity 거부. 실패하면 error(메시지)."""
    try:
        text = data.decode("utf-8") if isinstance(data, bytes) else data
        return json.loads(text, object_pairs_hook=_reject_duplicate_keys,
                          parse_constant=_reject_constant)
    except (UnicodeDecodeError, ValueError) as e:
        raise error("%s JSON 오류: %s" % (what, e))


POLICY_SCHEMA_VERSION = 1
POLICY_KEYS = ("schemaVersion", "issueKeyPattern", "approverUserIds", "approvalThreadIds",
               "issueScopedThreads", "implBackend", "reviewBackend", "reviewModel",
               "pythonMinVersion", "pythonRecommendedVersion")


def _require_keys(obj, required, optional, what):
    if not isinstance(obj, dict):
        raise PolicyError("%s는 JSON 객체여야 함" % what)
    keys = set(obj)
    missing = sorted(set(required) - keys)
    extra = sorted(keys - set(required) - set(optional))
    if missing or extra:
        raise PolicyError("%s key 불일치: 누락 %s / 허용 안 됨 %s (secret·임의 key 금지)"
                          % (what, missing, extra))
    v = obj.get("schemaVersion")
    if type(v) is not int or v != POLICY_SCHEMA_VERSION:
        raise PolicyError("%s schemaVersion은 %d이어야 함(현재 %r)"
                          % (what, POLICY_SCHEMA_VERSION, v))


SUPPORTED_IMPL_BACKENDS = ("claude",)
SUPPORTED_REVIEW_BACKENDS = ("codex",)
_ID_RE = re.compile(r"[A-Za-z0-9:_-]{1,80}")
_MODEL_RE = re.compile(r"[A-Za-z0-9][A-Za-z0-9._:-]{0,63}")
# 실제 issue key는 branch·evidence 경로에 들어간다 — 정책 정규식과 별개로 안전 문자만.
_ISSUE_SAFE_RE = re.compile(r"[A-Za-z0-9][A-Za-z0-9._-]{0,63}")
_SECRET_RE = re.compile(
    r"(?i)(sk-[a-z0-9]|ghp_|gho_|ghs_|github_pat_|xox[abprs]-|AKIA[0-9A-Z]{8}|AIza[0-9A-Za-z_-]{10}"
    r"|-----BEGIN|eyJ[A-Za-z0-9_-]{8,}\.|bearer\s)")


def _strings(obj):
    if isinstance(obj, str):
        yield obj
    elif isinstance(obj, dict):
        for k, v in obj.items():
            yield k
            for s in _strings(v):
                yield s
    elif isinstance(obj, list):
        for v in obj:
            for s in _strings(v):
                yield s


def _reject_secrets(obj, what):
    for s in _strings(obj):
        if _SECRET_RE.search(s):
            raise PolicyError("%s에 secret으로 보이는 값이 있음 — policy에는 secret을 두지 않는다"
                              % what)


def _id_list(obj, key):
    v = obj[key]
    if not isinstance(v, list) or not all(isinstance(x, str) and _ID_RE.fullmatch(x) for x in v):
        raise PolicyError("%s는 ID 문자열 목록이어야 함([A-Za-z0-9:_-]{1,80})" % key)
    if len(set(v)) != len(v):
        raise PolicyError("%s에 중복 ID가 있음" % key)
    return v


def _version(obj, key, parts):
    v = obj[key]
    if not isinstance(v, str) or not re.fullmatch(r"[0-9]+(\.[0-9]+){%d}" % (parts - 1), v):
        raise PolicyError("%s는 %d단 버전 문자열이어야 함(현재 %r)" % (key, parts, v))
    return _version_tuple(v)


def compile_issue_regexes(pattern):
    """issue key 정규식으로 승인 본문·feature branch 정규식을 만든다(정책 검증과 공유)."""
    if not isinstance(pattern, str) or not pattern or len(pattern) > 200:
        raise PolicyError("issueKeyPattern은 1~200자 문자열이어야 함")
    if re.search(r"\(\?(?!:)", pattern):
        # inline flag((?i) 등)는 Python 3.10에서 승인 본문 정규식 전체에 전파되고, lookaround·named
        # group은 issue 경계를 흐린다 — 비포획 그룹 (?: 만 허용한다.
        raise PolicyError("issueKeyPattern에는 (?: 외의 (?…) 구문(inline flag·lookaround·named group)을 "
                          "쓸 수 없음")
    try:
        issue = re.compile(pattern)
        body = re.compile(r"APPROVE (?P<issue>(?:%s)) PLAN (?P<plan>[0-9a-f]{40}) "
                          r"REVIEW (?P<review>[0-9a-f]{64})" % pattern)
        branch = re.compile(r"feat/(?P<issue>(?:%s))/(?P<slug>[a-z0-9][a-z0-9-]*)" % pattern)
    except re.error as e:
        raise PolicyError("issueKeyPattern 정규식 오류: %s" % e)
    if issue.fullmatch(""):
        raise PolicyError("issueKeyPattern이 빈 문자열과 일치함")
    return issue, body, branch


POLICY_REL = ".harness/policy.json"
LOCAL_POLICY_REL = ".harness/policy.local.json"
POLICY_MAX_BYTES = 1 << 16


def read_regular_file(path, what, error, max_bytes=POLICY_MAX_BYTES):
    """symlink·hardlink·상위 symlink를 따라가지 않고 regular file bytes를 읽는다."""
    import stat as _stat
    path = Path(path)
    parent = path.parent
    try:
        pst = os.lstat(str(parent))
    except FileNotFoundError:
        raise error("%s 없음: %s" % (what, path))
    if not _stat.S_ISDIR(pst.st_mode):
        raise error("%s 상위가 실제 디렉터리가 아님(symlink 등): %s" % (what, parent))
    try:
        st = os.lstat(str(path))
    except FileNotFoundError:
        raise error("%s 없음: %s" % (what, path))
    if not _stat.S_ISREG(st.st_mode) or st.st_nlink != 1:
        raise error("%s는 regular file이어야 함(symlink·hardlink 거부): %s" % (what, path))
    try:
        fd = os.open(str(path), os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0))
    except OSError as e:
        raise error("%s 열기 실패: %s" % (what, e))
    try:
        fst = os.fstat(fd)
        if (fst.st_ino, fst.st_dev) != (st.st_ino, st.st_dev) or fst.st_nlink != 1:
            raise error("%s가 읽는 중 바뀜: %s" % (what, path))
        chunks, total = [], 0
        while True:
            b = os.read(fd, 65536)
            if not b:
                break
            chunks.append(b)
            total += len(b)
            if total > max_bytes:
                raise error("%s가 너무 큼(> %d bytes): %s" % (what, max_bytes, path))
        return b"".join(chunks)
    finally:
        os.close(fd)


def read_policy(root):
    """<root>/.harness/policy.json → Policy. 없거나 형식이 틀리면 PolicyError(fail closed)."""
    path = Path(root) / POLICY_REL
    if not os.path.lexists(str(path)):
        raise PolicyError("policy 없음: %s — templates/project/.harness/policy.json을 기준으로 "
                          "승인자·thread·issue key를 채워라(harness.py init이 seed로 만든다)"
                          % path)
    return parse_policy(read_regular_file(path, "policy", PolicyError))


LOCAL_POLICY_KEYS = ("approvedBaseInterpreter", "extraProtectedPaths")


def _abs_path_str(v, what):
    if (not isinstance(v, str) or not v.startswith("/") or len(v) > 4096
            or any(c in v for c in "\x00\n\r")):
        raise PolicyError("%s는 절대경로 문자열이어야 함: %r" % (what, v))
    return v


def parse_local_policy(data):
    """policy.local.json bytes → dict. 호스트 전용 선택값만(배포하지 않는다)."""
    obj = strict_json_loads(data, "policy.local", PolicyError)
    _require_keys(obj, ("schemaVersion",), LOCAL_POLICY_KEYS, "policy.local")
    _reject_secrets(obj, "policy.local")
    out = {}
    if "approvedBaseInterpreter" in obj:
        out["approvedBaseInterpreter"] = _abs_path_str(obj["approvedBaseInterpreter"],
                                                       "approvedBaseInterpreter")
    if "extraProtectedPaths" in obj:
        v = obj["extraProtectedPaths"]
        if not isinstance(v, list) or len(set(map(str, v))) != len(v):
            raise PolicyError("extraProtectedPaths는 중복 없는 절대경로 목록이어야 함")
        out["extraProtectedPaths"] = [_abs_path_str(p, "extraProtectedPaths") for p in v]
    return out


def read_local_policy(root):
    """<root>/.harness/policy.local.json → dict(없으면 빈 dict). 형식이 틀리면 PolicyError."""
    path = Path(root) / LOCAL_POLICY_REL
    if not os.path.lexists(str(path)):
        return {}
    return parse_local_policy(read_regular_file(path, "policy.local", PolicyError))


_POLICY_CACHE = {}


def load_repo_policy(root=None):
    """하네스 설치 root(기본 REPO_ROOT)의 policy — 프로세스당 한 번 읽는다(실패는 캐시 안 함)."""
    key = str(Path(root if root is not None else REPO_ROOT))
    if key not in _POLICY_CACHE:
        _POLICY_CACHE[key] = read_policy(key)
    return _POLICY_CACHE[key]


def policy():
    """현재 하네스의 project policy. 모든 모듈은 이 함수로만 policy를 얻는다."""
    return load_repo_policy()


def local_policy():
    """현재 하네스 root의 policy.local.json(호스트 전용 선택값). 없으면 빈 dict."""
    return read_local_policy(REPO_ROOT)


def extra_protected_paths():
    """sandbox가 추가로 쓰기 거부할 호스트 경로(예: 원본 템플릿 checkout). 기본은 없음."""
    return list(local_policy().get("extraProtectedPaths", []))


def review_model():
    return policy().review_model


def parse_policy(data):
    """policy bytes → Policy. 형식이 틀리면 PolicyError."""
    obj = strict_json_loads(data, "policy", PolicyError)
    _require_keys(obj, POLICY_KEYS, (), "policy")
    _reject_secrets(obj, "policy")
    issue_re = compile_issue_regexes(obj["issueKeyPattern"])[0]
    _id_list(obj, "approverUserIds")
    threads = _id_list(obj, "approvalThreadIds")
    scoped = obj["issueScopedThreads"]
    if not isinstance(scoped, dict):
        raise PolicyError("issueScopedThreads는 {thread: issue} 객체여야 함")
    for t, issue in scoped.items():
        if not _ID_RE.fullmatch(t) or t in threads:
            raise PolicyError("issueScopedThreads thread ID 오류/전역 thread와 겹침: %r" % t)
        if not (isinstance(issue, str) and issue_re.fullmatch(issue)
                and _ISSUE_SAFE_RE.fullmatch(issue)):
            raise PolicyError("issueScopedThreads issue가 issueKeyPattern과 맞지 않음: %r" % issue)
    if obj["implBackend"] not in SUPPORTED_IMPL_BACKENDS:
        raise PolicyError("implBackend는 %s만 지원(현재 %r)"
                          % ("/".join(SUPPORTED_IMPL_BACKENDS), obj["implBackend"]))
    if obj["reviewBackend"] not in SUPPORTED_REVIEW_BACKENDS:
        raise PolicyError("reviewBackend는 %s만 지원(현재 %r)"
                          % ("/".join(SUPPORTED_REVIEW_BACKENDS), obj["reviewBackend"]))
    if not (isinstance(obj["reviewModel"], str) and _MODEL_RE.fullmatch(obj["reviewModel"])):
        raise PolicyError("reviewModel 형식 오류: %r" % obj["reviewModel"])
    lo = _version(obj, "pythonMinVersion", 2)
    rec = _version(obj, "pythonRecommendedVersion", 3)
    if lo < MIN_VERSION:
        raise PolicyError("pythonMinVersion은 %s 이상이어야 함"
                          % ".".join(str(x) for x in MIN_VERSION))
    if rec[:2] < lo:
        raise PolicyError("pythonRecommendedVersion이 pythonMinVersion보다 낮음")
    return Policy(obj)
