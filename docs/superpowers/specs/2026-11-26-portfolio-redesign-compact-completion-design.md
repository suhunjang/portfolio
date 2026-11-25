# HOO-81 compact completion 설계 (v90: review-plan v89 record 27176f9a… major 2 교정)

- phase: `HOO-81-portfolio-redesign-compact-completion`(step 0~11, 12개)
- 근거 결정: 대표 `compact-product-scope-v87`, `compact-v88-findings-dea8de`, `compact-v89-findings-4389e6`, `compact-v90-findings-27176f`(PRODUCT-SCOPE-001 계획 예산 1회 추가 승인).
- 정본 정책: `/Users/hoon/.hermes/company/operations/product-task-scope-control-policy.md`
- 전환 계획: `/Users/hoon/.hermes/profiles/ryan/cache/scratch/HOO-103-product-scope-control-and-compact-plan.md`. 이 계획의 §4 대응표가 제품 정본이다.
- review-plan 교정 이력:
  - v87 record `dea8de41636e784c29ae3b1c9951f7aed8d68b730fbc8737597ba36af602c1a1`
  - v88 record `4389e65cd9c1530747b37a256472769fb5ef45583fe8d377dedeaa2db27a60c4`
  - v89 record `27176f9a91b5019ac244453c320dbba4526a3669c6f4dbc3219ef650c04ebfc0`. major 2건은 §C3 SHOT, §C7, §C8, §C9, step 10·11에서만 교정했다.
- 수정하지 않는 유효 문서: 원 설계 `docs/superpowers/specs/2026-11-23-portfolio-layout-redesign-design.md`(§n), resume 설계 `docs/superpowers/specs/2026-11-24-portfolio-redesign-resume-design.md`.
- 감사 증거로 보존하고 확장하지 않는 것:
  - phase `HOO-81-portfolio-redesign-official-runner-resume`과 commit `3887bec96f0d4bcdd21519d2cb443b3cdd3352d9`
  - color-resume 계획
  - 원 phase step 0~39와 resume phase step 0~16의 산출물. 다시 실행하지 않는다.
- step 경계는 원 resume 작업 단위를 그대로 쓴다. step 수 12는 비례성 휴리스틱 범위 안이다.
- `CLAUDE.md`·회사 승인 정책과 충돌하면 그쪽이 우선하고 실행을 중단한다.

## C0. 공통 선행조건 (모든 step, 파일을 쓰기 전)

- 다음을 먼저 읽는다:
  - `CLAUDE.md`, 회사 정책, compact 대응표
  - 원 설계(§3·§4·§5·§6·§7·§11.2), resume 설계
  - 해당 step의 현재 source와 spec
- 충돌하거나 빠진 것이 있거나 해석할 수 없으면, 아무것도 쓰지 않고 중단·보고한다.
- AC가 실패하면 그 자리에서 중단하고 evidence를 기록한다. 복구는 C8 절차로만 한다.

## C1. 제품 계약 (불변)

- `js/data.js`: PROJECTS index 1·5·7의 `title` 바로 다음 줄에 `featured: true,`를 정확히 3줄만 추가한다. 나머지 bytes는 step 0 baseline HEAD와 같아야 한다(v70b).
- 대표 카드:
  - `#heroFeatured`(div, role `region`, aria-label `대표 프로젝트`)는 `#heroStats`의 다음 형제다.
  - 카드는 `button[type=button]` 3개이고 data-project는 1·5·7이다.
  - 카드마다 `span`이 정확히 2개이고, nested interactive는 0개다.
  - click이나 Enter로 모달이 열리고, 어떤 방법으로 닫든 trigger로 focus가 돌아온다.
- FINAL 섹션 구조(원 §4 표 그대로):

| 순서 | id | class | kicker | heading |
|---|---|---|---|---|
| 1 | hero | hero | 없음 | h1 `#heroName` |
| 2 | career | section | `01 — Career` | h2 경력 &amp; 창업 |
| 3 | projects | section section-alt | `02 — Projects` | h2 프로젝트 &amp; 제품 |
| 4 | strengths | section | `03 — Strengths` | h2 업무상 강점 (section-sub 유지) |
| 5 | about | section section-alt | `04 — About` | h2 소개 |
| 6 | contact | section | `05 — Contact` | h2 연락처 |

  - about: 본문 뒤에 `h3.subsection-title` 기술 스택과 `#skillsGrid`(skill-group 제목은 h4)를 둔다.
  - contact: `.contact-card`와 h3 함께 만들어요를 유지한다.
  - nav와 스크롤스파이 배열 순서: career, projects, strengths, about, contact. `.scroll-hint`의 href는 `#career`다.
  - 허용되는 콘텐츠 변경은 원 §5의 예외 (1)~(5)뿐이다. 그 밖의 문구·수치는 바꾸지 않는다.
