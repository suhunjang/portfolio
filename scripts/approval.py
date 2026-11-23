#!/usr/bin/env python3
"""구현 승인 기록·검증 — 계획 commit·content hash·clean Astra review·Discord 승인 메시지 결속.

승인 메시지는 계획 합의 메시지와 **별개**다. 본문은 정확히
`APPROVE <ISSUE> PLAN <40자 commit SHA> REVIEW <64자 review-record SHA>`.
승인 record와 approved-plan snapshot은 worktree 밖 회사 evidence 경로에 쓴다.

승인자 user ID·전역 승인 thread·issue-scoped thread·issue key 정규식은 하네스 root의
`.harness/policy.json`(runtime.policy())에서만 읽는다. 없거나 틀리면 승인·검증 모두 거부한다.

Usage:
  ./.venv/bin/python scripts/harness.py plan-session record-approval ...   (기록)
  ./.venv/bin/python scripts/harness.py approval verify --task T --evidence-dir E \
        --record-sha <Linear에 기록된 sha> [--first-run]                     (검증)

3.9에서도 파싱되어야 한다 — 3.10+ 문법 금지.
"""
import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import runtime  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
_MSG_RE = re.compile(r"[A-Za-z0-9:_-]{1,80}")


class ApprovalError(Exception):
    exit_code = 1


def _policy():
    """project policy(.harness/policy.json). 없거나 틀리면 ApprovalError(fail closed)."""
    try:
        return runtime.policy()
    except runtime.PolicyError as e:
        raise ApprovalError("승인 policy 오류: %s" % e)


def approver_authorized(user_id, policy=None):
    pol = policy or _policy()
    return isinstance(user_id, str) and user_id in pol.approver_user_ids


class Verified:
    def __init__(self, record, record_sha, snapshot, manifest):
        self.record = record
        self.record_sha = record_sha
        self.snapshot = snapshot
        self.manifest = manifest


def _sha(data):
    if isinstance(data, str):
        data = data.encode("utf-8")
    return hashlib.sha256(data).hexdigest()


def _git(repo, *args):
    return subprocess.run(["git"] + list(args), cwd=str(repo), capture_output=True, text=True,
                          encoding="utf-8")


def gateway_sha(body, user_id, thread_id, message_id):
    return _sha(json.dumps({"body": body, "userId": user_id, "threadId": thread_id,
                            "messageId": message_id}, sort_keys=True, ensure_ascii=False))


def _outside(path, repo):
    p, r = Path(path).resolve(), Path(repo).resolve()
    if p == r or r in p.parents:
        raise ApprovalError("evidence 경로는 repo 밖이어야 함: %s" % p)


def parse_body(body):
    pol = _policy()
    if body.endswith("\n"):
        body = body[:-1]
    m = pol.body_re.fullmatch(body)
    if not m or not pol.issue_matches(m.group("issue")):
        raise ApprovalError("승인 본문이 exact 형식이 아님: "
                            "'APPROVE <ISSUE> PLAN <40hex> REVIEW <64hex>' "
                            "(ISSUE는 policy issueKeyPattern)")
    return body, m.group("issue"), m.group("plan"), m.group("review")


REQUIRED_BASE_BRANCH = "main"
# merge-base·ancestry는 항상 local branch ref로 — 같은 이름 tag가 끼어들지 못하게.
BASE_REF = "refs/heads/%s" % REQUIRED_BASE_BRANCH
_SHA40 = re.compile(r"[0-9a-f]{40}")


def thread_authorized(thread_id, issue, policy=None):
    """승인 생성·검증 공통: thread가 이 issue의 구현 승인을 받을 수 있는가.
    전역 승인 thread는 모든 issue, issue-scoped thread는 policy에 지정된 issue만."""
    pol = policy or _policy()
    return pol.thread_authorized(thread_id, issue)


