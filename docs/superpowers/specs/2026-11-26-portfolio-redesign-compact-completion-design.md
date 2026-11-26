# HOO-81 compact completion 설계 (v92: review-plan v91 record 23c89e56… major 1 교정)

- phase: `HOO-81-portfolio-redesign-compact-completion`, step 0~11(12개)
- 근거 결정(대표): `compact-product-scope-v87`, `compact-v88-findings-dea8de`, `compact-v89-findings-4389e6`, `compact-v90-findings-27176f`, `compact-v91-findings-548fc9`, `compact-v92-findings-23c89e`. 교정 1회와 공식 리뷰 1회를 추가 승인받았다.
- 정본 정책: `/Users/hoon/.hermes/company/operations/product-task-scope-control-policy.md`
- 전환 계획: `/Users/hoon/.hermes/profiles/ryan/cache/scratch/HOO-103-product-scope-control-and-compact-plan.md`. 이 문서 §4의 대응표가 제품 정본이다.
- review-plan 교정 이력:
  - v87 `dea8de41636e784c29ae3b1c9951f7aed8d68b730fbc8737597ba36af602c1a1`
  - v88 `4389e65cd9c1530747b37a256472769fb5ef45583fe8d377dedeaa2db27a60c4`
  - v89 `27176f9a91b5019ac244453c320dbba4526a3669c6f4dbc3219ef650c04ebfc0`
  - v90 `548fc920bf65ddb65beb1efef732a92f93b5052c1c87f7430bfae37a36df825c`
  - v91 `23c89e565ce6809d91991c338077ed799466e1e6e799f96788eb6eca03d87ced`. major 1건은 step 9 작업 5와 §C6 판정 문장에서만 교정했다.
- 수정하지 않는 유효 문서: 원 설계 `docs/superpowers/specs/2026-11-23-portfolio-layout-redesign-design.md`(§n), resume 설계 `docs/superpowers/specs/2026-11-24-portfolio-redesign-resume-design.md`
- 보존(감사 증거, 확장하지 않음):
  - phase `HOO-81-portfolio-redesign-official-runner-resume`, commit `3887bec96f0d4bcdd21519d2cb443b3cdd3352d9`
  - color-resume 계획
  - 원 phase step 0~39, resume step 0~16 산출물. 재실행하지 않는다.
- step 경계는 원 resume 작업 단위를 재사용한다. step 12개는 비례성 휴리스틱 범위 안이다.
- `CLAUDE.md`나 회사 승인 정책과 충돌하면 그쪽을 우선하고 실행을 중단한다.

## C0. 공통 선행조건 (모든 step, 쓰기 전)

- 쓰기 전에 다음을 읽는다:
  - `CLAUDE.md`, 회사 정책, compact 대응표
  - 원 설계(§3·§4·§5·§6·§7·§11.2), resume 설계
  - 현재 source와 spec
- 충돌·누락·해석 불가가 하나라도 있으면 아무것도 쓰지 않고 중단·보고한다.
- AC가 실패하면 그 자리에서 중단하고 evidence를 남긴다. 복구는 C8로만 한다.

## C1. 제품 계약 (불변)

- `js/data.js`: PROJECTS index 1·5·7의 `title` 바로 다음 줄에 `featured: true,`를 정확히 3줄만 추가한다. 나머지 bytes는 step 0 baseline HEAD와 같아야 한다(v70b).
- 대표 카드:
  - `#heroFeatured`(div, role `region`, aria-label `대표 프로젝트`)를 `#heroStats` 바로 다음 형제로 둔다.
  - 카드는 `button[type=button]` 3개(data-project 1·5·7)이고, 각각 `span`이 정확히 2개이며 nested interactive는 0개다.
  - click·Enter로 모달을 열고, 어떤 경로로 닫든 trigger로 focus가 돌아온다.
- FINAL 섹션 구조(원 §4 표):

