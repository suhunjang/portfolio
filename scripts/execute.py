#!/usr/bin/env python3
"""
Harness Step Executor (macOS 하네스 모드) — 승인된 계획의 step을 순차 실행한다.

Usage (외부 runner만):
    HARNESS_LAUNCH_DESCRIPTOR=<runner가 만든 read-only descriptor> \\
    HARNESS_REVIEW_BACKEND=codex HARNESS_REVIEW_MODEL=gpt-6-astra \\
    ./.venv/bin/python scripts/harness.py execute <task> --base main

계약:
  - launch descriptor(외부 runner, read-only, repo 밖)가 없으면 거부한다(직접 진입 차단).
  - 승인 record·clean Astra 계획 리뷰·canonical plan hash를 preflight와 매 Claude 호출·
    리뷰·finalize 직전에 다시 검증한다. step prompt는 승인 snapshot에서 만든다.
  - 구현 Claude만 `--dangerously-skip-permissions`이며 항상 sandbox-exec deny-default
    profile 안에서 돈다(허용 source/test 경로·출력 디렉터리만 쓰기).
  - git checkout·add·commit은 하네스만 한다. 자동 branch 전환·--push·HARNESS_NO_GIT 없음.
  - phase 완료 metadata를 포함한 candidate commit을 먼저 만들고 그 exact SHA에서 테스트와
    codex gpt-6-astra(read-only) 리뷰를 한다. PASS 뒤에는 파일·commit을 만들지 않는다.
  - 리뷰 실패·누락·degraded·불일치는 needs-review(종료코드 3)로 막는다.
"""

import argparse
import collections
import contextlib
import fnmatch
import hashlib
import json
import os
import re
import shlex
import signal
import subprocess
import sys
import tempfile
import threading
import time
import types
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Optional

sys.path.insert(0, str(Path(__file__).resolve().parent))
import runtime  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent

for _stream in (sys.stdout, sys.stderr):
    with contextlib.suppress(AttributeError, ValueError):
        _stream.reconfigure(encoding="utf-8")

SANDBOX_EXEC = "/usr/bin/sandbox-exec"


def build_impl_argv():
    """구현·리뷰 수정 Claude argv — 권한 우회는 **여기에만** 있다(항상 sandbox로 감싼다)."""
    return ["claude", "-p", "--dangerously-skip-permissions", "--output-format", "json"]


def build_code_review_argv():
    """코드 리뷰 argv — codex gpt-6-astra read-only(계획 리뷰와 같은 argv)."""
    import review_plan as rp
    return rp.build_review_argv()


def preflight():
    """실행 **전에** 정책(codex/gpt-6-astra 명시, NO_GIT 금지)·sandbox-exec를 검증한다."""
    errors = runtime.review_policy_errors()
    if not Path(SANDBOX_EXEC).exists():
        errors.append("%s 없음 — macOS sandbox 없이 구현 Claude를 띄우지 않는다" % SANDBOX_EXEC)
    if errors:
        for e in errors:
            print(f"ERROR: {e}")
        sys.exit(1)


AgentRun = collections.namedtuple("AgentRun", "returncode stdout stderr timed_out")


def _kill_process_tree(proc, timeout=None):
    """proc의 프로세스 그룹 전체에 SIGKILL을 보낸다(자기 그룹만). 예외를 내지 않는다 —
    종료 **판정**은 하지 않는다. 판정은 _reap_process_group이 probe로 확정한다
    (EPERM을 '정리됨'으로 보지 않는다)."""
    try:
        os.killpg(proc.pid, signal.SIGKILL)
    except (ProcessLookupError, PermissionError):
        pass


REAP_GRACE = 5.0


class DescendantSurvived(OSError):
    """자기 프로세스 그룹 종료를 확정하지 못함 — 이후 commit/test/review의 전제가 깨진다."""


GROUP_GONE, GROUP_ALIVE, GROUP_UNCERTAIN = "gone", "alive", "uncertain"


def _group_state(pgid: int) -> str:
    """**자기가 만든** 프로세스 그룹의 상태(신호 0). ESRCH만 '없음'을 확정한다.
    EPERM·기타 오류는 판단 불가(uncertain) — 좀비만 남았다는 증거가 아니다."""
    try:
        os.killpg(pgid, 0)
        return GROUP_ALIVE
    except ProcessLookupError:
        return GROUP_GONE
    except Exception:  # PermissionError 포함: 확정 불가
        return GROUP_UNCERTAIN


def _reap_process_group(proc, grace: Optional[float] = None):
    """리더가 끝난 뒤(성공·실패·시간 초과) **자기가 만든 프로세스 그룹만** 끄고, 종료가
    **확정**될 때만 돌아온다. 확정 조건: 리더를 거뒀고(poll) 그룹 probe가 ESRCH.
    그 밖(살아 있음·EPERM·기타 오류·리더 미회수)은 grace까지 재시도 후 DescendantSurvived.

    MVP 신뢰 가정(2026-11-22 amendment): Claude Code·Codex는 신뢰한 개발 에이전트다. 일반적인
    background child는 같은 그룹이라 여기서 정리된다. 그룹을 의도적으로 벗어난 프로세스
    (setsid·double fork·launchd 경유)의 격리는 production-hardening 범위이며 주장하지 않는다 —
    대신 호출자가 실행 뒤 Git HEAD·작업 트리·허용 경로·control 불변을 검증해 실패를 막는다.
    시스템 전체 PID 스캔이나 다른 PID(리더 포함)에 대한 개별 kill은 하지 않는다.
    """
    grace = REAP_GRACE if grace is None else max(0.2, grace)
    deadline = time.monotonic() + grace
    state = GROUP_UNCERTAIN
    leader_reaped = False
    while True:
        _kill_process_tree(proc, timeout=max(0.0, deadline - time.monotonic()))
        try:
            leader_reaped = proc.poll() is not None  # 리더 좀비 회수(신호 아님)
        except Exception:
            leader_reaped = False
        state = _group_state(proc.pid)
        if state == GROUP_GONE and leader_reaped:
            return
        if time.monotonic() >= deadline:
            why = ("리더 미회수" if state == GROUP_GONE else
                   "그룹 생존" if state == GROUP_ALIVE else "생존 여부 확인 불가(EPERM 등)")
            raise DescendantSurvived(
                f"에이전트 프로세스 그룹({proc.pid}) 종료를 확정하지 못함: {why} — "
                f"작업 트리를 신뢰할 수 없음")
        time.sleep(0.05)


def _read_output(path) -> str:
    """에이전트 출력 파일을 텍스트로 읽는다(지금 크기까지만)."""
    with open(path, "rb") as f:
        data = f.read(os.fstat(f.fileno()).st_size)
    text = data.decode("utf-8", errors="replace")
    return text.replace("\r\n", "\n").replace("\r", "\n")


def _run_agent_process(argv, *, input, cwd, timeout, kill_grace=30, env=None):
    """에이전트 프로세스를 새 세션으로 실행하고 시간 초과 시 프로세스 트리째 끈다.

    입출력은 파이프가 아니라 임시 파일이다: 에이전트가 남긴 자손이 파이프를 쥐면 EOF가
    오지 않아 시간 제한까지 기다린다(10-31 phase 리뷰가 17시간 멈춘 전례).

    성공·실패·시간 초과·중단 모두 돌아가기 전에 **자기 프로세스 그룹**을 끈다. 그룹을 끄지
    못하면 DescendantSurvived — 호출자는 막는다.
    """
    with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as tmp:
        stdin_path, out_path, err_path = (os.path.join(tmp, n) for n in ("stdin", "stdout", "stderr"))
        with open(stdin_path, "wb") as f:
            f.write(input.encode("utf-8"))
        with open(stdin_path, "rb") as fin, open(out_path, "wb") as fout, \
                open(err_path, "wb") as ferr:
            proc = subprocess.Popen(argv, stdin=fin, stdout=fout, stderr=ferr, cwd=cwd,
                                    start_new_session=True, env=env)
        try:
            proc.wait(timeout=timeout)
            _reap_process_group(proc)
            return AgentRun(proc.returncode, _read_output(out_path), _read_output(err_path), False)
        except subprocess.TimeoutExpired:
            pass
        except DescendantSurvived:
            raise
        except BaseException:
            # Ctrl+C 등: 새 세션이라 신호가 자식에 안 간다. 트리를 끄고 다시 던진다.
            _kill_process_tree(proc, timeout=kill_grace)
            raise
        # 시간 초과: 그룹만 끈다. 리더 PID 직접 kill 대체 경로는 없다 — 그룹 종료를 확정하지
        # 못하면 _reap_process_group이 DescendantSurvived로 막는다.
        deadline = time.monotonic() + kill_grace
        _kill_process_tree(proc, timeout=kill_grace)
        try:
            proc.wait(timeout=max(0, deadline - time.monotonic()))
        except subprocess.TimeoutExpired:
            pass
        _reap_process_group(proc, grace=deadline - time.monotonic())
        rc = proc.returncode if proc.returncode is not None else -1
        return AgentRun(rc, _read_output(out_path), _read_output(err_path), True)


def _install_signal_exit():
    """SIGTERM·SIGHUP을 SystemExit으로 바꿔 _run_agent_process가 에이전트 트리를 끄게 한다."""
    def _exit(signum, frame):
        sys.exit(128 + signum)

    signal.signal(signal.SIGTERM, _exit)
    if signal.getsignal(signal.SIGHUP) is not signal.SIG_IGN:
        signal.signal(signal.SIGHUP, _exit)


@contextlib.contextmanager
def progress_indicator(label: str):
    """터미널 진행 표시기. with 문으로 사용하며 .elapsed 로 경과 시간을 읽는다."""
    frames = "◐◓◑◒"
    stop = threading.Event()
    t0 = time.monotonic()

    def _animate():
        idx = 0
        while not stop.wait(0.12):
            sec = int(time.monotonic() - t0)
            sys.stderr.write(f"\r{frames[idx % len(frames)]} {label} [{sec}s]")
            sys.stderr.flush()
            idx += 1
        sys.stderr.write("\r" + " " * (len(label) + 20) + "\r")
        sys.stderr.flush()

    th = threading.Thread(target=_animate, daemon=True)
    th.start()
    info = types.SimpleNamespace(elapsed=0.0)
    try:
        yield info
    finally:
        stop.set()
        th.join()
        info.elapsed = time.monotonic() - t0