def check_repo_boundary(repo, issue, expected_branch=None):
    """B1: repo root = git toplevel, 독립 clone(linked worktree 아님), 승인 feature branch.
    main·detached·패턴 밖 branch는 거부한다. 현재 branch 이름을 돌려준다.
    issue는 policy issueKeyPattern과 안전 문자 규칙을 만족해야 한다."""
    if not _policy().issue_matches(issue):
        raise ApprovalError("issue key %r가 policy issueKeyPattern과 맞지 않음" % (issue,))
    repo = Path(repo)
    top = _git(repo, "rev-parse", "--show-toplevel")
    if top.returncode != 0 or Path(top.stdout.strip()).resolve() != repo.resolve():
        raise ApprovalError("repo root가 git toplevel이 아님: %s" % repo)
    gd = _git(repo, "rev-parse", "--absolute-git-dir").stdout.strip()
    common = _git(repo, "rev-parse", "--git-common-dir").stdout.strip()
    common_abs = (repo / common).resolve() if common else None
    dot_git = repo / ".git"
    if (not gd or not dot_git.is_dir() or dot_git.is_symlink()
            or Path(gd).resolve() != dot_git.resolve() or common_abs != dot_git.resolve()):
        raise ApprovalError("독립 clone이 아님(linked worktree·공유 .git) — runner의 독립 clone에서만")
    r = _git(repo, "symbolic-ref", "--short", "-q", "HEAD")
    branch = r.stdout.strip()
    if r.returncode != 0 or not branch:
        raise ApprovalError("detached HEAD — 승인 feature branch에서만")
    if branch == REQUIRED_BASE_BRANCH or not re.fullmatch(
            r"feat/%s/[a-z0-9][a-z0-9-]*" % re.escape(issue), branch):
        raise ApprovalError("branch '%s'가 승인 패턴 feat/%s/<slug>가 아님(main 금지)"
                            % (branch, issue))
    if expected_branch is not None and branch != expected_branch:
        raise ApprovalError("현재 branch '%s'가 승인 branch '%s'가 아님" % (branch, expected_branch))
    return branch


def require_plan_committed(repo, commit, task, m):
    """manifest 입력 전부(index.json 포함)가 exact plan commit에 regular blob으로 있고
    작업트리 bytes와 같은가. ignored·untracked·skip-worktree 입력은 git status에 안 보인다."""
    import plan_manifest as pm
    index_rel = "phases/%s/index.json" % task
    paths = sorted(set(m.files) | {index_rel})
    for rel in paths:
        try:
            local = m.files[rel] if rel in m.files else pm.read_regular(repo, rel)
        except pm.ManifestError as e:
            raise ApprovalError("계획 입력 읽기 실패: %s" % e)
        tree = _git(repo, "ls-tree", "--full-tree", commit, "--", rel).stdout.split("\t")[0]
        if tree.split(" ")[:2] not in (["100644", "blob"], ["100755", "blob"]):
            raise ApprovalError("계획 입력이 plan commit에 regular file로 없음: %s" % rel)
        blob = subprocess.run(["git", "cat-file", "blob", "%s:%s" % (commit, rel)],
                              cwd=str(repo), capture_output=True)
        if blob.returncode != 0 or blob.stdout != local:
            raise ApprovalError("계획 입력이 plan commit 내용과 다름: %s" % rel)


def _snapshot_rels(snap_rel, include_staging=False):
    """approved-plan/<sha>와 files 루트(+선택적으로 staging) — 경계 검사 대상 상대경로."""
    rels = (snap_rel, snap_rel + "/files")
    if include_staging:
        rels += (snap_rel + ".staging",)
    return rels


def _require_safe_approval_dirs(evidence_dir, task, repo, extra=()):
    import review_plan as rp
    rels = (task, "%s/approvals" % task, "%s/approved-plan" % task,
            "%s/plan-reviews" % task, "approval-messages") + tuple(extra)
    try:
        rp.require_safe_evidence_dirs(evidence_dir, rels, (repo, rp.ROOT))
    except rp.PlanReviewError as e:
        raise ApprovalError(str(e))


def start_marker_path(evidence_dir, task, approval_sha):
    return Path(evidence_dir) / task / "runs" / ("%s.json" % approval_sha)


