#!/usr/bin/env python3
"""가벼운 TDD 편집 hook (DEV-LITE-001 §3). 실수 방지용이며 우회 가능성은 수용된 위험이다.

구현 파일(tdd.json implGlobs)을 편집하려면, 마지막 구현 변경 이후에 테스트(testGlobs) 변경이
있어야 한다: 미커밋(staged·worktree·untracked) 테스트 변경, 또는 가장 최근 구현 commit보다
뒤에 있는 테스트 commit. tdd-exception.json의 files 목록은 면제(승인된 리팩터링).
입력 해석 실패·설정 없음은 차단(exit 2)."""
import json, os, re, subprocess, sys


def deny(msg):
    sys.stderr.write("BLOCKED(tdd-guard): " + msg + "\n")
    sys.exit(2)


def glob_re(pat):
    out, i = "", 0
    while i < len(pat):
        if pat.startswith("**", i):
            out += ".*"; i += 2
        elif pat[i] == "*":
            out += "[^/]*"; i += 1
        else:
            out += re.escape(pat[i]); i += 1
    return re.compile("^" + out + "$")


def match(path, pats):
    return any(p.match(path) for p in pats)


def git(root, *args):
    r = subprocess.run(["git", "-C", root] + list(args), capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError(r.stderr.strip())
    return [l for l in r.stdout.splitlines() if l]


def git_paths(root, *args):
    """경로 목록은 -z(NUL 구분)로 읽는다. core.quotePath 인용("\355...")으로 비ASCII 경로를 놓치지 않기 위함."""
    r = subprocess.run(["git", "-C", root] + list(args) + ["-z"], capture_output=True)
    if r.returncode != 0:
        raise RuntimeError(r.stderr.decode("utf-8", "replace").strip())
    return [p.decode("utf-8", "surrogateescape") for p in r.stdout.split(b"\0") if p]


def paths_from_input(d):
    ti = d.get("tool_input")
    tool = d.get("tool_name")
    # null·누락도 형식 오류로 본다(기본값으로 바꾸면 검사를 건너뛰어 통과된다).
    if not isinstance(ti, dict) or not isinstance(tool, str):
        deny("hook 입력 형식이 올바르지 않습니다(tool_input은 객체, tool_name은 문자열이어야 합니다).")
    paths = []
    for k in ("file_path", "path", "notebook_path"):
        if isinstance(ti.get(k), str):
            paths.append(ti[k])
    if "edits" in ti:
        edits = ti["edits"]
        if not isinstance(edits, list) or not all(isinstance(e, dict) for e in edits):
            deny("hook 입력 형식이 올바르지 않습니다(edits는 객체 배열이어야 합니다).")
        for e in edits:
            if isinstance(e.get("file_path"), str):
                paths.append(e["file_path"])
    text = ""
    for k in ("command", "patch", "input"):
        v = ti.get(k)
        if isinstance(v, str):
            text += "\n" + v
        elif isinstance(v, list):
            text += "\n" + "\n".join(x for x in v if isinstance(x, str))
    for m in re.finditer(r"^\*\*\* (?:Add|Update|Delete) File: (.+)$", text, re.M):
        paths.append(m.group(1).strip())
    for m in re.finditer(r"^\*\*\* Move to: (.+)$", text, re.M):
        paths.append(m.group(1).strip())
    if "apply_patch" in tool and not paths:
        deny("apply_patch 입력에서 대상 파일을 찾지 못했습니다.")
    return paths


def main():
    try:
        d = json.load(sys.stdin)
        if not isinstance(d, dict):
            raise ValueError
    except Exception:
        deny("hook 입력(JSON)을 해석할 수 없습니다.")
    root = os.environ.get("CLAUDE_PROJECT_DIR") or d.get("cwd") or os.getcwd()
    try:
        root = git(root, "rev-parse", "--show-toplevel")[0]
    except Exception as e:
        deny("git 저장소를 찾지 못했습니다: %s" % e)
    root = os.path.realpath(root)
    try:
        cfg = json.load(open(os.path.join(root, "tdd.json")))
        impl = [glob_re(p) for p in cfg["implGlobs"]]
        tests = [glob_re(p) for p in cfg["testGlobs"]]
        base = cfg.get("baseRef", "origin/main")
    except Exception as e:
        deny("tdd.json을 읽지 못했습니다: %s" % e)
    exc = set()
    ep = os.path.join(root, "tdd-exception.json")
    if os.path.exists(ep):
        try:
            exc = set(json.load(open(ep))["files"])
        except Exception:
            deny("tdd-exception.json 형식 오류")

    targets = []
    for p in paths_from_input(d):
        ap = os.path.realpath(p if os.path.isabs(p) else os.path.join(d.get("cwd") or root, p))
        if ap != root and not ap.startswith(root + os.sep):
            continue  # 이 프로젝트 밖
        rel = os.path.relpath(ap, root)
        if match(rel, impl) and rel not in exc:
            targets.append(rel)
    if not targets:
        sys.exit(0)

    try:
        unc = set(git_paths(root, "diff", "--name-only")) | set(git_paths(root, "diff", "--name-only", "--cached")) \
            | set(git_paths(root, "ls-files", "--others", "--exclude-standard"))
        if any(match(f, tests) for f in unc):
            sys.exit(0)
        mb = git(root, "merge-base", base, "HEAD")[0]
        for c in git(root, "rev-list", "%s..HEAD" % mb):
            files = git_paths(root, "diff-tree", "--no-commit-id", "--name-only", "-r", c)
            if any(match(f, impl) for f in files):
                break  # 최근 구현 commit 이후 테스트 변경 없음
            if any(match(f, tests) for f in files):
                sys.exit(0)
    except Exception as e:
        deny("git 상태 확인 실패: %s" % e)
    deny("구현 파일 %s 편집 전에 tests/specs/ 테스트를 먼저 추가·수정하세요(실패하는 테스트 먼저). "
         "동작 불변 리팩터링이면 승인된 tdd-exception.json에 파일을 등록하세요." % ", ".join(targets))


if __name__ == "__main__":
    try:
        main()
    except SystemExit:
        raise
    except Exception as e:  # 예상 못 한 오류가 exit 1(통과)로 새지 않게 한다
        deny("hook 내부 오류: %s: %s" % (type(e).__name__, e))
