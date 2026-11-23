#!/usr/bin/env python3
"""계획(phases/{task})을 실행 전에 Codex gpt-6-astra로 read-only 리뷰한다.

Usage: ./.venv/bin/python scripts/harness.py review-plan {task} --issue <ISSUE> \
        --repo-root <target 독립 clone> --evidence-dir <회사 evidence>

- --repo-root·--issue 필수(기본값으로 하네스 저장소를 고르지 않는다). Codex spawn 전에
  target을 검증한다: git toplevel·독립 clone·symlink 아님·feat/<ISSUE>/<slug> branch
  (main·detached 금지)·baseBranch=main·local main·clean docs/phases·evidence는
  target·하네스 양쪽 밖. record(version 2)에 issue·repoRoot·branch·baseBranch·
  planCommitSha·reviewBaseSha를 결속한다.

- 리뷰 backend=codex, model=gpt-6-astra를 **명시**해야 한다(HARNESS_REVIEW_BACKEND /
  HARNESS_REVIEW_MODEL). 다른 값·미설정은 실패.
- Codex는 read-only sandbox로 띄우고 stdout의 JSON을 하네스가 evidence record로 쓴다.
- hash는 scripts/plan_manifest.py 단일 canonical manifest로 계산한다.
- findings가 있으면 **자동 수정하지 않는다**(종료코드 4). 같은 planning session으로
  계획을 재생성한 뒤 새 hash로 이 명령을 다시 돌려야 한다.
- 종료코드: 0 clean / 4 has_findings / 2 리뷰 실패(누락·손상·degraded·불일치·timeout·
  리뷰 중 계획/HEAD/branch 변경) / 1 preflight 실패(정책·target·evidence — Codex 미실행).

3.9에서도 파싱되어야 한다 — 3.10+ 문법 금지.
"""
import argparse
import contextlib
import hashlib
import json
import os
import re
import stat
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import runtime  # noqa: E402

for _s in (sys.stdout, sys.stderr):
    with contextlib.suppress(AttributeError, ValueError):
        _s.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parent.parent
VALID_SEVERITY = ("critical", "major", "minor")
REVIEW_TIMEOUT = 900
RESULT_KEYS = {"task", "review_backend", "review_model", "reviewed_plan_sha", "verdict",
               "findings"}
FINDING_KEYS = {"severity", "step_file", "principle", "summary", "fix"}
EXIT_CLEAN, EXIT_PREFLIGHT, EXIT_FAILED, EXIT_FINDINGS = 0, 1, 2, 4
RECORD_VERSION = 2
BINDING_KEYS = ("issue", "repoRoot", "branch", "baseBranch", "planCommitSha", "reviewBaseSha")


class PlanReviewError(Exception):
    pass


def build_review_argv():
    return ["codex", "exec", "--dangerously-bypass-hook-trust",
            "--sandbox", "read-only", "--model", runtime.review_model()]


def _verify_index_integrity(index, target=None):
    """step 번호 연속성·중복 없음·name kebab-case 검증. 오류 목록 반환.
    (strict 검증의 정본은 plan_manifest.validate_index — 이 함수는 사람용 진단)"""
    errors = []
    steps = index.get("steps", [])
    nums = [s.get("step") for s in steps]
    if sorted(n for n in nums if isinstance(n, int)) != list(range(len(steps))):
        errors.append("step 번호가 0..%d 연속이 아님: %s" % (len(steps) - 1, nums))
    for s in steps:
        name = s.get("name", "")
        if not re.fullmatch(r"[a-z0-9]+(-[a-z0-9]+)*", name):
            errors.append("name '%s'이 kebab-case가 아님" % name)
    if target is not None:
        indexed = {n for n in nums if isinstance(n, int)}
        for n in sorted(indexed):
            if not (Path(target) / ("step%d.md" % n)).is_file():
                errors.append("index의 step %d에 해당하는 step%d.md 파일이 없음" % (n, n))
    return errors


