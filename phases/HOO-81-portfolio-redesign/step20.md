# Step 20 — design-guard-integration

- 목적: 설계 §11.4 step 20 markup·입력 수집·실저장소 guard(이후 `FULL`에서 위반 0).
- 15분 / 선행 0~19 / 공통 §9 / gate GATE
- 허용(exact): `tests/helpers/design-guard.js`, `tests/specs/design-guard.spec.js`(신규)
- runtime: R0
- 추가 금지: 사이트 파일, step 13~19 수정, Git 상태 변경

## 작업
1. `SNAP 20` → RED → 구현 → GREEN.
2. spec: 추가 줄 `<img src="a.png">`·`<svg>`·`<i class="x">`·`style="color:red"`·`el.style.color = x` → `markup-asset:{kind}:{n}`; 삭제·문맥·헤더 줄 무시; 정상 `[]`; 가짜 git 기록이 `show <BASE>:css/style.css`, `show <BASE>:css/themes.css`, `diff --no-renames --unified=0 <BASE> -- index.html`, `-- js/main.js`뿐, fs는 두 CSS 읽기만; 실저장소 `runGuard(await collectGuardInput())` → `[]`.

## AC
- `T GS && FULL && GATE 20 tests/helpers/design-guard.js,tests/specs/design-guard.spec.js tests/helpers/design-guard.js,tests/specs/design-guard.spec.js`
