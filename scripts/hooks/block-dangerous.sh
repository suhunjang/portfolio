#!/bin/bash
# Block-Dangerous Hook — PreToolUse[Bash]
# stdin JSON의 tool_input.command에서 위험 명령을 차단한다.
# claude/codex 공통 (Bash tool은 양쪽 다 tool_input.command).
# 인터프리터: hook 자신의 위치(BASH_SOURCE) 기준 repo-local .venv. 없으면 python3.
# bare `python`은 macOS에 없을 수 있다 — 없으면 아래 파싱이 실패한다.
HOOK_HERE=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
PY="$HOOK_HERE/../../.venv/bin/python"
[ -x "$PY" ] || PY=python3
INPUT=$(cat)

# ── command 추출: 반드시 JSON 파서로 한다 ────────────────────────────────────
# ⚠ 예전엔 grep -o '"command"..."[^"]*"' 로 뽑았는데, 값 안에 큰따옴표가 하나만
# 있어도 거기서 잘려 **뒤쪽 위험 패턴이 검사되지 않고 통과했다**. 즉
# `git commit -m "msg" && rm -rf /` 가 그대로 실행됐다(2026-07-31 실측).
# 정규식으로 JSON을 파싱하려던 것이 근본 원인이라 패턴을 땜질하지 않고
# 실제 파서로 교체했다. 여기 되돌리지 말 것.
#
# 파싱 실패는 **fail-closed(exit 2)** 다 — 조용히 통과시키면 가드가 무력화된
# 사실을 아무도 모른다. 단, JSON은 정상인데 command 키가 없는 경우(다른 tool)는
# 차단 대상이 아니므로 빈 값으로 두고 아래에서 통과시킨다.
CMD=$(printf '%s' "$INPUT" | "$PY" -c '
import json, sys
try:
    d = json.load(sys.stdin)
except Exception:
    sys.exit(3)
ti = d.get("tool_input") or {}
c = ti.get("command")
sys.stdout.write(c if isinstance(c, str) else "")
' 2>/dev/null)
PARSE_RC=$?

if [ "$PARSE_RC" -ne 0 ]; then
  echo 'BLOCKED: hook 입력(JSON)을 해석할 수 없습니다. 안전을 위해 차단합니다.' >&2
  exit 2
fi

if [ -z "$CMD" ]; then
  exit 0
fi

if printf '%s' "$CMD" | grep -qE 'rm[[:space:]]+-rf|git[[:space:]]+push[[:space:]]+--force|git[[:space:]]+reset[[:space:]]+--hard|DROP[[:space:]]+TABLE'; then
  echo 'BLOCKED: 위험한 명령어가 감지되었습니다.' >&2
  exit 2
fi
exit 0