- 보존: 색, 서체 asset·weight, 이미지·아이콘, PROJECTS 13개와 순서. `css/themes.css`는 읽기 전용이다.
- 색 변경: 확인된 color-contrast 결함을 고칠 때만, 기존 token `var(--x)`로 선언 단위로 최소한만 바꾼다.
- 레이아웃: 원 §3·§7·§11.2를 따르고, 수치는 `tests/fixtures/claude-design-intake.json`의 tokens를 쓴다.
- 현재 DOM의 axe 10개 시나리오에서 위반은 0이어야 한다.

## C2. 범위 금지

- 만들지 않는다: 범용 mapper, influence/transaction framework, custom coordinator, 새 공통 helper, 새 Harness 기능.
- 대응표에 없는 요구는 자동으로 흡수하지 않는다.
- 금지 명령·행위: `git reset/restore/checkout/clean`, 광범위 삭제, main 직접 변경, merge, deploy, push, PR.
- git checkout·add·commit은 Harness runner만 한다.

## C3. 약어 (argv)

- `T <specs>` = `sh tests/scripts/with-env.sh npm --prefix tests test -- <specs>`
- `FULL` = `sh tests/scripts/with-env.sh npm --prefix tests test`
- `VS` = `sh tests/scripts/with-env.sh npm --prefix tests run verify-scope`
- `VSST` = `sh tests/scripts/with-env.sh npm --prefix tests run verify-scope:selftest`
- `DI` = `python3 -I tests/scripts/design-intake-check.py`
- `GS` = `specs/design-guard.spec.js specs/design-guard-css.spec.js specs/design-guard-font.spec.js specs/design-guard-color.spec.js specs/design-guard-color-rules.spec.js specs/design-guard-color-pairs.spec.js specs/css-parse.spec.js specs/color-vocab.spec.js`
- `AXE0`는 아래 다섯 명령을 순서대로 실행한다. baseline의 pending/check 상태는 완료 증거로 보지 않는다.
  1. `T specs/axe-helper.spec.js`
  2. `sh tests/scripts/with-env.sh node tests/helpers/axe.js --reset`
  3. `env AXE_COLLECT=1 sh tests/scripts/with-env.sh npm --prefix tests test -- specs/axe.spec.js`
  4. `sh tests/scripts/with-env.sh node tests/helpers/axe.js --merge --out tests/.tmp/axe-current.json`
  5. `sh tests/scripts/with-env.sh node tests/helpers/axe.js --assert-no-violations --collected tests/.tmp/axe-current.json`
- `OWN_SPEC <p>` = `python3 -I -c "import os,stat,sys; p=sys.argv[1]; sys.exit('own-spec: '+p) if not os.path.lexists(p) or not stat.S_ISREG(os.lstat(p).st_mode) else print('own-spec: OK '+p)" <p>`
- `SPEC_GATE`(step 11에서만) = `python3 -I -c "import os,stat,sys; P=['tests/specs/featured.spec.js','tests/specs/focus-modal.spec.js','tests/specs/screenshots.spec.js','tests/specs/final-contract.spec.js']; bad=[p for p in P if not os.path.lexists(p) or not stat.S_ISREG(os.lstat(p).st_mode)]; sys.exit('spec-gate: '+','.join(bad)) if bad else print('spec-gate: OK 4')"`
- `SHOT <prefix> <tag>`: 실행할 때마다 새 ID를 만들어 기록하고, 그 ID로 desktop-dark project 하나만 실행한다.
  - 형식: `sh -c 'id=<prefix>-$(date -u +%Y%m%dT%H%M%SZ); mkdir -p tests/.tmp/compact; printf %s "$id" > tests/.tmp/compact/shot-id-<tag>.txt; COMPACT_RUN_ID=$id sh tests/scripts/with-env.sh npm --prefix tests test -- specs/screenshots.spec.js --project=desktop-dark'`
  - prefix·tag 조합은 세 가지다:
    - step 10: prefix `s10`, tag `s10`
    - step 11: prefix `final`, tag `final`
    - C8 복구 cycle: prefix `recovery-<n>`, tag `recovery-<n>`
  - 고정 ID(`step10`, `final`)는 쓰지 않는다.

## C4. 허용 범위

