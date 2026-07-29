# 포트폴리오 시각 리디자인 ("경영자의 절제") Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 개발자 포트폴리오의 전형적 기본값(보라/시안 그라데이션·배경 그리드·글로우·Space Grotesk)을 걷어내고, CTO·COO 포지셔닝에 맞는 절제된 시각 언어로 전환한다.

**Architecture:** 빌드 도구 없는 정적 사이트. 변경은 `css/themes.css`(변수)와 `css/style.css`(규칙)에 한정한다. HTML 구조와 JS 콘텐츠는 건드리지 않는다. 대부분의 전환은 CSS 변수 교체만으로 전파되므로, 변수 레이어 → 개별 규칙 순으로 진행한다.

**Tech Stack:** 순수 CSS (변수 + 미디어쿼리). 빌드 없음. Google Fonts CDN.

**Spec:** `docs/superpowers/specs/2026-07-29-quiet-executive-redesign-design.md`

## Global Constraints

- **빌드 도구 도입 금지** — npm/번들러 없음 (`CLAUDE.md` 규칙). 파일을 그대로 GitHub Pages에 올려 동작해야 한다.
- **`js/data.js`, `js/main.js` 수정 금지** — 콘텐츠와 렌더링 로직은 이번 작업 범위 밖.
- **`index.html` 수정 금지** — 폰트 링크 포함. Space Grotesk 링크는 SVG가 쓰므로 유지.
- **`assets/favicon.svg` 수정 금지** — Space Grotesk 사용 중.
- **`--font-display` / `--accent-2` / `.thumb-*` 클래스명 삭제 금지** — 각각 style.css 21곳, 8곳, data.js가 참조. 값만 교체한다.
- **테마 토글 동작 보존** — `localStorage` 키 `portfolio-theme`, HTML 기본값 `data-theme="dark"`.
- **`prefers-reduced-motion` 대응 보존.**
- 액센트 색: 라이트 `#1e3a5f`, 다크 `#7ea8d8`.

## File Structure

| 파일 | 책임 | 이번 변경 |
|---|---|---|
| `css/themes.css` | 색·서체·형태 변수 정의 | 전면 교체 (Task 1) |
| `css/style.css` | 레이아웃·컴포넌트 규칙 | 그라데이션/그림자/여백 정리 (Task 2–5) |

Task 1이 변수 레이어를 바꾸면 사이트 전체 톤이 한 번에 전환된다. Task 2 이후는 변수로 흡수되지 않는 개별 규칙(하드코딩된 그라데이션, 여백, hover)을 정리한다.

---

### Task 1: 변수 레이어 교체 — 색·서체·형태

**Files:**
- Modify: `css/themes.css` (전체)

**Interfaces:**
- Produces: `--accent`, `--accent-2`, `--accent-soft`, `--bg`, `--bg-elev`, `--bg-alt`, `--text`, `--text-muted`, `--text-faint`, `--border`, `--border-strong`, `--nav-bg`, `--tag-bg`, `--tag-text`, `--grid-line`, `--glow`, `--card-hover-border`, `--font-sans`, `--font-display`, `--container`, `--radius`, `--radius-sm`, `--shadow`, `--ease`
- 변수 이름은 **하나도 바꾸지 않는다**. `style.css`가 전부 참조 중.

- [ ] **Step 1: `css/themes.css` 전체를 아래 내용으로 교체**

