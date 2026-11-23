#!/usr/bin/env python3
"""Discord thread ↔ Claude 계획 세션 제어 (하네스 모드 전용).

Usage: ./.venv/bin/python scripts/harness.py plan-session <command> --thread-id <id> ...

  start             --request-message-id --prompt-file   최초 호출(read-only plan 모드)
  resume            --message-id --prompt-file           같은 session_id로 --resume
  begin-post        --outbound-hash                      Discord 게시 직전 표시(본문 출력)
  record-posted     --outbound-hash --discord-message-id 게시된 Discord message ID 결속
  record-agreement  --message-id                         계획 대화 합의(구현 승인 아님)
  materialize       --task --output-json                 합의된 계획을 허용 경로에만 기록
  record-approval   (approval.py 참고)                   별도 구현 승인 메시지 결속
  resolve-recovery  --operator --reason --evidence-id    recovery-required 수동 해제
  status                                               상태 출력

계약:
- Claude는 `--permission-mode plan --allowedTools Read,Glob,Grep,Skill`, Write/Edit/Bash 금지,
  권한 우회 없음. 최초 응답의 session_id를 저장하고 이후는 반드시 `--resume <session_id>`.
- thread별 파일 lock으로 직렬화, Discord message ID로 중복 전달 방지.
- 호출 전 inflight를 기록한다. 비정상 종료·시간 초과·저장 전 crash는 자동 재전송 없이
  recovery-required로 멈춘다. 해제는 resolve-recovery(근거·사유 필수, append-only log)만.
- 종료코드: 0 성공 / 1 거부 / 3 recovery-required / 4 중복 message / 5 다른 호출 진행 중.

3.9에서도 파싱되어야 한다 — 3.10+ 문법 금지.
"""
import argparse
import contextlib
import fcntl
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

for _s in (sys.stdout, sys.stderr):
    with contextlib.suppress(AttributeError, ValueError):
        _s.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parent.parent
PLAN_TIMEOUT = 900
PLAN_ALLOWED_TOOLS = "Read,Glob,Grep,Skill"
PLAN_DISALLOWED_TOOLS = "Write,Edit,MultiEdit,NotebookEdit,Bash,WebFetch,Task"
GRILLING_SKILL_PATHS = (Path.home() / ".claude" / "skills" / "grilling" / "SKILL.md",)
EXIT_OK, EXIT_REJECT, EXIT_RECOVERY, EXIT_DUPLICATE, EXIT_BUSY = 0, 1, 3, 4, 5
_THREAD_RE = re.compile(r"\d{5,25}")
_SESSION_RE = re.compile(r"[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}")
_MSG_RE = re.compile(r"[A-Za-z0-9:_-]{1,80}")


class SessionError(Exception):
    exit_code = EXIT_REJECT


class RecoveryRequired(SessionError):
    exit_code = EXIT_RECOVERY


class DuplicateMessage(SessionError):
    exit_code = EXIT_DUPLICATE


class LockBusy(SessionError):
    exit_code = EXIT_BUSY


def build_plan_argv(session_id=None):
    """계획 단계 Claude argv — read-only. 권한 우회·쓰기 도구·--add-dir 없음."""
    argv = ["claude", "-p", "--output-format", "stream-json", "--verbose",
            "--permission-mode", "plan",
            "--allowedTools", PLAN_ALLOWED_TOOLS,
            "--disallowedTools", PLAN_DISALLOWED_TOOLS]
    if session_id is not None:
        if not isinstance(session_id, str) or not _SESSION_RE.fullmatch(session_id):
            raise SessionError("session_id 형식 오류: %r" % (session_id,))
        argv += ["--resume", session_id]
    return argv


