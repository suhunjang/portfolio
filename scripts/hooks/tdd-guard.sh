#!/bin/bash
# TDD Guard Hook — PreToolUse[Edit|Write]
# 구현 코드를 작성하려 할 때, 해당 모듈의 테스트 파일이 먼저 존재하는지 체크.
# 테스트 없이 구현 코드를 작성하려 하면 차단.

# 인터프리터: hook 자신의 위치(BASH_SOURCE) 기준 repo-local .venv. 없으면 python3.
# bare `python`은 macOS에 없을 수 있다 — 없으면 아래 파싱이 실패한다.
HOOK_HERE=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
PY="$HOOK_HERE/../../.venv/bin/python"
[ -x "$PY" ] || PY=python3
INPUT=$(cat)

# ── file_path / command 추출: 반드시 JSON 파서로 한다 ────────────────────────
# ⚠ 예전엔 grep -o '"file_path"..."[^"]*"' 로 뽑고 sed로 이스케이프를 되돌렸다.
# 값 안에 큰따옴표가 하나만 있어도 거기서 잘려 **엉뚱한 경로를 검사하거나
# 빈 값이 되어 가드가 통째로 건너뛰어졌다**. block-dangerous.sh에서 같은
# 정규식 파싱이 critical 구멍으로 확인돼(2026-07-31) 여기도 함께 교체했다.
# 파서는 \n·\\·\/ 이스케이프를 알아서 처리하므로 sed 복원도 필요 없다.
#
# 이 hook은 파싱 실패 시 **통과(exit 0)** 다 — block-dangerous.sh와 의도적으로
# 다르다. 저기는 실패하면 인프라가 깨지지만, 여기는 최악이 "TDD 가드 누락"이라
# 편집 자체를 막아 작업을 멈추게 하는 편이 더 해롭다.
# 두 필드를 한 번에 뽑아 구분자로 잇고 싶겠지만 하지 말 것 — bash 명령치환은
# NUL 바이트를 버려서 두 번째 필드가 조용히 사라진다(실측: apply_patch 가드가
# 통째로 무력화됐다). 필드마다 파서를 한 번씩 부르는 편이 안전하다.
_extract() {
  printf '%s' "$INPUT" | "$PY" -c '
import json, sys
try:
    d = json.load(sys.stdin)
except Exception:
    sys.exit(0)
ti = d.get("tool_input") or {}
v = ti.get(sys.argv[1])
sys.stdout.write(v if isinstance(v, str) else "")
' "$1" 2>/dev/null
}
FILE_PATH=$(_extract file_path)
# Windows 경로(C:\...\page.tsx)도 아래 '*/page.tsx' 같은 예외 패턴에 걸리도록 구분자를 '/'로 맞춘다
FILE_PATH=${FILE_PATH//\\//}
RAW_CMD=$(_extract command)

# ── apply_patch 처리: file_path가 없고 command가 patch envelope면 대상 파일 추출 ──
if [ -z "$FILE_PATH" ]; then
  CMD="$RAW_CMD"

  # apply_patch가 아니면(패치 마커 없음) 통과 (Bash 등 다른 tool)
  if ! printf '%s' "$CMD" | grep -q '\*\*\* \(Begin Patch\|Add File:\|Update File:\|Delete File:\|Move to:\)'; then
    exit 0
  fi

  # 대상 파일 추출: Add/Update는 그 경로, Move to는 새 경로로 대체(직전 Update를 덮음)
  TARGETS=$(printf '%s' "$CMD" | grep -oE '\*\*\* (Add|Update) File: .*|\*\*\* Move to: .*' \
            | sed -E 's/\*\*\* (Add|Update) File: //; s/\*\*\* Move to: //' \
            | sed -E 's/[[:space:]]+$//')

  # fail-closed: 패치인데 대상 0개면 deny
  if [ -z "$TARGETS" ]; then
    # Delete만 있는 패치는 예외(allow)
    if printf '%s' "$CMD" | grep -q '\*\*\* Delete File:' && \
       ! printf '%s' "$CMD" | grep -qE '\*\*\* (Add|Update) File:|\*\*\* Move to:'; then
      exit 0
    fi
    echo '{"hookSpecificOutput": {"hookEventName": "PreToolUse", "permissionDecision": "deny", "permissionDecisionReason": "TDD GUARD: apply_patch에서 대상 파일을 추출하지 못했습니다(fail-closed)."}}'
    exit 0
  fi

  # 각 대상에 대해 TDD 검사. 경로 이탈(..)이면 deny.
  DENIED=""
  while IFS= read -r TP; do
    [ -z "$TP" ] && continue
    case "$TP" in
      *..*) DENIED="$TP (경로 이탈)"; break ;;
    esac
    # 예외 확장자/경로는 skip
    case "$TP" in
      *test*|*spec*|*.test.*|*.spec.*|*__tests__*) continue ;;
      *.json|*.css|*.scss|*.md|*.yml|*.yaml|*.env*|*.config.*|*tailwind*|*postcss*|*next.config*|*tsconfig*) continue ;;
      */types/*|*/types.ts|*/types.d.ts) continue ;;
      */layout.tsx|*/layout.ts|*/page.tsx|*/page.ts|*/loading.tsx|*/error.tsx|*/not-found.tsx|*/globals.css) continue ;;
    esac
    case "$TP" in
      *.ts|*.tsx|*.js|*.jsx)
        D=$(dirname "$TP"); B=$(basename "$TP" | sed -E 's/\.(ts|tsx|js|jsx)$//')
        FOUND=false
        for E in ts tsx js jsx; do
          if [ -f "${D}/${B}.test.${E}" ] || [ -f "${D}/${B}.spec.${E}" ] || \
             [ -f "${D}/__tests__/${B}.test.${E}" ]; then FOUND=true; break; fi
        done
        [ "$FOUND" = false ] && { DENIED="$B"; break; }
        ;;
    esac
  done <<EOF2