```css
/* ==========================================================================
   테마 변수 — 라이트(기본) / 다크
   data-theme 속성으로 전환. 색상/간격은 모두 여기서 관리.
   ========================================================================== */

:root {
  /* 브랜드 액센트 — 딥 잉크 블루 단일 계열 */
  --accent: #1e3a5f;
  --accent-2: #2c5580;        /* accent의 밝은 변주 (그라데이션 잔존 참조용) */
  --accent-soft: rgba(30, 58, 95, 0.07);

  /* 타이포 — Inter 단일 (Space Grotesk는 data.js의 SVG 전용) */
  --font-sans: "Inter", system-ui, -apple-system, "Segoe UI", Roboto, sans-serif;
  --font-display: var(--font-sans);

  /* 레이아웃 */
  --container: 1100px;
  --radius: 6px;
  --radius-sm: 4px;
  --shadow: none;

  /* 모션 */
  --ease: cubic-bezier(0.22, 1, 0.36, 1);
}

/* ---------- 라이트 테마 ---------- */
:root,
[data-theme="light"] {
  --bg: #fafafa;
  --bg-elev: #ffffff;
  --bg-alt: #f4f4f5;
  --text: #18181b;
  --text-muted: #52525b;
  --text-faint: #8a8a93;
  --border: rgba(0, 0, 0, 0.09);
  --border-strong: rgba(0, 0, 0, 0.16);
  --nav-bg: rgba(250, 250, 250, 0.85);
  --tag-bg: rgba(0, 0, 0, 0.045);
  --tag-text: #52525b;
  --grid-line: transparent;
  --glow: transparent;
  --card-hover-border: rgba(30, 58, 95, 0.35);
}

/* ---------- 다크 테마 ---------- */
[data-theme="dark"] {
  --accent: #7ea8d8;
  --accent-2: #9dbde4;
  --accent-soft: rgba(126, 168, 216, 0.12);

  --bg: #0d0f12;
  --bg-elev: #16181c;
  --bg-alt: #111316;
  --text: #f4f4f5;
  --text-muted: #a1a1aa;
  --text-faint: #71717a;
  --border: rgba(255, 255, 255, 0.10);
  --border-strong: rgba(255, 255, 255, 0.18);
  --nav-bg: rgba(13, 15, 18, 0.85);
  --tag-bg: rgba(255, 255, 255, 0.06);
  --tag-text: #a1a1aa;
  --grid-line: transparent;
  --glow: transparent;
  --card-hover-border: rgba(126, 168, 216, 0.45);
}
```

- [ ] **Step 2: 변수 참조 무결성 검증**

`style.css`가 참조하는 모든 변수가 `themes.css`에 정의되어 있는지 확인한다.

Run:
```bash
cd "C:/shjang/personal/resume/portfolio" && \
comm -23 \
  <(grep -oh 'var(--[a-z0-9-]*' css/style.css | sed 's/var(//' | sort -u) \
  <(grep -oh '^\s*--[a-z0-9-]*' css/themes.css | tr -d ' ' | sort -u)
```
Expected: **아무 것도 출력되지 않음** (미정의 변수 0개). 출력이 있으면 그 변수를 `themes.css`에 추가해야 한다.

- [ ] **Step 3: 육안 확인 — 톤 전환**

`index.html`을 브라우저로 연다. 확인 항목:
- 전체가 회색조 + 남색 액센트로 바뀌었는가
- 다크/라이트 토글 시 양쪽 모두 텍스트가 읽히는가 (대비 확보)
- 히어로 이름 그라데이션이 아직 남아 있음 → **정상** (Task 2에서 처리)

- [ ] **Step 4: 커밋**

```bash
cd "C:/shjang/personal/resume/portfolio" && \
git add css/themes.css && \
git commit -m "style: replace theme variables with ink-blue neutral palette"
```

---

### Task 2: 배경 데코 제거 + UI 그라데이션 단색화

**Files:**
- Modify: `css/style.css:41-62` (`.bg-grid`, `.bg-glow`)
- Modify: `css/style.css:103` (`.brand-mark`)
- Modify: `css/style.css:189-193` (`.btn-primary`)
- Modify: `css/style.css:243`, `:280` (`.typed`, `.stat-value` 계열)
- Modify: `css/style.css:385`, `:414`, `:506`, `:816`, `:902`

**Interfaces:**
- Consumes: Task 1의 `--accent`, `--accent-soft`, `--bg-elev`, `--border`

- [ ] **Step 1: 배경 데코 숨김**

`.bg-grid`와 `.bg-glow` 규칙 **각각의 첫 줄**(`position: fixed;` 앞)에 `display: none;`을 추가한다. 규칙 전체를 지우지 않는 이유 — 되돌리기 쉽고 `index.html`의 div를 건드릴 필요가 없다.

```css
.bg-grid {
  display: none;
  position: fixed;
  /* 이하 기존 유지 */
```

```css
.bg-glow {
  display: none;
  position: fixed;
  /* 이하 기존 유지 */
```

- [ ] **Step 2: 그라데이션 5곳을 단색으로 교체**

각 줄을 아래로 바꾼다.

`css/style.css:103` — `.brand-mark`:
```css
  background: var(--accent);
```

`css/style.css:189` — `.btn-primary`:
```css
  background: var(--accent);
```

`css/style.css:385` — `.about-avatar`:
```css
  background: var(--accent);
```

`css/style.css:506` — 프로젝트 카드 상단 라인:
```css
  background: var(--accent);
```