def sha256_text(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _now():
    return datetime.now(timezone.utc).isoformat()


def parse_stream(stdout):
    """stream-json 출력 → (session_id, result_text, skills). 오류면 SessionError."""
    session_ids, skills, result = set(), [], None
    for n, line in enumerate((stdout or "").splitlines(), 1):
        if not line.strip():
            continue
        try:
            ev = json.loads(line)
        except ValueError:
            raise SessionError("Claude 출력 %d번째 줄이 JSON이 아님" % n)
        if not isinstance(ev, dict):
            raise SessionError("Claude 출력 이벤트가 객체가 아님")
        if ev.get("session_id"):
            session_ids.add(ev["session_id"])
        if ev.get("type") == "assistant":
            for item in (ev.get("message") or {}).get("content") or []:
                if (isinstance(item, dict) and item.get("type") == "tool_use"
                        and item.get("name") == "Skill"):
                    skill = (item.get("input") or {}).get("skill")
                    if isinstance(skill, str):
                        skills.append(skill)
        if ev.get("type") == "result":
            result = ev
    if result is None:
        raise SessionError("Claude result 이벤트 없음")
    if result.get("is_error") or result.get("subtype") not in (None, "success"):
        raise SessionError("Claude result 오류: %s" % result.get("subtype"))
    if len(session_ids) != 1:
        raise SessionError("session_id가 없거나 여러 개: %s" % sorted(session_ids))
    sid = session_ids.pop()
    if not _SESSION_RE.fullmatch(sid):
        raise SessionError("session_id 형식 오류")
    text = result.get("result")
    if not isinstance(text, str) or not text.strip():
        raise SessionError("Claude 응답 본문이 비어 있음")
    return sid, text, skills


def _grilling(skills):
    return any(s == "grilling" or s.endswith(":grilling") for s in skills)


def _new_state(thread_id):
    return {
        "version": 1, "threadId": thread_id, "status": "new", "sessionId": None,
        "processedMessageIds": [], "inflight": None, "turns": 0,
        "grillingInvoked": False, "pendingOutbound": None, "posted": [],
        "agreementMessageId": None, "implementationApproval": None,
        "recovery": None, "history": [], "createdAt": _now(),
    }


START_PROMPT = """[하네스 계획 세션 — read-only]
1. 먼저 Skill 도구로 `superpowers:brainstorming` 스킬을 호출하라.
2. 이어서 Skill 도구로 `grilling` 스킬을 직접 호출해 질문 라운드를 진행하라(grill-me 아님).
3. 이 세션은 하네스 모드 전용이다. SDD(subagent-driven-development)로 라우팅하지 마라.
4. 합의 전에는 어떤 파일도 쓰거나 수정하지 마라. 질문은 한 번에 하나씩 — 답변 원문이
   그대로 Discord 스레드에 게시된다.

--- 대표 요청 (Discord message {mid}) ---
{body}
"""

RESUME_PROMPT = """--- 대표 답변 (Discord message {mid}) ---
{body}
"""

MATERIALIZE_PROMPT = """[materialize — 합의된 계획을 하네스 모드 문서로 반환]
합의(Discord message {agreement})된 내용을 아래 JSON 하나로만 출력하라(설명·마크다운 금지).
파일은 하네스 제어 코드가 쓴다. 너는 쓰지 마라.
{{"task": "{task}", "files": [
  {{"path": "docs/superpowers/specs/<YYYY-MM-DD>-<topic>-design.md", "content": "..."}},
  {{"path": "phases/{task}/index.json", "content": "<JSON 문자열>"}},
  {{"path": "phases/{task}/step0.md", "content": "..."}}
]}}
index.json 필수 필드: project, phase, baseBranch("main"), designDoc(위 설계 경로),
allowedPaths(구현이 쓸 source/test 경로만, 예: ["src/", "tests/"]), testCommand(argv 목록),
steps([{{"step":0,"name":"kebab-case","status":"pending"}}, ...]). 허용 경로 밖 파일 금지.
"""


class Session:
    def __init__(self, root, runtime_dir, thread_id, timeout=PLAN_TIMEOUT, runner=None):
        if not isinstance(thread_id, str) or not _THREAD_RE.fullmatch(thread_id):
            raise SessionError("thread_id 형식 오류: %r" % (thread_id,))
        self.root = Path(root)
        self.rt = Path(runtime_dir)
        self.thread_id = thread_id
        self.timeout = timeout
        self._runner = runner
        self.state_path = self.rt / ("%s.json" % thread_id)
        self.lock_path = self.rt / ("%s.lock" % thread_id)
        self.log_path = self.rt / "recovery-log.jsonl"

    # --- 저장·잠금 ---

    @contextlib.contextmanager
    def _lock(self):
        self.rt.mkdir(parents=True, exist_ok=True)
        fd = os.open(str(self.lock_path), os.O_RDWR | os.O_CREAT, 0o600)
        try:
            try:
                fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
            except BlockingIOError:
                raise LockBusy("thread %s에 다른 호출이 진행 중 — 거부" % self.thread_id)
            yield
        finally:
            os.close(fd)

    def _load(self):
        if not self.state_path.exists():
            return None
        return json.loads(self.state_path.read_text(encoding="utf-8"))

    def _save(self, st):
        st["updatedAt"] = _now()
        tmp = self.state_path.with_name(self.state_path.name + ".tmp")
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(st, f, indent=2, ensure_ascii=False)
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp, self.state_path)

    def _require(self):
        st = self._load()
        if st is None:
            raise SessionError("thread %s 상태 없음 — start 먼저" % self.thread_id)
        return st

    def _to_recovery(self, st, reason):
        st["status"] = "recovery-required"
        st["recovery"] = {"reason": reason, "since": _now()}
        self._save(st)
        return RecoveryRequired(reason)

    def _guard(self, st):
        if st["status"] == "recovery-required":
            raise RecoveryRequired("recovery-required: %s — resolve-recovery 필요"
                                   % (st.get("recovery") or {}).get("reason"))
        if st.get("inflight"):
            raise self._to_recovery(
                st, "이전 호출(message %s)이 완료 기록 없이 끝남 — 자동 재전송 안 함"
                % st["inflight"].get("messageId"))

    # --- 사전 검사 ---

    def _check_grilling(self):
        if not any(Path(p).is_file() for p in GRILLING_SKILL_PATHS):
            raise SessionError("grilling 스킬이 설치돼 있지 않음: %s"
                               % ", ".join(str(p) for p in GRILLING_SKILL_PATHS))

    def _plan_diff(self):
        r = subprocess.run(["git", "status", "--porcelain", "--untracked-files=all", "--",
                            "docs", "phases"], cwd=str(self.root), capture_output=True,
                           text=True, encoding="utf-8")
        if r.returncode != 0:
            return "git status 실패: %s" % r.stderr.strip()
        return r.stdout.strip()

    # --- Claude 호출 ---

    def _invoke(self, argv, prompt):
        runner = self._runner
        if runner is None:
            import execute as ex
            runner = ex._run_agent_process
        return runner(argv, input=prompt, cwd=str(self.root), timeout=self.timeout)

    def _call(self, st, argv, prompt, message_id, kind, check_diff):
        st["inflight"] = {"messageId": message_id, "kind": kind, "startedAt": _now(),
                          "promptSha256": sha256_text(prompt)}
        st["status"] = "invoking"
        self._save(st)
        try:
            result = self._invoke(argv, prompt)
        except (OSError, ValueError) as e:
            raise self._to_recovery(st, "Claude 실행 실패: %s" % type(e).__name__)
        try:
            if result.timed_out:
                raise SessionError("Claude 시간 초과(%ss) — 프로세스 트리 종료" % self.timeout)
            if result.returncode != 0:
                raise SessionError("Claude 비정상 종료(code %s)" % result.returncode)
            sid, text, skills = parse_stream(result.stdout)
        except SessionError as e:
            raise self._to_recovery(st, str(e))
        if st["sessionId"] is None:
            st["sessionId"] = sid
        elif sid != st["sessionId"]:
            raise self._to_recovery(st, "session_id가 바뀜(%s) — 같은 세션이 아님" % sid)
        if check_diff:
            diff = self._plan_diff()
            if diff:
                raise self._to_recovery(st, "합의 전 docs/phases 변경 발생: %s" % diff[:200])
        st["inflight"] = None
        st["turns"] += 1
        st["grillingInvoked"] = bool(st["grillingInvoked"] or _grilling(skills))
        st["history"].append({"messageId": message_id, "kind": kind, "at": _now(),
                              "skills": skills, "responseSha256": sha256_text(text)})
        return text

    def _set_outbound(self, st, text, message_id):
        st["pendingOutbound"] = {"hash": sha256_text(text), "text": text,
                                 "forMessageId": message_id}
        st["status"] = "awaiting-post"
        self._save(st)
        return {"sessionId": st["sessionId"], "outboundHash": st["pendingOutbound"]["hash"],
                "text": text}

    # --- 명령 ---

    def start(self, message_id, prompt_text):
        _check_msg(message_id)
        with self._lock():
            st = self._load()
            if st is not None and st["status"] == "abandoned":
                os.replace(self.state_path, self.state_path.with_name(
                    "%s.abandoned-%s.json" % (self.thread_id, _now().replace(":", ""))))
                st = None
            if st is not None:
                self._guard(st)
                raise SessionError("thread %s는 이미 시작됨 — resume 사용" % self.thread_id)
            self._check_grilling()
            diff = self._plan_diff()
            if diff:
                raise SessionError("합의 전인데 docs/phases 변경이 있음: %s" % diff[:200])
            st = _new_state(self.thread_id)
            st["processedMessageIds"].append(message_id)
            prompt = START_PROMPT.format(mid=message_id, body=prompt_text)
            text = self._call(st, build_plan_argv(), prompt, message_id, "start", True)
            return self._set_outbound(st, text, message_id)

    def resume(self, message_id, prompt_text):
        _check_msg(message_id)
        with self._lock():
            st = self._require()
            self._guard(st)
            if message_id in st["processedMessageIds"]:
                raise DuplicateMessage("message %s는 이미 전달됨 — 재전송하지 않음" % message_id)
            if st["status"] != "idle":
                raise SessionError("status=%s — 이전 응답 게시(record-posted)를 먼저 하라"
                                   % st["status"])
            before_agreement = st["agreementMessageId"] is None
            if before_agreement:
                diff = self._plan_diff()
                if diff:
                    raise SessionError("합의 전인데 docs/phases 변경이 있음: %s" % diff[:200])
            st["processedMessageIds"].append(message_id)
            prompt = RESUME_PROMPT.format(mid=message_id, body=prompt_text)
            text = self._call(st, build_plan_argv(st["sessionId"]), prompt, message_id,
                              "resume", before_agreement)
            return self._set_outbound(st, text, message_id)

    def begin_post(self, outbound_hash):
        with self._lock():
            st = self._require()
            if st["status"] == "posting":
                raise self._to_recovery(
                    st, "이전 게시가 record-posted 없이 끝남 — 게시 여부를 스레드에서 대조하라")
            self._guard(st)
            pend = st.get("pendingOutbound")
            if st["status"] != "awaiting-post" or not pend:
                raise SessionError("게시할 응답이 없음(status=%s)" % st["status"])
            if pend["hash"] != outbound_hash:
                raise SessionError("outbound hash 불일치")
            st["status"] = "posting"
            st["postingSince"] = _now()
            self._save(st)
            return {"outboundHash": pend["hash"], "text": pend["text"]}

    def record_posted(self, outbound_hash, discord_message_id):
        _check_msg(discord_message_id)
        with self._lock():
            st = self._require()
            if st["status"] != "posting":
                raise SessionError("begin-post 없이 record-posted 불가(status=%s)" % st["status"])
            pend = st["pendingOutbound"]
            if pend["hash"] != outbound_hash:
                raise SessionError("outbound hash 불일치")
            st["posted"].append({"outboundHash": outbound_hash,
                                 "discordMessageId": discord_message_id,
                                 "forMessageId": pend.get("forMessageId"), "postedAt": _now()})
            st["pendingOutbound"] = None
            st["status"] = "idle"
            self._save(st)
            return {"status": "idle"}

    def record_agreement(self, message_id):
        _check_msg(message_id)
        with self._lock():
            st = self._require()
            self._guard(st)
            if st["status"] != "idle":
                raise SessionError("status=%s — 응답 게시 후 합의를 기록하라" % st["status"])
            if st["agreementMessageId"]:
                raise SessionError("합의는 이미 기록됨(%s)" % st["agreementMessageId"])
            if not st["grillingInvoked"]:
                raise SessionError("grilling 스킬 호출이 확인되지 않음 — 계획 완료로 처리하지 않음")
            if st["turns"] < 2:
                raise SessionError("질문 라운드(최소 1회 답변)가 확인되지 않음")
            st["agreementMessageId"] = message_id
            st["agreementAt"] = _now()
            self._save(st)
            return {"agreementMessageId": message_id}

    def materialize(self, task, output_json):
        import plan_manifest as pm
        with self._lock():
            st = self._require()
            self._guard(st)
            if not st["agreementMessageId"]:
                raise SessionError("합의(record-agreement) 전 materialize 거부")
            if st["status"] != "idle":
                raise SessionError("status=%s" % st["status"])
            try:
                pm._check_task(task)
            except pm.ManifestError as e:
                raise SessionError(str(e))
            mid = "materialize-%d" % st["turns"]
            prompt = MATERIALIZE_PROMPT.format(task=task, agreement=st["agreementMessageId"])
            text = self._call(st, build_plan_argv(st["sessionId"]), prompt, mid,
                              "materialize", False)
            st["status"] = "idle"
            self._save(st)
            files = validate_payload(text, task)
            write_plan_files(self.root, task, files)
            try:
                m = pm.build_manifest(self.root, task)
            except pm.ManifestError as e:
                raise SessionError("materialize 결과가 유효한 계획이 아님: %s" % e)
            report = {"task": task, "planSha": m.sha, "sessionId": st["sessionId"],
                      "agreementMessageId": st["agreementMessageId"],
                      "files": [{"path": p, "sha256": hashlib.sha256(
                          c.encode("utf-8")).hexdigest()} for p, c in sorted(files.items())]}
            Path(output_json).write_text(json.dumps(report, indent=2, ensure_ascii=False),
                                         encoding="utf-8")
            return report

    def resolve_recovery(self, operator, reason, evidence_id, requeue=False,
                         posted_message_id=None, session_id=None):
        for name, v in (("operator", operator), ("reason", reason), ("evidence-id", evidence_id)):
            if not isinstance(v, str) or not v.strip():
                raise SessionError("%s 필수(근거 없는 해제 불가)" % name)
        with self._lock():
            st = self._require()
            if st["status"] != "recovery-required" and not st.get("inflight"):
                raise SessionError("recovery-required 상태가 아님(status=%s)" % st["status"])
            prev = json.loads(json.dumps(st))
            inflight = st.get("inflight") or {}
            requeued = None
            if requeue and inflight.get("messageId") in st["processedMessageIds"]:
                requeued = inflight["messageId"]
                st["processedMessageIds"].remove(requeued)
            if session_id:
                if not _SESSION_RE.fullmatch(session_id):
                    raise SessionError("session_id 형식 오류")
                if st["sessionId"] not in (None, session_id):
                    raise SessionError("기존 session_id와 다름 — 새 세션은 새 thread 상태로")
                st["sessionId"] = session_id
            if posted_message_id:
                _check_msg(posted_message_id)
                pend = st.get("pendingOutbound")
                if not pend:
                    raise SessionError("결속할 outbound가 없음")
                st["posted"].append({"outboundHash": pend["hash"],
                                     "discordMessageId": posted_message_id,
                                     "forMessageId": pend.get("forMessageId"),
                                     "postedAt": _now(), "viaRecovery": True})
                st["pendingOutbound"] = None
            entry = {
                "threadId": self.thread_id, "resolvedAt": _now(), "operator": operator,
                "reason": reason, "evidenceId": evidence_id,
                "evidenceSha": sha256_text(evidence_id),
                "previousState": prev,
                "previousStateSha": hashlib.sha256(json.dumps(
                    prev, sort_keys=True, ensure_ascii=False).encode("utf-8")).hexdigest(),
                "requeued": requeued, "postedMessageId": posted_message_id,
                "sessionId": st["sessionId"],
            }
            with open(self.log_path, "a", encoding="utf-8") as f:
                f.write(json.dumps(entry, ensure_ascii=False) + "\n")
                f.flush()
                os.fsync(f.fileno())
            st["inflight"] = None
            st["recovery"] = None
            st.pop("postingSince", None)
            if st["sessionId"] is None:
                st["status"] = "abandoned"
            elif st.get("pendingOutbound"):
                st["status"] = "awaiting-post"
            else:
                st["status"] = "idle"
            self._save(st)
            return {"status": st["status"]}

    def status(self):
        return self._require()