| 순서 | id | class | kicker | heading |
|---|---|---|---|---|
| 1 | hero | hero | 없음 | h1 `#heroName` |
| 2 | career | section | `01 — Career` | h2 경력 &amp; 창업 |
| 3 | projects | section section-alt | `02 — Projects` | h2 프로젝트 &amp; 제품 |
| 4 | strengths | section | `03 — Strengths` | h2 업무상 강점 (section-sub 유지) |
| 5 | about | section section-alt | `04 — About` | h2 소개 |
| 6 | contact | section | `05 — Contact` | h2 연락처 |

  - about: 본문 뒤에 `h3.subsection-title` 기술 스택과 `#skillsGrid`를 둔다. skill-group 제목은 h3다(기존 `.skill-group h3` 색·서체 규칙 유지, design-guard 불변. 2026-11-26 대표 결정). 이 결정은 원 설계 §4와 원·resume phase의 skill-group `h4` 요구를 대체하며, C0의 충돌 중단 대상이 아니다.
  - contact: `.contact-card`와 h3 함께 만들어요를 유지한다.
  - nav와 스크롤스파이 순서: career, projects, strengths, about, contact.
  - `.scroll-hint`의 href는 `#career`다.
  - 콘텐츠 변경은 원 §5 허용 예외 (1)~(5)만 허용한다.
- 보존: 색, 서체 asset·weight, 이미지·아이콘, PROJECTS 13개와 그 순서. `css/themes.css`는 read-only다.
- 색 변경은 확인된 color-contrast 결함을 고칠 때만 한다. 선언 단위로, 기존 token만 써서 최소한으로 바꾼다.
- 레이아웃: 원 §3·§7·§11.2를 따르고, 값은 `tests/fixtures/claude-design-intake.json`의 tokens에서 가져온다.
- 현재 DOM에서 axe 10개 시나리오 위반이 0이어야 한다.

## C2. 범위 금지

- 만들지 않는 것: 범용 mapper, influence/transaction framework, custom coordinator, 새 공통 helper, 새 Harness 기능.
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
- `AXE0`는 아래를 순서대로 실행한다. baseline이 pending이든 check든 그것을 완료 증거로 보지 않는다.
  1. `T specs/axe-helper.spec.js`
  2. `sh tests/scripts/with-env.sh node tests/helpers/axe.js --reset`
  3. `env AXE_COLLECT=1 sh tests/scripts/with-env.sh npm --prefix tests test -- specs/axe.spec.js`
  4. `sh tests/scripts/with-env.sh node tests/helpers/axe.js --merge --out tests/.tmp/axe-current.json`
  5. `sh tests/scripts/with-env.sh node tests/helpers/axe.js --assert-no-violations --collected tests/.tmp/axe-current.json`
- `OWN_SPEC <p>` = `python3 -I -c "import os,stat,sys; p=sys.argv[1]; sys.exit('own-spec: '+p) if not os.path.lexists(p) or not stat.S_ISREG(os.lstat(p).st_mode) else print('own-spec: OK '+p)" <p>`
- `SPEC_GATE`(step 11에서만) = `python3 -I -c "import os,stat,sys; P=['tests/specs/featured.spec.js','tests/specs/focus-modal.spec.js','tests/specs/screenshots.spec.js','tests/specs/final-contract.spec.js']; bad=[p for p in P if not os.path.lexists(p) or not stat.S_ISREG(os.lstat(p).st_mode)]; sys.exit('spec-gate: '+','.join(bad)) if bad else print('spec-gate: OK 4')"`
- `SHOT <prefix> <tag>` = `sh -c 'id=<prefix>-$(date -u +%Y%m%dT%H%M%SZ); mkdir -p tests/.tmp/compact; printf %s "$id" > tests/.tmp/compact/shot-id-<tag>.txt; COMPACT_RUN_ID=$id sh tests/scripts/with-env.sh npm --prefix tests test -- specs/screenshots.spec.js --project=desktop-dark'`
  - 사용하는 prefix/tag:
    - step 10: `s10`/`s10`
    - step 11: `final`/`final`
    - C8 복구: `recovery-<n>`/`recovery-<n>`
  - 고정 ID는 쓰지 않는다.

## C4. 허용 범위

- tracked 파일(exact, index와 같음):
  - product: `index.html`, `css/style.css`, `js/main.js`, `js/data.js`
  - 기존 검증 파일(최소 수정): `tests/scripts/verify-scope.mjs`, `tests/specs/verify-scope-resume.spec.js`, `tests/helpers/design-guard-color-rules.js`, `tests/specs/design-guard-color-rules.spec.js`
  - 신규 spec 4개:
    - `tests/specs/featured.spec.js`: step 1에서 생성, step 2·3에서 보강
    - `tests/specs/final-contract.spec.js`: step 4에서 생성, step 5·6·7·10에서 보강
    - `tests/specs/focus-modal.spec.js`: step 8에서 생성
    - `tests/specs/screenshots.spec.js`: step 10에서 생성