`css/style.css:816` — 타임라인 세로선:
```css
  background: var(--border-strong);
```

- [ ] **Step 3: 텍스트 그라데이션 2곳 제거**

그라데이션 텍스트 처리를 쓰는 규칙은 정확히 2개다. 각각 블록 전체를 아래로 교체한다.

`css/style.css:242-247` — `.typed` (기존 4줄 → 1줄):
```css
.typed {
  color: var(--accent);
}
```

`css/style.css:275-284` — `.stat-value` (그라데이션 4줄만 제거, 나머지 유지):
```css
.stat-value {
  display: block;
  font-family: var(--font-display);
  font-weight: 700;
  font-size: clamp(1.6rem, 4vw, 2.2rem);
  font-variant-numeric: tabular-nums;
  color: var(--text);
}
```

> **주의**: `-webkit-text-fill-color: transparent`를 지우지 않고 `color`만 넣으면 글자가 투명하게 남아 **보이지 않는다.** 위 교체는 4줄을 모두 걷어낸 형태다.
>
> `.stat-value`에 `font-variant-numeric`이 이미 포함되어 있으므로 **Task 4 Step 2는 건너뛴다.**

- [ ] **Step 4: 연락처 카드 radial 그라데이션 제거**

`css/style.css:902` 부근 `.contact-card`의 `background`를 단색으로:
```css
  background: var(--bg-elev);
```

- [ ] **Step 5: 잔존 그라데이션 개수 검증**

Run:
```bash
cd "C:/shjang/personal/resume/portfolio" && \
grep -n 'linear-gradient\|radial-gradient' css/style.css
```
Expected: `.bg-grid`/`.bg-glow` 내부(4줄, display:none이라 무해)와 `.thumb-*` 3줄(Task 3에서 처리)**만** 남아야 한다. 그 외 그라데이션이 보이면 누락된 것이다.

- [ ] **Step 6: 육안 확인**

브라우저 새로고침 후:
- 배경 그리드·글로우가 사라졌는가
- **히어로의 타이핑 텍스트가 보이는가** (Step 3의 함정 — 안 보이면 `-webkit-text-fill-color` 잔존)
- 버튼·브랜드 마크가 단색 남색인가

- [ ] **Step 7: 커밋**

```bash
cd "C:/shjang/personal/resume/portfolio" && \
git add css/style.css && \
git commit -m "style: remove background decor and flatten UI gradients"
```

---

### Task 3: 프로젝트 썸네일 색 재구성

**Files:**
- Modify: `css/style.css:527-529` (`.thumb-violet`, `.thumb-blue`, `.thumb-cyan`)

**Interfaces:**
- Consumes: 없음 (하드코딩 색값)
- Produces: 클래스명 3종 유지 — `js/main.js:176,258,259`가 `data.js`의 `accent` 값으로 참조

**배경 (읽고 시작할 것):** `js/data.js`가 프로젝트마다 `accent: "violet"|"blue"|"cyan"`을 지정하고, 그 값이 **썸네일 배경 클래스와 SVG 일러스트 내부 색 양쪽에** 쓰인다. 배경만 회색으로 바꾸면 일러스트와 따로 논다. 그래서 클래스명은 두고 **채도만 낮춘 잉크 블루 명도 변주**로 바꾼다.

- [ ] **Step 1: 3줄 교체**

`css/style.css:527-529`를 아래로 바꾼다. 그라데이션을 유지하되 채도를 크게 낮춘다 (SVG 일러스트가 배경 위에 얹히므로 완전 단색보다 미세한 그라데이션이 자연스럽다).

```css
.thumb-violet { background: linear-gradient(135deg, #3d4a5c, #55637a); }
.thumb-blue { background: linear-gradient(135deg, #2f4459, #456179); }
.thumb-cyan { background: linear-gradient(135deg, #37505c, #4d6b77); }
```

- [ ] **Step 2: 육안 확인 — 3종 모두**

브라우저에서 프로젝트 섹션을 연다. `data.js` 기준 각 accent별 최소 1개씩 카드를 열어 모달의 SVG 일러스트를 확인한다:
- `violet`: Motion AD 계열
- `blue`: ONYX / NDI 계열
- `cyan`: 상담 챗봇 계열

확인 항목:
- SVG 일러스트의 선·텍스트가 배경 대비 **읽히는가** (가장 중요 — 채도를 낮췄으므로 대비 부족 위험)
- 일러스트 색과 배경이 조화로운가

