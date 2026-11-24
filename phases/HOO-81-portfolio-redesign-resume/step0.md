# Resume Step 0 — verify-scope-resume-compat

- 목적: §R3 — commit된 resume 설계(정확한 경로)와 `phases/HOO-81-portfolio-redesign-resume/**`를 verify-scope가 허용하도록 최소 변경, 무관 경로·미커밋 변경 거부 유지.
- 18분 / 선행 없음 / 공통 원 §9 + §R1 / gate `RGATE 0`
- 허용(exact): `tests/scripts/verify-scope.mjs`, `tests/specs/verify-scope-resume.spec.js`(신규)
- runtime: R0
- 추가 금지: 원 설계·`CLAUDE.md`·원 phase 수정, 다른 문서·경로 면제 추가, 접두 일치 완화, diff 인자 상수·기존 위반 판정 변경, 기존 self-test 사례 삭제

## 작업
1. `RSNAP 0`; `git log --format=%H HEAD`에 `4b2ec3b325f400edefca0fbcfb8ff83bf739ff89` 포함 확인(아니면 중단).
2. RED: `VS`가 resume 설계·resume phase 경로로 실패함을 확인(로그).
3. `verify-scope-resume.spec.js`(node, desktop-dark, 가짜 git 입력으로 `collectInput`·경로 판정 호출): 허용 — committed resume 설계, committed·worktree·untracked `phases/HOO-81-portfolio-redesign-resume/index.json`·`step0.md`; 위반 — worktree·staged 변경 resume 설계, committed `docs/superpowers/specs/other.md`, committed `docs/superpowers/specs/2026-11-24-portfolio-redesign-resume-design.md.bak`, committed·worktree `phases/OTHER/x.json`, committed `phases/HOO-81-portfolio-redesign-resume-x/a.json`, 미커밋 `.harness/policy.json`, worktree 원 설계, 미커밋 `CLAUDE.md`.
4. `verify-scope.mjs`: §R3 두 면제 추가, `--self-test`에 같은 사례 추가.

## AC
- `T verify-scope-resume.spec.js && W npm --prefix tests run verify-scope:selftest && FULL && VS && RGATE 0 tests/scripts/verify-scope.mjs,tests/specs/verify-scope-resume.spec.js tests/specs/verify-scope-resume.spec.js`(`VS` stdout `verify-scope: OK`)
