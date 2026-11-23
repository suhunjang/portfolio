"""D. 구현 승인 — exact 본문·user·thread·message 결속, 합의 재사용 금지, 실행 전 재검증."""
import hashlib
import json
import os
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent))
import approval as ap  # noqa: E402
import execute as ex  # noqa: E402
import plan_manifest as pm  # noqa: E402
import plan_session as ps  # noqa: E402
import review_plan as rp  # noqa: E402
from conftest import FIXTURE_APPROVER, FIXTURE_SCOPED_THREAD, FIXTURE_THREAD, git  # noqa: E402

# 실제 운영 Discord ID 대신 conftest의 가짜 fixture policy ID를 쓴다.
THREAD = FIXTURE_THREAD
USER = FIXTURE_APPROVER
SID = "11111111-2222-3333-4444-555555555555"


def clean_review(repo, evidence, task="demo", verdict="clean", findings=(), issue="DEMO-74"):
    def runner(argv, *, input, cwd, timeout, kill_grace=30):
        obj = {"task": task, "review_backend": "codex", "review_model": "gpt-6-astra",
               "reviewed_plan_sha": pm.build_manifest(repo, task).sha,
               "verdict": verdict, "findings": list(findings)}
        return ex.AgentRun(0, json.dumps(obj), "", False)
    code, path, sha = rp.run_review(repo, task, evidence, issue, runner=runner)
    return sha


class World:
    def __init__(self, repo, tmp_path):
        self.repo = repo
        self.ev = tmp_path / "evidence"
        self.ev.mkdir()
        self.rt = tmp_path / "runtime"
        self.session = self.make_session(THREAD)
        self.plan_commit = git(repo, "rev-parse", "HEAD")
        self.review_sha = clean_review(repo, self.ev)

    def make_session(self, thread, agreement="agree-1"):
        s = ps.Session(self.repo, self.rt, thread)
        st = ps._new_state(thread)
        st.update(status="idle", sessionId=SID, turns=3, grillingInvoked=True,
                  agreementMessageId=agreement, processedMessageIds=["m1", "m2", "m3"])
        s.rt.mkdir(parents=True, exist_ok=True)
        s._save(st)
        return s

    def body(self, plan=None, review=None, issue="DEMO-74"):
        return f"APPROVE {issue} PLAN {plan or self.plan_commit} REVIEW {review or self.review_sha}"

    def approve(self, message_id="appr-1", user=USER, body=None, session=None, plan_commit=None,
                issue="DEMO-74"):
        return ap.record_approval(
            session=session or self.session, repo=self.repo, task="demo", issue=issue,
            message_id=message_id, user_id=user, body=self.body() if body is None else body,
            plan_commit=plan_commit or self.plan_commit, evidence_dir=self.ev)


@pytest.fixture
def w(plan_repo, tmp_path):
    return World(plan_repo, tmp_path)


def _rej(fn, *a, **k):
    with pytest.raises(ap.ApprovalError):
        fn(*a, **k)


class TestApprovalPolicyExternalized:
    """승인자·전역/issue-scoped thread·issue key 규칙은 .harness/policy.json에서만 온다."""

    def _use(self, monkeypatch, **over):
        import runtime
        from conftest import FIXTURE_POLICY
        p = dict(FIXTURE_POLICY)
        p.update(over)
        pol = runtime.parse_policy(json.dumps(p).encode("utf-8"))
        monkeypatch.setattr(runtime, "policy", lambda: pol)
        return pol

    def test_body_issue_pattern_from_policy(self, monkeypatch):
        self._use(monkeypatch, issueKeyPattern="PROJ-[0-9]+", issueScopedThreads={})
        body = "APPROVE PROJ-12 PLAN %s REVIEW %s" % ("a" * 40, "b" * 64)
        assert ap.parse_body(body)[1:] == ("PROJ-12", "a" * 40, "b" * 64)
        with pytest.raises(ap.ApprovalError):
            ap.parse_body(body.replace("PROJ-12", "DEMO-74"))

    def test_threads_and_approvers_from_policy(self, monkeypatch):
        self._use(monkeypatch, approvalThreadIds=["777"], approverUserIds=["888"],
                  issueScopedThreads={"779": "DEMO-9"})
        assert ap.thread_authorized("777", "DEMO-1")
        assert ap.thread_authorized("779", "DEMO-9")
        assert not ap.thread_authorized("779", "DEMO-1")
        assert not ap.thread_authorized("10002", "DEMO-1")
        assert ap.approver_authorized("888")
        assert not ap.approver_authorized("20001")

    def test_record_approval_rejects_user_not_in_policy(self, w, monkeypatch):
        self._use(monkeypatch, approverUserIds=["888"])
        _rej(w.approve)

    def test_missing_policy_fails_closed(self, w, monkeypatch, tmp_path):
        import runtime
        monkeypatch.setattr(runtime, "policy",
                            lambda: runtime.load_repo_policy(tmp_path / "no-policy-root"))
        with pytest.raises(ap.ApprovalError, match="policy"):
            w.approve()