# --- phase-end 리뷰: 범위 manifest·분할·결과 검증 ---
# 정본: .claude/commands/harness.md §E (분할 리뷰·기준 고정).

# 리뷰 관문: 추가 3,000줄을 넘으면 판정 없이 범위 축소를 요청한다.
# 관문은 그대로 두고 하네스가 범위를 나눠 넘긴다.
REVIEW_ADD_LIMIT = 3000
REVIEW_SEVERITIES = ("critical", "major", "minor", "nit")
_SEV_RANK = {"nit": 0, "minor": 1, "major": 2, "critical": 3}
# 경로 접두어를 한 단계 더 깊게 보는 최상위 폴더(설계 §3).
_REVIEW_DEEP_DIRS = ("src", "scripts")
_GIT_STATUS = {"A": "added", "M": "modified", "D": "deleted", "R": "renamed",
               "C": "copied", "T": "typechange"}


def _review_unit_key(path: str) -> str:
    """코드와 그 테스트를 한 단위로 묶는 키.

    foo.ts ↔ foo.test.ts(x)·__tests__/foo.test.*, foo.mjs ↔ foo.test.mjs,
    x.py ↔ test_x.py — 같은 폴더(테스트가 __tests__ 안이면 그 위 폴더)의 같은 이름.
    """
    folder, _, name = path.rpartition("/")
    if folder.rpartition("/")[2] == "__tests__":
        folder = folder.rpartition("/")[0]
    m = re.match(r"test_(.+)\.py$", name)
    if m:
        stem = m.group(1)
    elif ".test." in name:
        stem = name.split(".test.", 1)[0]
    elif "." in name.lstrip("."):
        stem = name.rsplit(".", 1)[0]
    else:
        stem = name
    return f"{folder}/{stem}"


def _review_prefix(path: str) -> str:
    """묶음을 모을 경로 접두어: 최상위 폴더, src/·scripts/는 한 단계 더."""
    dirs = path.split("/")[:-1]
    depth = 2 if dirs and dirs[0] in _REVIEW_DEEP_DIRS else 1
    return "/".join(dirs[:depth])


def plan_review_bundles(files, limit=REVIEW_ADD_LIMIT):
    """리뷰 대상 파일을 묶음(추가 줄 ≤ limit)으로 나눈다. 같은 입력이면 같은 묶음.

    files: [{"path", "added"}]. 한 파일이 limit를 넘는 경우는 호출 전에 막는다.
    1) 코드·테스트를 한 단위로 묶는다(단위가 넘치면 그 단위만 파일별로 푼다).
    2) 단위를 경로 접두어로 모아 접두어·경로 순서대로 채운다 — 접두어 묶음이
       새 묶음에 통째로 들어가면 쪼개지 않는다(경계를 넘는 계약을 줄인다).
    반환: 묶음별 경로 목록.
    """
    added = {f["path"]: f["added"] for f in files}
    units = {}
    for path in sorted(added):
        units.setdefault(_review_unit_key(path), []).append(path)
    groups = {}
    for members in units.values():
        parts = ([members] if sum(added[p] for p in members) <= limit
                 else [[p] for p in members])
        for unit in parts:
            groups.setdefault(min(_review_prefix(p) for p in unit), []).append(unit)

    bundles, cur, cur_added = [], [], 0
    for prefix in sorted(groups):
        group = sorted(groups[prefix])
        group_added = sum(added[p] for unit in group for p in unit)
        if cur and cur_added + group_added > limit >= group_added:
            bundles.append(cur)
            cur, cur_added = [], 0
        for unit in group:
            unit_added = sum(added[p] for p in unit)
            if cur and cur_added + unit_added > limit:
                bundles.append(cur)
                cur, cur_added = [], 0
            cur.extend(unit)
            cur_added += unit_added
    if cur:
        bundles.append(cur)
    return bundles


def _parse_numstat_z(text: str) -> list:
    """`git diff --numstat -z -M` → [(added|None, deleted|None, path, old_path|None)].
    바이너리는 added/deleted가 '-'라 None. rename은 경로가 다음 두 토큰에 온다."""
    toks = text.split("\0")
    out, i = [], 0
    while i < len(toks):
        if not toks[i]:
            i += 1
            continue
        added, deleted, path = toks[i].split("\t", 2)
        if path:
            old = None
            i += 1
        else:
            old, path = toks[i + 1], toks[i + 2]
            i += 3
        out.append((None if added == "-" else int(added),
                    None if deleted == "-" else int(deleted), path, old))
    return out


def _parse_name_status_z(text: str) -> dict:
    """`git diff --name-status -z -M` → {path: status}. rename·copy는 새 경로 기준."""
    toks = text.split("\0")
    out, i = {}, 0
    while i < len(toks):
        code = toks[i]
        if not code:
            i += 1
            continue
        if code[0] in "RC":
            path = toks[i + 2]
            i += 3
        else:
            path = toks[i + 1]
            i += 2
        out[path] = _GIT_STATUS.get(code[0], code)
    return out


def _review_exclude_error(rules) -> Optional[str]:
    """index.json reviewExclude 검사. 제외는 이유를 공개해야 하므로 둘 다 필수."""
    if not isinstance(rules, list):
        return "목록이 아님"
    for n, r in enumerate(rules, 1):
        if not (isinstance(r, dict)
                and isinstance(r.get("glob"), str) and r["glob"].strip()
                and isinstance(r.get("reason"), str) and r["reason"].strip()):
            return f"{n}번째 항목에 glob·reason이 모두 있어야 함"
    return None


def check_review_result(obj) -> Optional[str]:
    """리뷰 결과 JSON을 검사한다. 통과면 None, 아니면 사유.

    `{}`·status 없음·complete가 아닌 status·finding 형식 오류는 전부 실패다.
    빈 객체를 findings=[]로 읽으면 리뷰가 없었는데 phase가 통과한다.
    """
    if not isinstance(obj, dict):
        return "결과 형식 오류: JSON 객체가 아님"
    status = obj.get("status")
    if status is None:
        return "결과 형식 오류: status 없음"
    if status != "complete":
        return f"판정 보류(status={status}): {obj.get('reason', '사유 없음')}"
    findings = obj.get("findings")
    if not isinstance(findings, list):
        return "결과 형식 오류: findings가 목록이 아님"
    for n, f in enumerate(findings, 1):
        if not isinstance(f, dict):
            return f"결과 형식 오류: finding {n}이 객체가 아님"
        if f.get("severity") not in REVIEW_SEVERITIES:
            return f"결과 형식 오류: finding {n}의 severity={f.get('severity')!r}"
        line = f.get("line", "누락")
        if not (line is None or (type(line) is int and line >= 0)):
            return f"결과 형식 오류: finding {n}의 line={line!r}"
        for key in ("file", "title", "detail"):
            if not isinstance(f.get(key), str):
                return f"결과 형식 오류: finding {n}의 {key}가 문자열이 아님"
        if not f["file"].strip() or not f["title"].strip():
            return f"결과 형식 오류: finding {n}의 file·title이 비어 있음"
    return None


def merge_review_findings(results) -> list:
    """여러 리뷰 결과의 findings를 합친다. 같은 (file, line, title)만 하나로
    합치고 가장 높은 severity를 남긴다. 순서: severity 높은 순 → 처음 나온 순."""
    best, order = {}, []
    for findings in results:
        for f in findings:
            key = (f["file"], f["line"], f["title"])
            if key not in best:
                order.append(key)
                best[key] = f
            elif _SEV_RANK[f["severity"]] > _SEV_RANK[best[key]["severity"]]:
                best[key] = f
    merged = [best[k] for k in order]
    merged.sort(key=lambda f: -_SEV_RANK[f["severity"]])
    return merged



ASTRA_RESULT_KEYS = {"status", "reviewed_head", "review_model", "findings", "reason"}


def check_astra_review(obj, head) -> Optional[str]:
    """codex gpt-6-astra 리뷰 결과 strict 검증: 기본 schema + model + reviewed head."""
    err = check_review_result(obj)
    if err:
        return err
    extra = set(obj) - ASTRA_RESULT_KEYS
    if extra:
        return f"결과 형식 오류: 허용되지 않은 키 {sorted(extra)}"
    if obj.get("review_model") != runtime.review_model():
        return f"리뷰 모델 불일치: {obj.get('review_model')!r}"
    if obj.get("reviewed_head") != head:
        return f"reviewed_head 불일치: {obj.get('reviewed_head')!r} ≠ {head}"
    return None


def _overlaps_path(a, b) -> bool:
    ra, rb = Path(os.path.realpath(a)), Path(os.path.realpath(b))
    return ra == rb or ra in rb.parents or rb in ra.parents


def _sha256(text) -> str:
    if isinstance(text, str):
        text = text.encode("utf-8")
    return hashlib.sha256(text).hexdigest()


