# Color-resume Step 2 — coordinator-anchor-validate-overlap

- 존재 이유: 파일 유형별 fileRules 검사기와 모든 변경 줄의 owner 경계 검증을 만들고, 이를 쓰는 `validate-lane`·`check-overlap`을 확정한다(Astra v59 #2·#3).
- 시간: agent 예상 ≤20분. 근거: owner map 3종(CSS는 기존 `css-parse.js` 재사용), 유형 검사기 6종, 판정 함수 2개, 표 기반 spec. Harness hard timeout은 30분.
- 선행: 0~1
- 공통 규칙: 원 §9 + §C1·§C5·§C6
- gate: `XGATE 2`
- 허용(exact): `tests/helpers/parallel-wave-anchor.js`, `tests/specs/parallel-wave-anchor.spec.js`(둘 다 신규), `tests/scripts/parallel-wave.mjs`(dispatch 추가만)
- runtime: R0 + `tests/.tmp/parallel/**`
- 추가 금지: step 1 contract 변경, 사이트 파일 수정, 다른 파일 수정

## 작업
1. `XSNAP 2`
2. `parallel-wave-anchor.js`를 작성한다.
   - export: `ownerMapCss`, `ownerMapJs`, `ownerMapHtml`, `checkFileRule(rule, baseText, resultText, diff)`, `validateLane`, `checkOverlap`
   - 동작은 §C6 그대로다. step 1의 `WAVE1_CONTRACT`를 import한다.
3. CLI에 `validate-lane`과 `check-overlap`을 연결한다.
4. spec을 작성한다. synthetic repo를 쓴다.
   - 유형별 정상·범위 위반 사례
     - existing-css: 허용 selector에 비색 선언 → PASS, 금지 selector → FAIL, color 선언 → `fileRule:color-forbidden`
     - existing-js: 허용 fn → PASS, 금지 fn → FAIL
     - existing-html: 허용 subtree → PASS, 다른 id → FAIL
     - data-featured: 1·5·7 → PASS, 2 → FAIL, 다른 필드 변경 → FAIL, 삭제 → FAIL
     - new-test·new-helper·new-script: 정상 → PASS, base에 이미 존재 → FAIL, 필수 export 누락 → FAIL, forbidden 패턴 → FAIL
     - json-structured: 정상 → PASS, 키 순서 위반 → FAIL, 여분 키 → FAIL
   - cross-boundary FAIL: CSS selector block 2개에 걸친 hunk, JS `fn:a`에서 `fn:b` 머리까지 이어진 hunk, HTML `#about` subtree에서 `#career` 여는 tag까지 삭제
   - hunk 시작 줄은 허용 owner이고 이후 줄은 금지 owner인 경우 FAIL(시작 줄만으로 판정하지 않음을 확인)
   - validate-lane:
     - 정상 → PASS
     - 잘못된 base → `lane:bad-base`
     - 허용 밖 파일 → `lane:files`
     - checkpoint 누락 → `lane:checkpoints`
     - command 누락 또는 exit≠0 → `lane:commands`
     - result 변조 → FAIL
   - check-overlap: 같은 파일 disjoint hunk와 다른 owner → PASS, 교차 hunk → FAIL, 같은 owner → FAIL

## AC
- `T parallel-wave-anchor.spec.js parallel-wave.spec.js parallel-wave-contract.spec.js && FULL && VS && XGATE 2 tests/helpers/parallel-wave-anchor.js,tests/specs/parallel-wave-anchor.spec.js,tests/scripts/parallel-wave.mjs tests/helpers/parallel-wave-anchor.js,tests/specs/parallel-wave-anchor.spec.js`