- tracked(exact, index와 동일):
  - product: `index.html`, `css/style.css`, `js/main.js`, `js/data.js`
  - 기존 검증 파일(최소 수정): `tests/scripts/verify-scope.mjs`, `tests/specs/verify-scope-resume.spec.js`, `tests/helpers/design-guard-color-rules.js`, `tests/specs/design-guard-color-rules.spec.js`
  - 신규 spec 4개(괄호는 생성 step / 보강 step):
    - `tests/specs/featured.spec.js`(1 / 2·3)
    - `tests/specs/final-contract.spec.js`(4 / 5·6·7·10)
    - `tests/specs/focus-modal.spec.js`(8)
    - `tests/specs/screenshots.spec.js`(10)
- runtime(ignore 대상): `tests/.tmp/**`, `tests/screenshots/**`, `tests/test-results/**`, `tests/.npm-cache/**`. tracked 허용 파일과 verify-scope 면제는 넓히지 않는다.

## C5. step (예상 시간은 테스트 실행 포함 20분 이하, hard timeout 30분, 실행 중 임의로 분할하지 않음)

| # | name | 원 resume 경계 | 예상(분) |
|---|---|---|---|
| 0 | baseline-read-evidence | — | 15 |
| 1 | featured-cards | r18 | 18 |
| 2 | hero-first-screen | r19 | 16 |
| 3 | hero-two-column | r20 | 16 |
| 4 | section-structure | r21 | 18 |
| 5 | section-layout | r22 | 16 |
| 6 | component-states | r23·r26·r27(clamp·stripe 담당) | 18 |
| 7 | print | r30 | 15 |
| 8 | focus-overlays | r28·r29 | 18 |
| 9 | contrast-nested | a11y | 16 |
| 10 | visual-final-contract | r34 | 20 |
| 11 | final-verification(read-only) | — | 20 |

## C6. 고정 interface

- `renderFeaturedProjects(): void`
  - PROJECTS의 원래 index를 그대로 쓰고, 1·5·7을 `#heroFeatured`에 `button` 안 `span` 2개 구조로 렌더한다.
  - boot에서 grid render 직후 1회만 호출한다.
  - click·keydown은 container에서 위임으로 받아 `openProjectModal(projectIndex, triggerElement = document.activeElement)`를 호출한다.
  - 모달을 닫는 모든 경로에서 저장해 둔 trigger로 focus를 돌려준다.
- `trapFocus(container, { returnFocusTo = null } = {}): () => void`
  - document keydown handler 1개와 stack 하나로 동작한다. Tab은 stack 맨 위의 trap만 처리한다.
  - 반환하는 release 함수는 여러 번 불러도 결과가 같다.
  - modal: 열 때 push하고, 닫을 때 release한 뒤 trigger로 focus를 돌려준다.
  - lightbox: 열린 modal 위에 push한다.
    - 첫 Esc는 lightbox가 소비한다. release하고 `.shot-zoom`으로 focus를 돌려주며, modal trap이 다시 맨 위가 된다.
    - 다음 Esc가 modal을 닫는다.
  - 기존 lightbox 전용 Tab listener는 제거한다.
- `HOO81_COLOR_V52_ALLOW`(`tests/helpers/design-guard-color-rules.js`에서 export)
  - 원소: `{file, chain, selector, occurrence, prop, base, to}`
    - `chain`: 기존 parser의 at-rule chain
    - `occurrence`: 같은 file·chain·selector rule 중 몇 번째인지(0부터)
  - guard는 지정된 선언 하나의 값이 `base` 또는 `to`일 때만 위반에서 제외한다. rule 전체를 제외하지 않는다.

## C7. screenshot (`screenshots.spec.js`)

- `COMPACT_RUN_ID`가 없으면 suite 전체를 명시적으로 `test.skip`한다. 그래서 일반 `FULL`과 §C9 testCommand는 이 변수 없이도 통과한다.
- 실행 주체는 하나다:
  - coordinator suite(`test.describe.serial`)는 Playwright project `desktop-dark`에서만 돈다. 나머지 5개 project에서는 `testInfo.project.name`을 보고 suite 전체를 skip한다.
  - SHOT은 항상 `--project=desktop-dark`로 실행한다.
- suite 시작 시 정확히 한 번 검사한다:
  - `COMPACT_RUN_ID`가 `^[a-z0-9][a-z0-9-]{2,40}$`와 맞지 않으면 실패한다.
  - `tests/screenshots/compact-${COMPACT_RUN_ID}/`가 이미 있으면 실패한다.
  - 둘 다 통과하면 디렉터리를 1회 만든다.