def _check_msg(mid):
    if not isinstance(mid, str) or not _MSG_RE.fullmatch(mid):
        raise SessionError("message id 형식 오류: %r" % (mid,))


_SPEC_RE = re.compile(r"docs/superpowers/specs/[A-Za-z0-9][A-Za-z0-9._-]*\.md")


def validate_payload(text, task):
    import plan_manifest as pm
    s = text.strip()
    fence = re.fullmatch(r"```(?:json)?\s*\n(.*)\n```", s, re.DOTALL)
    if fence:
        s = fence.group(1).strip()
    try:
        payload = json.loads(s)
    except ValueError:
        raise SessionError("materialize payload가 JSON이 아님")
    if not isinstance(payload, dict) or set(payload) != {"task", "files"}:
        raise SessionError("payload 키는 task, files여야 함")
    if payload["task"] != task:
        raise SessionError("payload task 불일치")
    files = {}
    if not isinstance(payload["files"], list):
        raise SessionError("files가 목록이 아님")
    step_re = re.compile(r"phases/%s/step(\d+)\.md" % re.escape(task))
    specs = []
    for f in payload["files"]:
        if not isinstance(f, dict) or set(f) != {"path", "content"} or not all(
                isinstance(f[k], str) for k in ("path", "content")):
            raise SessionError("file 항목 형식 오류")
        p = f["path"]
        if p in files:
            raise SessionError("중복 경로: %s" % p)
        if _SPEC_RE.fullmatch(p):
            specs.append(p)
        elif p != "phases/%s/index.json" % task and not step_re.fullmatch(p):
            raise SessionError("허용되지 않은 경로: %r" % p)
        files[p] = f["content"]
    if len(specs) != 1:
        raise SessionError("설계 문서는 정확히 1개여야 함(%d개)" % len(specs))
    index_rel = "phases/%s/index.json" % task
    if index_rel not in files:
        raise SessionError("index.json 없음")
    try:
        index = json.loads(files[index_rel])
        pm.validate_index(index, task)
    except (ValueError, pm.ManifestError) as e:
        raise SessionError("index.json 검증 실패: %s" % e)
    if index["designDoc"] != specs[0]:
        raise SessionError("designDoc이 payload 설계 문서와 다름")
    if any(s.get("status", "pending") != "pending" or set(s) - {"step", "name", "status"}
           for s in index["steps"]) or set(index) - {
               "project", "phase", "baseBranch", "designDoc", "allowedPaths", "testCommand",
               "reviewExclude", "steps"}:
        raise SessionError("새 계획은 pending step과 불변 필드만 가져야 함")
    expected = {"phases/%s/step%d.md" % (task, i) for i in range(len(index["steps"]))}
    got = {p for p in files if step_re.fullmatch(p)}
    if got != expected:
        raise SessionError("step 파일 집합이 index와 다름")
    return files


