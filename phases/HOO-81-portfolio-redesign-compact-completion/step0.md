# Compact Step 0 — baseline-read-evidence

- 목적: 구현 전 상태를 보존하고, 승인 identity와 요구사항↔step↔명령 매핑을 확인한다. verify-scope에는 exact 면제만 추가한다. product source는 쓰지 않는다.
- 예상 15분, hard timeout 30분. 선행 없음. 공통 선행조건 §C0.
- 허용 파일(exact): `tests/scripts/verify-scope.mjs`, `tests/specs/verify-scope-resume.spec.js`
- runtime: `tests/.tmp/**`, `tests/test-results/**`, `tests/.npm-cache/**`
- 금지: product 수정, 이력 phase·설계 수정, prefix·glob 면제, 기존 면제·거부 사례의 변경 또는 삭제

## 작업
1. 아래 검사를 메모리에서만 한다(파일 쓰기 0).
   - `git rev-parse HEAD`
   - `git status --porcelain=v1 -z --untracked-files=all`: 승인 범위 밖에 dirty path가 있으면 실패
   - 허용 파일 12개의 SHA-256: 없는 파일은 null, symlink이거나 non-regular이면 실패
   - 승인 PLAN/REVIEW identity 확인
   - §C10 이력 committed exact path 목록
2. `tests/.tmp`와 `tests/.tmp/compact`가 안전한 regular directory chain인지 확인한다. 없으면 0700으로 만든다. 그 뒤 `git check-ignore -q tests/.tmp/compact/evidence-step0.json`이 성공해야 한다.
3. `tests/.tmp/compact/evidence-step0.json`에 다음을 기록한다.
   - `baselineHead`
   - status(hex)
   - 허용 파일 SHA
   - 이력 path 목록
   - 대응표 행 → §C5 step → §C3 명령 매핑
4. §C10의 exact path를 `HARNESS_OWNED_FILES`에 추가한다.
5. `--self-test`와 spec에 아래 사례를 추가한다. 기존 사례는 유지한다.
   - 허용: committed exact path
   - 위반:
     - staged·worktree 상태의 `index.json`·`step0.md`·설계 문서
     - 목록에 없는 `phases/HOO-81-portfolio-redesign-compact-completion/extra.md`
     - `phases/HOO-81-portfolio-redesign-compact-completion-x/a.json`
6. 목록 밖 outside-scope가 나오거나, metadata 때문에 `harness-uncommitted`가 나오면 중단하고 보고한다.

## AC
- `T specs/verify-scope-resume.spec.js`
- `VSST`
- `VS`