def is_first_run(evidence_dir, task, approval_sha, plan_commit=None):
    """M4: 최초 실행 여부는 **이 승인 record**의 marker로만 정한다."""
    p = start_marker_path(evidence_dir, task, approval_sha)
    if not p.exists():
        return True
    try:
        d = json.loads(p.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        raise ApprovalError("start marker 손상: %s" % p)
    if d.get("approvalRecordSha") != approval_sha or (
            plan_commit is not None and d.get("planCommitSha") != plan_commit):
        raise ApprovalError("start marker가 현재 승인/계획 commit과 다름: %s" % p)
    return False


def write_start_marker(evidence_dir, task, approval_sha, plan_commit, head=None):
    p = start_marker_path(evidence_dir, task, approval_sha)
    p.parent.mkdir(parents=True, exist_ok=True)
    with open(p, "x", encoding="utf-8") as f:
        json.dump({"approvalRecordSha": approval_sha, "planCommitSha": plan_commit,
                   "head": head, "at": datetime.now(timezone.utc).isoformat()}, f)
    os.chmod(p, 0o444)
    return p


def record_approval(session, repo, task, issue, message_id, user_id, body, plan_commit,
                    evidence_dir):
    import plan_manifest as pm
    import review_plan as rp
    repo, evidence_dir = Path(repo), Path(evidence_dir)
    _outside(evidence_dir, repo)
    _require_safe_approval_dirs(evidence_dir, task, repo)
    if not isinstance(message_id, str) or not _MSG_RE.fullmatch(message_id):
        raise ApprovalError("approval message id 형식 오류")
    if not approver_authorized(user_id):
        raise ApprovalError("승인 권한 없는 user(policy approverUserIds 밖): %s" % user_id)
    thread_id = session.thread_id
    if not thread_authorized(thread_id, issue):
        raise ApprovalError("정본 thread가 아님(issue %s): %s" % (issue, thread_id))
    body, b_issue, b_plan, b_review = parse_body(body)
    if b_issue != issue:
        raise ApprovalError("본문 issue %s ≠ %s" % (b_issue, issue))
    if b_plan != plan_commit:
        raise ApprovalError("본문 PLAN SHA가 계획 commit과 다름")
    branch = check_repo_boundary(repo, issue)
    head = _git(repo, "rev-parse", "HEAD").stdout.strip()
    if head != plan_commit:
        raise ApprovalError("HEAD(%s)가 계획 commit과 다름 — 승인은 계획 commit 직후에" % head[:10])
    dirty = _git(repo, "status", "--porcelain", "--untracked-files=all", "--", "docs", "phases")
    if dirty.returncode != 0 or dirty.stdout.strip():
        raise ApprovalError("docs/phases에 커밋되지 않은 변경이 있음")
    try:
        m = pm.build_manifest(repo, task)
    except pm.ManifestError as e:
        raise ApprovalError("계획 manifest 검증 실패: %s" % e)
    require_plan_committed(repo, plan_commit, task, m)
    index = json.loads((repo / "phases" / task / "index.json").read_text(encoding="utf-8"))
    if index.get("baseBranch") != REQUIRED_BASE_BRANCH:
        raise ApprovalError("계획 baseBranch는 %s여야 함(현재 %r)"
                            % (REQUIRED_BASE_BRANCH, index.get("baseBranch")))
    if any(s.get("status", "pending") != "pending" for s in index["steps"]):
        raise ApprovalError("이미 실행된 계획은 승인할 수 없음")
    base = _git(repo, "merge-base", BASE_REF, plan_commit).stdout.strip()
    if not _SHA40.fullmatch(base):
        raise ApprovalError("main과의 merge-base를 구할 수 없음")
    try:
        review = rp.verify_clean_review(evidence_dir, task, b_review, m.sha, repo, issue,
                                        plan_commit, review_base=base)
    except rp.PlanReviewError as e:
        raise ApprovalError("clean Astra 계획 리뷰 검증 실패: %s" % e)

    # M3: 세션 상태 판정·record 기록·세션 결속·공개를 **하나의 thread lock** 안에서 한다.
    # 공개(approval-current.json)는 마지막 — 그 전에 실패하면 실행 가능한 승인이 없다.
    with session._lock():
        st = session._load()
        if st is None:
            raise ApprovalError("planning session 상태 없음")
        agreement = st.get("agreementMessageId")
        if not agreement:
            raise ApprovalError("계획 합의(record-agreement)가 없음")
        if message_id == agreement:
            raise ApprovalError("합의 message를 구현 승인으로 재사용할 수 없음")
        if message_id in st.get("processedMessageIds", []):
            raise ApprovalError("계획 대화 message는 승인으로 쓸 수 없음")
        if st.get("status") != "idle" or st.get("inflight"):
            raise ApprovalError("planning session이 idle이 아님(status=%s)" % st.get("status"))

        used_dir = evidence_dir / "approval-messages"
        used_dir.mkdir(parents=True, exist_ok=True)
        try:
            with open(used_dir / ("%s.json" % message_id), "x", encoding="utf-8") as f:
                json.dump({"task": task, "planCommitSha": plan_commit, "reviewSha": b_review}, f)
        except FileExistsError:
            raise ApprovalError("이 승인 message는 이미 사용됨 — 재결속 불가")

        snap_rel = "%s/approved-plan/%s" % (task, m.sha)
        _require_safe_approval_dirs(evidence_dir, task, repo,
                                    _snapshot_rels(snap_rel, include_staging=True))
        (evidence_dir / task / "approved-plan").mkdir(parents=True, exist_ok=True)
        _require_safe_approval_dirs(evidence_dir, task, repo,
                                    _snapshot_rels(snap_rel, include_staging=True))
        try:
            pm.write_snapshot(m, evidence_dir / snap_rel)
        except pm.ManifestError as e:
            raise ApprovalError("snapshot 생성 실패: %s" % e)
        record = {
            "kind": "implementation-approval", "version": 2, "task": task, "issue": issue,
            "planCommitSha": plan_commit, "planContentSha": m.sha,
            "approvalMessageId": message_id, "approvalUserId": user_id,
            "discordThreadId": thread_id, "agreementMessageId": agreement,
            "sessionId": st.get("sessionId"),
            "threadStatePath": str(session.state_path.resolve()),
            "approvedAt": datetime.now(timezone.utc).isoformat(),
            "planReviewRecordSha": b_review, "reviewModel": review["reviewModel"],
            "body": body, "bodySha256": _sha(body),
            "gatewaySha256": gateway_sha(body, user_id, thread_id, message_id),
            "manifestCodeSha": pm.code_sha(), "snapshotDir": snap_rel,
            "repoRoot": str(repo.resolve()), "branch": branch,
            "baseBranch": REQUIRED_BASE_BRANCH, "reviewBaseSha": base,
        }
        data = json.dumps(record, indent=2, ensure_ascii=False, sort_keys=True).encode("utf-8")
        rec_sha = _sha(data)
        adir = evidence_dir / task / "approvals"
        adir.mkdir(parents=True, exist_ok=True)
        name = "%s.json" % message_id
        with open(adir / name, "xb") as f:
            f.write(data)
        os.chmod(adir / name, 0o444)
        st["implementationApproval"] = {
            "messageId": message_id, "recordSha": rec_sha, "planCommitSha": plan_commit,
            "planContentSha": m.sha, "userId": user_id}
        session._save(st)  # 실패하면 공개하지 않는다
        cur = evidence_dir / task / "approval-current.json"
        try:
            rp.publish_pointer(cur, cur.with_name(cur.name + ".tmp"), json.dumps(
                {"recordFile": name, "recordSha": rec_sha}).encode("utf-8"))
        except OSError as e:
            raise ApprovalError("approval-current.json 공개 실패: %s" % e)
    return {"recordSha": rec_sha, "path": str(adir / name), "planContentSha": m.sha}


def _verify_session_binding(rec, record_sha):
    """M3: thread 상태에 이 승인 record가 별도 implementation approval로 결속돼 있는가."""
    path = rec.get("threadStatePath")
    try:
        st = json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, ValueError, TypeError) as e:
        raise ApprovalError("planning session 상태를 읽을 수 없음: %s" % e)
    bound = st.get("implementationApproval") or {}
    if not (st.get("threadId") == rec["discordThreadId"]
            and st.get("agreementMessageId") == rec["agreementMessageId"]
            and bound.get("messageId") == rec["approvalMessageId"]
            and bound.get("recordSha") == record_sha
            and bound.get("planCommitSha") == rec["planCommitSha"]
            and bound.get("planContentSha") == rec["planContentSha"]):
        raise ApprovalError("planning session의 implementation approval 결속이 이 record와 다름")


