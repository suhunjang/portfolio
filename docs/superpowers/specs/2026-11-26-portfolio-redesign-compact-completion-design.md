# HOO-81 compact completion 설계 (v88: review-plan v87 record dea8de41… 교정)

- phase: `HOO-81-portfolio-redesign-compact-completion`, step 0~7.
- 근거:
  - 대표 결정 `compact-product-scope-v87`, `compact-v88-findings-dea8de`
  - 정본 정책 `/Users/hoon/.hermes/company/operations/product-task-scope-control-policy.md`
  - 전환 계획 `/Users/hoon/.hermes/profiles/ryan/cache/scratch/HOO-103-product-scope-control-and-compact-plan.md`. 이 문서 §4의 승인 요구사항↔검증 대응표가 제품 정본이다.
- review-plan v87 record `dea8de41636e784c29ae3b1c9951f7aed8d68b730fbc8737597ba36af602c1a1`의 major 9건·minor 1건을 반영했다.
- 수정 금지인 유효 문서: 원 설계 `docs/superpowers/specs/2026-11-23-portfolio-layout-redesign-design.md`(§n), resume 설계 `docs/superpowers/specs/2026-11-24-portfolio-redesign-resume-design.md`.
- 감사 증거로만 보존하고 확장하지 않는 것:
  - phase `HOO-81-portfolio-redesign-official-runner-resume`, commit `3887bec96f0d4bcdd21519d2cb443b3cdd3352d9`
  - color-resume 계획
  - 원 phase step 0~39, resume phase step 0~16의 산출물. 재실행하지 않고 현재 HEAD에서 검증만 한다.
- repository `CLAUDE.md`, 회사 승인 정책과 충돌하면 그쪽이 우선하고 실행을 중단한다.

## C0. 공통 선행조건 (모든 step, 쓰기 전)

- 아래를 먼저 읽는다:
  - `CLAUDE.md`, 회사 정책, compact 대응표
  - 원 설계, resume 설계
  - 해당 step이 다루는 현재 source(`index.html`, `css/style.css`, `js/main.js`, `js/data.js`)와 관련 spec
- 충돌, 누락, 해석 불가 중 하나라도 있으면 아무것도 쓰지 않고 중단·보고한다.

## C1. 제품 계약 (불변)

- `js/data.js`: PROJECTS index 1·5·7의 `title` 줄 바로 다음에 `featured: true,` 정확히 3줄만 추가한다(v70b). 나머지 bytes는 step 0 baseline HEAD와 같아야 한다.
- 대표 카드:
  - `#heroFeatured`(div, role `region`, aria-label `대표 프로젝트`)는 `#heroStats`의 다음 형제다.
  - 카드 3개는 각각 `button[type=button]`이고 data-project는 1·5·7이다.
  - 카드마다 `span`이 정확히 2개이고, nested interactive는 0이다.
  - click·Enter로 모달을 연다. 닫는 모든 경로에서 trigger로 focus가 돌아온다.
- 보존:
  - 색, 서체 asset·weight, 문구, 수치
  - FINAL IA(hero→Career→Projects→Strengths→About→Contact, 6개 섹션)
  - PROJECTS 13개와 순서, 이미지·아이콘
- `css/themes.css`는 읽기 전용이다.
- 색은 확인된 color-contrast 결함을 고칠 때만 기존 token `var(--x)`로 최소한 바꾼다.
- 375/768/1280에서 가로 스크롤 0, 1280×800 첫 화면 AC(원 §3), print 보존(원 §7).
- theme·menu·typing·reduced-motion·modal·lightbox·focus trap에 회귀가 없어야 한다.
- 현재 DOM의 axe 10개 시나리오에서 위반이 0이어야 한다.

## C2. 범위 금지

- 만들지 않는 것: 범용 declaration mapper, BASE influence framework, transaction framework, custom coordinator, 새 Harness 공통 기능, 새 범용 검증 파이프라인.
- 대응표 밖의 요구는 자동으로 흡수하지 않는다. 계획 변경이 필요하면 재리뷰와 재승인을 받는다.
- 금지 명령·행위: `git reset/restore/checkout/clean`, 광범위 삭제, main 직접 변경, merge, deploy, push, PR.
- git checkout·add·commit은 Harness runner만 한다.

## C3. 약어 (argv)

