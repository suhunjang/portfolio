#!/usr/bin/env python3
"""가벼운 TDD 완료 검증 (DEV-LITE-001 §3). 담당 PM이 완료 직전에 실행한다.

사용: python3 scripts/tdd-verify.py [--out tdd-evidence.json] [--skip-full]
- 구현 변경 없음(문서·설정·테스트만): 최종 HEAD 전체 테스트 GREEN만 요구.
- 구현 변경 있음: 첫 구현 commit 이전의 테스트 commit에서 새·변경 테스트가 RED(실패 1개 이상,
  수집 0·실행 오류는 RED 아님) → 최종 HEAD에서 같은 테스트 + 전체 GREEN.
- tdd-exception.json의 files(승인된 리팩터링)만 바뀐 경우 RED 생략, 전체 GREEN 필수.
- 각 실행은 임시 worktree에서, 포트가 비어 있을 때만, 그 worktree를 루트로 띄운 서버로 한다.
exit 0 = PASS, 1 = FAIL."""
import argparse, hashlib, json, os, re, shutil, socket, subprocess, sys, tempfile, time, urllib.request


def sh(args, cwd, check=True, env=None):
    r = subprocess.run(args, cwd=cwd, capture_output=True, text=True, env=env)
    if check and r.returncode != 0:
        raise RuntimeError("%s: %s" % (" ".join(args), r.stderr.strip()[:500]))
    return r


def git(root, *a):
    return [l for l in sh(["git", "-C", root] + list(a), root).stdout.splitlines() if l]


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


def m(path, pats):
    return any(p.match(path) for p in pats)


def port_busy(port):
    with socket.socket() as s:
        s.settimeout(0.5)
        return s.connect_ex(("127.0.0.1", port)) == 0


def sha(b):
    return hashlib.sha256(b).hexdigest()


