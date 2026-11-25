# HOO-81 compact completion 설계 (v89: review-plan v88 record 4389e65c… 교정, 마지막 targeted closure)

- phase: `HOO-81-portfolio-redesign-compact-completion`(step 0~11, 12개)
- 근거:
  - 대표 결정: `compact-product-scope-v87`, `compact-v88-findings-dea8de`, `compact-v89-findings-4389e6`
  - 정본 정책: `/Users/hoon/.hermes/company/operations/product-task-scope-control-policy.md`(PRODUCT-SCOPE-001)
  - 전환 계획: `/Users/hoon/.hermes/profiles/ryan/cache/scratch/HOO-103-product-scope-control-and-compact-plan.md`. 이 문서 §4의 대응표가 제품 정본이다.
- review-plan 교정 이력: v87 record `dea8de41636e784c29ae3b1c9951f7aed8d68b730fbc8737597ba36af602c1a1`, v88 record `4389e65cd9c1530747b37a256472769fb5ef45583fe8d377dedeaa2db27a60c4`(major 8)
- 수정하지 않는 유효 문서: 원 설계 `docs/superpowers/specs/2026-11-23-portfolio-layout-redesign-design.md`(§n), resume 설계 `docs/superpowers/specs/2026-11-24-portfolio-redesign-resume-design.md`
- 감사 증거로 보존하고 확장하지 않는 것:
  - phase `HOO-81-portfolio-redesign-official-runner-resume`과 commit `3887bec96f0d4bcdd21519d2cb443b3cdd3352d9`
  - color-resume 계획
  - 원 phase step 0~39, resume step 0~16의 산출물(재실행하지 않음)
- step 경계는 원 resume 계획의 작업 단위를 재사용한다. step 수 12는 정책 비례성 휴리스틱(5~12) 범위 안이다.
- `CLAUDE.md` 또는 회사 승인 정책과 충돌하면 그쪽이 우선하고, 실행을 중단한다.

## C0. 공통 선행조건 (모든 step, 쓰기 전)

- 쓰기 전에 다음을 읽는다:
  - `CLAUDE.md`, 회사 정책, compact 대응표
  - 원 설계(특히 §3·§4·§5·§6·§7·§11.2), resume 설계
  - 해당 step이 다루는 현행 source와 spec
- 충돌, 누락, 해석 불가 중 하나라도 있으면 아무것도 쓰지 않고 중단·보고한다.
- 모든 step 공통: AC가 실패하면 그 자리에서 중단한다. 증거를 기록하고, 복구는 C8 절차로만 한다.

## C1. 제품 계약 (불변)

- **`js/data.js`**: PROJECTS index 1·5·7의 `title` 줄 바로 다음에 `featured: true,`를 넣는다. 정확히 3줄만 추가하고, 나머지 bytes는 step 0 baseline HEAD와 같아야 한다(v70b).
- **대표 카드**
  - 컨테이너: `#heroFeatured`(div, role `region`, aria-label `대표 프로젝트`)는 `#heroStats`의 바로 다음 형제다.
  - 카드: `button[type=button]` 3개, data-project 1·5·7. 각 카드에 `span`이 정확히 2개이고 nested interactive는 0개다.
  - 동작: click이나 Enter로 모달이 열린다. 모달을 닫는 모든 경로에서 trigger로 focus가 돌아온다.
- **FINAL 섹션 구조**(원 §4 표를 그대로 옮김)

| 순서 | id | class | kicker | heading |
|---|---|---|---|---|
| 1 | hero | hero | 없음 | h1 `#heroName` |
| 2 | career | section | `01 — Career` | h2 경력 &amp; 창업 |
| 3 | projects | section section-alt | `02 — Projects` | h2 프로젝트 &amp; 제품 |
| 4 | strengths | section | `03 — Strengths` | h2 업무상 강점 (section-sub 유지) |
| 5 | about | section section-alt | `04 — About` | h2 소개 |
| 6 | contact | section | `05 — Contact` | h2 연락처 |

  - about: 본문 뒤에 `h3.subsection-title` 기술 스택 + `#skillsGrid`(skill-group 제목은 h4). contact: `.contact-card`와 h3 함께 만들어요는 그대로 둔다.
  - nav와 스크롤스파이 배열은 career, projects, strengths, about, contact 순서다. `.scroll-hint`의 href는 `#career`다.
  - 콘텐츠 변경은 원 §5 허용 예외 (1)~(5)만 허용한다: featured 3줄, kickers의 FINAL 집합, sectionTitles의 FINAL 집합과 `h3.subsection-title` 기술 스택 정확히 1개, nav·섹션 순서, skill-group heading level. 그 밖의 문구·수치는 바꾸지 않는다.