- `T <specs>` = `sh tests/scripts/with-env.sh npm --prefix tests test -- <specs>`
- `FULL` = `sh tests/scripts/with-env.sh npm --prefix tests test`
- `VS` = `sh tests/scripts/with-env.sh npm --prefix tests run verify-scope`
- `VSST` = `sh tests/scripts/with-env.sh npm --prefix tests run verify-scope:selftest`
- `DI` = `python3 -I tests/scripts/design-intake-check.py`
- `GS` = `specs/design-guard.spec.js specs/design-guard-css.spec.js specs/design-guard-font.spec.js specs/design-guard-color.spec.js specs/design-guard-color-rules.spec.js specs/design-guard-color-pairs.spec.js specs/css-parse.spec.js specs/color-vocab.spec.js`
- `AXE0`: 아래를 순서대로 실행한다. baseline이 pending·check 상태인 것은 완료 증거가 아니다. 현재 수집 결과가 정확히 빈 배열이어야 한다.
  1. `T specs/axe-helper.spec.js`
  2. `sh tests/scripts/with-env.sh node tests/helpers/axe.js --reset`
  3. `env AXE_COLLECT=1 sh tests/scripts/with-env.sh npm --prefix tests test -- specs/axe.spec.js`
  4. `sh tests/scripts/with-env.sh node tests/helpers/axe.js --merge --out tests/.tmp/axe-current.json`
  5. `sh tests/scripts/with-env.sh node tests/helpers/axe.js --assert-no-violations --collected tests/.tmp/axe-current.json`
- `OWN_SPEC <p>`: 신규 spec을 만드는 step이 자기 spec 하나에 대해 실행한다. `python3 -I -c "import os,stat,sys; p=sys.argv[1]; sys.exit('own-spec: '+p) if not os.path.lexists(p) or not stat.S_ISREG(os.lstat(p).st_mode) else print('own-spec: OK '+p)" <p>`
- `SPEC_GATE`: step 7에서만 실행한다. 4개 파일 모두 regular이고 non-symlink인지 확인한다. 하나라도 아니면 테스트를 실행하지 않고 해당 생성 step의 blocker로 끝낸다. `python3 -I -c "import os,stat,sys; P=['tests/specs/featured.spec.js','tests/specs/focus-modal.spec.js','tests/specs/screenshots.spec.js','tests/specs/final-contract.spec.js']; bad=[p for p in P if not os.path.lexists(p) or not stat.S_ISREG(os.lstat(p).st_mode)]; sys.exit('spec-gate: '+','.join(bad)) if bad else print('spec-gate: OK 4')"`

## C4. 허용 파일 (exact, index와 동일)

- product: `index.html`, `css/style.css`, `js/main.js`, `js/data.js`
- 기존 검증 파일(최소 수정): `tests/scripts/verify-scope.mjs`, `tests/specs/verify-scope-resume.spec.js`, `tests/helpers/design-guard-color-rules.js`, `tests/specs/design-guard-color-rules.spec.js`
- 신규 검증 파일: `tests/specs/featured.spec.js`(step 1), `tests/specs/focus-modal.spec.js`(step 3), `tests/specs/screenshots.spec.js`, `tests/specs/final-contract.spec.js`(둘 다 step 6)
- runtime(ignore 대상): `tests/.tmp/**`, `tests/screenshots/**`

## C5. step (각 step 예상 20분 이하, hard timeout 30분, 실행 중 임의 분할 금지)

| # | name | 쓰는 파일 | 예상 |
|---|---|---|---|
| 0 | baseline-read-evidence | `verify-scope.mjs`, `verify-scope-resume.spec.js` | 15 |
| 1 | featured-hero | `js/data.js`, `index.html`, `js/main.js`, `css/style.css`, `featured.spec.js` | 20 |
| 2 | section-layout | `index.html`, `js/main.js`, `css/style.css` | 18 |
| 3 | focus-overlays | `js/main.js`, `css/style.css`(`:focus-visible`만), `focus-modal.spec.js` | 18 |
| 4 | contrast-nested | `css/style.css`, `js/main.js`, `design-guard-color-rules.js`, `design-guard-color-rules.spec.js` | 15 |
| 5 | focused-fix | product 4개, `featured.spec.js`, `focus-modal.spec.js` | 15 |
| 6 | visual-final-contract | `screenshots.spec.js`, `final-contract.spec.js` | 20 |
| 7 | final-verification | 없음(read-only, runtime evidence만) | 18 |

## C6. 고정 interface

- **`renderFeaturedProjects(): void`**
  - PROJECTS의 원래 index를 그대로 쓴다.
  - 1·5·7번을 `button` + `span` 2개 구조로 `#heroFeatured`에 렌더한다.
  - boot에서 grid render 직후 1회만 호출한다.
  - container의 click·keydown은 위임으로 받아 `openProjectModal(projectIndex, triggerElement = document.activeElement)`를 호출한다.
  - 닫는 모든 경로(button·backdrop·Esc)에서 저장해 둔 trigger로 focus를 돌려준다.
