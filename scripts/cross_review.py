#!/usr/bin/env python3
"""Claude가 만든 것을 codex가 교차 리뷰한다(읽기 전용, stdout 출력).

Usage:
    python scripts/cross_review.py              # = diff (기본)
    python scripts/cross_review.py diff [ref]   # 코드 변경, 기본 HEAD
    python scripts/cross_review.py spec <경로>  # 설계 문서
    python scripts/cross_review.py plan <task> --evidence-dir <dir>  # review_plan.py 위임

execute.py의 phase-end 리뷰가 하네스 안에서만 도는 것과 달리, 이 스크립트는
일반 세션에서 애드혹으로 호출한다. 리뷰어는 항상 read-only로 띄우고 결과를
파일이 아니라 stdout으로 받는다 — 리뷰는 읽기 작업이므로 쓰기 권한을 주지
않는다. 모델은 하네스 리뷰 게이트와 같은 codex gpt-6-astra다.
"""
import contextlib
import hashlib
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import execute as ex  # noqa: E402

for _s in (sys.stdout, sys.stderr):
    with contextlib.suppress(AttributeError, ValueError):
        _s.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parent.parent
STATE_FILE = ROOT / ".claude" / ".cross-review-state"
REVIEW_TIMEOUT = 900

REVIEW_CRITERIA = {
    "diff": (
        "버그·회귀·경계조건·에러 처리 누락·기존 코드와의 일관성을 본다. "
        "포매팅이나 네이밍 취향 같은 스타일 지적은 하지 마라."
    ),
    "spec": (
        "내부 모순·누락된 케이스·검증 불가능한 성공 기준·과도한 범위를 본다. "
        "문장 다듬기 제안은 하지 마라."
    ),
}

USAGE = (
    "Usage: python scripts/cross_review.py [diff [ref] | spec <경로> | plan <task>]"
)


def _parse_target(argv):
    """(kind, arg)를 반환한다. 무인자는 ('diff', None)."""
    if not argv:
        return ("diff", None)
    kind = argv[0]
    if kind == "diff":
        return ("diff", argv[1] if len(argv) > 1 else None)
    if kind in ("spec", "plan"):
        if len(argv) < 2:
            print(f"ERROR: '{kind}'에는 인자가 필요합니다.\n{USAGE}")
            sys.exit(1)
        return (kind, argv[1])
    print(f"ERROR: 알 수 없는 대상 '{kind}'.\n{USAGE}")
    sys.exit(1)


def _collect_diff(ref):
    """git diff <ref> 결과를 반환한다. 변경이 없으면 빈 문자열."""
    result = subprocess.run(
        ["git", "diff", ref], cwd=str(ROOT), capture_output=True,
        text=True, encoding="utf-8",
    )
    return result.stdout


def _collect_spec(path_str):
    """리포 안의 파일 내용을 반환한다. 밖이거나 없으면 종료."""
    target = (ROOT / path_str).resolve()
    if not target.is_relative_to(ROOT.resolve()):
        print(f"ERROR: '{path_str}'는 리포 밖 경로입니다.")
        sys.exit(1)
    if not target.exists():
        print(f"ERROR: {target} 없음.")
        sys.exit(1)
    return target.read_text(encoding="utf-8")


def _run_review(kind, body):
    """codex를 read-only로 띄워 리뷰시킨다. 성공하면 True.

    대상 텍스트를 stdin으로 통째로 넘기므로 codex가 파일을 열 필요가 없다 —
    그래서 read-only로 충분하다.
    """
    prompt = (
        f"당신은 교차 리뷰어입니다. 아래 내용을 리뷰하세요.\n"
        f"기준: {REVIEW_CRITERIA[kind]}\n\n"
        f"각 지적에 severity를 붙이세요: critical / major / minor.\n"
        f"지적할 것이 없으면 정확히 'CLEAN' 한 단어만 답하세요.\n"
        f"아래 내용만 보고 판단하고, 파일을 열려고 하지 마세요.\n\n"
        f"---\n\n{body}\n"
    )
    # 리뷰는 항상 codex gpt-6-astra read-only — 하네스 리뷰 게이트와 같은 argv.
    argv = ex.build_code_review_argv()
    try:
        with ex.progress_indicator(f"Cross review ({kind}, codex)"):
            result = subprocess.run(
                argv, input=prompt, cwd=str(ROOT), capture_output=True,
                text=True, encoding="utf-8", timeout=REVIEW_TIMEOUT,
            )
    except FileNotFoundError:
        print("ERROR: codex CLI를 찾을 수 없습니다. "
              "https://github.com/openai/codex 설치 후 다시 시도하세요.")
        return False
    except subprocess.TimeoutExpired:
        print(f"ERROR: 리뷰가 {REVIEW_TIMEOUT}초 안에 끝나지 않았습니다.")
        return False

    if result.returncode != 0:
        print(f"ERROR: codex 실패 (exit {result.returncode})")
        if result.stderr:
            print(result.stderr.strip())
        return False
    if not result.stdout.strip():
        print("ERROR: codex가 아무 출력도 하지 않았습니다.")
        return False

    print(result.stdout.strip())
    return True