class TestRecordApproval:
    def test_success_record_fields(self, w):
        out = w.approve()
        rec = json.loads(Path(out["path"]).read_text(encoding="utf-8"))
        assert hashlib.sha256(Path(out["path"]).read_bytes()).hexdigest() == out["recordSha"]
        assert rec["task"] == "demo"
        assert rec["planCommitSha"] == w.plan_commit
        assert rec["planContentSha"] == pm.build_manifest(w.repo, "demo").sha
        assert rec["approvalMessageId"] == "appr-1"
        assert rec["approvalUserId"] == USER
        assert rec["discordThreadId"] == THREAD
        assert rec["planReviewRecordSha"] == w.review_sha
        assert rec["reviewModel"] == "gpt-6-astra"
        assert rec["agreementMessageId"] == "agree-1"
        assert rec["approvedAt"]
        assert rec["body"] == w.body()
        assert rec["bodySha256"] == hashlib.sha256(w.body().encode()).hexdigest()
        assert rec["gatewaySha256"]
        assert rec["manifestCodeSha"] == pm.code_sha()
        assert not (Path(out["path"]).stat().st_mode & 0o222)
        st = w.session.status()
        assert st["implementationApproval"]["messageId"] == "appr-1"
        assert st["agreementMessageId"] == "agree-1"

    def test_snapshot_created_read_only(self, w):
        out = w.approve()
        rec = json.loads(Path(out["path"]).read_text())
        snap = pm.load_snapshot(w.ev / rec["snapshotDir"], rec["planContentSha"])
        assert snap.read("phases/demo/step0.md")

    def test_wrong_user(self, w):
        _rej(w.approve, user="99999")

    def test_wrong_thread(self, w):
        other = w.make_session("10099")
        _rej(w.approve, session=other)

    @pytest.mark.parametrize("mut", [
        lambda b: b.lower(),
        lambda b: b + " ",
        lambda b: " " + b,
        lambda b: b + " thanks",
        lambda b: b.replace("APPROVE", "APPROVED"),
        lambda b: b.replace("DEMO-74", "DEMO-75"),
        lambda b: "LGTM",
        lambda b: b.replace("PLAN ", "PLAN  "),
    ])
    def test_body_must_be_exact(self, w, mut):
        _rej(w.approve, body=mut(w.body()))

    def test_trailing_newline_from_file_ok(self, w):
        w.approve(body=w.body() + "\n")

    def test_body_plan_sha_must_match(self, w):
        _rej(w.approve, body=w.body(plan="a" * 40))

    def test_body_review_sha_must_match(self, w):
        _rej(w.approve, body=w.body(review="b" * 64))

    def test_agreement_message_cannot_be_approval(self, w):
        _rej(w.approve, message_id="agree-1")

    def test_conversation_message_cannot_be_approval(self, w):
        _rej(w.approve, message_id="m2")

    def test_no_agreement_rejected(self, w):
        s = w.make_session(THREAD, agreement=None)
        _rej(w.approve, session=s)

    def test_same_message_cannot_rebind(self, w):
        w.approve()
        _rej(w.approve)  # 같은 계획이라도 재결속 불가

    def test_findings_review_rejected(self, w):
        sha = clean_review(w.repo, w.ev, verdict="has_findings", findings=[{
            "severity": "major", "step_file": "step0.md", "principle": "p",
            "summary": "s", "fix": "f"}])
        _rej(w.approve, body=w.body(review=sha))

    def test_old_clean_review_superseded_by_findings(self, w):
        clean_review(w.repo, w.ev, verdict="has_findings", findings=[{
            "severity": "major", "step_file": "step0.md", "principle": "p",
            "summary": "s", "fix": "f"}])
        _rej(w.approve)  # w.review_sha는 더 이상 최신이 아님

    def test_review_of_previous_plan_rejected(self, w):
        (w.repo / "phases/demo/step0.md").write_text("v2\n", encoding="utf-8")
        git(w.repo, "commit", "-qam", "docs: plan v2")
        new_commit = git(w.repo, "rev-parse", "HEAD")
        _rej(w.approve, body=w.body(plan=new_commit), plan_commit=new_commit)

    def test_head_must_equal_plan_commit(self, w):
        (w.repo / "README.md").write_text("later\n", encoding="utf-8")
        git(w.repo, "commit", "-qam", "chore: later")
        _rej(w.approve)

    def test_dirty_plan_rejected(self, w):
        (w.repo / "phases/demo/step1.md").write_text("dirty", encoding="utf-8")
        _rej(w.approve)

    def test_evidence_inside_repo_rejected(self, w):
        with pytest.raises(ap.ApprovalError):
            ap.record_approval(session=w.session, repo=w.repo, task="demo", issue="DEMO-74",
                               message_id="appr-1", user_id=USER, body=w.body(),
                               plan_commit=w.plan_commit, evidence_dir=w.repo / ".harness/ev")

    def test_rereview_and_new_approval_after_scope_change(self, w):
        w.approve()
        (w.repo / "phases/demo/step0.md").write_text("scope change\n", encoding="utf-8")
        git(w.repo, "commit", "-qam", "docs: plan v2")
        w.plan_commit = git(w.repo, "rev-parse", "HEAD")
        w.review_sha = clean_review(w.repo, w.ev)
        _rej(w.approve)  # 같은 승인 message 재사용 금지
        out = w.approve(message_id="appr-2")
        assert json.loads(Path(out["path"]).read_text())["planCommitSha"] == w.plan_commit


