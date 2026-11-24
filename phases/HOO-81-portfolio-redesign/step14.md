# Step 14 — design-guard-markup

- 목적: markup 판정, Git 입력 수집, 실저장소 통합 guard(이후 모든 step의 전체 테스트에서 위반 0 요구).
- 예상 16분 / 선행 0~13 / 공통 절차 설계 §15 / 종료 gate: CLI
- read-first: 설계 §16.3, §16.4(step 14); `tests/helpers/design-guard-css.js`(import만)
- tracked 허용(exact): `tests/helpers/design-guard.js`(신규), `tests/specs/design-guard.spec.js`(신규)
- runtime: R0
- 금지: §15.7, 사이트 파일, `design-guard-css.js` 수정, Git 상태 변경

## 작업

1. 시작 snapshot: `python3 -I tests/scripts/start-snapshot.py step14`
2. `design-guard.js`: `checkMarkupPatch(patch, kind)`, `collectGuardInput({ git = runGit, fs })`, `runGuard(input)`(설계 §16.4).
3. `design-guard.spec.js`(node 전용, desktop-dark만)
   - 단위: 추가 줄 `<img`, `<svg`, `<i class`, `style="color:x"`, `el.style.color = …` → `markup-asset:{kind}:{n}`; 삭제 줄·문맥 줄은 무시; 정상 patch `[]`
   - 가짜 git으로 `collectGuardInput` 호출 인자 기록: `show <BASE>:css/style.css`, `show <BASE>:css/themes.css`, `diff --no-renames --unified=0 <BASE> -- index.html`, `-- js/main.js`만, 변경 명령 없음
   - 실저장소: `runGuard(await collectGuardInput())` → `[]`

## AC

- `sh tests/scripts/with-env.sh npm --prefix tests test -- design-guard.spec.js design-guard-css.spec.js && sh tests/scripts/with-env.sh npm --prefix tests test && sh tests/scripts/with-env.sh node tests/scripts/scope-snapshot.mjs --check tests/.tmp/start-snapshot-step14.json --allow tests/helpers/design-guard.js,tests/specs/design-guard.spec.js --require-absent tests/helpers/design-guard.js,tests/specs/design-guard.spec.js` → exit 0