def _worktree_fingerprint():
    """워킹트리 내용의 지문 "<HEAD sha> <sha256(status+diff)>"를 만든다.

    시각(mtime)이 아니라 **내용**을 기록하므로, 내용이 같은 재저장은 미리뷰로
    잡히지 않는다. HEAD sha를 함께 넣는 이유는 diff만 해시하면 리뷰 후 커밋한
    순간 diff가 비어 "리뷰됨"과 같아져 미리뷰 코드를 놓치기 때문이다.

    ⚠ 이 형식은 hooks/cross-review-nudge.sh와의 계약이다. 한쪽만 바꾸면
    지문이 영영 어긋나 알림이 계속 뜬다. 반드시 함께 고칠 것.
    """
    # 현재 작업 디렉토리의 repo를 본다(ROOT 고정이 아니다). nudge hook은 자기
    # repo 루트에서 이 스크립트를 부르므로, 다른 repo에서 불려도 그 repo의
    # 지문이 나와야 한다.
    #
    # 출력을 **바이트 그대로** 다룬다(text=True 금지). 비-UTF-8 텍스트나 경로가
    # 섞이면 디코드에서 터지는데, hook의 `|| exit 0`이 그 실패를 삼켜 이후
    # 알림이 영영 사라진다 — 조용한 실패는 이 도구에서 가장 나쁜 실패 모드다.
    def _git(*args):
        r = subprocess.run(["git", *args], capture_output=True)
        if r.returncode != 0:
            raise RuntimeError(f"git {args[0]} 실패 (exit {r.returncode})")
        return r.stdout

    head = _git("rev-parse", "HEAD").strip()
    body = _git("status", "--porcelain", "-uall") + _git("diff", "HEAD")

    # untracked 파일은 위 둘 중 어디에도 **내용**이 안 들어간다(status는 경로만,
    # diff는 tracked만). 경로만 해시하면 새 파일을 리뷰한 뒤 내용을 고쳐도
    # 지문이 그대로여서 미리뷰 변경을 놓친다. git이 계산한 blob 해시를 붙인다.
    # -o(untracked) + --exclude-standard로 .gitignore는 그대로 존중된다.
    untracked = _git("ls-files", "-o", "--exclude-standard", "-z").split(b"\0")
    for path in sorted(p for p in untracked if p):
        blob = _git("hash-object", "--", path).strip()
        body += b"\n" + path + b" " + blob

    digest = hashlib.sha256(body).hexdigest()
    return f"{head.decode('utf-8', 'replace')} {digest}"


def _touch_state():
    """리뷰 완료 시점의 워킹트리 지문을 기록한다. nudge hook이 이것을 비교한다."""
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    STATE_FILE.write_text(_worktree_fingerprint() + "\n", encoding="utf-8")


def _delegate_plan(task, extra=()):
    """plan 대상은 review_plan.py(strict Astra 계획 리뷰 — 자동 수정 없음)에 위임한다.
    --evidence-dir 등 나머지 인자는 그대로 넘긴다."""
    result = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "review_plan.py"), task, *extra],
        cwd=str(ROOT),
    )
    sys.exit(result.returncode)


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv

    # nudge hook 전용 조회 경로. 지문 계산을 여기 한 곳에만 두기 위한 것이다
    # (bash에서 재구현하면 바이트/문자 해시 차이로 값이 갈린다).
    # 순수 조회 — codex를 부르지도, state를 갱신하지도 않는다.
    if argv and argv[0] == "--fingerprint":
        print(_worktree_fingerprint())
        sys.exit(0)

    kind, arg = _parse_target(argv)

    if kind == "plan":
        _delegate_plan(arg, argv[2:])

    if kind == "diff":
        body = _collect_diff(arg or "HEAD")
        if not body.strip():
            print("리뷰할 변경이 없습니다.")
            sys.exit(0)
    else:
        body = _collect_spec(arg)

    if not _run_review(kind, body):
        sys.exit(2)
    # state는 "코드가 마지막 리뷰 이후 바뀌었나"의 기준이므로 diff 리뷰에만
    # 갱신한다. spec 리뷰로 갱신하면 리뷰되지 않은 코드가 리뷰된 것으로
    # 표시되어 nudge가 조용해진다.
    if kind == "diff":
        _touch_state()
    sys.exit(0)


if __name__ == "__main__":
    main()
