# Compact Step 0 — baseline-read-evidence

- 목적:
  - 구현 전 상태를 보존하고 승인 identity를 확인한다.
  - 요구사항↔step↔명령 매핑을 evidence로 남긴다.
  - verify-scope가 committed 계획 파일을 exact path 단위로 허용하게 한다.
  - product source는 쓰지 않는다.
- 예상 15분, hard timeout 30분, 선행 없음.
- 공통 선행조건: 설계 §C0.
- 허용 파일(exact): `tests/scripts/verify-scope.mjs`, `tests/specs/verify-scope-resume.spec.js`
- 금지:
  - product 4개 파일 수정
  - 이력 phase·설계 수정
  - prefix·glob 면제
  - 기존 verify-scope 면제·거부 사례 변경·삭제

## 작업
1. **메모리 검사(쓰기 0).** 아래를 모두 메모리에서 먼저 끝낸다. 하나라도 실패하면 아무것도 쓰지 않고 중단한다.
   - `git rev-parse HEAD`
   - `git status --porcelain=v1 -z --untracked-files=all`. 승인 범위 밖에 dirty path가 있으면 실패.
   - 허용 파일 12개의 SHA-256. 없는 파일은 null, symlink·non-regular면 실패.
   - 승인된 PLAN/REVIEW identity가 일치하는지(Harness launch 결과).
   - 설계 §C10의 이력 계획 committed 파일을 exact path 목록으로 계산한다.
2. **evidence 디렉터리 검사.** 다음을 모두 확인한다.
   - `tests/.tmp`와 `tests/.tmp/compact`가 symlink가 없는 regular directory chain이다. 없는 경로는 0700으로 만든다.
   - `git check-ignore -q tests/.tmp/compact/evidence-step0.json`가 성공한다.
3. **evidence 기록.** `tests/.tmp/compact/evidence-step0.json`에 쓴다.
   - `baselineHead`, status bytes(hex), 허용 파일 SHA 맵, 이력 계획 exact path 목록
   - 요구사항→소유 step→명령 매핑: 대응표 각 행 → C5 step → C3 명령
4. **verify-scope 면제 추가.** `tests/scripts/verify-scope.mjs`의 `HARNESS_OWNED_FILES`에 exact path만 추가한다.
   - 이 phase의 설계 문서
   - `phases/HOO-81-portfolio-redesign-compact-completion/index.json`, `step0.md`~`step7.md`
   - 1단계에서 계산한 이력 계획 exact path
5. **회귀 사례 추가.** `--self-test`와 `tests/specs/verify-scope-resume.spec.js`에 아래 사례를 추가한다.
   - 허용: 위 committed 경로
   - 위반:
     - staged·worktree 상태로 바뀐 `index.json`·`step0.md`·설계 문서
     - 열거되지 않은 `phases/HOO-81-portfolio-redesign-compact-completion/extra.md`
     - `phases/HOO-81-portfolio-redesign-compact-completion-x/a.json`
   - 기존 사례는 모두 유지한다.
6. **VS 결과 확인.**
   - `VS`가 이 범위 밖의 committed outside-scope를 보고하면 면제를 넓히지 않고 중단·보고한다.
   - `harness-uncommitted`가 runner의 실행 중 metadata 갱신 때문이면 중단·보고한다(설계 §C10).

## AC
- `T specs/verify-scope-resume.spec.js`
- `VSST`
- `VS` (stdout `verify-scope: OK`)