def run_at(root, cfg, commit, test_files, label):
    """commit을 임시 worktree에 꺼내 격리 서버로 테스트를 돌린다."""
    port = cfg.get("port", 4173)
    if port_busy(port):
        raise RuntimeError("포트 %d가 이미 사용 중입니다. 기존 서버 재사용을 막기 위해 중단합니다." % port)
    tmp = tempfile.mkdtemp(prefix="tdd-verify-")
    wt = os.path.join(tmp, "wt")
    sh(["git", "-C", root, "worktree", "add", "--detach", wt, commit], root)
    srv = None
    try:
        tcwd = os.path.join(wt, cfg.get("testCwd", "tests"))
        lock_src = os.path.join(root, cfg.get("testCwd", "tests"), "package-lock.json")
        lock_wt = os.path.join(tcwd, "package-lock.json")
        if open(lock_src, "rb").read() != open(lock_wt, "rb").read():
            raise RuntimeError("%s의 package-lock.json이 현재 작업 트리와 다릅니다(의존성 재설치 필요)." % label)
        os.symlink(os.path.join(root, cfg.get("testCwd", "tests"), "node_modules"), os.path.join(tcwd, "node_modules"))
        srv = subprocess.Popen(["python3", "-m", "http.server", str(port), "--bind", "127.0.0.1"], cwd=wt,
                               stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        served = None
        for _ in range(50):
            try:
                served = urllib.request.urlopen("http://127.0.0.1:%d/index.html" % port, timeout=1).read()
                break
            except Exception:
                time.sleep(0.2)
        want = open(os.path.join(wt, "index.html"), "rb").read()
        if served is None or sha(served) != sha(want):
            raise RuntimeError("%s: 테스트 서버가 대상 worktree의 index.html을 제공하지 않습니다." % label)
        env = dict(os.environ)
        env["PLAYWRIGHT_BROWSERS_PATH"] = os.path.join(root, cfg.get("testCwd", "tests"), ".pw-browsers")
        env["TMPDIR"] = tmp
        rel = [os.path.relpath(os.path.join(wt, f), tcwd) for f in test_files]
        r = subprocess.run(cfg["testCommand"] + ["--reporter=json"] + rel, cwd=tcwd, capture_output=True,
                           text=True, env=env)
        try:
            rep = json.loads(r.stdout)
            st = rep.get("stats", {})
            failed_names, passed = [], 0
            def walk(suite):
                nonlocal passed
                for sp in suite.get("specs", []):
                    if sp.get("ok"):
                        passed += 1
                    else:
                        failed_names.append(sp.get("title"))
                for s in suite.get("suites", []):
                    walk(s)
            for s in rep.get("suites", []):
                walk(s)
            errors = len(rep.get("errors", []))
        except Exception:
            st, failed_names, passed, errors = {}, [], 0, -1
        return {"label": label, "commit": commit, "port": port, "serverPid": srv.pid,
                "servedIndexSha256": sha(served), "command": cfg["testCommand"] + rel, "exitCode": r.returncode,
                "expected": st.get("expected", 0), "unexpected": st.get("unexpected", 0),
                "skipped": st.get("skipped", 0), "collectionErrors": errors,
                "failedSpecs": sorted(set(failed_names))[:50], "passedSpecs": passed,
                "outputSha256": sha((r.stdout + r.stderr).encode())}
    finally:
        if srv:
            srv.terminate(); srv.wait(10)
        sh(["git", "-C", root, "worktree", "remove", "--force", wt], root, check=False)
        shutil.rmtree(tmp, ignore_errors=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="tdd-evidence.json")
    ap.add_argument("--base", help="검증 시작 기준 commit(기본: tdd.json baseRef와의 merge-base). 오래된 브랜치의 이번 작업 구간만 볼 때 사용")
    ap.add_argument("--skip-full", action="store_true", help="자체 시험용: 전체 테스트 생략(실제 완료 판정에 쓰지 말 것)")
    a = ap.parse_args()
    root = git(os.getcwd(), "rev-parse", "--show-toplevel")[0]
    cfg = json.load(open(os.path.join(root, "tdd.json")))
    impl = [glob_re(p) for p in cfg["implGlobs"]]
    tests = [glob_re(p) for p in cfg["testGlobs"]]
    exc = set()
    if os.path.exists(os.path.join(root, "tdd-exception.json")):
        exc = set(json.load(open(os.path.join(root, "tdd-exception.json")))["files"])
    if git(root, "status", "--porcelain", "--untracked-files=no"):
        print("FAIL: 커밋되지 않은 변경이 있습니다. 검증은 commit 기준입니다."); return 1
    head = git(root, "rev-parse", "HEAD")[0]
    mb = git(root, "rev-parse", a.base)[0] if a.base else git(root, "merge-base", cfg.get("baseRef", "origin/main"), "HEAD")[0]
    commits = list(reversed(git(root, "rev-list", "%s..HEAD" % mb)))
    per = [(c, git(root, "diff-tree", "--no-commit-id", "--name-only", "-r", c)) for c in commits]
    impl_files = sorted({f for _, fs in per for f in fs if m(f, impl)})
    strict_impl = [f for f in impl_files if f not in exc]
    ev = {"policy": "DEV-LITE-001", "head": head, "mergeBase": mb, "implFiles": impl_files,
          "exceptionFiles": sorted(exc), "runs": []}
    reasons = []
    if not strict_impl:
        ev["classification"] = "no-impl-change" if not impl_files else "approved-refactor-only"
    else:
        ev["classification"] = "impl-change"
        first_impl = next(i for i, (_, fs) in enumerate(per) if any(m(f, impl) and f not in exc for f in fs))
        pre = per[:first_impl]
        tfiles = sorted({f for _, fs in pre for f in fs if m(f, tests)})
        test_commits = [c for c, fs in pre if any(m(f, tests) for f in fs)]
        if not test_commits:
            reasons.append("첫 구현 commit 이전에 테스트 commit이 없습니다.")
        else:
            red_c = test_commits[-1]
            mixed = [c for c, fs in pre if c in test_commits and any(m(f, impl) for f in fs)]
            if mixed:
                reasons.append("테스트 commit에 구현 파일이 섞여 있습니다: %s" % mixed)
            existing = [f for f in tfiles if os.path.exists(os.path.join(root, f))]
            ev["redTestFiles"] = existing
            red = run_at(root, cfg, red_c, existing, "RED")
            ev["runs"].append(red)
            if red["collectionErrors"] != 0 or red["unexpected"] < 1 or (red["expected"] + red["unexpected"]) == 0:
                reasons.append("테스트 commit에서 RED가 아닙니다(실패 %s, 수집 오류 %s)."
                               % (red["unexpected"], red["collectionErrors"]))
            green_f = run_at(root, cfg, head, existing, "GREEN-focused")
            ev["runs"].append(green_f)
            if green_f["exitCode"] != 0 or green_f["unexpected"] != 0 or green_f["expected"] == 0:
                reasons.append("최종 HEAD에서 같은 테스트가 통과하지 않습니다.")
    if a.skip_full:
        ev["fullSuite"] = "skipped(self-test only)"
    else:
        full = run_at(root, cfg, head, [], "GREEN-full")
        ev["runs"].append(full)
        if full["exitCode"] != 0 or full["unexpected"] != 0 or full["expected"] == 0:
            reasons.append("최종 HEAD 전체 테스트가 통과하지 않습니다(실패 %s)." % full["unexpected"])
    ev["result"] = "FAIL" if reasons or a.skip_full else "PASS"
    ev["reasons"] = reasons
    with open(a.out, "w") as f:
        json.dump(ev, f, ensure_ascii=False, indent=2)
    print(ev["result"] + ("" if not reasons else ": " + " / ".join(reasons)))
    return 0 if ev["result"] == "PASS" else 1


if __name__ == "__main__":
    try:
        sys.exit(main())
    except RuntimeError as e:
        print("FAIL: %s" % e); sys.exit(1)