def build_prompt(task, m):
    idx = m.index
    steps_md = "\n\n".join(
        "### step%d.md\n%s" % (s["step"], m.read("phases/%s/step%d.md" % (task, s["step"]))
                               .decode("utf-8"))
        for s in idx["steps"])
    design = m.read(idx["designDoc"]).decode("utf-8")
    schema = json.dumps({
        "task": task, "review_backend": "codex", "review_model": runtime.review_model(),
        "reviewed_plan_sha": m.sha, "verdict": "clean|has_findings",
        "findings": [{"severity": "critical|major|minor", "step_file": "stepN.md",
                      "principle": "...", "summary": "...", "fix": "..."}]},
        ensure_ascii=False)
    return (
        "당신은 계획 리뷰어입니다(read-only). 아래 계획을 실행 전에 검토하세요. 파일을 수정하지 마라.\n"
        "기준: scope 최소화 / 자기완결성 / 사전 준비 강제 / 시그니처 수준 지시 / "
        "AC는 실행 가능한 커맨드 / 구체적 주의사항 / kebab-case 네이밍 / allowedPaths가 "
        "step 작업에 충분하고 최소인가 / CLAUDE.md·docs 가드레일. "
        "step 예산(에이전트 예상 소요 20분 이하, 하네스 제한 30분) — 예상이 20분을 넘으면 "
        "major로 적고 fix는 원래 작업 경계대로 step 분할.\n\n"
        "## 설계 문서 (%s)\n%s\n\n## index.json 불변 필드\n%s\n\n## steps\n%s\n\n---\n\n"
        "출력: **JSON 객체 하나만** stdout으로 내라(설명·마크다운 금지). 스키마:\n%s\n"
        "- reviewed_plan_sha는 반드시 %s 그대로.\n"
        "- 문제 없으면 verdict=\"clean\", findings=[]. 문제가 있으면 verdict=\"has_findings\".\n"
        "- step_file은 위 stepN.md 중 하나. 모든 finding 필드는 비어 있지 않은 문자열.\n"
        % (idx["designDoc"], design, json.dumps(idx, ensure_ascii=False, indent=2), steps_md,
           schema, m.sha))


def parse_stdout(text):
    s = (text or "").strip()
    fence = re.fullmatch(r"```(?:json)?\s*\n(.*)\n```", s, re.DOTALL)
    if fence:
        s = fence.group(1).strip()
    try:
        obj = json.loads(s)
    except ValueError as e:
        raise PlanReviewError("stdout이 JSON 하나가 아님: %s" % e)
    if not isinstance(obj, dict):
        raise PlanReviewError("결과가 JSON 객체가 아님")
    return obj


def validate_result(obj, task, plan_sha, step_files):
    """strict 검증. 'clean' 또는 'has_findings'를 돌려주고, 아니면 PlanReviewError."""
    keys = set(obj)
    if keys != RESULT_KEYS:
        raise PlanReviewError("결과 키 불일치: 누락 %s / 초과 %s"
                              % (sorted(RESULT_KEYS - keys), sorted(keys - RESULT_KEYS)))
    if obj["task"] != task:
        raise PlanReviewError("task 불일치: %r" % obj["task"])
    if obj["review_backend"] != runtime.REQUIRED_REVIEW_BACKEND:
        raise PlanReviewError("review_backend 불일치: %r" % obj["review_backend"])
    if obj["review_model"] != runtime.review_model():
        raise PlanReviewError("review_model 불일치: %r" % obj["review_model"])
    if obj["reviewed_plan_sha"] != plan_sha:
        raise PlanReviewError("reviewed_plan_sha 불일치")
    verdict, findings = obj["verdict"], obj["findings"]
    if verdict not in ("clean", "has_findings"):
        raise PlanReviewError("verdict 값 오류(degraded 등): %r" % (verdict,))
    if not isinstance(findings, list):
        raise PlanReviewError("findings가 목록이 아님")
    if verdict == "clean" and findings:
        raise PlanReviewError("verdict=clean인데 findings가 있음")
    if verdict == "has_findings" and not findings:
        raise PlanReviewError("verdict=has_findings인데 findings가 비어 있음")
    for n, f in enumerate(findings, 1):
        if not isinstance(f, dict) or set(f) != FINDING_KEYS:
            raise PlanReviewError("finding %d 키 불일치" % n)
        if f["severity"] not in VALID_SEVERITY:
            raise PlanReviewError("finding %d severity 오류: %r" % (n, f["severity"]))
        if f["step_file"] not in step_files:
            raise PlanReviewError("finding %d step_file이 실제 step이 아님: %r" % (n, f["step_file"]))
        for k in ("principle", "summary", "fix"):
            if not isinstance(f[k], str) or not f[k].strip():
                raise PlanReviewError("finding %d %s가 비어 있음" % (n, k))
    return verdict