$TARGETS
EOF2

  if [ -n "$DENIED" ]; then
    echo "{\"hookSpecificOutput\": {\"hookEventName\": \"PreToolUse\", \"permissionDecision\": \"deny\", \"permissionDecisionReason\": \"TDD GUARD: '${DENIED}'에 대한 테스트 파일이 없습니다. 테스트를 먼저 작성하세요.\"}}"
  fi
  exit 0
fi

# 테스트 파일 자체를 수정하는 건 허용
case "$FILE_PATH" in
  *test*|*spec*|*.test.*|*.spec.*|*__tests__*)
    exit 0
    ;;
esac

# 설정/타입/스타일 파일은 테스트 불필요 — 허용
case "$FILE_PATH" in
  *.json|*.css|*.scss|*.md|*.yml|*.yaml|*.env*|*.config.*|*tailwind*|*postcss*|*next.config*|*tsconfig*)
    exit 0
    ;;
esac

# types/ 폴더는 테스트 불필요 — 허용
case "$FILE_PATH" in
  */types/*|*/types.ts|*/types.d.ts)
    exit 0
    ;;
esac

# Next.js 프레임워크 파일은 허용 (layout, page, loading, error, not-found, global styles)
case "$FILE_PATH" in
  */layout.tsx|*/layout.ts|*/page.tsx|*/page.ts|*/loading.tsx|*/error.tsx|*/not-found.tsx|*/globals.css)
    exit 0
    ;;
esac

# lib/ 또는 소스 파일이면 테스트 파일 존재 여부 확인
case "$FILE_PATH" in
  *.ts|*.tsx|*.js|*.jsx)
    # 파일명 추출
    DIR=$(dirname "$FILE_PATH")
    BASENAME=$(basename "$FILE_PATH" | sed -E 's/\.(ts|tsx|js|jsx)$//')

    # 테스트 파일 후보 경로들
    TEST_FOUND=false

    # 같은 폴더에 .test 파일
    for EXT in ts tsx js jsx; do
      if [ -f "${DIR}/${BASENAME}.test.${EXT}" ] || [ -f "${DIR}/${BASENAME}.spec.${EXT}" ]; then
        TEST_FOUND=true
        break
      fi
    done

    # __tests__ 폴더
    if [ "$TEST_FOUND" = false ]; then
      PARENT=$(dirname "$DIR")
      for EXT in ts tsx js jsx; do
        if [ -f "${PARENT}/__tests__/${BASENAME}.test.${EXT}" ] || [ -f "${DIR}/__tests__/${BASENAME}.test.${EXT}" ]; then
          TEST_FOUND=true
          break
        fi
      done
    fi

    # src/__tests__/ 루트 테스트 폴더
    if [ "$TEST_FOUND" = false ]; then
      PROJECT_ROOT=$(git rev-parse --show-toplevel 2>/dev/null || echo ".")
      for EXT in ts tsx js jsx; do
        if [ -f "${PROJECT_ROOT}/src/__tests__/${BASENAME}.test.${EXT}" ]; then
          TEST_FOUND=true
          break
        fi
      done
    fi

    if [ "$TEST_FOUND" = false ]; then
      cat << EOF
{
  "hookSpecificOutput": {
    "hookEventName": "PreToolUse",
    "permissionDecision": "deny",
    "permissionDecisionReason": "TDD GUARD: '${BASENAME}'에 대한 테스트 파일이 존재하지 않습니다. 구현 코드를 작성하기 전에 테스트를 먼저 작성하세요. (테스트 파일 예: ${BASENAME}.test.ts)"
  }
}
EOF
    fi
    ;;
esac

exit 0
