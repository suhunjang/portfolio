# Color-resume Step 0 — inherit-preflight

- 존재 이유: 승계 상태를 exact 확인한다. 또 새 phase 경로를 VS와 호환시키고 lane별 `PW_PORT`를 준비한다. 이게 없으면 VS가 실패하고, lane끼리 서버를 재사용해 결과가 오염된다.
- 시간: agent 예상 ≤20분, Harness hard timeout 30분. 선행 없음. 공통 규칙: 원 §9 + §C1. gate: `XGATE 0`.
- 허용(exact): `tests/scripts/verify-scope.mjs`, `tests/specs/verify-scope-resume.spec.js`, `tests/playwright.config.js`, `tests/specs/smoke.spec.js`
- runtime: R0
- 추가 금지: 이력 phase·설계·`CLAUDE.md`·collected·pairs 수정, 기존 verify-scope 거부 사례 삭제·완화, 기본 포트 4173 변경

## 작업
1. `XSNAP 0` → `PREFLIGHT`(§C3 블록 그대로). stdout이 `color-resume-preflight: OK`가 아니면 중단하고 보고한다.
2. verify-scope 면제 추가:
   - 하네스 소유 committed 면제에 정확히 `docs/superpowers/specs/2026-11-25-portfolio-redesign-color-resume-design.md`
   - 런타임 면제에 접두 정확 일치 `phases/HOO-81-portfolio-redesign-color-resume/`
   - `--self-test`와 `verify-scope-resume.spec.js`에 사례를 추가한다. 기존 사례는 모두 유지한다.
     - 허용: committed 새 설계, committed·worktree·untracked `phases/HOO-81-portfolio-redesign-color-resume/index.json`
     - 위반: worktree·staged로 변경된 새 설계, committed `…color-resume-design.md.bak`, committed `phases/HOO-81-portfolio-redesign-color-resume-x/a.json`
3. `tests/playwright.config.js`: env `PW_PORT`로 baseURL·webServer command·url의 포트를 정한다.
   - 값이 없으면 `4173`.
   - `^[0-9]+$`가 아니거나 1024~65535 밖이면 `playwright.config: bad PW_PORT`를 throw한다.
   - 그 밖의 설정은 그대로 둔다.
4. `smoke.spec.js`에 node 회귀 테스트 1개를 추가한다. subprocess로 config를 import해 확인한다.
   - env 없음 → baseURL `http://127.0.0.1:4173`
   - `PW_PORT=4180` → `:4180`
   - `PW_PORT=80` → throw

## AC
- `PREFLIGHT && T verify-scope-resume.spec.js smoke.spec.js && W npm --prefix tests run verify-scope:selftest && FULL && VS && XGATE 0 tests/scripts/verify-scope.mjs,tests/specs/verify-scope-resume.spec.js,tests/playwright.config.js,tests/specs/smoke.spec.js`
