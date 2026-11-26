# Resume Step 25 — state-colors-fixture (원 step 48, §R10 분기)

- 목적: 원 §11.2 BASE 상태 색 fixture generator·fixture·`--check`(정상·변형 별도 test, 각 75초).
- 19분 / 선행 0~24 / 공통 원 §9 + §R1·§R10 / gate `RGATE_B 25`
- 허용(exact): `tests/scripts/make-state-colors.mjs`, `tests/fixtures/component-state-colors.json`, `tests/specs/state-colors.spec.js`(신규)
- 분기 R: `tests/scripts/make-state-colors.mjs,tests/fixtures/component-state-colors.json,tests/specs/state-colors.spec.js`
- runtime: R0 + 브라우저(`tests/.tmp/state-colors-<pid>/`)
- 추가 금지: 사이트 파일, helper·기존 spec, fixture 손편집, `measureStateSequence` 밖 측정, page 단위 테마 주입, 비-null 저장값 덮어쓰기, Git 쓰기, 정상·변형 한 test 묶기, 실행별 다른 timeout, start snapshot 수정·재생성, existing 분기에서 R 파일 수정·fixture 재생성

## 작업
1. `RSNAP 25` → `RBRANCH 25 tests/scripts/make-state-colors.mjs,tests/fixtures/component-state-colors.json,tests/specs/state-colors.spec.js`.
   - `existing`: 작업 2~4 생략, 쓰기 없는 AC 전체 실행(`--check`는 쓰기 없음) → 통과 시 `resume step25: no-op`, 실패 시 tracked 불변 중단·재계획.
   - `new`: 아래 진행. `branch-mixed`면 중단.
2. generator: 원 step 48 작업 2 그대로(테마별 context 1280×800, `route('http://base.invalid/**')`로 BASE 파일, BASE `THEME_KEY` 정규식 추출, `context.addInitScript` 1회 null-only, `measureStateSequence`로 `hero-cta-btn-{i}`·`grid-card-0`·`grid-card-1`, color·backgroundColor·borderColor만, 키 정렬·2칸·끝 개행 1, `--check [--fixture]` → `state-colors: OK`/`state-colors: mismatch`, 그 밖 인자 exit 2).
3. 생성 `W node tests/scripts/make-state-colors.mjs`.
4. spec(node, desktop-dark; 독립 test 4개): `schema`, `serialization`, `check-ok`(첫 줄 `test.setTimeout(75000)`, subprocess 60000ms), `check-mismatch`(첫 줄 `test.setTimeout(75000)`, 사본 변경·subprocess 60000ms·원본 불변·finally 삭제) — 원 step 48 작업 4 그대로.

## AC
- `W node tests/scripts/make-state-colors.mjs --check && T state-colors.spec.js state-sequence.spec.js && FULL && VS && RGATE_B 25 tests/scripts/make-state-colors.mjs,tests/fixtures/component-state-colors.json,tests/specs/state-colors.spec.js tests/scripts/make-state-colors.mjs,tests/fixtures/component-state-colors.json,tests/specs/state-colors.spec.js`(첫 명령 `state-colors: OK`)