class TestVerifyApproval:
    def _ok(self, w):
        out = w.approve()
        return out["recordSha"]

    def test_verify_first_run(self, w):
        sha = self._ok(w)
        v = ap.verify_approval(w.ev, "demo", w.repo, sha, first_run=True)
        assert v.record["approvalMessageId"] == "appr-1"
        assert v.snapshot.sha == v.record["planContentSha"]

    def test_first_run_requires_head_equal_plan_commit(self, w):
        sha = self._ok(w)
        (w.repo / "README.md").write_text("impl\n", encoding="utf-8")
        git(w.repo, "commit", "-qam", "feat: impl")
        _rej(ap.verify_approval, w.ev, "demo", w.repo, sha, first_run=True)
        ap.verify_approval(w.ev, "demo", w.repo, sha, first_run=False)  # resume는 허용

    def test_plan_commit_must_be_ancestor(self, w):
        sha = self._ok(w)
        git(w.repo, "checkout", "-q", "main")
        _rej(ap.verify_approval, w.ev, "demo", w.repo, sha, first_run=False)

    def test_plan_change_after_approval_blocked(self, w):
        sha = self._ok(w)
        p = w.repo / "phases/demo/step1.md"
        p.write_bytes(p.read_bytes() + b"x")
        _rej(ap.verify_approval, w.ev, "demo", w.repo, sha, first_run=True)

    def test_plan_change_committed_after_approval_blocked(self, w):
        sha = self._ok(w)
        p = w.repo / "phases/demo/step1.md"
        p.write_bytes(p.read_bytes() + b"x")
        git(w.repo, "commit", "-qam", "sneak")
        _rej(ap.verify_approval, w.ev, "demo", w.repo, sha, first_run=False)

    def test_immutable_index_change_blocked(self, w):
        sha = self._ok(w)
        p = w.repo / "phases/demo/index.json"
        d = json.loads(p.read_text())
        d["allowedPaths"] = ["src/", "tests/", "lib/"]
        p.write_text(json.dumps(d))
        _rej(ap.verify_approval, w.ev, "demo", w.repo, sha, first_run=True)

    def test_mutable_index_change_allowed(self, w):
        sha = self._ok(w)
        p = w.repo / "phases/demo/index.json"
        d = json.loads(p.read_text())
        d["steps"][0].update(status="completed", summary="done")
        d["reviewBaseSha"] = "a" * 40
        p.write_text(json.dumps(d))
        ap.verify_approval(w.ev, "demo", w.repo, sha, first_run=False)

    def test_step_symlink_swap_blocked(self, w, tmp_path):
        sha = self._ok(w)
        p = w.repo / "phases/demo/step0.md"
        target = tmp_path / "same.md"
        target.write_bytes(p.read_bytes())
        p.unlink()
        p.symlink_to(target)
        _rej(ap.verify_approval, w.ev, "demo", w.repo, sha, first_run=True)

    def test_extra_step_added_blocked(self, w):
        sha = self._ok(w)
        (w.repo / "phases/demo/step2.md").write_text("new", encoding="utf-8")
        _rej(ap.verify_approval, w.ev, "demo", w.repo, sha, first_run=True)

    def test_change_then_restore_uses_snapshot(self, w):
        """계획을 바꿨다 되돌려도 실행 입력은 snapshot이다(같은 bytes)."""
        sha = self._ok(w)
        p = w.repo / "phases/demo/step0.md"
        orig = p.read_bytes()
        p.write_text("evil", encoding="utf-8")
        p.write_bytes(orig)
        v = ap.verify_approval(w.ev, "demo", w.repo, sha, first_run=True)
        assert v.snapshot.read("phases/demo/step0.md") == orig

    def test_pinned_record_sha_mismatch(self, w):
        self._ok(w)
        _rej(ap.verify_approval, w.ev, "demo", w.repo, "0" * 64, first_run=True)

    def test_tampered_approval_record(self, w):
        sha = self._ok(w)
        cur = json.loads((w.ev / "demo/approval-current.json").read_text())
        p = w.ev / "demo/approvals" / cur["recordFile"]
        p.chmod(0o644)
        d = json.loads(p.read_text())
        d["approvalUserId"] = "1"
        p.write_text(json.dumps(d))
        _rej(ap.verify_approval, w.ev, "demo", w.repo, sha, first_run=True)

    def test_consistent_approval_and_review_tamper_rejected(self, w):
        """review·approval을 함께 위조해 서로 맞춰도 고정된 approval sha로 거부."""
        sha = self._ok(w)
        cur = json.loads((w.ev / "demo/approval-current.json").read_text())
        p = w.ev / "demo/approvals" / cur["recordFile"]
        p.chmod(0o644)
        d = json.loads(p.read_text())
        d["planReviewRecordSha"] = "c" * 64
        d["body"] = w.body(review="c" * 64)
        d["bodySha256"] = hashlib.sha256(d["body"].encode()).hexdigest()
        p.write_text(json.dumps(d))
        new_sha = hashlib.sha256(p.read_bytes()).hexdigest()
        (w.ev / "demo/approval-current.json").write_text(
            json.dumps({"recordFile": cur["recordFile"], "recordSha": new_sha}))
        _rej(ap.verify_approval, w.ev, "demo", w.repo, sha, first_run=True)
        # 위조 sha로 고정해도 review record가 없으므로 거부
        _rej(ap.verify_approval, w.ev, "demo", w.repo, new_sha, first_run=True)

    def test_snapshot_tamper_rejected(self, w):
        sha = self._ok(w)
        rec = json.loads(next((w.ev / "demo/approvals").glob("*.json")).read_text())
        f = w.ev / rec["snapshotDir"] / "files/phases/demo/step0.md"
        f.chmod(0o644)
        f.write_text("evil", encoding="utf-8")
        _rej(ap.verify_approval, w.ev, "demo", w.repo, sha, first_run=True)

    def test_manifest_code_change_rejected(self, w, monkeypatch):
        sha = self._ok(w)
        monkeypatch.setattr(pm, "code_sha", lambda: "d" * 64)
        _rej(ap.verify_approval, w.ev, "demo", w.repo, sha, first_run=True)

    def test_new_findings_review_after_approval_blocks(self, w):
        sha = self._ok(w)
        clean_review(w.repo, w.ev, verdict="has_findings", findings=[{
            "severity": "critical", "step_file": "step1.md", "principle": "p",
            "summary": "s", "fix": "f"}])
        _rej(ap.verify_approval, w.ev, "demo", w.repo, sha, first_run=True)