def _sha(data):
    if isinstance(data, str):
        data = data.encode("utf-8")
    return hashlib.sha256(data).hexdigest()


def _stamp():
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")


def require_outside_repo(path, root):
    p = Path(path).resolve()
    r = Path(root).resolve()
    if p == r or r in p.parents:
        raise PlanReviewError("evidence 경로는 repo 밖이어야 함: %s" % p)
    return p


def require_safe_evidence_dirs(evidence_dir, rels, repos):
    """evidence_dir 아래 실제 디렉터리 component(task·plan-reviews 등)를 하나씩 lstat해
    symlink·비디렉터리를 거부하고, resolve된 목적지가 모든 repo 밖인지 확인한다."""
    base = Path(evidence_dir)
    for rel in rels:
        cur = base
        for part in rel.split("/"):
            cur = cur / part
            try:
                st = os.lstat(str(cur))
            except FileNotFoundError:
                break
            except OSError as e:
                raise PlanReviewError("evidence 경로 확인 실패 %s: %s" % (cur, e))
            if stat.S_ISLNK(st.st_mode) or not stat.S_ISDIR(st.st_mode):
                raise PlanReviewError("evidence 하위 경로가 실제 디렉터리가 아님(symlink 등): %s"
                                      % cur)
        for r in repos:
            require_outside_repo(base / rel, r)


def preflight_target(repo_root, issue, task, evidence_dir):
    """Codex spawn 전 외부 target 경계 검증(fail-closed). 실패하면 PlanReviewError.

    공통 경계(git toplevel·독립 clone·feature branch)는 approval.check_repo_boundary를
    재사용하고, 리뷰 단계 고유 검사(입력 symlink·baseBranch·local main·clean plan tree·
    evidence 위치)만 여기서 한다. 리뷰 record에 결속할 target binding을 돌려준다."""
    import approval as ap
    raw = Path(repo_root)
    if raw.is_symlink():
        raise PlanReviewError("--repo-root가 symlink임: %s" % raw)
    if not raw.is_dir():
        raise PlanReviewError("--repo-root가 디렉터리가 아님: %s" % raw)
    repo = raw.resolve()
    try:
        branch = ap.check_repo_boundary(repo, issue)
    except ap.ApprovalError as e:
        raise PlanReviewError(str(e))
    require_outside_repo(evidence_dir, repo)
    require_outside_repo(evidence_dir, ROOT)
    require_safe_evidence_dirs(evidence_dir, review_evidence_rels(task), (repo, ROOT))
    try:
        index = json.loads((repo / "phases" / task / "index.json").read_text(encoding="utf-8"))
    except (OSError, ValueError) as e:
        raise PlanReviewError("plan index를 읽을 수 없음: %s" % e)
    if not isinstance(index, dict) or index.get("baseBranch") != ap.REQUIRED_BASE_BRANCH:
        raise PlanReviewError("계획 baseBranch는 %s여야 함" % ap.REQUIRED_BASE_BRANCH)
    if ap._git(repo, "rev-parse", "--verify", "-q",
               "refs/heads/%s^{commit}" % ap.REQUIRED_BASE_BRANCH).returncode != 0:
        raise PlanReviewError("local %s ref 없음" % ap.REQUIRED_BASE_BRANCH)
    head = ap._git(repo, "rev-parse", "HEAD").stdout.strip()
    if not ap._SHA40.fullmatch(head):
        raise PlanReviewError("HEAD가 40자 commit SHA가 아님")
    base = ap._git(repo, "merge-base", ap.BASE_REF, head).stdout.strip()
    if not ap._SHA40.fullmatch(base):
        raise PlanReviewError("%s와의 merge-base를 구할 수 없음" % ap.REQUIRED_BASE_BRANCH)
    dirty = ap._git(repo, "status", "--porcelain", "--untracked-files=all", "--",
                    "docs", "phases")
    if dirty.returncode != 0 or dirty.stdout.strip():
        raise PlanReviewError("docs/phases에 커밋되지 않은 변경이 있음")
    return {"issue": issue, "repoRoot": str(repo), "branch": branch,
            "baseBranch": ap.REQUIRED_BASE_BRANCH, "planCommitSha": head,
            "reviewBaseSha": base}