def verify_approval(evidence_dir, task, repo, expected_record_sha, first_run):
    """execute preflight·매 step·리뷰·finalize 직전에 쓰는 승인 결속 검증."""
    import plan_manifest as pm
    import review_plan as rp
    evidence_dir, repo = Path(evidence_dir), Path(repo)
    _require_safe_approval_dirs(evidence_dir, task, repo)
    try:
        cur = json.loads((evidence_dir / task / "approval-current.json").read_text(
            encoding="utf-8"))
    except (OSError, ValueError) as e:
        raise ApprovalError("승인 record 없음: %s" % e)
    if cur.get("recordSha") != expected_record_sha:
        raise ApprovalError("현재 승인 record sha가 고정값(Linear)과 다름")
    name = cur.get("recordFile") or ""
    if not re.fullmatch(r"[A-Za-z0-9:_-]{1,80}\.json", name):
        raise ApprovalError("승인 record 파일명 오류")
    try:
        data = pm.read_regular(evidence_dir / task / "approvals", name)
    except pm.ManifestError as e:
        raise ApprovalError("승인 record 읽기 실패: %s" % e)
    if _sha(data) != expected_record_sha:
        raise ApprovalError("승인 record hash 불일치(변조)")
    rec = json.loads(data.decode("utf-8"))
    try:
        body, issue, plan, review = parse_body(rec.get("body", ""))
    except ApprovalError:
        raise ApprovalError("record 본문 형식 오류")
    checks = [
        (rec.get("kind") == "implementation-approval", "kind"),
        (rec.get("task") == task, "task"),
        (approver_authorized(rec.get("approvalUserId")), "approver"),
        (thread_authorized(rec.get("discordThreadId"), rec.get("issue")), "thread"),
        (bool(rec.get("approvalMessageId")) and bool(rec.get("agreementMessageId"))
         and rec["approvalMessageId"] != rec["agreementMessageId"], "agreement≠approval"),
        (issue == rec.get("issue") and plan == rec.get("planCommitSha")
         and review == rec.get("planReviewRecordSha"), "본문 결속"),
        (rec.get("bodySha256") == _sha(body), "bodySha"),
        (rec.get("gatewaySha256") == gateway_sha(body, rec.get("approvalUserId"),
                                                  rec.get("discordThreadId"),
                                                  rec.get("approvalMessageId")), "gatewaySha"),
        (rec.get("reviewModel") == _policy().review_model, "reviewModel"),
        (rec.get("manifestCodeSha") == pm.code_sha(), "manifestCodeSha(manifest 코드 변경)"),
        (rec.get("snapshotDir") == "%s/approved-plan/%s" % (task, rec.get("planContentSha")),
         "snapshotDir"),
        (rec.get("baseBranch") == REQUIRED_BASE_BRANCH, "baseBranch=main"),
        (isinstance(rec.get("reviewBaseSha"), str)
         and bool(_SHA40.fullmatch(rec["reviewBaseSha"])), "reviewBaseSha"),
        (rec.get("repoRoot") == str(repo.resolve()), "repoRoot(다른 clone)"),
    ]
    for ok, what in checks:
        if not ok:
            raise ApprovalError("승인 record 검증 실패: %s" % what)
    check_repo_boundary(repo, rec["issue"], expected_branch=rec["branch"])
    _verify_session_binding(rec, expected_record_sha)
    try:
        rp.verify_clean_review(evidence_dir, task, rec["planReviewRecordSha"],
                               rec["planContentSha"], repo, rec["issue"], rec["planCommitSha"],
                               review_base=rec["reviewBaseSha"])
    except rp.PlanReviewError as e:
        raise ApprovalError("계획 리뷰 검증 실패: %s" % e)
    _require_safe_approval_dirs(evidence_dir, task, repo, _snapshot_rels(rec["snapshotDir"]))
    try:
        snapshot = pm.load_snapshot(evidence_dir / rec["snapshotDir"], rec["planContentSha"])
        manifest = pm.verify_matches(repo, task, rec["planContentSha"])
    except pm.ManifestError as e:
        raise ApprovalError("승인 후 계획 변경 차단: %s" % e)
    plan_commit = rec["planCommitSha"]
    r = _git(repo, "merge-base", "--is-ancestor", plan_commit, "HEAD")
    if r.returncode != 0:
        raise ApprovalError("계획 commit %s가 현재 branch의 조상이 아님" % plan_commit[:10])
    for anc, desc in ((rec["reviewBaseSha"], plan_commit),
                      (rec["reviewBaseSha"], BASE_REF)):
        if _git(repo, "merge-base", "--is-ancestor", anc, desc).returncode != 0:
            raise ApprovalError("reviewBaseSha가 %s의 조상이 아님 — 리뷰 범위 변조" % desc)
    if first_run:
        head = _git(repo, "rev-parse", "HEAD").stdout.strip()
        if head != plan_commit:
            raise ApprovalError("최초 실행 HEAD(%s)가 승인된 계획 commit이 아님" % head[:10])
    return Verified(rec, expected_record_sha, snapshot, manifest)


def main(argv=None):
    runtime.require_runtime()
    p = argparse.ArgumentParser(description="구현 승인 검증")
    sub = p.add_subparsers(dest="cmd", required=True)
    v = sub.add_parser("verify")
    v.add_argument("--task", required=True)
    v.add_argument("--evidence-dir", required=True)
    v.add_argument("--record-sha", required=True)
    v.add_argument("--repo-root", default=str(ROOT))
    v.add_argument("--first-run", action="store_true")
    args = p.parse_args(argv)
    try:
        res = verify_approval(args.evidence_dir, args.task, args.repo_root, args.record_sha,
                              args.first_run)
    except ApprovalError as e:
        print("ERROR: %s" % e, file=sys.stderr)
        return 1
    print(json.dumps({"ok": True, "planContentSha": res.record["planContentSha"],
                      "planCommitSha": res.record["planCommitSha"]}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
