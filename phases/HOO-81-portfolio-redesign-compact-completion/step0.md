# Compact Step 0 — baseline-read-evidence

- 목적:
  - 구현 전 상태를 보존한다.
  - 승인 identity와 요구사항↔step↔명령 매핑을 기록한다.
  - verify-scope에 exact 면제를 추가한다.
  - product source는 쓰지 않는다.
- 예상 15분, hard timeout 30분. 선행 step 없음. 공통 선행조건은 §C0.
- 허용 파일(exact): `tests/scripts/verify-scope.mjs`, `tests/specs/verify-scope-resume.spec.js`
- runtime: `tests/.tmp/**`, `tests/test-results/**`, `tests/.npm-cache/**`
- 금지:
  - product 파일 수정
  - 이력 phase·설계 문서 수정
  - prefix·glob 면제 추가
  - 기존 면제·거부 사례의 변경이나 삭제

## 작업
1. 메모리에서만 검사한다(파일 쓰기 0).
   - `git rev-parse HEAD`
   - `git status --porcelain=v1 -z --untracked-files=all`: 승인 범위 밖의 dirty path가 있으면 실패
   - 허용 파일 12개의 SHA-256: 파일이 없으면 null, symlink나 non-regular면 실패
   - 승인 PLAN/REVIEW identity
   - §C10 이력 계획의 committed exact path 목록
2. 기록 위치를 확인한다.
   - `tests/.tmp`와 `tests/.tmp/compact`가 안전한 regular directory chain인지 확인한다. 없으면 0700으로 만든다.
   - `git check-ignore -q tests/.tmp/compact/evidence-step0.json`이 성공해야 한다.
3. `tests/.tmp/compact/evidence-step0.json`에 다음을 기록한다.
   - `baselineHead`, status(hex), SHA, 이력 path
   - 대응표 각 행 → §C5의 step → §C3의 명령 매핑
4. §C10에 정한 exact path를 `HARNESS_OWNED_FILES`에 추가한다.
5. `--self-test`와 `tests/specs/verify-scope-resume.spec.js`에 사례를 추가한다.
   - 허용 사례: committed exact path
   - 위반 사례:
     - staged나 worktree 상태의 `index.json`, `step0.md`, 설계 문서
     - 목록에 없는 `phases/HOO-81-portfolio-redesign-compact-completion/extra.md`
     - `phases/HOO-81-portfolio-redesign-compact-completion-x/a.json`
   - 기존 사례는 모두 유지한다.
6. `VS`가 위 목록 밖의 경로를 outside-scope로 보고하거나, metadata 때문에 `harness-uncommitted`를 보고하면 중단하고 보고한다.

## AC
- `T specs/verify-scope-resume.spec.js`
- `VSST`
- `VS`