def _recheck_target(root, binding):
    """리뷰 종료 후 target HEAD·branch가 리뷰 시작 시점과 같은가."""
    import approval as ap
    head = ap._git(root, "rev-parse", "HEAD").stdout.strip()
    if head != binding["planCommitSha"]:
        raise PlanReviewError("리뷰 중 target HEAD가 변경됨 — 다시 리뷰하라")
    branch = ap._git(root, "symbolic-ref", "--short", "-q", "HEAD").stdout.strip()
    if branch != binding["branch"]:
        raise PlanReviewError("리뷰 중 target branch가 변경됨 — 다시 리뷰하라")


def review_evidence_rels(task):
    return (task, "%s/plan-reviews" % task)


def _write_record(evidence_dir, task, record):
    require_safe_evidence_dirs(evidence_dir, review_evidence_rels(task),
                               (Path(record["repoRoot"]), ROOT))
    d = Path(evidence_dir) / task / "plan-reviews"
    d.mkdir(parents=True, exist_ok=True)
    data = json.dumps(record, indent=2, ensure_ascii=False, sort_keys=True).encode("utf-8")
    sha = _sha(data)
    name = "%s-%s.json" % (record["recordedAt"], sha[:12])
    path = d / name
    with open(path, "xb") as f:
        f.write(data)
    os.chmod(path, 0o444)
    latest = {"recordFile": name, "recordSha": sha, "reviewedPlanSha": record["reviewedPlanSha"],
              "verdict": record["verdict"]}
    try:
        publish_pointer(d / "latest.json", d / ("latest.json.tmp-%d" % os.getpid()),
                        json.dumps(latest, indent=2).encode("utf-8"))
    except OSError as e:
        raise PlanReviewError("latest.json 공개 실패: %s" % e)
    return path, sha


def publish_pointer(dest, tmp, data):
    """tmp를 배타·no-follow로 새로 만들어 쓴 뒤 dest로 rename한다. tmp 자리에 무엇이든
    (symlink 포함) 이미 있으면 OSError — dest와 기존 항목은 건드리지 않는다."""
    fd = os.open(str(tmp), os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o644)
    try:
        with os.fdopen(fd, "wb") as f:
            f.write(data)
        os.replace(str(tmp), str(dest))
    except BaseException:
        with contextlib.suppress(OSError):
            os.unlink(str(tmp))
        raise