class TestPlanSessionCli:
    def test_record_approval_via_plan_session(self, w, tmp_path, monkeypatch):
        body = tmp_path / "body.txt"
        body.write_text(w.body(), encoding="utf-8")
        monkeypatch.setenv("HARNESS_RUNTIME_DIR", str(w.rt))
        code = ps.main(["record-approval", "--repo-root", str(w.repo), "--thread-id", THREAD,
                        "--message-id", "appr-9", "--approver-user-id", USER,
                        "--plan-commit", w.plan_commit, "--body-file", str(body),
                        "--task", "demo", "--issue", "DEMO-74", "--evidence-dir", str(w.ev)])
        assert code == 0
        code = ps.main(["record-approval", "--repo-root", str(w.repo), "--thread-id", THREAD,
                        "--message-id", "agree-1", "--approver-user-id", USER,
                        "--plan-commit", w.plan_commit, "--body-file", str(body),
                        "--task", "demo", "--issue", "DEMO-74", "--evidence-dir", str(w.ev)])
        assert code == 1


# ---------------------------------------------------------------------------
# Astra 리뷰 지적 회귀 시험 (B1·M1·M3·M4)
# ---------------------------------------------------------------------------

class TestB1BranchBaseRepoClone:
    """B1 — main·잘못된 branch/base/repo/clone에서 승인·실행이 열리면 안 된다."""

    def test_main_branch_rejected(self, w):
        git(w.repo, "branch", "-f", "main", "HEAD")
        git(w.repo, "checkout", "-q", "main")
        _rej(w.approve)

    @pytest.mark.parametrize("branch", ["feat-demo", "feat/DEMO-75/demo", "feat/DEMO-74/Demo_X",
                                        "fix/DEMO-74/demo", "feat/DEMO-74/a/b"])
    def test_branch_pattern_enforced(self, w, branch):
        git(w.repo, "checkout", "-q", "-b", branch)
        _rej(w.approve)

    def test_detached_head_rejected(self, w):
        git(w.repo, "checkout", "-q", "--detach")
        _rej(w.approve)

    def test_base_branch_must_be_main(self, plan_repo, tmp_path):
        p = plan_repo / "phases/demo/index.json"
        d = json.loads(p.read_text())
        d["baseBranch"] = "develop"
        p.write_text(json.dumps(d))
        git(plan_repo, "branch", "develop", "main")
        git(plan_repo, "commit", "-qam", "docs: plan on develop base")
        w = World(plan_repo, tmp_path)
        _rej(w.approve)

    def test_repo_subdirectory_rejected(self, w):
        with pytest.raises(ap.ApprovalError):
            ap.record_approval(session=w.session, repo=w.repo / "phases", task="demo",
                               issue="DEMO-74", message_id="appr-1", user_id=USER,
                               body=w.body(), plan_commit=w.plan_commit, evidence_dir=w.ev)

    def test_linked_worktree_rejected(self, w, tmp_path):
        wt = tmp_path / "wt"
        git(w.repo, "worktree", "add", "-q", "-b", "feat/DEMO-74/wt", str(wt), "HEAD")
        s = ps.Session(wt, w.rt / "wt", THREAD)
        st = ps._new_state(THREAD)
        st.update(status="idle", sessionId=SID, turns=3, grillingInvoked=True,
                  agreementMessageId="agree-1", processedMessageIds=["m1"])
        s.rt.mkdir(parents=True)
        s._save(st)
        with pytest.raises(ap.ApprovalError):
            ap.record_approval(session=s, repo=wt, task="demo", issue="DEMO-74",
                               message_id="appr-1", user_id=USER, body=w.body(),
                               plan_commit=w.plan_commit, evidence_dir=w.ev)

    def test_verify_rejects_switch_to_main_after_approval(self, w):
        sha = w.approve()["recordSha"]
        git(w.repo, "branch", "-f", "main", "HEAD")
        git(w.repo, "checkout", "-q", "main")
        _rej(ap.verify_approval, w.ev, "demo", w.repo, sha, first_run=False)

    def test_verify_rejects_other_feature_branch(self, w):
        sha = w.approve()["recordSha"]
        git(w.repo, "checkout", "-q", "-b", "feat/DEMO-74/other")
        _rej(ap.verify_approval, w.ev, "demo", w.repo, sha, first_run=False)


class TestM1ReviewBaseBound:
    def test_record_pins_merge_base_with_main(self, w):
        rec = json.loads(Path(w.approve()["path"]).read_text())
        assert rec["reviewBaseSha"] == git(w.repo, "merge-base", "main", w.plan_commit)
        assert rec["baseBranch"] == "main"

    def test_tampered_record_base_rejected(self, w):
        out = w.approve()
        p = Path(out["path"])
        p.chmod(0o644)
        d = json.loads(p.read_text())
        d["reviewBaseSha"] = w.plan_commit  # 범위를 좁히려는 변조
        p.write_text(json.dumps(d))
        _rej(ap.verify_approval, w.ev, "demo", w.repo, out["recordSha"], first_run=False)