def _check_target(root, rel):
    """쓰기 대상과 상위 디렉터리가 symlink/특수 파일이 아닌지 확인(없는 건 허용)."""
    cur = Path(root)
    for part in rel.split("/")[:-1]:
        cur = cur / part
        if os.path.lexists(cur):
            st = os.lstat(cur)
            import stat as _stat
            if not _stat.S_ISDIR(st.st_mode):
                raise SessionError("쓰기 경로 상위가 디렉터리가 아님(symlink 등): %s" % rel)
    target = Path(root) / rel
    if os.path.lexists(target):
        import stat as _stat
        st = os.lstat(target)
        if not _stat.S_ISREG(st.st_mode) or st.st_nlink != 1:
            raise SessionError("쓰기 대상이 regular file이 아님(symlink/hardlink): %s" % rel)


def write_plan_files(root, task, files):
    root = Path(root)
    for rel in files:
        _check_target(root, rel)
    task_dir = root / "phases" / task
    if task_dir.is_dir():
        for p in task_dir.iterdir():
            rel = "phases/%s/%s" % (task, p.name)
            if re.fullmatch(r"step.*\.md", p.name, re.IGNORECASE) and rel not in files:
                _check_target(root, rel)
                p.unlink()
    for rel, content in files.items():
        target = root / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        tmp = target.with_name(target.name + ".materialize-tmp")
        tmp.write_text(content, encoding="utf-8")
        os.replace(tmp, target)