def run_review(root, task, evidence_dir, issue, runner=None):
    """리뷰 1회. (exit_code, record_path|None, record_sha|None).
    target preflight 실패는 Codex를 띄우지 않고 EXIT_PREFLIGHT(record 없음)."""
    import execute as ex
    import plan_manifest as pm
    runner = runner or ex._run_agent_process
    try:
        binding = preflight_target(root, issue, task, evidence_dir)
    except PlanReviewError as e:
        print("  ✗ target preflight 실패: %s" % e)
        return EXIT_PREFLIGHT, None, None
    root = Path(binding["repoRoot"])
    try:
        m = pm.build_manifest(root, task)
    except pm.ManifestError as e:
        print("  ✗ 계획 manifest 검증 실패: %s" % e)
        return EXIT_FAILED, None, None
    import approval as ap
    try:
        ap.require_plan_committed(root, binding["planCommitSha"], task, m)
    except ap.ApprovalError as e:
        print("  ✗ target preflight 실패: %s" % e)
        return EXIT_PREFLIGHT, None, None
    not_pending = [s for s in json.loads(
        (root / "phases" / task / "index.json").read_text(encoding="utf-8"))["steps"]
        if s.get("status", "pending") != "pending"]
    if not_pending:
        print("  ✗ 이미 실행된 계획은 리뷰·승인 대상이 아님(step %s)" % not_pending[0]["step"])
        return EXIT_FAILED, None, None

    argv = build_review_argv()
    prompt = build_prompt(task, m)
    step_files = {"step%d.md" % s["step"] for s in m.index["steps"]}
    record = {
        "kind": "plan-review", "version": RECORD_VERSION, "task": task,
        "reviewBackend": runtime.REQUIRED_REVIEW_BACKEND,
        "reviewModel": runtime.review_model(),
        "argv": argv, "inputSha256": _sha(prompt), "reviewedPlanSha": m.sha,
        "manifestCodeSha": pm.code_sha(), "runtime": runtime.runtime_evidence(),
        "recordedAt": None, "exitCode": None, "timedOut": None, "stdoutSha256": None,
        "stderrSha256": None, "verdict": "failed", "failure": None, "findings": [],
        "result": None,
    }
    record.update(binding)
    try:
        result = runner(argv, input=prompt, cwd=str(root), timeout=REVIEW_TIMEOUT)
    except (OSError, ValueError) as e:
        record["failure"] = "리뷰어 실행 실패: %s" % type(e).__name__
        result = None
    if result is not None:
        record.update(exitCode=result.returncode, timedOut=bool(result.timed_out),
                      stdoutSha256=_sha(result.stdout), stderrSha256=_sha(result.stderr))
        try:
            if result.timed_out:
                raise PlanReviewError("리뷰 시간 초과(%ds)" % REVIEW_TIMEOUT)
            if result.returncode != 0:
                raise PlanReviewError("리뷰어 비정상 종료(code %s)" % result.returncode)
            try:
                after = pm.build_manifest(root, task).sha
            except pm.ManifestError as e:
                raise PlanReviewError("리뷰 중 계획이 변경/손상됨: %s" % e)
            if after != m.sha:
                raise PlanReviewError("리뷰 중 계획이 변경됨 — 다시 리뷰하라")
            _recheck_target(root, binding)
            obj = parse_stdout(result.stdout)
            record["result"] = obj
            record["verdict"] = validate_result(obj, task, m.sha, step_files)
            record["findings"] = obj["findings"]
        except PlanReviewError as e:
            record["verdict"] = "failed"
            record["failure"] = str(e)
    record["recordedAt"] = _stamp()
    try:
        path, sha = _write_record(evidence_dir, task, record)
    except PlanReviewError as e:
        print("  ✗ 리뷰 record 기록 거부: %s" % e)
        return EXIT_FAILED, None, None
    if record["verdict"] == "clean":
        print("  ✓ 계획 리뷰 clean (gpt-6-astra) — record %s" % sha)
        return EXIT_CLEAN, path, sha
    if record["verdict"] == "has_findings":
        print("  ✗ 계획 리뷰 지적 %d건 — 자동 수정하지 않는다. 같은 planning session으로 "
              "계획을 재생성한 뒤 다시 리뷰하라. record %s" % (len(record["findings"]), sha))
        for f in record["findings"]:
            print("    - [%s] %s: %s → %s" % (f["severity"], f["step_file"], f["summary"], f["fix"]))
        return EXIT_FINDINGS, path, sha
    print("  ✗ 계획 리뷰 실패: %s — record %s" % (record["failure"], sha))
    return EXIT_FAILED, path, sha


