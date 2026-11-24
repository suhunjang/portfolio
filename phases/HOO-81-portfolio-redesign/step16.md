# Step 16 — design-guard-integration

- 목적: markup 판정, Git 입력 수집, 실저장소 통합 guard(이후 모든 step의 전체 테스트에서 위반 0).
- 예상 15분 / 선행 0~15 / 공통 절차 설계 §15 / 종료 gate: CLI
- read-first: 설계 §16.3, §16.4(step 16); `tests/helpers/design-guard-css.js`(import만)
- tracked 허용(exact): `tests/helpers/design-guard.js`(신규), `tests/specs/design-guard.spec.js`(신규)
- runtime: R0
- 금지: §15.7, 사이트 파일, step 13~15 helper·spec 수정, Git 상태 변경

## 작업

1. 시작 snapshot: `python3 -I tests/scripts/start-snapshot.py step16`
2. `design-guard.js`: `checkMarkupPatch(patch, kind)`, `collectGuardInput({ git = runGit, fs })`, `runGuard(input)`.
3. `design-guard.spec.js`(node 전용, desktop-dark만)
   - 단위: 추가 줄 `<img src="a.png">`·`<svg>`·`<i class="x">`·`style="color:red"`·`el.style.color = x` → `markup-asset:{kind}:{n}`(n은 patch 안 줄 번호); 삭제 줄·문맥·헤더 줄 무시; 정상 patch `[]`
   - 가짜 git 호출 기록: `show <BASE>:css/style.css`, `show <BASE>:css/themes.css`, `diff --no-renames --unified=0 <BASE> -- index.html`, 같은 인자 `-- js/main.js`만 호출되고 변경 명령 없음; fs는 `css/style.css`·`css/themes.css` 읽기만
   - 실저장소: `runGuard(await collectGuardInput())` → `[]`

## AC

- `sh tests/scripts/with-env.sh npm --prefix tests test -- design-guard.spec.js design-guard-css.spec.js design-guard-color.spec.js css-parse.spec.js && sh tests/scripts/with-env.sh npm --prefix tests test && sh tests/scripts/with-env.sh node tests/scripts/scope-snapshot.mjs --check tests/.tmp/start-snapshot-step16.json --allow tests/helpers/design-guard.js,tests/specs/design-guard.spec.js --require-absent tests/helpers/design-guard.js,tests/specs/design-guard.spec.js` → exit 0