class TestM3TransactionalBinding:
    def test_lock_held_publishes_nothing(self, w):
        import fcntl
        lock = w.rt / f"{THREAD}.lock"
        fd = os.open(lock, os.O_RDWR | os.O_CREAT)
        fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        try:
            with pytest.raises((ap.ApprovalError, ps.SessionError)):
                w.approve()
        finally:
            os.close(fd)
        assert not (w.ev / "demo/approval-current.json").exists()
        assert w.session.status()["implementationApproval"] is None

    def test_session_bind_failure_publishes_nothing(self, w, monkeypatch):
        real = ps.Session._save

        def boom(self, st):
            if st.get("implementationApproval"):
                raise OSError("disk full")
            return real(self, st)
        monkeypatch.setattr(ps.Session, "_save", boom)
        with pytest.raises((ap.ApprovalError, OSError)):
            w.approve()
        assert not (w.ev / "demo/approval-current.json").exists()

    def test_session_changed_concurrently_is_reread_under_lock(self, w, monkeypatch):
        """잠금 밖에서 읽은 상태로 결정하지 않는다 — 잠금 안에서 recovery 상태를 본다."""
        st = w.session.status()
        st["status"] = "recovery-required"
        w.session._save(st)
        _rej(w.approve)
        assert not (w.ev / "demo/approval-current.json").exists()

    def test_record_names_thread_state(self, w):
        rec = json.loads(Path(w.approve()["path"]).read_text())
        assert Path(rec["threadStatePath"]) == w.session.state_path.resolve()

    def test_verify_requires_session_binding(self, w):
        sha = w.approve()["recordSha"]
        st = w.session.status()
        st["implementationApproval"] = None
        w.session._save(st)
        _rej(ap.verify_approval, w.ev, "demo", w.repo, sha, first_run=True)

    def test_verify_rejects_binding_to_other_record(self, w):
        sha = w.approve()["recordSha"]
        st = w.session.status()
        st["implementationApproval"]["recordSha"] = "e" * 64
        w.session._save(st)
        _rej(ap.verify_approval, w.ev, "demo", w.repo, sha, first_run=True)

    def test_verify_rejects_missing_state(self, w):
        sha = w.approve()["recordSha"]
        w.session.state_path.unlink()
        _rej(ap.verify_approval, w.ev, "demo", w.repo, sha, first_run=True)


class TestM4StartMarkerBoundToApproval:
    def test_marker_is_per_approval(self, w):
        sha = w.approve()["recordSha"]
        assert ap.is_first_run(w.ev, "demo", sha) is True
        ap.write_start_marker(w.ev, "demo", sha, w.plan_commit)
        assert ap.is_first_run(w.ev, "demo", sha) is False
        assert ap.is_first_run(w.ev, "demo", "f" * 64) is True  # 다른 승인은 여전히 최초

    def test_legacy_task_marker_ignored(self, w):
        sha = w.approve()["recordSha"]
        legacy = w.ev / "demo/runs/started.json"
        legacy.parent.mkdir(parents=True)
        legacy.write_text("{}")
        assert ap.is_first_run(w.ev, "demo", sha) is True

    def test_marker_content_must_match(self, w):
        sha = w.approve()["recordSha"]
        p = ap.write_start_marker(w.ev, "demo", sha, w.plan_commit)
        p.chmod(0o644)
        p.write_text(json.dumps({"approvalRecordSha": sha, "planCommitSha": "0" * 40}))
        with pytest.raises(ap.ApprovalError):
            ap.is_first_run(w.ev, "demo", sha, plan_commit=w.plan_commit)

    def test_new_approval_first_run_requires_plan_commit(self, w):
        """승인 A로 실행을 시작한 뒤 계획을 바꿔 승인 B를 받으면, B의 최초 실행은
        B의 계획 commit에서만 시작할 수 있다(A의 marker로 우회 불가)."""
        a = w.approve()["recordSha"]
        ap.write_start_marker(w.ev, "demo", a, w.plan_commit)
        (w.repo / "phases/demo/step0.md").write_text("v2\n", encoding="utf-8")
        git(w.repo, "commit", "-qam", "docs: plan v2")
        w.plan_commit = git(w.repo, "rev-parse", "HEAD")
        w.review_sha = clean_review(w.repo, w.ev)
        b = w.approve(message_id="appr-2")["recordSha"]
        (w.repo / "README.md").write_text("later\n")
        git(w.repo, "commit", "-qam", "chore: later")
        assert ap.is_first_run(w.ev, "demo", b) is True
        _rej(ap.verify_approval, w.ev, "demo", w.repo, b,
             first_run=ap.is_first_run(w.ev, "demo", b))


# ---------------------------------------------------------------------------
# approval은 현재 target에 결속된 review만 수락 / issue-scoped thread
# ---------------------------------------------------------------------------

import subprocess  # noqa: E402
import textwrap  # noqa: E402

from conftest import make_harness_root, make_plan  # noqa: E402

SCOPED_THREAD = FIXTURE_SCOPED_THREAD   # policy: DEMO-81 issue 전용 thread
FIX_THREAD = "10003"     # policy에 없는 thread(원 지적 스레드 역할)
HARNESS_PY = Path(__file__).resolve().parent / "harness.py"
VENV_PY = Path(__file__).resolve().parent.parent / ".venv" / "bin" / "python"


class TestApprovalUsesBoundReview:
    def test_review_from_other_clone_rejected(self, w, tmp_path):
        """같은 commit·같은 plan bytes라도 다른 clone에서 만든 review로는 승인 불가."""
        other = tmp_path / "other-clone"
        git(tmp_path, "clone", "-q", str(w.repo), str(other))
        git(other, "branch", "main", "origin/main")
        assert git(other, "rev-parse", "HEAD") == w.plan_commit
        s = ps.Session(other, tmp_path / "rt-other", THREAD)
        st = ps._new_state(THREAD)
        st.update(status="idle", sessionId=SID, turns=3, grillingInvoked=True,
                  agreementMessageId="agree-1", processedMessageIds=["m1"])
        s.rt.mkdir(parents=True)
        s._save(st)
        with pytest.raises(ap.ApprovalError, match="repoRoot"):
            ap.record_approval(session=s, repo=other, task="demo", issue="DEMO-74",
                               message_id="appr-1", user_id=USER, body=w.body(),
                               plan_commit=w.plan_commit, evidence_dir=w.ev)

    def test_review_commit_must_equal_approved_commit(self, w):
        """review 뒤 plan bytes를 바꾸지 않은 새 commit을 승인하려 하면 거부(exact equality)."""
        (w.repo / "README.md").write_text("same plan bytes\n", encoding="utf-8")
        git(w.repo, "commit", "-qam", "chore: other commit")
        new_commit = git(w.repo, "rev-parse", "HEAD")
        with pytest.raises(ap.ApprovalError, match="planCommitSha"):
            w.approve(body=w.body(plan=new_commit), plan_commit=new_commit)

    def test_verify_rechecks_review_binding(self, w):
        sha = w.approve()["recordSha"]
        v = ap.verify_approval(w.ev, "demo", w.repo, sha, first_run=True)
        assert v.record["planCommitSha"] == w.plan_commit