- **보존**: 색, 서체 asset·weight, 이미지·아이콘, PROJECTS 13개와 그 순서. `css/themes.css`는 읽기 전용이다.
- **색 변경**: 확인된 color-contrast 결함을 고칠 때만, 기존 token `var(--x)`를 써서 선언 단위로 최소한만 바꾼다.
- **레이아웃**: 원 §3·§7·§11.2를 따른다. 기대값은 `tests/fixtures/claude-design-intake.json`의 tokens(`sectionPaddingPx`, `hitTargetMinPx`, `heroAreas`)에서 읽는다.
- **현재 DOM의 axe 10개 시나리오**: 위반 0.

## C2. 범위 금지

- 만들지 않는 것: 범용 mapper, influence 또는 transaction framework, custom coordinator, 새 공통 helper, 새 Harness 기능.
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
- `AXE0`: 아래를 순서대로 실행한다. baseline이 pending이든 check든 그것을 완료 증거로 보지 않는다.
  1. `T specs/axe-helper.spec.js`
  2. `sh tests/scripts/with-env.sh node tests/helpers/axe.js --reset`
  3. `env AXE_COLLECT=1 sh tests/scripts/with-env.sh npm --prefix tests test -- specs/axe.spec.js`
  4. `sh tests/scripts/with-env.sh node tests/helpers/axe.js --merge --out tests/.tmp/axe-current.json`
  5. `sh tests/scripts/with-env.sh node tests/helpers/axe.js --assert-no-violations --collected tests/.tmp/axe-current.json`
- `OWN_SPEC <p>`: 그 spec을 생성하거나 보강하는 step에서만 쓴다.
  `python3 -I -c "import os,stat,sys; p=sys.argv[1]; sys.exit('own-spec: '+p) if not os.path.lexists(p) or not stat.S_ISREG(os.lstat(p).st_mode) else print('own-spec: OK '+p)" <p>`
- `SPEC_GATE`: step 11에서만 쓴다.
  `python3 -I -c "import os,stat,sys; P=['tests/specs/featured.spec.js','tests/specs/focus-modal.spec.js','tests/specs/screenshots.spec.js','tests/specs/final-contract.spec.js']; bad=[p for p in P if not os.path.lexists(p) or not stat.S_ISREG(os.lstat(p).st_mode)]; sys.exit('spec-gate: '+','.join(bad)) if bad else print('spec-gate: OK 4')"`
- `SHOT <id>` = `env COMPACT_RUN_ID=<id> sh tests/scripts/with-env.sh npm --prefix tests test -- specs/screenshots.spec.js`

## C4. 허용 범위

- tracked 파일(exact, index와 동일)
  - product: `index.html`, `css/style.css`, `js/main.js`, `js/data.js`
  - 기존 검증 파일(최소 수정): `tests/scripts/verify-scope.mjs`, `tests/specs/verify-scope-resume.spec.js`, `tests/helpers/design-guard-color-rules.js`, `tests/specs/design-guard-color-rules.spec.js`
  - 신규 spec 4개:
    - `tests/specs/featured.spec.js`: 생성 1, 보강 2·3
    - `tests/specs/final-contract.spec.js`: 생성 4, 보강 5·6·7·10
    - `tests/specs/focus-modal.spec.js`: 생성 8
    - `tests/specs/screenshots.spec.js`: 생성 10
- runtime 쓰기는 ignore 대상인 다음 경로만 허용한다: `tests/.tmp/**`, `tests/screenshots/**`, `tests/test-results/**`, `tests/.npm-cache/**`. tracked 허용 파일과 verify-scope 면제는 넓히지 않는다.

## C5. step 구성 (예상 시간은 테스트 실행 포함 20분 이하, hard timeout 30분, 실행 중 임의 분할 금지)

| # | name | 원 resume 경계 | 예상 |
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

- **`renderFeaturedProjects(): void`**
  - PROJECTS의 원래 index를 보존하고, 1·5·7을 `#heroFeatured`에 `button`과 `span` 2개로 렌더한다.
  - boot에서 grid render 직후 1회만 호출한다.
  - container의 click·keydown은 위임으로 처리하며 `openProjectModal(projectIndex, triggerElement = document.activeElement)`를 부른다.
  - 모달을 닫는 모든 경로에서 저장해 둔 trigger로 focus를 돌려준다.
- **`trapFocus(container, { returnFocusTo = null } = {}): () => void`**
  - document keydown handler는 1개이고 trap stack을 둔다. Tab은 stack 맨 위 trap만 처리한다. 반환하는 release는 여러 번 불러도 결과가 같다.
  - modal:
    - 열 때 trap을 push한다.
    - 닫을 때 release하고 trigger로 focus를 돌려준다.
  - lightbox:
    - modal 위에 trap을 push한다.
    - 첫 Esc는 lightbox가 소비한다. release하고 `.shot-zoom`으로 focus를 돌려준다. 이때 modal trap이 다시 stack 맨 위가 된다.
    - 다음 Esc가 modal을 닫는다.
  - 기존의 개별 lightbox Tab listener는 제거한다.