def verify_clean_review(evidence_dir, task, record_sha, current_plan_sha, repo, issue,
                        plan_commit, review_base=None):
    """승인·실행용: record_sha가 task의 **최신** clean 리뷰이고 현재 계획 hash와 일치하며,
    현재 target(repo·issue·branch)과 approval이 고정한 plan commit에 결속돼 있는가.

    - plan_commit: approval이 고정한(또는 승인할) 계획 commit — review commit과 exact 동일.
    - review_base: 주어지면 record의 reviewBaseSha와 exact 동일해야 한다.
    - 현재 HEAD는 plan_commit의 descendant면 허용(구현 진행), reviewBaseSha는 plan commit과
      현재 local main의 조상이어야 한다(정상 fast-forward 허용, ancestry 깨진 rewrite 거부).
    - version 2 + binding 필드 필수. legacy(version 1·필드 누락)는 재리뷰·재승인 필요."""
    import approval as ap
    import plan_manifest as pm
    require_safe_evidence_dirs(evidence_dir, review_evidence_rels(task), (repo, ROOT))
    d = Path(evidence_dir) / task / "plan-reviews"
    try:
        latest = json.loads((d / "latest.json").read_text(encoding="utf-8"))
    except (OSError, ValueError) as e:
        raise PlanReviewError("plan review latest 없음/손상: %s" % e)
    if latest.get("recordSha") != record_sha:
        raise PlanReviewError("지정한 리뷰가 최신 리뷰가 아님 — 최신 리뷰 기준으로 다시 승인하라")
    name = latest.get("recordFile", "")
    if not re.fullmatch(r"[0-9TZ]+-[0-9a-f]{12}\.json", name or ""):
        raise PlanReviewError("record 파일명 형식 오류")
    try:
        data = pm.read_regular(d, name)
    except pm.ManifestError as e:
        raise PlanReviewError("record 읽기 실패: %s" % e)
    if _sha(data) != record_sha:
        raise PlanReviewError("plan review record hash 불일치(변조)")
    rec = json.loads(data.decode("utf-8"))
    if not isinstance(rec, dict):
        raise PlanReviewError("plan review record 형식 오류")
    argv = rec.get("argv") or []
    repo = Path(repo)
    checks = [
        (rec.get("kind") == "plan-review", "kind"),
        (rec.get("version") == RECORD_VERSION,
         "version(legacy record — 새 CLI로 재리뷰·재승인 필요)"),
        (all(isinstance(rec.get(k), str) and rec.get(k) for k in BINDING_KEYS),
         "binding 필드 누락"),
        (rec.get("task") == task, "task"),
        (rec.get("reviewBackend") == runtime.REQUIRED_REVIEW_BACKEND, "reviewBackend"),
        (rec.get("reviewModel") == runtime.review_model(), "reviewModel"),
        (argv == build_review_argv(), "argv(--model gpt-6-astra --sandbox read-only)"),
        (rec.get("exitCode") == 0 and rec.get("timedOut") is False, "exit"),
        (rec.get("verdict") == "clean" and rec.get("findings") == [] and not rec.get("failure"),
         "verdict clean"),
        (isinstance(rec.get("result"), dict) and rec["result"].get("verdict") == "clean",
         "result"),
        (rec.get("reviewedPlanSha") == current_plan_sha, "reviewedPlanSha(현재 계획과 다름)"),
        (rec.get("manifestCodeSha") == pm.code_sha(), "manifestCodeSha"),
        (rec.get("issue") == issue, "issue"),
        (rec.get("repoRoot") == str(repo.resolve()), "repoRoot(다른 clone)"),
        (rec.get("baseBranch") == ap.REQUIRED_BASE_BRANCH, "baseBranch=main"),
        (rec.get("planCommitSha") == plan_commit, "planCommitSha(승인 commit과 다름)"),
        (bool(ap._SHA40.fullmatch(rec.get("reviewBaseSha") or "")), "reviewBaseSha 형식"),
        (review_base is None or rec.get("reviewBaseSha") == review_base,
         "reviewBaseSha(승인 merge-base와 다름)"),
    ]
    for ok, what in checks:
        if not ok:
            raise PlanReviewError("plan review record 검증 실패: %s" % what)
    try:
        ap.check_repo_boundary(repo, issue, expected_branch=rec["branch"])
    except ap.ApprovalError as e:
        raise PlanReviewError("plan review target 검증 실패(branch): %s" % e)
    for anc, desc in ((plan_commit, "HEAD"), (rec["reviewBaseSha"], plan_commit),
                      (rec["reviewBaseSha"], ap.BASE_REF)):
        if ap._git(repo, "merge-base", "--is-ancestor", anc, desc).returncode != 0:
            raise PlanReviewError("plan review 결속 실패: %s가 %s의 조상이 아님"
                                  % (anc[:10], desc[:10]))
    return rec


def main(argv=None):
    runtime.require_runtime()
    import execute as ex
    ex._install_signal_exit()
    parser = argparse.ArgumentParser(description="Codex gpt-6-astra 계획 리뷰")
    parser.add_argument("task")
    parser.add_argument("--repo-root", required=True)
    parser.add_argument("--issue", required=True)
    parser.add_argument("--evidence-dir", default=os.environ.get("HARNESS_EVIDENCE_DIR"))
    args = parser.parse_args(argv)
    errors = runtime.review_policy_errors()
    if not args.evidence_dir:
        errors.append("--evidence-dir(회사 evidence 경로, repo 밖) 필수")
    else:
        try:
            require_outside_repo(args.evidence_dir, ROOT)
        except PlanReviewError as e:
            errors.append(str(e))
    if errors:
        for e in errors:
            print("ERROR: " + e)
        sys.exit(1)
    code, _, _ = run_review(args.repo_root, args.task, args.evidence_dir, args.issue)
    sys.exit(code)


if __name__ == "__main__":
    main()