def _runtime_dir(root):
    return Path(os.environ.get("HARNESS_RUNTIME_DIR") or (Path(root) / ".harness" / "runtime"))


def build_parser():
    p = argparse.ArgumentParser(description="Discord↔Claude 계획 세션 (하네스 모드)")
    sub = p.add_subparsers(dest="cmd", required=True)

    def add(name, *args):
        sp = sub.add_parser(name)
        sp.add_argument("--thread-id", required=True)
        sp.add_argument("--repo-root", default=str(ROOT))
        for a in args:
            sp.add_argument(a, required=a not in ("--requeue", "--posted-message-id",
                                                  "--session-id"))
        return sp

    add("start", "--request-message-id", "--prompt-file")
    add("resume", "--message-id", "--prompt-file")
    add("begin-post", "--outbound-hash")
    add("record-posted", "--outbound-hash", "--discord-message-id")
    add("record-agreement", "--message-id")
    add("materialize", "--task", "--output-json")
    sp = add("resolve-recovery", "--operator", "--reason", "--evidence-id",
             "--posted-message-id", "--session-id")
    sp.add_argument("--requeue", action="store_true")
    add("record-approval", "--message-id", "--approver-user-id", "--plan-commit",
        "--body-file", "--task", "--issue", "--evidence-dir")
    add("status")
    return p


