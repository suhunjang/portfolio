# HOO-81 compact completion 설계 (compact-product-scope-v87)

- phase: `HOO-81-portfolio-redesign-compact-completion`(step 0~7)
- 근거:
  - 대표 결정 `compact-product-scope-v87`
  - 정본 정책 `/Users/hoon/.hermes/company/operations/product-task-scope-control-policy.md`
  - 전환 계획 `/Users/hoon/.hermes/profiles/ryan/cache/scratch/HOO-103-product-scope-control-and-compact-plan.md`(§4 승인 요구사항↔검증 대응표가 제품 정본)
- 유효하며 수정하지 않는 문서:
  - 원 설계 `docs/superpowers/specs/2026-11-23-portfolio-layout-redesign-design.md`(§n)
  - resume 설계 `docs/superpowers/specs/2026-11-24-portfolio-redesign-resume-design.md`
- 감사 증거로 보존하고 확장하지 않는 것:
  - phase `HOO-81-portfolio-redesign-official-runner-resume`, commit `3887bec96f0d4bcdd21519d2cb443b3cdd3352d9`
  - color-resume 계획
  - 원 phase step 0~39, resume phase step 0~16의 산출물(재실행하지 않고 현재 HEAD에서 검증만 한다)
- 충돌하면 repository `CLAUDE.md`와 회사 승인 정책이 우선하고, 실행을 중단한다.

## C1. 제품 계약 (불변)

- `js/data.js`: PROJECTS 1·5·7에 `featured: true,` 정확히 3줄만 추가한다(v70b). 다른 줄·필드·순서는 바꾸지 않는다.
- 대표 카드:
  - `#heroStats` 다음 형제로 `#heroFeatured`(role `region`, aria-label `대표 프로젝트`)를 둔다.
  - 카드 3개는 각각 `button[type=button]`(data-project 1·5·7)이고, 안에 `span`이 정확히 2개다.
  - nested interactive는 0이다.
  - click과 Enter로 모달이 열리고, 닫으면(버튼·backdrop·Esc) trigger에 focus가 돌아온다.
- 보존:
  - 색, 서체 asset·weight, 문구, 수치
  - FINAL IA: hero→Career→Projects→Strengths→About→Contact, 6개 섹션
  - PROJECTS 13개와 그 순서, 이미지·아이콘
- `css/themes.css`는 읽기 전용이다.
- 색 변경 규칙:
  - 확인된 color-contrast 결함을 고칠 때만, 기존 color token(`var(--x)`)으로 최소한만 바꾼다.
  - 새 palette·gradient·glow·리터럴 색은 쓰지 않는다.
- 레이아웃: 375/768/1280에서 가로 스크롤이 없어야 하고, 1280×800 첫 화면 AC(원 §3)를 지킨다. print는 보존한다(원 §7).
- 기능 회귀가 없어야 한다: theme, menu, typing, reduced-motion, modal, lightbox, focus trap.
- 현재 DOM의 axe 10개 시나리오에서 위반은 0이어야 한다.

## C2. 범위 금지

- 범용 declaration mapper, BASE influence framework, transaction framework, custom coordinator, 새 Harness 공통 기능, 새 범용 검증 파이프라인은 만들지 않는다.
- 대응표에 없는 새 요구는 자동으로 흡수하지 않는다.
  - 실제 blocker이면 계획 변경과 재승인을 요청한다.
  - 비차단 항목은 별도 이슈로 추적한다.
- 다음 행위를 금지한다:
  - `git reset/restore/checkout/clean`, 광범위 삭제
  - main 직접 변경, merge, deploy
  - 승인 없는 push·PR
- git checkout·add·commit은 Harness runner만 한다.

## C3. 약어 (argv)

- `W` = `sh tests/scripts/with-env.sh`
- `T <specs>` = `sh tests/scripts/with-env.sh npm --prefix tests test -- <specs>`
- `FULL` = `sh tests/scripts/with-env.sh npm --prefix tests test`
- `VS` = `sh tests/scripts/with-env.sh npm --prefix tests run verify-scope`
- `VSST` = `sh tests/scripts/with-env.sh npm --prefix tests run verify-scope:selftest`
- `DI` = `python3 -I tests/scripts/design-intake-check.py`
- `GS` = spec 목록 `specs/design-guard.spec.js specs/design-guard-css.spec.js specs/design-guard-font.spec.js specs/design-guard-color.spec.js specs/design-guard-color-rules.spec.js specs/design-guard-color-pairs.spec.js specs/css-parse.spec.js specs/color-vocab.spec.js`
- `AXE0`(current-zero chain): 아래 5개 명령을 순서대로 실행한다. baseline이 pending인지 check인지는 완료 증거로 인정하지 않는다. 현재 수집 결과가 정확히 빈 배열이어야 한다.
  1. `T specs/axe-helper.spec.js`
  2. `sh tests/scripts/with-env.sh node tests/helpers/axe.js --reset`
  3. `env AXE_COLLECT=1 sh tests/scripts/with-env.sh npm --prefix tests test -- specs/axe.spec.js`
  4. `sh tests/scripts/with-env.sh node tests/helpers/axe.js --merge --out tests/.tmp/axe-current.json`
  5. `sh tests/scripts/with-env.sh node tests/helpers/axe.js --assert-no-violations --collected tests/.tmp/axe-current.json`
