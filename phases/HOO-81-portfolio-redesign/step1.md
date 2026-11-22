# Step 1 — hero-featured-projects

설계: §5.1

## 목표

히어로를 채용·영입 의사결정자용 첫 화면으로 재구성하고, 대표 프로젝트 3개를 노출한다.

## 변경 허용 파일

- `index.html` (hero 영역)
- `css/style.css`
- `js/main.js`
- `js/data.js` (Motion AD, VigoRight (의료 AI/VR), Lost Energy Intel 3개 항목에 `featured: true` 한 줄씩 추가만 허용)
- `tests/**`

## 작업 (TDD: 테스트를 먼저 작성해 실패를 확인한 뒤 구현)

1. `tests/specs/hero.spec.js`를 작성한다.
   - 대표 카드 컨테이너는 `#heroFeatured`, 카드에는 `[data-featured-card]`를 둔다. 카드가 정확히 3개이고 제목이 위 3개 프로젝트와 같은지 확인한다.
   - 1280×800에서 확인할 것:
     - `#heroName`, tagline, `#heroStats`의 bounding box가 첫 viewport(y<800) 안에 있다.
     - 대표 카드 3개 제목의 top이 1200px 미만이다.
   - 대표 카드를 클릭하거나 Enter를 누르면 해당 프로젝트의 모달이 열린다. 모달 제목이 카드 제목과 같아야 한다.
   - 주 CTA는 '프로젝트 보기'(btn-primary), '연락하기'는 btn-ghost인지 확인한다.
   - `.hero-eyebrow`와 `#typed`가 여전히 존재하고 동작하는지 확인한다.
2. `js/data.js` 3개 항목에 `featured: true`를 추가한다. 다른 필드는 건드리지 않는다.
3. `index.html` 히어로 순서를 바꾼다: 이름 → tagline → 역할(타이핑) → 요약 → CTA → STATS → `#heroFeatured`.
4. `js/main.js`에서 `PROJECTS.filter(p => p.featured)`로 대표 카드를 렌더링한다. 카드는 `button` 또는 링크 요소로 만들고, 클릭하면 원래 index로 `openProjectModal(idx)`를 호출한다. 카드 근거 문구는 data.js에 이미 있는 문자열(예: 프로젝트 요약 필드)만 쓰고, 새 문구를 하드코딩하지 않는다.
5. CSS 작업:
   - 인사말과 타이핑 문구의 크기·색 비중을 낮춘다.
   - STATS는 데스크톱에서 4열, 모바일에서 2×2로 배치한다.
   - 대표 카드는 데스크톱 3열, 768px 2+1, 375px 1열이다.
   - 기존 토큰(`--accent` 등)만 쓰고 그라데이션·글로우를 추가하지 않는다.

## 완료 기준

- `npm --prefix tests test`가 전부 통과한다(baseline 포함).
- `git diff js/data.js`에 `featured: true` 3줄 추가만 있다.