- runtime: `tests/.tmp/**`, `tests/screenshots/**`, `tests/test-results/**`, `tests/.npm-cache/**`
- tracked 허용 범위와 verify-scope 면제는 넓히지 않는다.

## C5. step (테스트 포함 20분 이하, hard timeout 30분, 임의 분할 금지)

| # | name | 원 resume 경계 | 예상(분) |
|---|---|---|---|
| 0 | baseline-read-evidence | — | 15 |
| 1 | featured-cards | r18 | 18 |
| 2 | hero-first-screen | r19 | 16 |
| 3 | hero-two-column | r20 | 16 |
| 4 | section-structure | r21 | 18 |
| 5 | section-layout | r22 | 16 |
| 6 | component-states | r23·r26·r27 (clamp·stripe 담당) | 18 |
| 7 | print | r30 | 15 |
| 8 | focus-overlays | r28·r29 | 18 |
| 9 | contrast-nested | a11y | 16 |
| 10 | visual-final-contract | r34 | 20 |
| 11 | final-verification (read-only) | — | 20 |

## C6. 고정 interface

- `renderFeaturedProjects(): void`
  - PROJECTS 원래 index를 그대로 쓰고, 1·5·7을 `#heroFeatured`에 `button`(안에 `span` 2개)으로 렌더한다.
  - boot에서 grid render 직후 1회만 호출한다.
  - click·keydown은 container에 위임하고, `openProjectModal(projectIndex, triggerElement = document.activeElement)`를 호출한다.
- focus 복귀 분담:
  - step 1:
    - `openProjectModal`이 `triggerElement`를 모듈 변수 `lastModalTrigger`에 저장한다.
    - 기존 공통 닫기 경로 `closeProjectModal`에서, 저장된 trigger가 `isConnected`이면 그 요소로 focus를 돌리고 변수를 비운다.
    - button·backdrop·Esc 닫기는 모두 이 공통 경로를 거친다.
  - step 8: 이 공통 경로를 재사용하고, 거기에 trap release만 연결한다.
- `trapFocus(container, { returnFocusTo = null } = {}): () => void`(step 8)
  - document keydown handler는 1개만 두고 trap은 stack으로 관리한다. Tab은 stack top의 trap만 처리한다.
  - 반환하는 release는 여러 번 호출해도 결과가 같다.
  - modal: 열 때 push한다. 닫을 때는 공통 경로에서 release하고 trigger로 focus를 돌린다.
  - lightbox:
    - modal 위에 push한다.
    - 첫 Esc는 lightbox가 소비해 release하고 `.shot-zoom`으로 focus를 돌린다. 이때 modal trap이 다시 stack top이 된다.
    - 다음 Esc에서 modal을 닫는다.
  - 기존 lightbox 개별 Tab listener는 제거한다.
- step 6 hover·active 색 비교 기준(2026-11-26 대표 결정): BASE css에 `HOO81_COLOR_V52_ALLOW` 선언만 base→to로 적용한 css(`applyColorAllow`, `tests/helpers/design-guard-color-rules.js`). 허용 목록 밖 색 변화는 계속 실패한다.
- `HOO81_COLOR_V52_ALLOW`
  - 원소: `{file, chain, selector, occurrence, prop, base, to}`. `chain`은 기존 parser의 at-rule chain이고, `occurrence`는 같은 file·chain·selector rule 중 몇 번째인지(0부터)다.
  - 판정 기준(v92): 같은 file·chain·selector·occurrence·prop에 해당하는 선언 하나만 예외로 다룬다.
    - 그 값이 `base`이거나 정확히 `to`이면 통과한다.
    - 계속 위반인 경우:
      - 그 선언의 값이 `base`도 `to`도 아닌 경우
      - chain이 다른 경우
      - occurrence가 다른 경우
      - 같은 rule의 다른 선언이 바뀐 경우
    - 허용 목록이 `[]`이면 기존 동작과 같다.
  - 이 기준은 step 9 작업 5의 회귀 사례와 1:1로 대응한다.

## C7. screenshot (`screenshots.spec.js`)