- `SPEC_GATE`: 테스트를 실행하기 전에 아래 4개가 모두 regular file이고 symlink가 아님을 확인한다. 하나라도 아니면 테스트를 실행하지 않고, 해당 파일을 만드는 step의 blocker로 종료한다. Playwright filter가 일부 통과한 것은 누락된 spec을 대신하는 증거가 아니다.
  - `tests/specs/featured.spec.js`, `tests/specs/focus-modal.spec.js`, `tests/specs/screenshots.spec.js`, `tests/specs/final-contract.spec.js`
  - 명령: `python3 -I -c "import os,stat,sys; P=['tests/specs/featured.spec.js','tests/specs/focus-modal.spec.js','tests/specs/screenshots.spec.js','tests/specs/final-contract.spec.js']; bad=[p for p in P if not os.path.lexists(p) or not stat.S_ISREG(os.lstat(p).st_mode)]; sys.exit('spec-gate: '+','.join(bad)) if bad else print('spec-gate: OK 4')"`

## C4. 허용 파일 (exact, index와 동일)

- product: `index.html`, `css/style.css`, `js/main.js`, `js/data.js`
- 검증 기존 파일(최소 수정): `tests/scripts/verify-scope.mjs`, `tests/specs/verify-scope-resume.spec.js`, `tests/helpers/design-guard-color-rules.js`, `tests/specs/design-guard-color-rules.spec.js`
- 검증 신규 파일: `tests/specs/featured.spec.js`, `tests/specs/focus-modal.spec.js`, `tests/specs/screenshots.spec.js`, `tests/specs/final-contract.spec.js`
- runtime(ignore): `tests/.tmp/**`, `tests/screenshots/**`

## C5. step 개요 (각 step 예상 20분 이하, hard timeout 30분)

| # | name | 목적 | 생성·소유 spec |
|---|---|---|---|
| 0 | baseline-evidence | 구현 전 evidence와 VS exact 호환 | — |
| 1 | featured-hero | featured data, 대표 카드, hero 첫 화면의 남은 diff | featured.spec.js |
| 2 | layout-interaction | section layout, hit target, hover/focus, modal/lightbox focus 복귀, print의 남은 diff | focus-modal.spec.js |
| 3 | contrast-nested | 확인된 contrast·nested-interactive 결함을 직접 수정, guard exact 예외 | — |
| 4 | focused-fix | focused 묶음과 AXE0를 돌리고 실제 실패만 수정 | — |
| 5 | final-verification | SPEC_GATE→FULL→AXE0→VS→screenshots·final-contract | screenshots.spec.js, final-contract.spec.js |
| 6 | exact-range-review | exact implementation range GPT-6 Astra review, blocker만 수정 | — |
| 7 | publish-gated | 대표의 별도 승인이 있을 때만 push·OPEN PR, SHA 동일 확인 | — |

- step 2의 남은 실제 diff가 20분을 넘으면, 구현 전에 plan batch로 2a·2b로 나눈다. 이유는 정책 §6의 비례성 기록으로 남긴다.

## C6. 실패·복구

- step 0에서 기록한 구현 전 evidence가 복구 기준이다.
- 실패하면 runner를 즉시 멈추고 다음을 evidence와 작업 스레드에 기록한 뒤 blocker 상태로 둔다: 현재 HEAD, status, diff, 실패 로그, 마지막 성공 step, 변경 파일.
- 자동 재실행과 파괴적 Git은 금지한다.
- 복구는 다음 순서를 따른다.
  1. 복구안은 실패한 step의 exact 허용 경로만 대상으로 작성한다.
  2. 새로 검토·승인된 계획을 받은 외부 Harness runner만 복구를 수행한다.
  3. 복구 후 focused, AXE0, FULL, VS를 다시 통과해야 재개한다.
- 결과가 불명확하거나, 중대성에 이견이 있거나, 승인이 만료·변경되었으면 새 exact 승인 전까지 재개하지 않는다.

## C7. 흐름

1. plan-only materialize와 commit
2. 공식 review-plan(GPT-6 Astra) CLEAN
3. 대표 exact `APPROVE HOO-81 PLAN <sha40> REVIEW <sha64>`. 이 승인 전에는 source를 쓰지 않는다.
4. step 0~5
5. step 6: exact range Astra CLEAN, tested = reviewed = HEAD
6. step 7: 대표의 별도 push/PR 승인이 있을 때만 실행

- 구현 승인은 push/PR 승인과 같은 것으로 보지 않는다. merge와 deploy는 하지 않는다.
