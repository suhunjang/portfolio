# Compact Step 0 — baseline-read-evidence

- 목적:
  - 구현 전 상태를 보존한다.
  - 승인 identity와, 요구사항↔step↔명령 매핑을 확인한다.
  - verify-scope에 exact 면제를 추가한다.
  - product source는 쓰지 않는다.
- 예상 15분, hard timeout 30분. 선행 step 없음. 공통 선행조건은 §C0.
- 허용 파일(exact): `tests/scripts/verify-scope.mjs`, `tests/specs/verify-scope-resume.spec.js`
- runtime: `tests/.tmp/**`, `tests/test-results/**`, `tests/.npm-cache/**`
- 금지:
  - product 수정
  - 이력 phase·설계 수정
  - prefix·glob 면제
  - 기존 면제·거부 사례의 변경·삭제

## 작업
1. 아래 검사를 모두 메모리에서만 한다. 이 단계에서는 아무것도 쓰지 않는다.
   - `git rev-parse HEAD`
   - `git status --porcelain=v1 -z --untracked-files=all`: 승인 범위 밖 dirty path가 있으면 실패한다.
   - 허용 파일 12개의 SHA-256: 파일이 없으면 null로 기록한다. symlink이거나 일반 파일이 아니면 실패한다.
   - 승인 PLAN/REVIEW identity
   - §C10의 이력 계획 committed exact path 목록
2. `tests/.tmp`와 `tests/.tmp/compact`가 안전한 일반 디렉터리 체인인지 확인한다. 없으면 0700으로 만든다. 그다음 `git check-ignore -q tests/.tmp/compact/evidence-step0.json`이 성공하는지 확인한다.
3. `tests/.tmp/compact/evidence-step0.json`에 다음을 기록한다.
   - `baselineHead`, status(hex), 각 SHA, 이력 path
   - 대응표 행 → §C5 step → §C3 명령 매핑
4. §C10의 exact path를 `HARNESS_OWNED_FILES`에 추가한다.
5. `--self-test`와 spec에 사례를 추가한다. 기존 사례는 유지한다.
   - 허용되어야 하는 경우: committed exact path
   - 위반이어야 하는 경우:
     - staged 또는 worktree 상태의 `index.json`·`step0.md`·설계
     - 목록에 없는 `phases/HOO-81-portfolio-redesign-compact-completion/extra.md`
     - `phases/HOO-81-portfolio-redesign-compact-completion-x/a.json`
6. 다음 경우에는 중단하고 보고한다.
   - 목록 밖의 outside-scope가 나오는 경우
   - metadata 때문에 `harness-uncommitted`가 나오는 경우

## AC
- `T specs/verify-scope-resume.spec.js`
- `VSST`
- `VS`