class StepExecutor:
    """승인된 phase의 step을 외부 runner 계약 안에서 순차 실행한다."""

    MAX_RETRIES = 3
    STEP_TIMEOUT = 1800  # step 에이전트 1회 실행 제한(초)
    TEST_TIMEOUT = 1800
    REVIEW_TIMEOUT = 900
    FIX_TIMEOUT = 1800
    FEAT_MSG = "feat({phase}): step {num} — {name}"
    CHORE_MSG = "chore({phase}): step {num} output"
    TZ = timezone(timedelta(hours=9))

    def __init__(self, phase_dir_name: str, *, descriptor: Optional[dict] = None,
                 base: Optional[str] = None, root=None):
        self._desc = descriptor
        root = Path(descriptor["repoRoot"]) if descriptor else Path(root or ROOT)
        self._root = str(root)
        self._phases_dir = root / "phases"
        self._phase_dir = self._phases_dir / phase_dir_name
        self._phase_dir_name = phase_dir_name
        self._top_index_file = self._phases_dir / "index.json"
        self._cli_base = base
        self._approved = None
        self._allowed = None
        self._fp = None
        self._candidate_sha = self._tested_sha = self._reviewed_sha = None
        if descriptor:
            self._task_ev = Path(descriptor["evidenceDir"]) / phase_dir_name
            self._out_dir = Path(descriptor["outputDir"])  # 에이전트가 쓸 수 있다(신뢰 안 함)
            self._trusted_out = self._task_ev / "outputs"   # 하네스만 쓴다(evidence)
            self._review_dir = self._task_ev / "code-review"
            self._feature_ref = "refs/heads/" + descriptor["branch"]
        else:
            # 단위 시험용 seam — run()은 descriptor 없이는 즉시 거부한다.
            self._task_ev = None
            self._out_dir = self._phase_dir
            self._trusted_out = self._phase_dir
            self._review_dir = self._phase_dir
            self._feature_ref = None

        if not self._phase_dir.is_dir():
            print(f"ERROR: {self._phase_dir} not found")
            sys.exit(1)
        self._index_file = self._phase_dir / "index.json"
        if not self._index_file.exists():
            print(f"ERROR: {self._index_file} not found")
            sys.exit(1)
        idx = self._read_json(self._index_file)
        self._project = idx.get("project", "project")
        self._phase_name = idx.get("phase", phase_dir_name)
        self._total = len(idx["steps"])

    def run(self):
        self._print_header()
        self._preflight_gates()
        self._check_blockers()
        self._require_base()
        self._ensure_created_at()
        self._execute_all_steps(self._load_guardrails())
        self._make_candidate()
        self._run_review()
        self._record_final()

    # --- timestamps / JSON ---

    def _stamp(self) -> str:
        return datetime.now(self.TZ).strftime("%Y-%m-%dT%H:%M:%S%z")

    @staticmethod
    def _read_json(p: Path) -> dict:
        return json.loads(p.read_text(encoding="utf-8"))

    @staticmethod
    def _write_json(p: Path, data: dict):
        p.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")

    # --- git ---

    def _run_git(self, *args) -> subprocess.CompletedProcess:
        cmd = ["git"] + list(args)
        return subprocess.run(cmd, cwd=self._root, capture_output=True, text=True, encoding="utf-8")

    def _head(self) -> str:
        r = self._run_git("rev-parse", "HEAD")
        return r.stdout.strip() if r.returncode == 0 else ""

    def _changed_paths(self) -> list:
        """미커밋 변경 경로(추적·미추적, rename 원래 경로 포함). git 실패는 막는다."""
        r = self._run_git("status", "--porcelain=v1", "-z", "--untracked-files=all")
        if r.returncode != 0:
            self._mark_needs_review(f"작업 트리 확인 실패: {r.stderr.strip()[:200]}")
        toks = r.stdout.split("\0")
        paths, i = [], 0
        while i < len(toks):
            entry = toks[i]
            if not entry:
                i += 1
                continue
            paths.append(entry[3:])
            if "R" in entry[:2] or "C" in entry[:2]:
                if i + 1 < len(toks) and toks[i + 1]:
                    paths.append(toks[i + 1])
                i += 2
            else:
                i += 1
        return paths

    def _harness_owned(self, path: str) -> bool:
        return path in ("phases/index.json", f"phases/{self._phase_dir_name}/index.json")

    def _disallowed_changes(self) -> list:
        import plan_manifest as pm
        out = []
        for p in self._changed_paths():
            if self._harness_owned(p):
                continue
            if self._allowed is not None and not pm.path_allowed(p, self._allowed):
                out.append(p)
        return out

    def _git_commit(self, msg: str, paths) -> bool:
        """하네스만 커밋한다(hook 비활성). 변경이 없으면 False. 실패는 막는다."""
        paths = list(paths)
        if not paths:
            return False
        r = self._run_git("add", "-A", "--", *paths)
        if r.returncode != 0:
            self._mark_needs_review(f"git add 실패: {r.stderr.strip()[:200]}")
        if self._run_git("diff", "--cached", "--quiet").returncode == 0:
            return False
        r = self._run_git("-c", "core.hooksPath=/dev/null", "commit", "-q", "-m", msg)
        if r.returncode != 0:
            self._mark_needs_review(f"commit 실패({msg}): {r.stderr.strip()[:200]}")
        print(f"  Commit: {msg}")
        return True

    def _commit_step(self, step_num: int, step_name: str):
        bad = self._disallowed_changes()
        if bad:
            self._mark_needs_review(f"허용 경로(allowedPaths) 밖 변경 — 커밋하지 않음: {bad[:5]}")
        changed = self._changed_paths()
        code = [p for p in changed if not self._harness_owned(p)]
        own = [p for p in changed if self._harness_owned(p)]
        self._git_commit(self.FEAT_MSG.format(phase=self._phase_name, num=step_num,
                                              name=step_name), code)
        self._git_commit(self.CHORE_MSG.format(phase=self._phase_name, num=step_num), own)

    # --- gates ---

    def _check_control(self):
        """M2: reviewed pin(control hash·runner 코드)과 profile을 매번 독립 재검증한다."""
        import runner as rn
        pin, pin_sha = rn.load_pin(self._desc["controlPin"], self._root)
        if pin_sha != self._desc["controlPinSha"] or pin["controlSha"] != self._desc["controlSha"]:
            raise rn.RunnerError("control pin이 descriptor와 다름")
        rn._verify_pin(pin, self._root, Path(__file__).resolve().parent)
        if rn.control_sha(self._root) != self._desc["controlSha"]:
            raise rn.RunnerError("control 파일(scripts/.claude/.codex/CLAUDE.md)이 바뀜")
        prof = Path(self._desc["sandboxProfile"]).read_bytes()
        if _sha256(prof) != self._desc["sandboxProfileSha"]:
            raise rn.RunnerError("sandbox profile이 바뀜")

    def _current_branch(self) -> str:
        return self._run_git("rev-parse", "--abbrev-ref", "HEAD").stdout.strip()

    def _preflight_gates(self):
        """step 0 전: descriptor·control·branch·승인 결속·clean tree. 실패는 종료코드 1."""
        import approval as ap
        import runner as rn
        if self._desc is None:
            print("  ERROR: launch descriptor 없음 — execute는 외부 runner로만 실행한다.")
            sys.exit(1)
        ev, sha = self._desc["evidenceDir"], self._desc["approvalRecordSha"]
        try:
            first = ap.is_first_run(ev, self._phase_dir_name, sha)
            self._check_control()
            if self._desc["task"] != self._phase_dir_name:
                raise rn.RunnerError("descriptor task 불일치")
            branch = self._current_branch()
            if branch != self._desc["branch"]:
                raise rn.RunnerError(
                    f"현재 branch '{branch}'가 승인 branch '{self._desc['branch']}'가 아님 "
                    f"— 자동 전환하지 않는다")
            self._approved = ap.verify_approval(self._desc["evidenceDir"], self._phase_dir_name,
                                                self._root, self._desc["approvalRecordSha"],
                                                first_run=first)
            if self._approved.record.get("branch") != branch:
                raise rn.RunnerError("승인 record의 branch와 현재 branch가 다름")
            ap.is_first_run(ev, self._phase_dir_name, sha,
                            plan_commit=self._approved.record["planCommitSha"])
        except (ap.ApprovalError, rn.RunnerError, OSError) as e:
            print(f"  ERROR: preflight 게이트 실패 — {e}")
            sys.exit(1)
        self._allowed = list(self._approved.snapshot.index["allowedPaths"])
        dirty = [p for p in self._changed_paths() if not self._harness_owned(p)]
        if dirty:
            print(f"  ERROR: 작업 트리가 clean하지 않음: {dirty[:5]}")
            sys.exit(1)
        self._fp = rn.git_fingerprint(self._root, self._feature_ref)
        final = self._task_ev / "final.json"
        if final.exists():
            final.chmod(0o644)
            final.unlink()
        if first:
            ap.write_start_marker(ev, self._phase_dir_name, sha,
                                  self._approved.record["planCommitSha"], head=self._head())
        print(f"  ✓ 승인 결속 확인: plan {self._approved.record['planContentSha'][:12]} · "
              f"approval {self._desc['approvalRecordSha'][:12]} · "
              f"{'최초 실행' if first else '재개'}")

    def _gate(self, where: str):
        """매 Claude 호출·테스트·리뷰·finalize 직전 재검증. 실패는 needs-review."""
        import approval as ap
        import runner as rn
        if self._desc is None:
            print("  ERROR: launch descriptor 없음")
            sys.exit(1)
        try:
            self._check_control()
            if self._current_branch() != self._desc["branch"]:
                raise rn.RunnerError("branch가 바뀜")
            ap.verify_approval(self._desc["evidenceDir"], self._phase_dir_name, self._root,
                               self._desc["approvalRecordSha"], first_run=False)
            if rn.git_fingerprint(self._root, self._feature_ref) != self._fp:
                raise rn.RunnerError("git metadata(HEAD·config·hooks·다른 ref)가 바뀜")
        except (ap.ApprovalError, rn.RunnerError, OSError) as e:
            self._mark_needs_review(f"[{where}] 게이트 실패: {e}")

    def _after_agent(self, label: str, head_before: Optional[str] = None):
        """에이전트·테스트 실행 뒤(그룹 정리 후) commit/test/review 전에 fail-closed 불변 검증:
        HEAD 불변(에이전트는 커밋 불가) + git metadata·branch 불변 + control·profile 불변."""
        import runner as rn
        if self._desc is not None:
            try:
                self._check_control()
            except (rn.RunnerError, OSError) as e:
                self._mark_needs_review(f"[{label}] 실행 뒤 control 불변 위반: {e}")
        if head_before is not None and self._head() != head_before:
            self._mark_needs_review(f"[{label}] 에이전트가 HEAD를 바꿈(직접 commit 등) — 하네스만 커밋한다")
        if self._fp is not None and rn.git_fingerprint(self._root, self._feature_ref) != self._fp:
            self._mark_needs_review(f"[{label}] 에이전트 실행 중 git metadata가 바뀜")
        if self._current_branch() != (self._desc or {}).get("branch", self._current_branch()):
            self._mark_needs_review(f"[{label}] 에이전트 실행 중 branch가 바뀜")

    def _sandboxed(self, argv) -> list:
        import runner as rn
        return rn.wrap_argv(self._desc["sandboxProfile"], argv)

    def _agent_env(self) -> dict:
        import runner as rn
        # B3: TMPDIR는 매번 새로 만든다 — 에이전트가 심은 symlink·파일을 따라가지 않는다.
        try:
            tmp = rn.fresh_agent_dir(self._out_dir, "tmp")
        except rn.RunnerError as e:
            self._mark_needs_review(f"에이전트 임시 디렉터리를 안전하게 만들 수 없음: {e}")
        env = dict(os.environ)
        env["TMPDIR"] = str(tmp)
        env.pop("HARNESS_LAUNCH_DESCRIPTOR", None)
        return env

    def _require_base(self):
        """리뷰 기준 브랜치 확인(자동 checkout 없음)·출발점 검사·reviewBaseSha 고정."""
        base = self._resolve_base_branch()
        if self._desc is not None and base != self._desc["baseBranch"]:
            print(f"  ERROR: 기준 브랜치 '{base}'가 승인된 '{self._desc['baseBranch']}'와 다릅니다.")
            sys.exit(1)
        self._require_contains_base(base, "HEAD")
        self._pin_review_base(base)

    def _resolve_base_branch(self) -> str:
        stored = self._read_json(self._index_file).get("baseBranch")
        cli = self._cli_base
        if cli and stored and cli != stored:
            print(f"  ERROR: --base '{cli}'가 index.json의 baseBranch '{stored}'와 다릅니다.")
            sys.exit(1)
        base = cli or stored
        if not base:
            print("  ERROR: 리뷰 기준 브랜치가 정해지지 않았습니다.")
            sys.exit(1)
        return base

    def _require_contains_base(self, base: str, target: str):
        r = self._run_git("merge-base", "--is-ancestor", base, target)
        if r.returncode == 0:
            return
        if r.returncode == 1:
            print(f"  ERROR: '{target}'가 기준 브랜치 '{base}'의 끝을 포함하지 않습니다.")
        else:
            print(f"  ERROR: 기준 브랜치 '{base}'를 확인할 수 없습니다: {r.stderr.strip()}")
        sys.exit(1)

    def _approved_review_base(self) -> Optional[str]:
        return self._approved.record["reviewBaseSha"] if self._approved is not None else None

    def _pin_review_base(self, base: str):
        """리뷰 기준 SHA를 index.json에 남긴다. 승인 실행에서는 승인 record의 값이 정본이고
        index의 다른 값(좁히기·HEAD 치환)은 거부한다(M1)."""
        index = self._read_json(self._index_file)
        sha = index.get("reviewBaseSha")
        approved = self._approved_review_base()
        if approved is not None:
            if sha and sha != approved:
                print(f"  ERROR: index.json reviewBaseSha({sha[:10]})가 승인된 리뷰 기준"
                      f"({approved[:10]})과 다름 — 리뷰 범위 변조")
                sys.exit(1)
            if not sha:
                index["reviewBaseSha"] = approved
                self._write_json(self._index_file, index)
            print(f"  Review base: {base} @ {approved[:10]} (승인 record)")
            return
        if sha:
            print(f"  Review base: {base} @ {sha[:10]} (저장값)")
            return
        r = self._run_git("merge-base", base, "HEAD")
        sha = r.stdout.strip()
        if r.returncode != 0 or not sha:
            print(f"  ERROR: git merge-base {base} HEAD 실패: {r.stderr.strip()}")
            sys.exit(1)
        index["reviewBaseSha"] = sha
        self._write_json(self._index_file, index)
        print(f"  Review base: {base} @ {sha[:10]} (index.json에 고정)")

    # --- top-level index ---

    def _update_top_index(self, status: str):
        if not self._top_index_file.exists():
            return
        top = self._read_json(self._top_index_file)
        ts = self._stamp()
        for phase in top.get("phases", []):
            if phase.get("dir") == self._phase_dir_name:
                phase["status"] = status
                ts_key = {"completed": "completed_at", "error": "failed_at",
                          "blocked": "blocked_at", "needs-review": "review_at"}.get(status)
                if ts_key:
                    phase[ts_key] = ts
                break
        self._write_json(self._top_index_file, top)

    # --- guardrails & context ---

    def _load_guardrails(self) -> str:
        sections = []
        claude_md = Path(self._root) / "CLAUDE.md"
        if claude_md.exists():
            sections.append(f"## 프로젝트 규칙 (CLAUDE.md)\n\n{claude_md.read_text(encoding='utf-8')}")
        docs_dir = Path(self._root) / "docs"
        if docs_dir.is_dir():
            for doc in sorted(docs_dir.glob("*.md")):
                sections.append(f"## {doc.stem}\n\n{doc.read_text(encoding='utf-8')}")
        return "\n\n---\n\n".join(sections) if sections else ""

    @staticmethod
    def _build_step_context(index: dict) -> str:
        lines = [
            f"- Step {s['step']} ({s['name']}): {s['summary']}"
            for s in index["steps"]
            if s["status"] == "completed" and s.get("summary")
        ]
        if not lines:
            return ""
        return "## 이전 Step 산출물\n\n" + "\n".join(lines) + "\n\n"

    def _build_preamble(self, guardrails: str, step_context: str,
                        prev_error: Optional[str] = None) -> str:
        retry_section = ""
        if prev_error:
            retry_section = (
                f"\n## ⚠ 이전 시도 실패 — 아래 에러를 반드시 참고하여 수정하라\n\n"
                f"{prev_error}\n\n---\n\n"
            )
        allowed = ", ".join(self._allowed or ["(계획의 allowedPaths)"])
        return (
            f"당신은 {self._project} 프로젝트의 개발자입니다. 아래 step을 TDD로 수행하세요.\n\n"
            f"{guardrails}\n\n---\n\n"
            f"{step_context}{retry_section}"
            f"## 작업 규칙\n\n"
            f"1. 이전 step에서 작성된 코드를 확인하고 일관성을 유지하라.\n"
            f"2. 이 step에 명시된 작업만 수행하라. 추가 기능이나 파일을 만들지 마라.\n"
            f"3. 쓰기는 승인된 경로만: {allowed}. phases/·docs/superpowers/specs/·scripts/·"
            f".claude/·.codex/·CLAUDE.md·.git/은 sandbox가 막는다.\n"
            f"4. 테스트를 먼저 쓰고 실패를 확인한 뒤 구현하라. 기존 테스트를 깨뜨리지 마라.\n"
            f"5. AC(Acceptance Criteria) 검증을 직접 실행하라.\n"
            f"6. git commit·checkout·push를 하지 마라 — 하네스가 검증 후 커밋한다.\n"
            f"7. 끝나기 전에 RESULT_FILE에 JSON 하나를 써라(index.json은 건드리지 마라):\n"
            f'   - AC 통과 → {{"status": "completed", "summary": "<산출물 한 줄 요약>"}}\n'
            f'   - {self.MAX_RETRIES}회 시도 후 실패 → {{"status": "error", "error_message": "..."}}\n'
            f'   - 사용자 개입 필요(API 키·인증 등) → {{"status": "blocked", "blocked_reason": "..."}}\n'
            f"\n---\n\n"
        )

    # --- 구현 에이전트 호출 ---

    def _step_text(self, step_num: int) -> str:
        rel = f"phases/{self._phase_dir_name}/step{step_num}.md"
        if self._approved is not None:
            return self._approved.snapshot.read(rel).decode("utf-8")
        p = Path(self._root) / rel
        if not p.exists():
            print(f"  ERROR: {p} not found")
            sys.exit(1)
        return p.read_text(encoding="utf-8")

    @staticmethod
    def _read_agent_result(path: Path) -> Optional[dict]:
        """B3: 에이전트 저장소의 결과는 dir fd + O_NOFOLLOW로만 읽는다(symlink·hardlink 거부)."""
        import runner as rn
        try:
            data = rn.read_agent_file(path.parent, path.name)
        except rn.RunnerError as e:
            return {"status": None, "error_message": f"결과 파일을 신뢰할 수 없음: {e}"}
        if data is None:
            return None
        try:
            obj = json.loads(data.decode("utf-8"))
        except (ValueError, UnicodeDecodeError):
            return {"status": None, "error_message": "결과 파일 JSON 오류"}
        if not isinstance(obj, dict):
            return {"status": None, "error_message": "결과 파일이 객체가 아님"}
        return obj

    def _invoke_agent(self, step: dict, preamble: str) -> dict:
        step_num, step_name = step["step"], step["name"]
        self._gate(f"step {step_num}")
        text = self._step_text(step_num)
        self._out_dir.mkdir(parents=True, exist_ok=True)
        result_file = self._out_dir / f"step{step_num}-result.json"
        self._remove_agent_entry(result_file)
        prompt = (preamble + f"STEP_NUMBER: {step_num}\nRESULT_FILE: {result_file}\n\n---\n\n"
                  + text)
        head_before = self._head()
        try:
            result = _run_agent_process(self._sandboxed(build_impl_argv()), input=prompt,
                                        cwd=self._root, timeout=self.STEP_TIMEOUT,
                                        env=self._agent_env())
        except DescendantSurvived as e:
            self._mark_needs_review(f"[step {step_num}] 에이전트 자손이 살아남음: {e}")
        self._after_agent(f"step {step_num}", head_before)
        if result.timed_out:
            print(f"\n  WARN: step 시간 초과 ({self.STEP_TIMEOUT}초)")
        elif result.returncode != 0:
            print(f"\n  WARN: Claude가 비정상 종료됨 (code {result.returncode})")
            if result.stderr:
                print(f"  stderr: {result.stderr[:500]}")
        output = {
            "step": step_num, "name": step_name,
            "exitCode": result.returncode,
            "stdout": result.stdout, "stderr": result.stderr,
            "timedOut": result.timed_out,
            "result": self._read_agent_result(result_file),
        }
        # B3: 신뢰 출력은 에이전트가 쓸 수 없는 evidence에 새 파일로 쓴다(따라갈 링크 없음).
        self._write_trusted(f"step{step_num}-output.json", output)
        return output

    def _write_trusted(self, name: str, obj):
        import runner as rn
        self._trusted_out.mkdir(parents=True, exist_ok=True)
        if self._desc is not None and _overlaps_path(self._trusted_out, self._out_dir):
            self._mark_needs_review("신뢰 출력 경로가 에이전트 저장소와 겹침")
        rn.write_read_only(self._trusted_out / name,
                           json.dumps(obj, indent=2, ensure_ascii=False))

    def _remove_agent_entry(self, path: Path):
        import runner as rn
        try:
            rn.remove_agent_entry(path.parent, path.name)
        except rn.RunnerError as e:
            self._mark_needs_review(f"에이전트 저장소 항목을 안전하게 지울 수 없음: {e}")

    # --- 헤더 & 검증 ---

    def _print_header(self):
        print(f"\n{'='*60}")
        print("  Harness Step Executor")
        print(f"  Phase: {self._phase_name} | Steps: {self._total}")
        print(f"  Review: codex {runtime.review_model()} (read-only)")
        print(f"{'='*60}")

    def _check_blockers(self):
        index = self._read_json(self._index_file)
        if index.get("status") == "needs-review":
            print(f"\n  ⚠ Phase '{self._phase_name}' is blocked on review.")
            print(f"  Reason: {index.get('review_reason', 'unknown')}")
            print(f"  Resolve, then reset status to 'pending'/'completed' to resume.")
            sys.exit(3)
        for s in reversed(index["steps"]):
            if s["status"] == "error":
                print(f"\n  ✗ Step {s['step']} ({s['name']}) failed.")
                print(f"  Error: {s.get('error_message', 'unknown')}")
                print(f"  Fix and reset status to 'pending' to retry.")
                sys.exit(1)
            if s["status"] == "blocked":
                print(f"\n  ⏸ Step {s['step']} ({s['name']}) blocked.")
                print(f"  Reason: {s.get('blocked_reason', 'unknown')}")
                print(f"  Resolve and reset status to 'pending' to retry.")
                sys.exit(2)
            if s["status"] != "pending":
                break

    def _ensure_created_at(self):
        index = self._read_json(self._index_file)
        if "created_at" not in index:
            index["created_at"] = self._stamp()
            self._write_json(self._index_file, index)

    # --- 실행 루프 ---

    def _set_step(self, index: dict, step_num: int, **fields):
        for s in index["steps"]:
            if s["step"] == step_num:
                s.update(fields)

    def _execute_single_step(self, step: dict, guardrails: str) -> bool:
        """단일 step 실행 (재시도 포함). 완료되면 True, 실패/차단이면 종료."""
        step_num, step_name = step["step"], step["name"]
        done = sum(1 for s in self._read_json(self._index_file)["steps"] if s["status"] == "completed")
        prev_error = None

        for attempt in range(1, self.MAX_RETRIES + 1):
            index = self._read_json(self._index_file)
            before = index
            step_context = self._build_step_context(index)
            preamble = self._build_preamble(guardrails, step_context, prev_error)

            tag = f"Step {step_num}/{self._total - 1} ({done} done): {step_name}"
            if attempt > 1:
                tag += f" [retry {attempt}/{self.MAX_RETRIES}]"

            with progress_indicator(tag) as pi:
                agent_out = self._invoke_agent(step, preamble)
            elapsed = int(pi.elapsed)

            # 시간 초과는 결과 파일(completed 포함)보다 먼저 본다 — 잘린 작업은 커밋하지 않는다.
            if agent_out.get("timedOut"):
                try:
                    index = self._read_json(self._index_file)
                except (json.JSONDecodeError, UnicodeDecodeError, OSError):
                    index = before
                ts = self._stamp()
                timeout_msg = (
                    f"[시간 초과 {self.STEP_TIMEOUT}초] step이 너무 크다 — 남은 작업을 "
                    "원래 작업 경계대로 나눠 다시 계획한 뒤(재리뷰·재승인) 이 step을 pending으로 되돌려라"
                )
                self._set_step(index, step_num, status="error", error_message=timeout_msg,
                               failed_at=ts)
                self._write_json(self._index_file, index)
                print(f"  ✗ Step {step_num}: {step_name} 시간 초과 [{elapsed}s]")
                print(f"    Error: {timeout_msg}")
                self._update_top_index("error")
                sys.exit(1)

            bad = self._disallowed_changes()
            if bad:
                self._mark_needs_review(f"허용 경로(allowedPaths) 밖 변경 — 커밋하지 않음: {bad[:5]}")

            res = agent_out.get("result") or {}
            status = res.get("status")
            index = self._read_json(self._index_file)
            ts = self._stamp()

            if status == "completed":
                summary = res.get("summary")
                fields = {"status": "completed", "completed_at": ts}
                if isinstance(summary, str) and summary.strip():
                    fields["summary"] = summary.strip()
                self._set_step(index, step_num, **fields)
                self._write_json(self._index_file, index)
                self._commit_step(step_num, step_name)
                print(f"  ✓ Step {step_num}: {step_name} [{elapsed}s]")
                return True

            if status == "blocked":
                reason = str(res.get("blocked_reason") or "")
                self._set_step(index, step_num, status="blocked", blocked_reason=reason,
                               blocked_at=ts)
                self._write_json(self._index_file, index)
                print(f"  ⏸ Step {step_num}: {step_name} blocked [{elapsed}s]")
                print(f"    Reason: {reason}")
                self._update_top_index("blocked")
                sys.exit(2)

            err_msg = str(res.get("error_message") or "Step이 RESULT_FILE에 결과를 남기지 않음")
            if attempt < self.MAX_RETRIES:
                prev_error = err_msg
                print(f"  ↻ Step {step_num}: retry {attempt}/{self.MAX_RETRIES} — {err_msg}")
            else:
                self._set_step(index, step_num, status="error",
                               error_message=f"[{self.MAX_RETRIES}회 시도 후 실패] {err_msg}",
                               failed_at=ts)
                self._write_json(self._index_file, index)
                self._commit_step(step_num, step_name)
                print(f"  ✗ Step {step_num}: {step_name} failed after {self.MAX_RETRIES} attempts [{elapsed}s]")
                print(f"    Error: {err_msg}")
                self._update_top_index("error")
                sys.exit(1)

        return False  # unreachable

    def _execute_all_steps(self, guardrails: str):
        while True:
            index = self._read_json(self._index_file)
            pending = next((s for s in index["steps"] if s["status"] == "pending"), None)
            if pending is None:
                print("\n  All steps completed!")
                return
            step_num = pending["step"]
            for s in index["steps"]:
                if s["step"] == step_num and "started_at" not in s:
                    s["started_at"] = self._stamp()
                    self._write_json(self._index_file, index)
                    break
            self._execute_single_step(pending, guardrails)

    # --- candidate·테스트·리뷰·final ---

    def _make_candidate(self):
        """phase 완료 metadata를 포함한 candidate commit — 이 SHA에서 테스트·리뷰한다."""
        self._gate("finalize")
        index = self._read_json(self._index_file)
        if index.get("status") != "completed" or "completed_at" not in index:
            index["completed_at"] = self._stamp()
            index["status"] = "completed"
        for k in ("review_reason", "review_at"):
            index.pop(k, None)
        self._write_json(self._index_file, index)
        self._update_top_index("completed")
        own = [p for p in self._changed_paths() if self._harness_owned(p)]
        self._git_commit(f"chore({self._phase_name}): mark phase completed", own)
        dirty = self._changed_paths()
        if dirty:
            self._mark_needs_review(f"candidate 뒤에도 미커밋 변경이 남음: {dirty[:5]}")
        self._candidate_sha = self._head()
        print(f"  ✓ candidate {self._candidate_sha[:12]} — 이 SHA에서 테스트·리뷰")

    def _run_tests(self):
        """현재 HEAD에서 계획의 testCommand를 sandbox 안에서 실행한다. 실패는 needs-review."""
        import runner as rn
        self._gate("test")
        head = self._head()
        argv = list(self._approved.snapshot.index["testCommand"])
        try:
            with progress_indicator(f"Tests @ {head[:10]}"):
                res = _run_agent_process(self._sandboxed(argv), input="", cwd=self._root,
                                         timeout=self.TEST_TIMEOUT, env=self._agent_env())
        except DescendantSurvived as e:
            self._mark_needs_review(f"테스트 자손이 살아남음: {e}")
        self._review_dir.mkdir(parents=True, exist_ok=True)
        rn.write_read_only(self._review_dir / f"tests-{head[:12]}-{int(time.time())}.json",
                           json.dumps({"head": head, "argv": argv, "exitCode": res.returncode,
                                       "timedOut": res.timed_out,
                                       "stdoutSha256": _sha256(res.stdout),
                                       "stdoutTail": res.stdout[-4000:],
                                       "stderrTail": res.stderr[-4000:]}, ensure_ascii=False,
                                      indent=2))
        self._after_agent("tests")
        if res.timed_out or res.returncode != 0:
            self._mark_needs_review(
                f"테스트 실패(code {res.returncode}{', 시간 초과' if res.timed_out else ''}) "
                f"@ {head[:10]}")
        if self._head() != head or self._changed_paths():
            self._mark_needs_review("테스트가 HEAD 또는 작업 트리를 바꿈")
        self._tested_sha = head
        print(f"  ✓ 테스트 통과 @ {head[:10]}")

    def _record_final(self):
        import runner as rn
        head = self._head()
        if not (self._tested_sha and self._tested_sha == self._reviewed_sha == head):
            self._mark_needs_review(
                f"tested({self._tested_sha}) = reviewed({self._reviewed_sha}) = HEAD({head}) 불일치")
        if self._changed_paths():
            self._mark_needs_review("리뷰 통과 뒤 작업 트리에 변경이 있음")
        rn.write_read_only(self._task_ev / "final.json", json.dumps({
            "task": self._phase_dir_name, "testedSha": self._tested_sha,
            "reviewedSha": self._reviewed_sha, "candidateSha": self._candidate_sha,
            "head": head, "branch": self._desc["branch"],
            "approvalRecordSha": self._desc["approvalRecordSha"],
            "planContentSha": self._approved.record["planContentSha"],
            "reviewModel": runtime.review_model(), "at": self._stamp()},
            indent=2, ensure_ascii=False))
        print(f"\n{'='*60}")
        print(f"  Phase '{self._phase_name}' completed — tested = reviewed = HEAD {head[:12]}")
        print(f"  push는 하지 않는다. Ryan: runner verify-final 뒤 feature branch만 push.")
        print(f"{'='*60}")

    # --- phase 리뷰 (2단계: 리뷰 → 수정 → 재리뷰) ---

    # 매 리뷰 회차가 새로 쓰는 산출물(evidence 쪽). 회차 시작 때 전부 지운다.
    REVIEW_OUTPUTS = ("review.json", "review.md", "review-manifest.json",
                      "review-bundle-*.json", "review-cross.json")
    REVIEW_ROUND1 = ("review-r1.json", "review-r1.md")
    FIX_RESULT = "review-fix.json"
    REVIEW_CONFIG_KEYS = ("baseBranch", "reviewBaseSha", "reviewExclude")
    CROSS_LABEL = "교차 리뷰"

    def _run_review(self):
        """candidate HEAD를 테스트·리뷰한다. major/minor는 수정→테스트→같은 기준 재리뷰."""
        self._review_dir.mkdir(parents=True, exist_ok=True)
        self._clear_review_outputs(self.REVIEW_ROUND1)
        cfg = self._load_review_config()
        self._run_tests()
        self._gate("review")
        findings = self._review_round(1, cfg)
        if not findings:
            return

        n_crit = sum(1 for f in findings if f["severity"] == "critical")
        if n_crit:
            self._mark_needs_review(f"리뷰가 critical {n_crit}건 발견")
        actionable = [f for f in findings if f["severity"] != "nit"]
        n_nit = len(findings) - len(actionable)
        if n_nit:
            print(f"  · nit {n_nit}건은 자동 수정 대상에서 제외 (review.md 참고)")
        if not actionable:
            return

        err = self._apply_review_fixes(actionable)
        if err:
            self._mark_needs_review(f"리뷰 수정 실패 — {err}")
        self._require_review_config_unchanged(cfg)
        bad = self._disallowed_changes()
        if bad:
            self._mark_needs_review(f"수정 단계가 허용 경로 밖을 바꿈: {bad[:5]}")
        self._git_commit(f"fix({self._phase_name}): apply review findings",
                         [p for p in self._changed_paths() if not self._harness_owned(p)])
        if self._changed_paths():
            self._mark_needs_review("수정 커밋 뒤에도 미커밋 변경이 남음")
        print(f"  ✓ Review 지적사항 {len(actionable)}건 반영 — 새 HEAD로 테스트·재리뷰")
        try:
            for name in self.REVIEW_ROUND1:
                os.replace(self._review_dir / name.replace("-r1", ""), self._review_dir / name)
        except OSError as e:
            self._mark_needs_review(f"1차 리뷰 기록 보존 실패: {e}")
        self._run_tests()
        self._gate("re-review")
        remaining = [f for f in self._review_round(2, cfg)
                     if _SEV_RANK[f["severity"]] >= _SEV_RANK["major"]]
        if remaining:
            self._mark_needs_review(f"수정 후 재리뷰에 major 이상 {len(remaining)}건 남음 (review.md 참조)")
        print("  ✓ 재리뷰 통과")

    def _load_review_config(self) -> dict:
        index = self._read_json(self._index_file)
        cfg = {k: index.get(k) for k in self.REVIEW_CONFIG_KEYS}
        approved = self._approved_review_base()
        if approved is not None:
            # M1: 리뷰 기준은 승인 record·snapshot이 정본 — 가변 index 값을 믿지 않는다.
            if cfg["reviewBaseSha"] != approved:
                self._mark_needs_review(
                    f"index.json reviewBaseSha가 승인된 리뷰 기준({approved[:10]})과 다름 — 변조")
            cfg = {"baseBranch": self._approved.record["baseBranch"], "reviewBaseSha": approved,
                   "reviewExclude": self._approved.snapshot.index.get("reviewExclude") or []}
        if not cfg["reviewBaseSha"]:
            self._mark_needs_review(
                "리뷰 기준(reviewBaseSha)이 index.json에 없음 — --base로 다시 실행")
        bad = _review_exclude_error(cfg["reviewExclude"] if cfg["reviewExclude"] is not None else [])
        if bad:
            self._mark_needs_review(f"index.json reviewExclude 형식 오류: {bad}")
        return cfg

    def _require_review_config_unchanged(self, cfg: dict):
        index = self._read_json(self._index_file)
        def norm(k, v):
            return (v or []) if k == "reviewExclude" else v
        changed = [k for k in self.REVIEW_CONFIG_KEYS
                   if norm(k, index.get(k)) != norm(k, cfg[k])]
        if changed:
            self._mark_needs_review(
                f"수정 단계가 index.json의 리뷰 기준을 바꿈({', '.join(changed)}) — "
                f"1차 리뷰 때 값으로 되돌린 뒤 재개")

    def _clear_review_outputs(self, patterns):
        try:
            for pat in patterns:
                for p in sorted(self._review_dir.glob(pat)):
                    p.unlink()
        except OSError as e:
            self._mark_needs_review(f"이전 리뷰 산출물 삭제 실패: {e}")

    def _review_round(self, round_no: int, cfg: dict) -> list:
        """리뷰 1회: manifest → 묶음별 codex 리뷰(+교차 리뷰) → strict 검증·합치기."""
        base_sha = cfg["reviewBaseSha"]
        excludes = cfg["reviewExclude"] if cfg["reviewExclude"] is not None else []

        self._review_dir.mkdir(parents=True, exist_ok=True)
        self._clear_review_outputs(self.REVIEW_OUTPUTS)
        manifest = self._build_review_manifest(base_sha, cfg["baseBranch"], excludes)
        self._write_json(self._review_dir / "review-manifest.json", manifest)

        if manifest["mode"] == "blocked":
            names = ", ".join(f"{f['path']}(+{f['added']})" for f in manifest["files"]
                              if f["path"] in manifest["oversize"])
            msg = f"한 파일의 추가 줄이 {REVIEW_ADD_LIMIT}을 넘어 리뷰하지 않음: {names}"
            self._write_review_md(manifest, round_no, {}, failure=msg)
            self._mark_needs_review(f"{msg} — 파일을 나누거나 reviewExclude에 이유를 적어 제외")

        if manifest["mode"] == "empty" and self._approved is not None:
            self._write_review_md(manifest, round_no, {},
                                  failure="리뷰할 변경 없음 — 리뷰 없이 통과할 수 없다")
            self._mark_needs_review("리뷰할 변경이 없음(빈 범위·전부 제외) — 리뷰 없이 통과 불가")

        bundles = manifest["bundles"]
        for b in bundles:
            r = self._run_git(*self._review_diff_args(base_sha, "--numstat",
                                                      pathspec=b["pathspec"]))
            if r.returncode != 0:
                self._mark_needs_review(
                    f"묶음 {b['id']} 줄 수 재계산 실패: {r.stderr.strip()[:200]}")
            b["recounted"] = sum(int(line.split("\t", 1)[0]) for line in r.stdout.splitlines()
                                 if line and not line.startswith("-"))
            if b["recounted"] > REVIEW_ADD_LIMIT:
                msg = (f"묶음 {b['id']}의 추가 줄을 리뷰어 명령으로 다시 세니 "
                       f"{b['recounted']} > {REVIEW_ADD_LIMIT} (manifest {b['added']})")
                self._write_json(self._review_dir / "review-manifest.json", manifest)
                self._write_review_md(manifest, round_no, {}, failure=msg)
                self._mark_needs_review(f"{msg} — review-manifest.json 확인")
        self._write_json(self._review_dir / "review-manifest.json", manifest)

        jobs = [(f"묶음 {b['id']}/{len(bundles)}", f"review-bundle-{b['id']}.json",
                 self._bundle_prompt(manifest, b)) for b in bundles]
        if len(bundles) > 1:
            jobs.append((self.CROSS_LABEL, "review-cross.json", self._cross_prompt(manifest)))

        results = {}
        for label, name, prompt in jobs:
            obj, err = self._invoke_reviewer(label, prompt, self._review_dir / name,
                                             head=manifest["head"])
            if err:
                self._write_review_md(manifest, round_no, results, failure=f"{label}: {err}")
                self._mark_needs_review(f"리뷰 불완전 — {label}: {err} (review.md 참조)")
            results[name] = obj["findings"]

        merged = merge_review_findings(results.values())
        self._write_json(self._review_dir / "review.json", {
            "status": "complete", "round": round_no, "range": manifest["range"],
            "head": manifest["head"], "mode": manifest["mode"],
            "bundles": len(bundles), "crossReview": len(bundles) > 1,
            "reviewModel": runtime.review_model(), "findings": merged,
        })
        self._write_review_md(manifest, round_no, results, merged=merged)
        if not bundles:
            print("  · 리뷰할 변경 없음 (review.md 참고)")
        self._reviewed_sha = manifest["head"]
        return merged

    @staticmethod
    def _review_diff_args(base_sha: str, *extra, pathspec=()) -> list:
        """리뷰 범위의 `git diff` 인자. manifest·묶음 재계산·리뷰어에게 주는 명령을
        모두 이것으로 만든다 — 옵션이 갈라지면(예: 리뷰어 명령에 -M 누락) 같은 범위를
        다르게 센다. diff.renames=false 저장소에서 큰 파일 rename이 삭제+추가로 세어져
        플러그인 3,000줄 관문에 다시 막힌다."""
        args = ["-c", "core.quotepath=false", "diff", *extra, "-M", f"{base_sha}...HEAD"]
        return args + ["--", *pathspec] if pathspec else args

    def _build_review_manifest(self, base_sha: str, base_branch, excludes) -> dict:
        """{base_sha}...HEAD의 변경 파일 전부(삭제·rename·바이너리 포함)를 기록하고
        제외·묶음을 배정한다. git 실패는 막는다 — 빈 목록으로 통과시키지 않는다."""
        diff_range = f"{base_sha}...HEAD"
        head = self._run_git("rev-parse", "HEAD")
        # -z: 경로를 따옴표·이스케이프 없이 그대로 받는다(rename·한글 경로 파싱).
        numstat = self._run_git(*self._review_diff_args(base_sha, "--numstat", "-z"))
        status = self._run_git(*self._review_diff_args(base_sha, "--name-status", "-z"))
        for r in (head, numstat, status):
            if r.returncode != 0:
                self._mark_needs_review(
                    f"리뷰 범위를 구하지 못함({diff_range}): {r.stderr.strip()[:200]}")

        statuses = _parse_name_status_z(status.stdout)
        files = []
        for added, deleted, path, old in _parse_numstat_z(numstat.stdout):
            rule = next((x for x in excludes if fnmatch.fnmatchcase(path, x["glob"])), None)
            files.append({
                "path": path, "oldPath": old,
                "status": statuses.get(path, "unknown"),
                "binary": added is None,
                "added": added or 0, "deleted": deleted or 0,
                "excluded": rule is not None,
                "excludeReason": rule["reason"] if rule else None,
                "bundle": None,
            })
        files.sort(key=lambda f: f["path"])

        reviewable = [f for f in files if not f["excluded"]]
        oversize = [f["path"] for f in reviewable if f["added"] > REVIEW_ADD_LIMIT]
        bundles = []
        if not oversize:
            by_path = {f["path"]: f for f in reviewable}
            for i, paths in enumerate(plan_review_bundles(reviewable), 1):
                pathspec = []
                for p in paths:
                    by_path[p]["bundle"] = i
                    pathspec.append(p)
                    # rename은 옛 경로도 넣어야 pathspec 안에서 -M이 rename을 찾는다.
                    if by_path[p]["oldPath"]:
                        pathspec.append(by_path[p]["oldPath"])
                bundles.append({"id": i, "added": sum(by_path[p]["added"] for p in paths),
                                "files": paths, "pathspec": pathspec})
        mode = ("blocked" if oversize else "empty" if not bundles
                else "single" if len(bundles) == 1 else "split")
        return {
            "baseBranch": base_branch, "reviewBaseSha": base_sha,
            "head": head.stdout.strip(), "range": diff_range,
            "limit": REVIEW_ADD_LIMIT,
            "totalAdded": sum(f["added"] for f in reviewable),
            "mode": mode, "oversize": oversize, "bundles": bundles, "files": files,
        }


    def _review_output_rules(self, head: str, name: str) -> str:
        return (
            f"RESULT_NAME: {name}\n"
            f"REVIEWED_HEAD: {head}\n"
            f"출력: **JSON 객체 하나만** stdout으로 내라(설명·마크다운 금지). 파일을 쓰지 마라.\n"
            f'  {{"status": "complete", "reviewed_head": "{head}", '
            f'"review_model": "{runtime.review_model()}", "findings": [{{"severity": "...", '
            f'"file": "...", "line": 0, "title": "...", "detail": "..."}}]}}\n'
            f"- severity는 critical/major/minor/nit 중 하나. 줄을 특정할 수 없으면 line은 null.\n"
            f"- `detail`에는 무엇이 어긋나 어떻게 깨지는지와 고칠 방법을 쓴다.\n"
            f"- 문제가 없으면 findings=[].\n"
            f"- 범위를 다 보지 못했으면 status를 \"degraded\"로 쓰고 \"reason\"에 사유를 적어라. "
            f"판정을 지어내지 마라.\n"
        )

    def _review_cmd(self, base_sha: str, *extra, pathspec=()) -> str:
        return shlex.join(["git", *self._review_diff_args(base_sha, *extra, pathspec=pathspec)])

    def _bundle_prompt(self, manifest: dict, bundle: dict) -> str:
        sha = manifest["reviewBaseSha"]
        n = len(manifest["bundles"])
        by_path = {f["path"]: f for f in manifest["files"]}
        lines = []
        for p in bundle["files"]:
            f = by_path[p]
            note = f"{f['status']}, +{f['added']}/-{f['deleted']}"
            if f["binary"]:
                note += ", binary"
            if f["oldPath"]:
                note += f", 옛 경로 {f['oldPath']}"
            lines.append(f"  - {p} ({note})")
        spec = bundle["pathspec"]
        cmds = (
            f"- 아래 세 명령을 **그대로** 써라. 옵션(-M 등)·범위·파일 목록을 바꾸지 마라 — 하네스가 "
            f"같은 명령으로 이 묶음의 추가 줄을 {bundle.get('recounted', bundle['added'])}줄"
            f"(한도 {REVIEW_ADD_LIMIT})로 확인했다.\n"
            f"  - 변경 확인: `{self._review_cmd(sha, '--quiet', pathspec=spec)}`\n"
            f"  - 줄 수: `{self._review_cmd(sha, '--numstat', pathspec=spec)}`\n"
            f"  - 본문: `{self._review_cmd(sha, pathspec=spec)}`\n"
        )
        scope = (f"이 phase('{self._phase_name}')가 만든 변경 전체" if n == 1
                 else f"이 phase('{self._phase_name}')가 만든 변경 중 묶음 {bundle['id']}/{n}")
        others = ("" if n == 1 else
                  "- 목록 밖 파일은 다른 묶음이 리뷰한다. 맥락이 필요하면 읽기만 하라.\n")
        return (
            f"당신은 {self._project} 프로젝트의 코드 리뷰어입니다(codex "
            f"{runtime.review_model()}, read-only).\n"
            f"{scope}를 리뷰하세요.\n\n"
            f"기준: correctness 버그·회귀·경계조건·보안·에러 처리 누락·테스트가 실제로 동작을 "
            f"검증하는가·CLAUDE.md 규칙 위반. 스타일·네이밍 취향은 nit로만.\n\n"
            f"- 범위: `{sha}...HEAD` — SHA 범위다. 브랜치 이름으로 바꾸지 마라.\n"
            f"- 대상 파일 {len(bundle['files'])}개, 추가 {bundle['added']}줄:\n"
            + "\n".join(lines) + "\n" + cmds + others
            + "\n---\n\n"
            + self._review_output_rules(manifest["head"], f"review-bundle-{bundle['id']}.json")
        )

    def _cross_prompt(self, manifest: dict) -> str:
        sha = manifest["reviewBaseSha"]
        lines = [f"  - 묶음 {b['id']} (+{b['added']}): " + ", ".join(b["files"])
                 for b in manifest["bundles"]]
        return (
            f"당신은 {self._project} 프로젝트의 코드 리뷰어입니다(codex "
            f"{runtime.review_model()}, read-only).\n"
            f"이 phase('{self._phase_name}')의 변경은 추가 {manifest['totalAdded']}줄이라 "
            f"{len(manifest['bundles'])}개 묶음으로 나눠 따로 리뷰했다. "
            f"당신은 **묶음 경계를 넘는 계약**만 확인한다.\n\n"
            f"- 범위: `{sha}...HEAD` — SHA 범위다. 브랜치 이름으로 바꾸지 마라.\n"
            f"- manifest: `{self._review_dir / 'review-manifest.json'}` "
            f"(파일별 추가/삭제 줄·상태·묶음·제외)\n"
            f"- 묶음별 파일:\n" + "\n".join(lines) + "\n\n"
            f"확인할 것: 한 묶음에서 바뀐 export·타입·설정·URL·스키마를 다른 묶음의 파일이 "
            f"쓰는 곳이 서로 맞는가(이름·인자·필드·경로가 어긋나 깨지는 곳).\n"
            f"확인하지 않을 것: 한 묶음 안에서 끝나는 문제(묶음 리뷰가 맡았다), 스타일.\n"
            f"필요한 파일만 읽어라(`{self._review_cmd(sha)} -- <파일>` — 옵션을 바꾸지 마라). "
            f"범위 전체 diff를 한 번에 읽지 마라.\n\n---\n\n"
            + self._review_output_rules(manifest["head"], "review-cross.json")
        )

    def _invoke_reviewer(self, label: str, prompt: str, out: Path, *, head: str):
        """codex gpt-6-astra read-only 리뷰 1회. stdout JSON을 하네스가 evidence로 쓴다.
        (결과, None) 또는 (None, 실패 사유)."""
        import review_plan as rp
        import runner as rn
        argv = build_code_review_argv()
        record = {"kind": "code-review", "label": label, "argv": argv,
                  "reviewModel": runtime.review_model(), "reviewedHead": head,
                  "inputSha256": _sha256(prompt), "exitCode": None, "timedOut": None,
                  "stdoutSha256": None, "failure": None, "result": None}

        def finish(obj, err):
            record["failure"] = err
            record["result"] = obj
            slug = re.sub(r"[^A-Za-z0-9]+", "-", out.stem)
            rn.write_read_only(self._review_dir / f"review-record-{slug}-{time.time_ns()}.json",
                               json.dumps(record, indent=2, ensure_ascii=False))
            if err:
                print(f"  ✗ Review {label}: {err}")
                return None, err
            self._write_json(out, obj)
            print(f"  ✓ Review {label} — 지적 {len(obj['findings'])}건 (gpt-6-astra)")
            return obj, None

        if self._head() != head:
            return finish(None, "리뷰 시작 시 HEAD가 manifest head와 다름")
        try:
            with progress_indicator(f"Review: {self._phase_name} {label}"):
                result = _run_agent_process(argv, input=prompt, cwd=self._root,
                                            timeout=self.REVIEW_TIMEOUT)
        except (OSError, subprocess.SubprocessError) as e:
            return finish(None, f"리뷰 에이전트 실행 실패: {type(e).__name__}")
        record.update(exitCode=result.returncode, timedOut=result.timed_out,
                      stdoutSha256=_sha256(result.stdout))
        if result.timed_out:
            return finish(None, f"시간 초과({self.REVIEW_TIMEOUT}s)")
        if result.returncode != 0:
            return finish(None, f"리뷰 단계 실패 (code {result.returncode})")
        if self._head() != head or self._changed_paths():
            return finish(None, "리뷰 중 HEAD 또는 작업 트리가 바뀜")
        try:
            obj = rp.parse_stdout(result.stdout)
        except rp.PlanReviewError as e:
            return finish(None, f"결과를 읽을 수 없음: {e}")
        return finish(obj, check_astra_review(obj, head))

    def _write_review_md(self, manifest: dict, round_no: int, results: dict, *,
                         merged=None, failure=None):
        """사람이 읽을 review.md(evidence). 범위·묶음·제외·교차 리뷰·지적을 모두 공개한다."""
        def cell(s):
            return str(s).replace("|", "\\|").replace("\n", " ")

        bundles = manifest["bundles"]
        mode = {
            "single": "단일 리뷰(codex 1회)",
            "split": f"분할 리뷰({len(bundles)}묶음 + 교차 리뷰)",
            "empty": "리뷰할 변경 없음",
            "blocked": "리뷰 안 함(한 파일이 한도 초과)",
        }[manifest["mode"]]
        title = "수정 후 재리뷰" if round_no > 1 else "phase 리뷰"
        out = [
            f"# {self._phase_name} — {title}", "",
            f"- 범위: `{manifest['range']}` (HEAD `{manifest['head']}`)",
            f"- 리뷰어: codex {runtime.review_model()} (read-only)",
            f"- 기준: `{manifest['baseBranch']}`와의 merge-base (index.json `reviewBaseSha`)",
            f"- 추가 줄(제외 뒤): {manifest['totalAdded']} / 한도 {manifest['limit']} → {mode}",
            f"- 파일별 기록: `{self._review_dir / 'review-manifest.json'}`", "",
        ]
        if failure:
            out += ["## ⚠ 리뷰 불완전 — needs-review", "", f"- {cell(failure)}", ""]
        out += ["## 묶음", ""]
        if bundles:
            out += ["| 묶음 | 추가 줄 | 지적 | 파일 |", "|---|---|---|---|"]
            for b in bundles:
                got = results.get(f"review-bundle-{b['id']}.json")
                out.append(f"| 묶음 {b['id']} | {b['added']} | "
                           f"{'—' if got is None else len(got)} | {cell(', '.join(b['files']))} |")
        else:
            out.append("(없음)")
        excluded = [f for f in manifest["files"] if f["excluded"]]
        out += ["", "## 제외 파일 (index.json `reviewExclude`)", ""]
        if excluded:
            out += ["| 파일 | 추가 줄 | 이유 |", "|---|---|---|"]
            out += [f"| {cell(f['path'])} | {f['added']} | {cell(f['excludeReason'])} |"
                    for f in excluded]
        else:
            out.append("(없음)")
        out += ["", f"## {self.CROSS_LABEL}", ""]
        cross = results.get("review-cross.json")
        if len(bundles) <= 1:
            out.append("해당 없음(묶음 1개 이하)")
        elif cross is None:
            out.append("결과 없음")
        else:
            out.append(f"지적 {len(cross)}건 (아래 표에 합쳤다)")
        if merged is not None:
            out += ["", f"## 지적 (중복 제거 뒤 {len(merged)}건)", ""]
            if merged:
                out += ["| severity | 위치 | 제목 | 내용 |", "|---|---|---|---|"]
                for f in merged:
                    where = f["file"] + ("" if f["line"] is None else f":{f['line']}")
                    out.append(f"| {f['severity']} | {cell(where)} | {cell(f['title'])} | "
                               f"{cell(f['detail'])} |")
            else:
                out.append("(없음)")
        self._review_dir.mkdir(parents=True, exist_ok=True)
        (self._review_dir / "review.md").write_text("\n".join(out) + "\n", encoding="utf-8")

    def _apply_review_fixes(self, findings: list) -> Optional[str]:
        """sandbox 안 구현 Claude가 지적을 반영하고 AC를 재검증한다. 커밋은 하네스가 한다.
        성공이면 None, 아니면 실패 사유. 결과 파일(status=passed)이 있어야 성공이다."""
        self._gate("fix")
        summary = "\n".join(
            f"- [{f.get('severity')}] {f.get('file')}"
            f"{'' if f.get('line') is None else ':' + str(f.get('line'))}: "
            f"{f.get('title')} — {f.get('detail')}"
            for f in findings
        )
        self._out_dir.mkdir(parents=True, exist_ok=True)
        out = self._out_dir / self.FIX_RESULT
        self._remove_agent_entry(out)
        allowed = ", ".join(self._allowed or [])
        prompt = (
            f"당신은 {self._project} 프로젝트의 개발자입니다.\n"
            f"codex {runtime.review_model()} 리뷰가 아래 지적사항을 남겼습니다. 반영해 "
            f"코드를 수정하고, 이 phase의 AC(각 step의 Acceptance Criteria)를 다시 실행해 "
            f"통과시키세요. 쓰기는 승인 경로({allowed})만 가능합니다.\n\n"
            f"{summary}\n\n---\n\n"
            f"git commit을 하지 마라 — 하네스가 허용 경로 diff를 검증한 뒤 커밋한다.\n"
            f"RESULT_FILE: {out}\n"
            f"작업을 마치기 전에 RESULT_FILE에 결과를 JSON으로 남겨라:\n"
            f'  AC 통과 → {{"status": "passed", "ac": "<실행한 AC와 결과 한 줄>"}}\n'
            f'  AC 실패 → {{"status": "failed", "reason": "<무엇이 실패했는지>"}}'
        )
        head_before = self._head()
        try:
            with progress_indicator(f"Fix: {self._phase_name} ({len(findings)} findings)"):
                result = _run_agent_process(self._sandboxed(build_impl_argv()), input=prompt,
                                            cwd=self._root, timeout=self.FIX_TIMEOUT,
                                            env=self._agent_env())
        except DescendantSurvived as e:
            return f"수정 에이전트 자손이 살아남음: {e}"
        except (OSError, subprocess.SubprocessError) as e:
            return f"수정 에이전트 실행 실패: {type(e).__name__}"
        self._after_agent("fix", head_before)
        if result.timed_out:
            return f"수정 에이전트 시간 초과({self.FIX_TIMEOUT}s)"
        if result.returncode != 0:
            return f"수정 에이전트 비정상 종료 (code {result.returncode})"
        obj = self._read_agent_result(out)
        if obj is None:
            return f"수정 결과 파일 없음({self.FIX_RESULT})"
        status = obj.get("status")
        if status == "passed":
            return None
        if status == "failed":
            return f"AC 재검증 실패: {obj.get('reason', '사유 없음')}"
        return f"수정 결과 형식 오류(status={status!r})"

    def _mark_needs_review(self, reason: str):
        """phase를 needs-review로 막고 사람 개입을 요구한 뒤 종료코드 3."""
        ts = self._stamp()
        index = self._read_json(self._index_file)
        index["status"] = "needs-review"
        index["review_reason"] = reason
        index["review_at"] = ts
        self._write_json(self._index_file, index)
        self._update_top_index("needs-review")
        print(f"\n  ⚠ Phase '{self._phase_name}' needs review — {reason}")
        print(f"    See {self._review_dir / 'review.md'}")
        print(f"    Resolve, then reset status to 'pending'/'completed' to resume.")
        sys.exit(3)