- **`HOO81_COLOR_V52_ALLOW`**(`tests/helpers/design-guard-color-rules.js`의 export)
  - 원소 형식: `{file, chain, selector, occurrence, prop, base, to}`
    - `chain`: 기존 design-guard parser의 at-rule chain
    - `occurrence`: 같은 file·chain·selector rule 중 몇 번째 등장인지(0부터)
  - guard가 예외로 보는 것은 그 선언 하나의 값이 `base`이거나 정확히 `to`인 경우뿐이다. rule 전체를 예외로 빼지 않는다.

## C7. screenshot (`screenshots.spec.js`, `test.describe.serial`)

- 출력 디렉터리: `tests/screenshots/compact-${COMPACT_RUN_ID}/`. `COMPACT_RUN_ID`는 `^[a-z0-9-]{1,32}$` 형식이어야 한다. 실행을 시작할 때 이 디렉터리가 이미 있으면 실패한다.
- 고정 15장:
  - `page-{project}.png`: Playwright project 6개 각각
  - `modal-project-{1|5|7}-{desktop-dark|desktop-light}.png`: 6장
  - `menu-open-mobile-dark.png`
  - `lightbox-desktop-dark.png`: 기존 helper가 찾은 첫 shots project ID를 기록한다
  - `print-desktop-light.png`
- 같은 serial 블록의 마지막 test가 다음을 처리한다.
  - 디렉터리의 png 목록이 위 15개와 정확히 같은지 확인한다(누락·중복·초과 없음).
  - 각 파일의 SHA-256을 계산한다.
  - `{runId, files: [{path, sha256}], lightboxProject}`를 `tests/.tmp/compact/screenshots-${COMPACT_RUN_ID}.json`에 쓴다.
- `final-contract.spec.js`는 screenshot 산출물에 의존하지 않는다.

## C8. 실패·복구 (자동 수정 루프 없음)

- 어느 step에서든 AC가 실패하면 runner를 즉시 멈춘다.
- 다음을 evidence와 작업 스레드에 기록하고 blocker 상태로 둔다: HEAD, status, diff, 실패 로그, 마지막 성공 step, 원인 추정 파일.
- 같은 step에서 즉시 수정하거나 재실행하지 않는다. 자동 재실행, 파괴적 Git도 금지다.
- 복구는 별도로 검토·승인된 exact 복구 cycle에서만 한다. 그 cycle에는 다음을 명시한다.
  - 원인 파일: 원래 소유 step의 허용 파일 중에서
  - 재검증 명령: 소유 step의 AC, 그다음 step 11 AC 전체
- 실행 주체는 외부 Harness runner다.
- 결과가 불명확하거나, 중대성에 이견이 있거나, 승인이 만료·변경되면 새 exact 승인 전까지 재개하지 않는다.

## C9. 흐름 (phase 밖 운영 절차)

1. plan-only materialize·commit → 공식 review-plan CLEAN → 대표 exact `APPROVE HOO-81 PLAN <sha40> REVIEW <sha64>`. 이 승인 전에는 source를 쓰지 않는다.
2. runner가 step 0~11을 실행한다.
3. step 11이 PASS하면 runner가 candidate HEAD에서 다음을 순서대로 수행한다.
   - `testCommand`
   - exact range `<baselineHead>..<candidateHead>` GPT-6 Astra review
   - `verify-final`: tested = reviewed = HEAD
4. review에서 major나 blocker가 남으면 CLEAN이 아니다. 별도 승인된 C8 cycle → 재테스트 → 재리뷰로 처리한다. 임의로 반복하거나 등급을 낮추지 않는다.
5. push와 OPEN PR은 runner 밖에서, 대표의 별도 승인을 받은 뒤 한다. merge·deploy는 하지 않는다.

## C10. verify-scope 면제

- prefix·glob을 쓰는 runtime 면제는 금지한다.
- `HARNESS_OWNED_FILES`에 아래 exact committed path만 추가한다(committed만 면제, staged·worktree는 위반).
  - 이 설계 문서
  - `phases/HOO-81-portfolio-redesign-compact-completion/index.json`, `step0.md`~`step11.md`
  - step 0이 baseline HEAD에서 열거한 이력 계획의 committed exact path: `phases/HOO-81-portfolio-redesign-official-runner-resume/**`, `phases/HOO-81-portfolio-redesign-color-resume/**`, `docs/superpowers/specs/2026-11-25-*`
- 이 범위 밖의 경로가 outside-scope로 나오거나, runner의 metadata 갱신 때문에 `harness-uncommitted`가 나오면 면제를 넓히지 않는다. 중단하고 보고한다.