def _scoped_repo(tmp_path, issue="DEMO-81", slug="portfolio-redesign"):
    repo = tmp_path / ("target-%s" % issue)
    repo.mkdir()
    git(repo, "init", "-q", "-b", "main")
    git(repo, "config", "user.email", "t@example.com")
    git(repo, "config", "user.name", "T")
    git(repo, "config", "commit.gpgsign", "false")
    (repo / "README.md").write_text("x\n", encoding="utf-8")
    git(repo, "add", "-A")
    git(repo, "commit", "-q", "-m", "init")
    git(repo, "checkout", "-q", "-b", "feat/%s/%s" % (issue, slug))
    make_plan(repo)
    git(repo, "add", "-A")
    git(repo, "commit", "-q", "-m", "docs: plan")
    return repo


FAKE_CODEX = textwrap.dedent("""\
    #!/bin/sh
    cat > /dev/null
    cat "$RESULT_FILE"
""")


class CliWorld:
    """public CLI만 쓰는 임시 외부 target: review-plan → plan-session record-approval →
    approval verify. 가짜 codex(실제 spawn)와 가짜 승인 fixture만 쓴다.
    CLI는 fixture policy가 든 임시 하네스 root에서 띄운다(운영 policy 비의존)."""

    def __init__(self, tmp_path, issue="DEMO-81", thread=SCOPED_THREAD):
        self.tmp = tmp_path
        existing = tmp_path / "harness-root"
        self.harness = existing if existing.is_dir() else make_harness_root(tmp_path)
        self.issue = issue
        self.repo = _scoped_repo(tmp_path, issue=issue)
        self.ev = tmp_path / "evidence"
        self.ev.mkdir()
        self.rt = tmp_path / "runtime"
        self.plan_commit = git(self.repo, "rev-parse", "HEAD")
        self.make_session(thread)
        self.review_sha = self.review()

    def env(self):
        env = {k: v for k, v in os.environ.items() if not k.startswith("HARNESS_")}
        env.update(HARNESS_REVIEW_BACKEND="codex", HARNESS_REVIEW_MODEL="gpt-6-astra",
                   HARNESS_RUNTIME_DIR=str(self.rt))
        return env

    def run(self, *args, extra_env=None):
        env = self.env()
        env.update(extra_env or {})
        return subprocess.run([str(VENV_PY), str(self.harness / "scripts" / HARNESS_PY.name)]
                              + list(args), env=env,
                              capture_output=True, text=True, encoding="utf-8")

    def make_session(self, thread):
        s = ps.Session(self.repo, self.rt, thread)
        st = ps._new_state(thread)
        st.update(status="idle", sessionId=SID, turns=3, grillingInvoked=True,
                  agreementMessageId="agree-81", processedMessageIds=["m1", "m2"])
        s.rt.mkdir(parents=True, exist_ok=True)
        s._save(st)
        return s

    def review(self):
        bindir = self.tmp / "bin"
        bindir.mkdir(exist_ok=True)
        (bindir / "codex").write_text(FAKE_CODEX, encoding="utf-8")
        (bindir / "codex").chmod(0o755)
        res = self.tmp / "result.json"
        res.write_text(json.dumps({
            "task": "demo", "review_backend": "codex", "review_model": "gpt-6-astra",
            "reviewed_plan_sha": pm.build_manifest(self.repo, "demo").sha,
            "verdict": "clean", "findings": []}), encoding="utf-8")
        r = self.run("review-plan", "demo", "--issue", self.issue, "--repo-root", str(self.repo),
                     "--evidence-dir", str(self.ev),
                     extra_env={"RESULT_FILE": str(res),
                                "PATH": "%s:%s" % (bindir, os.environ["PATH"])})
        assert r.returncode == 0, r.stdout + r.stderr
        return json.loads((self.ev / "demo/plan-reviews/latest.json").read_text())["recordSha"]

    def record_approval(self, thread, body_issue=None, message_id="appr-81"):
        body = self.tmp / ("body-%s.txt" % message_id)
        body.write_text("APPROVE %s PLAN %s REVIEW %s" % (
            body_issue or self.issue, self.plan_commit, self.review_sha), encoding="utf-8")
        return self.run("plan-session", "record-approval", "--repo-root", str(self.repo),
                        "--thread-id", thread, "--message-id", message_id,
                        "--approver-user-id", USER, "--plan-commit", self.plan_commit,
                        "--body-file", str(body), "--task", "demo", "--issue", self.issue,
                        "--evidence-dir", str(self.ev))

    def verify(self, record_sha):
        return self.run("approval", "verify", "--task", "demo", "--evidence-dir", str(self.ev),
                        "--record-sha", record_sha, "--repo-root", str(self.repo), "--first-run")