def main(argv=None):
    runtime.require_runtime()
    import runner as rn
    raw = list(sys.argv[1:] if argv is None else argv)
    if any(a == "--push" or a.startswith("--push=") for a in raw):
        print("ERROR: --push는 지원하지 않는다 — push는 Ryan이 runner verify-final로 "
              "tested = reviewed = HEAD를 확인한 뒤 feature branch만 한다.")
        sys.exit(2)
    parser = argparse.ArgumentParser(description="Harness Step Executor")
    parser.add_argument("phase_dir", help="Phase directory name (e.g. 0-mvp)")
    parser.add_argument("--base", help="리뷰 기준 브랜치 — main만 허용(승인된 baseBranch)")
    parser.add_argument("--repo-root", default=str(ROOT), help="독립 clone root")
    args = parser.parse_args(raw)

    preflight()
    try:
        desc = rn.load_descriptor(os.environ.get("HARNESS_LAUNCH_DESCRIPTOR"), args.repo_root)
    except rn.RunnerError as e:
        print(f"ERROR: {e}")
        sys.exit(1)
    if desc["task"] != args.phase_dir:
        print(f"ERROR: descriptor task '{desc['task']}' ≠ '{args.phase_dir}'")
        sys.exit(1)
    try:
        rn.consume_ticket(os.environ.get("HARNESS_LAUNCH_TICKET"),
                          os.environ.get("HARNESS_LAUNCH_DESCRIPTOR"), desc)
    except (rn.RunnerError, OSError, ValueError) as e:
        print(f"ERROR: {e}")
        sys.exit(1)
    _install_signal_exit()
    StepExecutor(args.phase_dir, descriptor=desc, base=args.base).run()


if __name__ == "__main__":
    main()