> 대비가 부족하면 위 색값의 명도를 낮춰(더 어둡게) 조정한다. SVG는 밝은 색 요소가 많다.

- [ ] **Step 3: 커밋**

```bash
cd "C:/shjang/personal/resume/portfolio" && \
git add css/style.css && \
git commit -m "style: desaturate project thumbnail palette to ink-blue range"
```

---

### Task 4: 타이포그래피 — 히어로 축소, 숫자 정렬, 키커

**Files:**
- Modify: `css/style.css:230` (`.hero-name` font-size)
- Modify: `css/style.css:275-280` 부근 (`.stat-value`)
- Modify: `css/style.css:324-332` 부근 (`.section-kicker`)

**Interfaces:**
- Consumes: Task 1의 `--font-display`(이제 Inter), `--text-faint`, `--accent`

- [ ] **Step 1: 히어로 이름 축소**

`css/style.css:230`:
```css
  font-size: clamp(2.4rem, 6vw, 3.6rem);
```
(기존 `clamp(2.6rem, 8vw, 5rem)`)

- [ ] **Step 2: (생략) 지표 숫자 정렬**

Task 2 Step 3에서 `.stat-value`를 교체할 때 `font-variant-numeric: tabular-nums`를 이미 넣었다. **이 단계는 할 일이 없다.** 확인만 한다:

Run:
```bash
cd "C:/shjang/personal/resume/portfolio" && grep -n 'tabular-nums' css/style.css
```
Expected: `.stat-value` 블록 내부에 1줄 출력.

- [ ] **Step 3: 섹션 키커를 대문자로**

`.section-kicker`는 **이미** `color: var(--accent)`와 `letter-spacing: 0.08em`을 갖고 있다(Task 1이 변수를 바꿨으므로 색은 자동으로 잉크 블루). 대문자 변환만 추가하고 굵기를 낮춘다.

`css/style.css:324-332`를 아래로 교체:
```css
.section-kicker {
  display: inline-block;
  font-family: var(--font-display);
  font-size: 0.78rem;
  font-weight: 500;
  letter-spacing: 0.12em;
  text-transform: uppercase;
  color: var(--accent);
  margin-bottom: 0.5rem;
}
```

- [ ] **Step 4: 육안 확인**

- 히어로 이름이 이전보다 작아지고 여백이 넉넉해졌는가
- 지표 숫자(15년+, ₩2억 등)의 자릿수가 흔들리지 않는가
- 섹션 번호(`01 — About`)가 남색 소문자→대문자로 바뀌었는가
- **전체 서체가 Inter 하나로 통일되었는가** (Space Grotesk의 기하학적 인상이 사라짐)

- [ ] **Step 5: 커밋**

```bash
cd "C:/shjang/personal/resume/portfolio" && \
git add css/style.css && \
git commit -m "style: tighten typographic hierarchy for restrained tone"
```

---

### Task 5: 여백 확대 + hover 정리

**Files:**
- Modify: `css/style.css:321` (`.section` padding-block)
- Modify: `css/style.css:140` (`.theme-toggle:hover`)
- Modify: `css/style.css:185-199` (`.btn` transition, `.btn-primary:hover`, `.btn-ghost:hover`)
- Modify: `css/style.css:495-513` 부근 (`.project-card` hover)

**Interfaces:**
- Consumes: Task 1의 `--border-strong`, `--card-hover-border`, `--accent-soft`

**핵심:** A 방향의 마무리. 색을 뺀 자리를 여백이 채운다.

- [ ] **Step 1: 섹션 여백 약 1.6배 확대**

`css/style.css:321`:
```css
.section { padding-block: clamp(6rem, 14vw, 11rem); }
```
(기존 `clamp(4rem, 10vw, 7rem)`)

- [ ] **Step 2: hover 부양 효과 제거 — 3곳**

`css/style.css:140` — `.theme-toggle:hover`:
```css
.theme-toggle:hover { border-color: var(--border-strong); }
```

`css/style.css:193` — `.btn-primary:hover`:
```css
.btn-primary:hover { opacity: 0.88; }
```

`css/style.css:199` — `.btn-ghost:hover`:
```css
.btn-ghost:hover { border-color: var(--border-strong); background: var(--accent-soft); }
```

- [ ] **Step 3: 버튼 transition에서 transform 제거**

