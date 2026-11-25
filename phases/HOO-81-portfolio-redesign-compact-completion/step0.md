# Compact Step 0 — baseline-evidence

- 목적:
  - 구현 전에 상태를 보존하고 승인 identity를 확인한다.
  - verify-scope가 이미 commit된 계획 경로를 허용하도록 exact 경로만 추가한다.
  - product source는 쓰지 않는다.
- 예상 10분, hard timeout 30분. 선행 없음.
- 허용 파일(exact): `tests/scripts/verify-scope.mjs`, `tests/specs/verify-scope-resume.spec.js`
- 금지: product 4개 파일 수정, 이력 phase·설계 문서 수정, 기존 verify-scope 거부 사례 삭제·완화, 면제를 prefix나 glob으로 넓히는 것

## 작업
1. 아래 상태를 runtime 파일 `tests/.tmp/compact/evidence-step0.json`에 기록한다. 이 파일은 tracked가 아니다.
   - `git rev-parse HEAD`
   - `git status --porcelain=v1 -z --untracked-files=all`
   - 허용 파일 12개 각각의 SHA-256. 없는 파일은 `null`로 적는다.
2. 다음 중 하나라도 해당하면 아무것도 쓰지 않고 중단한다.
   - 승인 범위 밖의 dirty path가 있다.
   - 허용 경로에 symlink나 non-regular path가 있다.
   - 승인된 PLAN/REVIEW identity가 일치하지 않는다(Harness launch가 확인한다).
3. `tests/scripts/verify-scope.mjs`에 exact 면제만 추가한다.
   - `HARNESS_OWNED_FILES`(committed 면제)에 다음 두 파일을 추가한다.
     - `docs/superpowers/specs/2026-11-26-portfolio-redesign-compact-completion-design.md`
     - `docs/superpowers/specs/2026-11-25-portfolio-redesign-color-resume-design.md`
   - `RUNTIME_EXEMPT_PREFIXES`에 다음 세 prefix를 접두 정확 일치로 추가한다.
     - `phases/HOO-81-portfolio-redesign-color-resume/`
     - `phases/HOO-81-portfolio-redesign-official-runner-resume/`
     - `phases/HOO-81-portfolio-redesign-compact-completion/`
   - `--self-test`와 `tests/specs/verify-scope-resume.spec.js`에 사례를 추가한다.
     - 허용: 위 경로들의 committed 파일
     - 위반: `phases/HOO-81-portfolio-redesign-compact-completion-x/a.json`, `.bak` 설계 파일, worktree·staged 상태로 바뀐 설계 문서
     - 기존 사례는 모두 그대로 둔다.
4. `VS`를 실행했을 때 위에 없는 committed 경로가 outside-scope로 나오면, 면제를 더 넓히지 않고 중단·보고한다.

## AC
- `T specs/verify-scope-resume.spec.js`
- `VSST`
- `VS` — stdout이 `verify-scope: OK`여야 한다.