- `COMPACT_RUN_ID`가 없으면 suite 전체를 `test.skip`한다. FULL과 testCommand는 이 변수 없이 통과해야 한다.
- coordinator suite(`test.describe.serial`)는 `desktop-dark` 하나에서만 실행한다. 나머지 5개 project에서는 `testInfo.project.name`을 보고 skip한다. SHOT은 `--project=desktop-dark`로 실행한다.
- suite 시작 시 아래를 각각 정확히 1회 수행한다.
  - ID가 `^[a-z0-9][a-z0-9-]{2,40}$`에 맞는지 검사한다.
  - `tests/screenshots/compact-${COMPACT_RUN_ID}/`가 아직 없는지 확인한다.
  - 그 디렉터리를 만든다.
- `tests/playwright.config.js`에서 6개 project의 `name`, `use.viewport`, `use.colorScheme`, `metadata.theme`, `use.baseURL`을 읽는다. project마다 순서대로 `browser.newContext({ baseURL, viewport, colorScheme })`를 만들고 `installProjectTheme(context, { project: { name } })`를 적용한다.
- 고정 15장(각 장은 `prepareForAxe` 후 촬영):
  - `page-{project}.png` × 6
  - `modal-project-{1|5|7}-{desktop-dark|desktop-light}.png` × 6
  - `menu-open-mobile-dark.png`
  - `lightbox-desktop-dark.png`(첫 shots project ID를 기록)
  - `print-desktop-light.png`
- suite 마지막에 아래를 각각 정확히 1회 수행한다.
  - 15개 exact 경로에 누락·중복·초과가 없는지 검사한다.
  - 각 파일의 SHA-256을 계산한다.
  - manifest `{runId, files: [{path, sha256}], lightboxProject}`를 `tests/.tmp/compact/screenshots-${COMPACT_RUN_ID}.json`에 쓴다.
- `final-contract.spec.js`는 screenshot에 의존하지 않는다.

## C8. 실패·복구 (자동 수정 루프 없음)

- AC가 실패하면 runner를 즉시 멈추고 다음을 기록한다: HEAD, status, diff, 로그, 마지막 성공 step, 원인 추정 파일.
- 같은 step 안에서 수정하거나 재실행하지 않는다. 자동 재실행과 파괴적 Git도 금지한다.
- 복구는 별도로 검토·승인된 exact 복구 cycle에서만 한다. 그 cycle에는 다음을 명시한다.
  - 원인 파일: 소유 step의 허용 파일 안에서만
  - 재검증 명령: 소유 step AC, 이어서 step 11 AC 전체. SHOT은 `SHOT recovery-<n> recovery-<n>`처럼 새 ID로 실행하고 그 ID를 기록한다.
  - 실행 주체: 외부 Harness runner
- 결과가 불명확하거나, 중대성에 대해 이견이 있거나, 승인이 만료·변경되었으면 새 exact 승인 전까지 재개하지 않는다.

## C9. 흐름 (phase 밖 운영 절차)

1. plan-only materialize와 commit을 한다.
2. 공식 review-plan이 CLEAN이어야 한다.
3. 대표 exact `APPROVE HOO-81 PLAN <sha40> REVIEW <sha64>`를 받는다. 그 전에는 source를 쓰지 않는다.
4. runner가 step 0~11을 실행한다.
5. step 11이 PASS하면 runner가 candidate HEAD에서 다음을 수행한다.
   - `testCommand`
   - exact range GPT-6 Astra review
   - `verify-final`로 tested = reviewed = HEAD 확인
6. review에서 major나 blocker가 남으면 CLEAN이 아니다. 별도 승인된 C8 cycle로 고친 뒤 재테스트·재리뷰한다. 임의로 반복하거나 등급을 낮추지 않는다.
7. push와 OPEN PR은 runner 밖에서 대표의 별도 승인을 받은 뒤 한다. merge와 deploy는 하지 않는다.

## C10. verify-scope 면제

- prefix·glob runtime 면제는 금지한다.
- `HARNESS_OWNED_FILES`에 exact committed path만 추가한다. committed 상태만 면제되고, staged·worktree 상태는 위반이다.
  - 이 설계 문서
  - `phases/HOO-81-portfolio-redesign-compact-completion/index.json`, `step0.md`~`step11.md`
  - step 0이 열거한 이력 계획의 committed exact path
- 목록 밖의 outside-scope가 나오거나, metadata 때문에 `harness-uncommitted`가 나오면 중단하고 보고한다.