`css/style.css:185-186`의 transition 목록에서 `transform`과 `box-shadow`를 뺀다:
```css
  transition: background 0.2s var(--ease), border-color 0.2s var(--ease),
    opacity 0.2s var(--ease);
```

- [ ] **Step 4: 프로젝트 카드 hover 정리**

카드는 `translateY(-6px)`로 크게 들린다. transition과 hover 양쪽을 손봐야 한다.

`css/style.css:498-499` — transition에서 `transform`·`box-shadow` 제거:
```css
  transition: border-color 0.28s var(--ease);
```

`css/style.css:510-514` — hover에서 부양·그림자 제거:
```css
.project-card:hover {
  border-color: var(--card-hover-border);
}
```

`css/style.css:506` — 카드 상단 라인은 Task 2 Step 2에서 이미 `var(--accent)` 단색으로 바뀌었다. 그대로 둔다(hover 시에만 나타나는 절제된 강조).

- [ ] **Step 5: 잔존 부양 효과 검증**

Run:
```bash
cd "C:/shjang/personal/resume/portfolio" && \
grep -n 'translateY(-' css/style.css
```
Expected: **아무 것도 출력되지 않음.**

> 패턴을 `translateY(-`로 넓게 잡은 이유: 카드가 `-6px`, 버튼이 `-2px`, 토글이 `-1px`로 값이 제각각이다. 특정 픽셀값을 나열하면 놓친다.

- [ ] **Step 6: 액센트 사용처 감사 — 스펙 §1 준수 확인**

스펙은 액센트를 **4곳으로 제한**한다: 링크 / 활성 네비 / 섹션 번호 / 주 CTA 버튼.

Run:
```bash
cd "C:/shjang/personal/resume/portfolio" && \
grep -n 'var(--accent)' css/style.css
```

출력된 각 줄이 아래 허용 목록에 속하는지 확인한다:

| 허용 | 규칙 |
|---|---|
| ✅ | `.nav-link.active` — 활성 네비 |
| ✅ | `.section-kicker` — 섹션 번호 |
| ✅ | `.btn-primary` — 주 CTA |
| ✅ | `.typed` — 히어로 타이핑(이름 강조, CTA에 준함) |
| ✅ | `.caret` — 타이핑 커서(`.typed`에 종속) |
| ✅ | `.brand-mark` / `.about-avatar` — 이니셜 마크(브랜드 아이덴티티) |
| ❌ | 그 외 — 중성색(`--border-strong`, `--text-muted`)으로 교체 |

허용 목록 밖의 사용처가 있으면 중성색으로 바꾼다. `--accent-soft`(hover 배경)와 `--card-hover-border`는 액센트 직접 사용이 아니므로 감사 대상이 아니다.

- [ ] **Step 7: 육안 확인 — 전체 통합 점검**

이 시점이 최종 상태다. 스펙의 검증 체크리스트를 전부 확인한다:

1. 전 섹션 렌더 정상 (히어로/About/강점/경력/프로젝트/스택+연락처)
2. 다크·라이트 토글 + `localStorage` 유지 + 양쪽 대비 확보
3. 프로젝트 모달의 SVG 서체가 깨지지 않음 (Space Grotesk 유지)
4. SVG 일러스트 색과 썸네일 배경 조화 (violet/blue/cyan 각 1개)
5. 모바일 ≤720px 햄버거 메뉴 동작
6. 스크롤 reveal · 타이핑 동작
7. 콘솔 에러 없음
8. 액센트 색 감사는 Step 6에서 완료 — 육안으로는 "남색이 과하게 흩어져 있지 않은가"만 본다

- [ ] **Step 8: 커밋**

```bash
cd "C:/shjang/personal/resume/portfolio" && \
git add css/style.css && \
git commit -m "style: expand section rhythm and quiet hover states"
```

---

## 롤백

문제 시 스펙 커밋 시점으로 되돌린다:
```bash
cd "C:/shjang/personal/resume/portfolio" && git checkout 3fba5c9 -- css/
```

## 미해결 위험

- **브라우저 검증 미확보**: Chrome 확장이 연결되어 있지 않다. 육안 확인 단계는 사용자가 `index.html`을 직접 열어 수행해야 한다. 확장이 연결되면 자동화 가능.
- **SVG 대비**: Task 3의 채도 축소가 SVG 일러스트 가독성을 해칠 수 있다. Step 2에서 반드시 3종 모두 확인한다.