- context 생성:
  - `tests/playwright.config.js`의 기존 6개 project 정의를 import해 읽는다. 읽는 값은 `name`, `use.viewport`, `use.colorScheme`, `metadata.theme`, 그리고 `use.baseURL`이다.
  - project마다 `browser.newContext({ baseURL, viewport, colorScheme })`로 하나씩 순서대로 만든다.
  - 기존 `installProjectTheme(context, { project: { name } })`를 적용한 뒤 촬영하고, 다 찍으면 context를 닫는다.
- 고정 15장:
  - `page-{project}.png` × 6
  - `modal-project-{1|5|7}-{desktop-dark|desktop-light}.png` × 6
  - `menu-open-mobile-dark.png`
  - `lightbox-desktop-dark.png`. 기존 helper가 찾은 첫 shots project ID를 함께 기록한다.
  - `print-desktop-light.png`
  - 각 장은 `prepareForAxe`를 거친 뒤 찍는다.
- suite 마지막에 정확히 한 번 한다:
  - 15개 exact 경로를 대조해 누락·중복·초과를 검사한다.
  - 파일마다 SHA-256을 계산한다.
  - manifest `{runId, files: [{path, sha256}], lightboxProject}`를 `tests/.tmp/compact/screenshots-${COMPACT_RUN_ID}.json`에 쓴다.
- `final-contract.spec.js`는 screenshot 산출물에 의존하지 않는다.

## C8. 실패·복구 (자동 수정 루프 없음)

- AC가 실패하면 runner를 즉시 멈춘다.
- 다음을 evidence와 작업 스레드에 기록하고 blocker 상태로 둔다: HEAD, status, diff, 실패 로그, 마지막 성공 step, 원인으로 추정되는 파일.
- 같은 step 안에서 즉시 수정하거나 재실행하지 않는다. 자동 재실행과 파괴적 Git도 금지한다.
- 복구는 별도로 검토·승인된 exact 복구 cycle에서만 한다. 그 cycle에는 다음을 명시한다:
  - 원인 파일: 원래 소유 step의 허용 파일 안에서만
  - 재검증 명령: 소유 step의 AC, 그다음 step 11 AC 전체
  - 재검증의 SHOT은 `SHOT recovery-<n> recovery-<n>`처럼 새 ID로 실행하고, 그 ID를 복구 evidence에 기록한다.
- 실행은 외부 Harness runner가 한다.
- 결과가 불분명하거나, 중대성 판단에 이견이 있거나, 승인이 만료·변경되었으면 새 exact 승인을 받기 전까지 재개하지 않는다.

## C9. 흐름 (phase 밖 운영 절차)

1. plan-only materialize와 commit을 한다.
2. 공식 review-plan이 CLEAN이어야 한다.
3. 대표 exact `APPROVE HOO-81 PLAN <sha40> REVIEW <sha64>`를 받는다. 그 전에는 source를 쓰지 않는다.
4. runner가 step 0~11을 실행한다.
5. step 11이 PASS하면 runner가 candidate HEAD에서 다음을 순서대로 수행한다:
   - `testCommand`(FULL; `COMPACT_RUN_ID`가 없으므로 screenshots suite는 skip)
   - exact range `<baselineHead>..<candidateHead>` GPT-6 Astra review
   - `verify-final`로 tested = reviewed = HEAD 확인
6. review에서 major나 blocker가 남으면 CLEAN이 아니다. 별도 승인된 C8 cycle(새 SHOT ID 사용)로 고친 뒤 다시 테스트하고 다시 리뷰한다. 임의로 반복하거나 등급을 낮추지 않는다.
7. push와 OPEN PR은 runner 밖에서, 대표의 별도 승인이 있을 때만 한다. merge·deploy는 하지 않는다.

## C10. verify-scope 면제

- prefix나 glob을 쓰는 runtime 면제는 금지한다.
- `HARNESS_OWNED_FILES`에 exact committed path만 추가한다. committed 상태만 면제되고, staged·worktree 변경은 위반으로 남는다. 추가할 path:
  - 이 설계 문서
  - `phases/HOO-81-portfolio-redesign-compact-completion/index.json`, `step0.md`~`step11.md`
  - step 0이 baseline HEAD에서 열거한 이력 계획의 committed exact path: `phases/HOO-81-portfolio-redesign-official-runner-resume/**`, `phases/HOO-81-portfolio-redesign-color-resume/**`, `docs/superpowers/specs/2026-11-25-*`
- 이 목록 밖의 outside-scope가 나오거나, metadata 때문에 `harness-uncommitted`가 나오면 중단하고 보고한다.
