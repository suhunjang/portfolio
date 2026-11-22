# Step 2 — section-order-and-layout

설계: §5.2, §5.3

## 목표

섹션을 근거 우선 순서로 재배치하고, 각 섹션 레이아웃과 모바일 배치를 재구성한다.

## 변경 허용 파일

`index.html`, `css/style.css`, `css/themes.css`(필요 시 간격 토큰만), `js/main.js`, `tests/**`

## 작업 (테스트 먼저)

1. `tests/specs/layout.spec.js`를 작성한다.
   - `main > section` id 순서가 `hero, career, projects, strengths, about, contact`인지 확인한다.
   - `#navLinks a` 의 href 순서가 `#career, #projects, #strengths, #about, #contact`인지 확인한다.
   - section-kicker 번호가 01부터 순서대로 매겨졌는지 확인한다.
   - 모든 viewport에서 `document.documentElement.scrollWidth <= innerWidth`(가로 스크롤 없음)인지 확인한다.
   - 그리드 열 수를 확인한다. 카드들의 고유 offsetLeft 개수로 센다.
     - `#projectGrid`: 1280에서 3, 768에서 2, 375에서 1
     - `#strengthsGrid`: 1280에서 3, 768에서 2, 375에서 1
   - Career highlights가 375px에서 모두 보이는지(접히지 않음) 확인한다.
   - `#skillsGrid`가 `#about` 섹션 안에 있고, `#contactActions`가 `#contact` 섹션 안에 있는지 확인한다.
   - nav 앵커를 클릭하면 해당 섹션으로 스크롤되고 `.nav-link.active`가 갱신되는지 확인한다.
2. `index.html`에서 섹션 블록을 재배치한다.
   - About 본문 문구는 그대로 옮긴다.
   - skillsGrid는 about 섹션으로 옮긴다.
   - contact-card는 독립 `#contact` 섹션으로 분리한다.
   - 섹션 헤더의 라벨 텍스트는 유지하고 번호만 다시 매긴다. 기존 '05 — Stack & Contact' 헤더는 둘로 나눈다. 기존 라벨 단어만 재사용한다.
3. Career 타임라인: 데스크톱은 2열(기간 | 내용), ≤720px은 1열로 만든다.
4. 섹션 리듬:
   - 세로 여백을 통일한다.
   - `section-alt` 배경을 새 순서에 맞게 교차 배치한다.
   - 모든 섹션이 같은 head 패턴을 따르게 한다.
5. `main.js`에서 섹션 순서에 의존하는 코드(활성 nav 계산 등)가 있으면 수정한다.

## 완료 기준

- `npm --prefix tests test`가 전부 통과한다.
- 콘텐츠 보존 테스트(baseline)가 그대로 통과한다.
- 문구 변경은 kicker 번호 외에 없다.