class TestIssueScopedThread:
    def test_scoped_thread_own_issue_passes_public_path(self, tmp_path):
        cw = CliWorld(tmp_path)
        r = cw.record_approval(SCOPED_THREAD)
        assert r.returncode == 0, r.stdout + r.stderr
        sha = json.loads(r.stdout)["recordSha"]
        v = cw.verify(sha)
        assert v.returncode == 0, v.stdout + v.stderr
        assert json.loads(v.stdout)["planCommitSha"] == cw.plan_commit

    @pytest.mark.parametrize("thread", [FIX_THREAD, "10099"])
    def test_fix_or_arbitrary_thread_rejected_for_scoped_issue(self, tmp_path, thread):
        cw = CliWorld(tmp_path, thread=thread)
        r = cw.record_approval(thread)
        assert r.returncode == 1
        assert "thread" in r.stderr
        assert not (cw.ev / "demo/approval-current.json").exists()

    def test_scoped_thread_other_issue_rejected_on_create(self, tmp_path):
        cw = CliWorld(tmp_path, issue="DEMO-82", thread=SCOPED_THREAD)
        r = cw.record_approval(SCOPED_THREAD)
        assert r.returncode == 1
        assert "thread" in r.stderr
        assert not (cw.ev / "demo/approval-current.json").exists()

    def test_scoped_thread_other_issue_rejected_on_verify(self, w):
        """scoped thread로 다른 issue를 승인한 record는 다른 필드가 전부 일관돼도 검증에서 거부."""
        out = w.approve()
        p = Path(out["path"])
        p.chmod(0o644)
        rec = json.loads(p.read_text())
        rec["discordThreadId"] = SCOPED_THREAD
        rec["gatewaySha256"] = ap.gateway_sha(rec["body"], rec["approvalUserId"], SCOPED_THREAD,
                                              rec["approvalMessageId"])
        data = json.dumps(rec, indent=2, ensure_ascii=False, sort_keys=True).encode("utf-8")
        p.write_bytes(data)
        new_sha = hashlib.sha256(data).hexdigest()
        (w.ev / "demo/approval-current.json").write_text(
            json.dumps({"recordFile": p.name, "recordSha": new_sha}))
        st = w.session.status()
        st["threadId"] = SCOPED_THREAD
        st["implementationApproval"]["recordSha"] = new_sha
        w.session._save(st)
        with pytest.raises(ap.ApprovalError, match="thread"):
            ap.verify_approval(w.ev, "demo", w.repo, new_sha, first_run=True)

    def test_canonical_thread_policy_unchanged(self):
        """전역 thread는 모든 issue, scoped thread는 지정 issue(DEMO-81)만.
        값은 policy에서 온다 — 운영자 실제 값 고정은 source-only
        test_docs_contract의 예시 policy 테스트가 맡는다."""
        import runtime
        pol = runtime.policy()
        assert pol.approval_thread_ids == (THREAD,)
        assert SCOPED_THREAD not in pol.approval_thread_ids
        assert ap.thread_authorized(THREAD, "DEMO-74")
        assert ap.thread_authorized(SCOPED_THREAD, "DEMO-81")
        assert not ap.thread_authorized(SCOPED_THREAD, "DEMO-74")
        assert not ap.thread_authorized(FIX_THREAD, "DEMO-81")


# ---------------------------------------------------------------------------
# exact-commit review fixes (public CLI regressions)
# ---------------------------------------------------------------------------

def _rewrite_main_unrelated_with_tag(repo):
    old_main = git(repo, "rev-parse", "refs/heads/main")
    git(repo, "tag", "main", old_main)
    tree = git(repo, "rev-parse", old_main + "^{tree}")
    orphan = git(repo, "commit-tree", tree, "-m", "unrelated rewrite")
    git(repo, "update-ref", "refs/heads/main", orphan)


class TestBaseRefIsLocalBranchApproval:
    def test_record_approval_rejects_tag_main_with_rewritten_branch(self, tmp_path):
        cw = CliWorld(tmp_path)
        _rewrite_main_unrelated_with_tag(cw.repo)
        r = cw.record_approval(SCOPED_THREAD)
        assert r.returncode == 1, r.stdout + r.stderr
        assert not (cw.ev / "demo/approval-current.json").exists()

    def test_verify_rejects_tag_main_with_rewritten_branch(self, tmp_path):
        cw = CliWorld(tmp_path)
        r = cw.record_approval(SCOPED_THREAD)
        assert r.returncode == 0, r.stdout + r.stderr
        sha = json.loads(r.stdout)["recordSha"]
        _rewrite_main_unrelated_with_tag(cw.repo)
        v = cw.verify(sha)
        assert v.returncode != 0, v.stdout + v.stderr


class TestPlanInputsCommittedApproval:
    def test_record_approval_rejects_hidden_index_change(self, tmp_path):
        cw = CliWorld(tmp_path)
        git(cw.repo, "update-index", "--skip-worktree", "phases/demo/index.json")
        p = cw.repo / "phases/demo/index.json"
        d = json.loads(p.read_text(encoding="utf-8"))
        d["created_at"] = "uncommitted"
        p.write_text(json.dumps(d), encoding="utf-8")
        assert git(cw.repo, "status", "--porcelain", "--untracked-files=all") == ""
        r = cw.record_approval(SCOPED_THREAD)
        assert r.returncode == 1, r.stdout + r.stderr
        assert not (cw.ev / "demo/approval-current.json").exists()


@pytest.fixture
def harness_dest(tmp_path):
    """spawn된 CLI의 하네스 root(CliWorld와 같은 fixture root) 안의 보호 디렉터리."""
    root = make_harness_root(tmp_path)
    d = root / ".harness" / ("nested-ap-%d" % os.getpid())
    d.mkdir(parents=True)
    yield d
    subprocess.run(["chmod", "-R", "u+w", str(d)], capture_output=True)


def _redirect(cw, component, dest):
    """evidence/<component>를 dest로 옮기고 그 자리에 symlink를 둔다(내용은 유지)."""
    import shutil
    src = cw.ev / component
    target = dest / "moved"
    if src.exists():
        subprocess.run(["chmod", "-R", "u+w", str(src)], check=True)
        shutil.move(str(src), str(target))
    else:
        target.mkdir()
    src.parent.mkdir(parents=True, exist_ok=True)
    src.symlink_to(target, target_is_directory=True)
    return target


def _dest(cw, into, harness_dest):
    if into == "target":
        d = cw.repo / ".harness" / "redirect"
        d.mkdir(parents=True)
        return d
    return harness_dest