def main(argv=None):
    runtime.require_runtime()
    args = build_parser().parse_args(argv)
    s = Session(args.repo_root, _runtime_dir(args.repo_root), args.thread_id)
    try:
        if args.cmd == "start":
            out = s.start(args.request_message_id,
                          Path(args.prompt_file).read_text(encoding="utf-8"))
        elif args.cmd == "resume":
            out = s.resume(args.message_id, Path(args.prompt_file).read_text(encoding="utf-8"))
        elif args.cmd == "begin-post":
            out = s.begin_post(args.outbound_hash)
        elif args.cmd == "record-posted":
            out = s.record_posted(args.outbound_hash, args.discord_message_id)
        elif args.cmd == "record-agreement":
            out = s.record_agreement(args.message_id)
        elif args.cmd == "materialize":
            out = s.materialize(args.task, args.output_json)
        elif args.cmd == "resolve-recovery":
            out = s.resolve_recovery(args.operator, args.reason, args.evidence_id,
                                     requeue=args.requeue,
                                     posted_message_id=args.posted_message_id,
                                     session_id=args.session_id)
        elif args.cmd == "record-approval":
            import approval
            out = approval.record_approval(
                session=s, repo=Path(args.repo_root), task=args.task, issue=args.issue,
                message_id=args.message_id, user_id=args.approver_user_id,
                body=Path(args.body_file).read_text(encoding="utf-8"),
                plan_commit=args.plan_commit, evidence_dir=Path(args.evidence_dir))
        else:
            out = s.status()
    except SessionError as e:
        print("ERROR: %s" % e, file=sys.stderr)
        return e.exit_code
    except Exception as e:  # approval.ApprovalError 등
        code = getattr(e, "exit_code", None)
        if code is None:
            raise
        print("ERROR: %s" % e, file=sys.stderr)
        return code
    print(json.dumps(out, indent=2, ensure_ascii=False))
    return EXIT_OK


if __name__ == "__main__":
    sys.exit(main())
