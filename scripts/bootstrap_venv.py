#!/usr/bin/env python3
"""repo-local .venv를 만들고 검증한다 — 승인 base interpreter는 호스트별로 정한다.

Usage:
  <python3.10+> scripts/bootstrap_venv.py --check   # 기본: 검증만
  <python3.10+> scripts/bootstrap_venv.py --plan    # 실행할 명령만 출력
  <python3.10+> scripts/bootstrap_venv.py --create  # .venv 생성 + pytest 설치 + 기록

승인 base interpreter:
- `.harness/policy.local.json`의 `approvedBaseInterpreter`(호스트 전용 exact pin, 배포 안 함)가
  있으면 그것만 쓴다.
- 없으면 bootstrap을 **실행한 interpreter(sys.executable)**를 쓰고, 만든 .venv의 base
  (pyvenv.cfg home·version)를 `.venv/harness-bootstrap.json`에 기록한다. --check는 .venv가
  그 기록(또는 pin)과 같은지, Python이 policy `pythonMinVersion`(코드 하한 3.10) 이상인지 본다.
  policy `pythonRecommendedVersion`과 다르면 경고만 한다.

3.9에서도 파싱되어야 한다 — 3.10+ 문법 금지.
"""
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import runtime  # noqa: E402

TEST_DEPS = ["pytest"]
RECORD_NAME = "harness-bootstrap.json"


def _read_cfg(path):
    out = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        if "=" in line:
            k, v = line.split("=", 1)
            out[k.strip()] = v.strip()
    return out


def _version_tuple(text):
    parts = []
    for x in (text or "").split("."):
        if not x.isdigit():
            break
        parts.append(int(x))
    return tuple(parts)


def _fmt(v):
    return ".".join(str(x) for x in v)


def base_interpreter(root):
    """승인 base interpreter: policy.local pin이 있으면 그것, 없으면 지금 실행 중인 interpreter."""
    pin = runtime.read_local_policy(root).get("approvedBaseInterpreter")
    return pin or sys.executable


def _policy_versions(root):
    """(최소, 권장) — policy가 없으면 (코드 하한, None). policy가 틀리면 PolicyError."""
    if not (Path(root) / runtime.POLICY_REL).exists():
        return runtime.MIN_VERSION, None
    pol = runtime.read_policy(root)
    return max(runtime.MIN_VERSION, pol.python_min_version), pol.python_recommended_version


def write_record(root, base):
    """만든 .venv의 base(pyvenv.cfg home·version)와 bootstrap interpreter를 기록한다."""
    venv = Path(root) / ".venv"
    cfg = _read_cfg(venv / "pyvenv.cfg")
    record = {"schemaVersion": 1, "baseExecutable": str(base), "home": cfg.get("home"),
              "version": cfg.get("version"),
              "createdAt": datetime.now(timezone.utc).isoformat()}
    (venv / RECORD_NAME).write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
    return record


def check_report(root):
    """(오류 목록, 경고 목록). 오류가 없으면 통과."""
    root = Path(root)
    errors, warnings = [], []
    cfg_path = root / ".venv" / "pyvenv.cfg"
    if not cfg_path.is_file() or not (root / ".venv" / "bin" / "python").exists():
        return [".venv 없음 — --create 로 만들어라"], warnings
    cfg = _read_cfg(cfg_path)
    try:
        pin = runtime.read_local_policy(root).get("approvedBaseInterpreter")
        lo, rec = _policy_versions(root)
    except runtime.PolicyError as e:
        return [str(e)], warnings
    if pin:
        if cfg.get("home") != str(Path(pin).parent):
            errors.append("base interpreter home=%r ≠ policy.local 승인값 %r"
                          % (cfg.get("home"), str(Path(pin).parent)))
    else:
        rpath = root / ".venv" / RECORD_NAME
        try:
            record = runtime.strict_json_loads(rpath.read_bytes(), "bootstrap 기록")
        except (OSError, ValueError) as e:
            return ["bootstrap 기록 없음/손상(%s) — bootstrap_venv.py --create로 다시 만들어라"
                    % e], warnings
        if (not isinstance(record, dict) or record.get("home") != cfg.get("home")
                or record.get("version") != cfg.get("version")):
            errors.append("pyvenv.cfg(home=%r, version=%r)가 bootstrap 기록과 다름 — .venv가 "
                          "기록 없이 다시 만들어짐" % (cfg.get("home"), cfg.get("version")))
    version = _version_tuple(cfg.get("version"))
    if len(version) < 2 or version[:2] < lo:
        errors.append("venv Python %r < %s (policy pythonMinVersion)"
                      % (cfg.get("version"), _fmt(lo)))
    pinned_file = root / ".python-version"
    pinned = pinned_file.read_text(encoding="utf-8").strip() if pinned_file.exists() else ""
    if rec is not None and pinned and _version_tuple(pinned) != rec:
        warnings.append(".python-version %r ≠ policy pythonRecommendedVersion %s"
                        % (pinned, _fmt(rec)))
    want = rec if rec is not None else _version_tuple(pinned)
    if want and version != want:
        warnings.append("venv Python %s ≠ 권장 %s (최소 버전은 만족)"
                        % (cfg.get("version"), _fmt(want)))
    return errors, warnings


def check(root):
    return check_report(root)[0]


def plan_commands(root):
    root = Path(root)
    return [
        [base_interpreter(root), "-m", "venv", str(root / ".venv")],
        [str(root / ".venv" / "bin" / "python"), "-m", "pip", "install"] + TEST_DEPS,
    ]


def _probe_version(base):
    r = subprocess.run([base, "-c", "import sys; print('%d.%d.%d' % sys.version_info[:3])"],
                       capture_output=True, text=True)
    return _version_tuple(r.stdout.strip()) if r.returncode == 0 else ()


def create(root):
    root = Path(root)
    try:
        base = base_interpreter(root)
        lo, _ = _policy_versions(root)
    except runtime.PolicyError as e:
        print("ERROR: %s" % e, file=sys.stderr)
        return 1
    if not Path(base).exists():
        print("ERROR: 승인 base interpreter 없음: %s" % base, file=sys.stderr)
        return 1
    found = _probe_version(base)
    if len(found) < 2 or found[:2] < lo:
        print("ERROR: Python >=%s 필요 — base %s 는 %s. 3.10 이상 interpreter로 실행하라."
              % (_fmt(lo), base, _fmt(found) or "알 수 없음"), file=sys.stderr)
        return 1
    for cmd in plan_commands(root):
        print("+ " + " ".join(cmd))
        rc = subprocess.call(cmd)
        if rc != 0:
            return rc
    write_record(root, base)
    errors, warnings = check_report(root)
    for w in warnings:
        print("WARNING: " + w, file=sys.stderr)
    for e in errors:
        print("ERROR: " + e, file=sys.stderr)
    return 1 if errors else 0


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    mode = argv[0] if argv else "--check"
    root = runtime.REPO_ROOT
    if mode == "--plan":
        try:
            cmds = plan_commands(root)
        except runtime.PolicyError as e:
            print("ERROR: %s" % e, file=sys.stderr)
            return 1
        for cmd in cmds:
            print(" ".join(cmd))
        return 0
    if mode == "--create":
        return create(root)
    if mode == "--check":
        errors, warnings = check_report(root)
        for w in warnings:
            print("WARNING: " + w, file=sys.stderr)
        for e in errors:
            print("ERROR: " + e, file=sys.stderr)
        if not errors:
            print("OK: .venv = %s" % _read_cfg(root / ".venv" / "pyvenv.cfg").get("home"))
        return 1 if errors else 0
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main())