- **`trapFocus(container, { returnFocusTo = null } = {}): () => void`**
  - document keydown handler 1개와 trap stack을 쓴다. Tab은 stack top의 trap만 처리한다.
  - 반환된 release는 idempotent하다.
  - modal:
    - 열 때 modal trap을 push한다.
    - 닫을 때 release하고 trigger로 focus를 돌려준다.
  - lightbox:
    - 열 때 modal 위에 lightbox trap을 push한다.
    - lightbox가 열린 상태의 첫 Esc는 lightbox만 처리한다. 이 Esc를 소비하고, release한 뒤 `.shot-zoom`으로 focus를 돌려준다.
    - modal trap은 다시 stack top이 되어 자동으로 재개된다.
    - 그다음 Esc가 modal을 닫는다.
  - 기존의 개별 lightbox Tab listener는 제거한다.

## C7. screenshot 고정 목록 (출력 `tests/screenshots/`)

- Playwright project 6개 각각 page 1장: `page-{project}.png`(6장)
- desktop-dark/light 각각 대표 모달 project 1·5·7 1장씩: `modal-project-{1|5|7}-{desktop-dark|desktop-light}.png`(6장)
- mobile-dark에서 menu를 연 상태 1장: `menu-open-mobile-dark.png`
- desktop-dark lightbox 1장: `lightbox-desktop-dark.png`. 기존 helper가 찾은 첫 shots project ID는 evidence에 기록한다.
- desktop-light print 1장: `print-desktop-light.png`
- 합계 15장. final-contract와 step 7이 누락·중복·초과 없이 검사한다.
- project 0·2·12의 modal 동작은 final-contract assertion으로만 검증하고, screenshot은 추가하지 않는다.

## C8. 실패·복구

- step 0 evidence가 복구 기준이다.
- 실패하면 runner를 즉시 멈춘다. 그리고 다음을 기록하고 blocker로 둔다: 현재 HEAD, status, diff, 로그, 마지막 성공 step, 변경 파일.
- 자동 재실행과 파괴적 Git은 금지한다.
- 복구는 실패 step의 exact 허용 경로만 대상으로 하고, 새로 검토·승인된 계획으로 외부 Harness runner가 수행한다.
- 복구 후 focused·AXE0·FULL·VS를 다시 통과해야 재개한다.
- 결과 불명, 중대성 이견, 승인 만료·변경 중 하나라도 있으면 새 exact 승인 전에는 재개하지 않는다.

## C9. 흐름 (phase 밖 운영 절차)

1. plan-only materialize와 commit을 한다.
2. 공식 review-plan(GPT-6 Astra)이 CLEAN이어야 한다.
3. 대표 exact `APPROVE HOO-81 PLAN <sha40> REVIEW <sha64>`를 받는다. 이 전에는 source를 쓰지 않는다.
4. Harness runner가 step 0~7을 실행한다.
5. step 7이 PASS하면 runner가 candidate HEAD에서 다음을 순서대로 수행한다(official Harness 2.0.1 명령):
   - `testCommand`(FULL)
   - exact implementation range `<step 0 baseline HEAD>..<candidate HEAD>`의 GPT-6 Astra review
   - `verify-final`로 tested = reviewed = HEAD 확인
6. phase step은 review·push를 직접 하지 않는다.
7. review에서 major·blocker가 나온 경우:
   - CLEAN이 아니다.
   - 원래 그 파일을 소유한 step의 exact 경로에 대해, 별도로 승인된 수정 cycle을 연다.
   - 수정 후 다시 테스트하고 다시 리뷰한다.
   - 임의로 반복하거나 등급을 낮추지 않는다. 비차단 항목은 원래 등급을 보존하고 별도 이슈로 남긴다.
8. push·OPEN PR은 runner 밖에서, 대표의 별도 승인이 있을 때만 한다. 구현 승인은 push/PR 승인이 아니다. merge·deploy는 하지 않는다.

## C10. verify-scope 면제 원칙

- prefix·glob runtime 면제는 추가하지 않는다. 대신 committed 상태인 exact path만 열거해 `HARNESS_OWNED_FILES`에 넣는다. 이 목록은 committed일 때만 면제되고, staged·worktree 변경은 위반으로 처리한다.
- 이 phase에서 열거하는 경로:
  - 이 설계 문서
  - `phases/HOO-81-portfolio-redesign-compact-completion/index.json`, `step0.md`~`step7.md`
- 이력 계획 경로:
  - 대상: `phases/HOO-81-portfolio-redesign-official-runner-resume/**`, `phases/HOO-81-portfolio-redesign-color-resume/**`, `docs/superpowers/specs/2026-11-25-*` 아래의 committed 파일
  - 현재 verify-scope에는 이 경로들의 면제가 없다.
  - step 0이 baseline HEAD에서 이 경로들의 committed 파일을 exact path로 열거해 함께 추가하고, 그 목록을 evidence에 남긴다.
  - 이 세 범위 밖의 committed 경로가 outside-scope로 나오면 면제를 넓히지 않고 중단한다.
- runner가 실행 중 `index.json` status를 worktree에서 갱신해 AC의 `VS`가 `harness-uncommitted`로 실패하면, 면제를 넓히지 않고 중단·보고한다. 이 경우 계획 변경과 재승인이 필요하다.