class TestNestedEvidenceSymlinksApproval:
    @pytest.mark.parametrize("component", ["demo", "demo/approvals", "demo/plan-reviews"])
    @pytest.mark.parametrize("into", ["target", "harness"])
    def test_record_approval_rejects_nested_symlink(self, tmp_path, harness_dest, component,
                                                    into):
        cw = CliWorld(tmp_path)
        moved = _redirect(cw, component, _dest(cw, into, harness_dest))
        before = sorted(str(p) for p in moved.rglob("*"))
        r = cw.record_approval(SCOPED_THREAD)
        assert r.returncode == 1, r.stdout + r.stderr
        assert sorted(str(p) for p in moved.rglob("*")) == before

    @pytest.mark.parametrize("component", ["demo", "demo/approvals", "demo/plan-reviews"])
    @pytest.mark.parametrize("into", ["target", "harness"])
    def test_verify_rejects_nested_symlink(self, tmp_path, harness_dest, component, into):
        cw = CliWorld(tmp_path)
        r = cw.record_approval(SCOPED_THREAD)
        assert r.returncode == 0, r.stdout + r.stderr
        sha = json.loads(r.stdout)["recordSha"]
        _redirect(cw, component, _dest(cw, into, harness_dest))
        v = cw.verify(sha)
        assert v.returncode != 0, v.stdout + v.stderr


def _listing(d):
    """경로·mode·파일 bytes·symlink target까지 비교하는 상태 스냅샷."""
    out = []
    for p in sorted(d.rglob("*")):
        st = os.lstat(str(p))
        if p.is_symlink():
            body = ("link", os.readlink(str(p)))
        elif p.is_file():
            body = ("file", p.read_bytes())
        else:
            body = ("dir", None)
        out.append((str(p), st.st_mode, body))
    return out


class TestApprovedPlanSnapshotRedirects:
    """approved-plan/<sha>·files·staging 경계(2차): 어떤 redirect도 따라가지 않는다."""

    @pytest.mark.parametrize("component", ["snapshot", "files", "staging"])
    @pytest.mark.parametrize("into", ["target", "harness"])
    def test_record_approval_rejects_snapshot_redirect(self, tmp_path, harness_dest, component,
                                                       into):
        cw = CliWorld(tmp_path)
        m = pm.build_manifest(cw.repo, "demo")
        ap_dir = cw.ev / "demo" / "approved-plan"
        ap_dir.mkdir(parents=True)
        dest = _dest(cw, into, harness_dest)
        if component == "snapshot":
            _redirect(cw, "demo/approved-plan/%s" % m.sha, dest)
        elif component == "files":
            pm.write_snapshot(m, ap_dir / m.sha)
            subprocess.run(["chmod", "-R", "u+w", str(ap_dir)], check=True)
            _redirect(cw, "demo/approved-plan/%s/files" % m.sha, dest)
        else:
            _redirect(cw, "demo/approved-plan/%s.staging" % m.sha, dest)
        link = cw.ev / {"snapshot": "demo/approved-plan/%s" % m.sha,
                        "files": "demo/approved-plan/%s/files" % m.sha,
                        "staging": "demo/approved-plan/%s.staging" % m.sha}[component]
        before = (_listing(dest), os.readlink(str(link)))
        r = cw.record_approval(SCOPED_THREAD)
        assert r.returncode == 1, r.stdout + r.stderr
        assert (_listing(dest), os.readlink(str(link))) == before
        assert not os.path.lexists(str(cw.ev / "demo/approval-current.json"))

    @pytest.mark.parametrize("component", ["snapshot", "files"])
    @pytest.mark.parametrize("into", ["target", "harness"])
    def test_verify_rejects_snapshot_redirect(self, tmp_path, harness_dest, component, into):
        cw = CliWorld(tmp_path)
        r = cw.record_approval(SCOPED_THREAD)
        assert r.returncode == 0, r.stdout + r.stderr
        sha = json.loads(r.stdout)["recordSha"]
        m = pm.build_manifest(cw.repo, "demo")
        rel = "demo/approved-plan/%s" % m.sha
        if component == "files":
            rel += "/files"
        subprocess.run(["chmod", "-R", "u+w", str(cw.ev / "demo/approved-plan")], check=True)
        moved = _redirect(cw, rel, _dest(cw, into, harness_dest))
        before = (_listing(moved), os.readlink(str(cw.ev / rel)))
        v = cw.verify(sha)
        assert v.returncode != 0, v.stdout + v.stderr
        assert (_listing(moved), os.readlink(str(cw.ev / rel))) == before


class TestApprovalPointerTempRedirect:
    """3차: approval-current.json.tmp가 기존 symlink면 따라가거나 교체하지 않는다."""

    @pytest.mark.parametrize("into", ["target", "harness"])
    def test_record_approval_refuses_preexisting_tmp_symlink(self, tmp_path, harness_dest,
                                                             into):
        cw = CliWorld(tmp_path)
        if into == "target":
            dest = cw.repo / "phases/demo/index.json"
        else:
            dest = harness_dest / "protected.json"
            dest.write_bytes(b'{"protected": true}\n')
        os.chmod(str(dest), 0o640)
        st = os.lstat(str(dest))
        before = (st.st_mode, dest.read_bytes())
        tmp = cw.ev / "demo/approval-current.json.tmp"
        tmp.symlink_to(dest)
        r = cw.record_approval(SCOPED_THREAD)
        assert r.returncode == 1, r.stdout + r.stderr
        st = os.lstat(str(dest))
        assert (st.st_mode, dest.read_bytes()) == before
        assert tmp.is_symlink() and os.readlink(str(tmp)) == str(dest)
        assert not os.path.lexists(str(cw.ev / "demo/approval-current.json"))
