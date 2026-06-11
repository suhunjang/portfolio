# 개인 포트폴리오

풀스택 개발자 & AI 제품을 사업화하는 CTO를 위한 1페이지 포트폴리오 사이트입니다.
빌드 도구 없이 **순수 HTML / CSS / JS**로 제작되어 GitHub Pages에 바로 배포할 수 있습니다.

## ✨ 특징

- 🌗 **다크 / 라이트 모드** — 토글 + `localStorage` 저장, 최초 방문 시 시스템 설정 자동 반영
- 📱 **반응형** — 모바일 · 태블릿 · 데스크톱 대응 (모바일 햄버거 메뉴)
- 🎬 **인터랙션** — 타이핑 애니메이션, 스크롤 진입 reveal, 호버 효과 (`prefers-reduced-motion` 존중)
- ⚡ **빌드 불필요** — 의존성/번들러 없음, 파일만 올리면 동작

## 📁 구조

```
portfolio/
├── index.html        # 전체 마크업
├── css/
│   ├── themes.css    # 색상/테마 변수 (라이트·다크)
│   └── style.css     # 레이아웃·컴포넌트·반응형·애니메이션
├── js/
│   ├── data.js       # ← 콘텐츠 데이터 (여기만 고치면 됩니다)
│   └── main.js       # 테마·네비·애니메이션·렌더링 로직
├── assets/
│   └── favicon.svg
├── .nojekyll         # GitHub Pages Jekyll 비활성화
└── README.md
```

## ✏️ 내용 수정하기

대부분의 내용은 **`js/data.js` 한 파일**에서 수정합니다.

- `PROFILE` — 이름, 이니셜, 타이틀(타이핑 문구), 소개, 이메일, GitHub/LinkedIn 링크
- `STATS` — Hero의 핵심 지표 숫자
- `CAREER` — 경력/창업 타임라인 (최신순)
- `PROJECTS` — 프로젝트/제품 카드 (`accent`: `violet` / `blue` / `cyan`)
- `SKILLS` — 카테고리별 기술 스택

> TODO 주석이 달린 placeholder(GitHub/LinkedIn URL, 프로젝트 링크 등)를 실제 값으로 바꾸세요.

색상 테마를 바꾸려면 `css/themes.css`의 `--accent`, `--accent-2` 변수를 수정하세요.

## 🚀 배포 (GitHub Pages)

1. GitHub에 저장소를 만들고 이 폴더의 파일을 푸시합니다.
   ```bash
   git init
   git add .
   git commit -m "Add portfolio site"
   git branch -M main
   git remote add origin https://github.com/<사용자명>/<저장소>.git
   git push -u origin main
   ```
2. 저장소 **Settings → Pages** 로 이동
3. **Source**: `Deploy from a branch`, **Branch**: `main` / `/ (root)` 선택 후 저장
4. 잠시 후 `https://<사용자명>.github.io/<저장소>/` 에서 확인

> 저장소 이름을 `<사용자명>.github.io` 로 만들면 루트 도메인(`https://<사용자명>.github.io/`)으로 바로 서비스됩니다.

## 🔍 로컬에서 보기

`index.html`을 브라우저로 그냥 열어도 동작합니다.
(원하면 정적 서버 사용 — 예: `npx serve` 또는 VS Code Live Server)
