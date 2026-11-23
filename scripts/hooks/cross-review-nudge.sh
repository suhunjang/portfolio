#!/bin/bash
# Cross-Review Nudge — Stop hook
# 마지막 /cross-review 이후 코드가 바뀌었으면 알린다.
# 차단하지 않는다. 어떤 상황에서도 exit 0 — 알림이 작업을 막으면 안 된다.

STATE=".claude/.cross-review-state"

# 지문 스크립트는 이 hook 옆에 있다. 검사 대상 repo($ROOT)가 아니라 **hook 자신의
# 위치**를 기준으로 찾아야 한다 — 다른 repo에서 돌 때 $ROOT/scripts/... 는 없다.
HERE=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
CR_PY="$HERE/../cross_review.py"
PY="$HERE/../../.venv/bin/python"
[ -x "$PY" ] || PY=python3

# git repo가 아니면 조용히 통과
ROOT=$(git rev-parse --show-toplevel 2>/dev/null) || exit 0
[ -n "$ROOT" ] || exit 0
cd "$ROOT" 2>/dev/null || exit 0

# state가 없으면 조용 (첫 도입 시 시끄럽지 않게)
[ -f "$STATE" ] || exit 0

# 지문 계산은 cross_review.py에 **위임한다**. 여기서 sha256sum으로 다시
# 구현하면 안 된다 — bash는 바이트를, Python은 디코드된 문자를 해시하므로
# 한글 주석이 든 diff에서 값이 갈린다(실측으로 겪었다). 지문을 쓰는 쪽과
# 읽는 쪽이 같은 코드를 쓰는 것이 유일하게 안전한 방법이다.
CURRENT=$("$PY" "$CR_PY" --fingerprint 2>/dev/null) || exit 0
[ -n "$CURRENT" ] || exit 0

SAVED=$(head -n 1 "$STATE" 2>/dev/null)

if [ "$CURRENT" != "$SAVED" ]; then
  echo "⚠ /cross-review 안 돌린 변경이 있습니다"
fi
exit 0
