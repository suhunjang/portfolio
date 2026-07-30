/**
 * 포트폴리오 콘텐츠 데이터
 * ------------------------------------------------------------------
 * 이 파일만 수정하면 사이트 내용을 바꿀 수 있습니다.
 * 내용은 resume/ 의 실제 이력서(장수훈 CTO/COO)를 기반으로 작성됨.
 */

const PROFILE = {
  name: "장수훈", // 표시할 이름
  initials: "SH", // 로고/파비콘용 이니셜 (Sang Hoon / 장수훈)
  // Hero 타이틀에서 순환 타이핑되는 문구들 (COO·CTO 동등 병기)
  roles: [
    "COO · CTO",
    "Tech-Driven COO",
    "Full-Stack & AI Leader",
    "Product & Operations",
  ],
  tagline: "코드와 사업을 동시에 운영하는, 기술 베이스의 COO·CTO",
  // Hero 하단 한 줄 가치 제안
  summary:
    "15년간 웹·AI·데이터 플랫폼을 직접 개발하고, 그 위에서 조직과 사업을 운영해온 COO·CTO입니다. " +
    "DRM 보안 엔지니어로 출발해 실리콘밸리·영국계 기업에서 풀스택과 머신러닝을 깊이 익혔고, " +
    "지금은 트라이업에서 50명 조직의 운영(COO)과 기술(CTO)을 함께 이끌며 기술을 매출로 연결합니다.",
  location: "경기 시흥, 대한민국",
  email: "jsslh@naver.com",
  phone: "010-9999-6241",
  // 소셜/외부 링크 (없으면 빈 문자열 → 자동 숨김)
  social: {
    github: "", // TODO: GitHub URL이 있으면 입력
    linkedin: "", // TODO: LinkedIn URL이 있으면 입력
    website: "",
  },
};

// 핵심 지표 (Hero/About 영역의 강조 숫자)
// 근거: 이력서 "경력 사항(총 15년 2개월)" · "□ 업무상 강점" 6개 항목.
// ※ 연 2억(ONYX 에너지)과 연 1.2억(트라이업 인프라)은 회사·시기가 다르므로 합산하지 않는다.
const STATS = [
  { value: "15년+", label: "Software & Leadership" },
  { value: "50명", label: "4개 부문 통합 운영 (COO)" },
  { value: "연 1.2억", label: "클라우드 인프라 비용 절감" },
  { value: "80%", label: "AI 마케팅 프로세스 단축" },
];

// 경력 / 창업 타임라인 (최신순)
const CAREER = [
  {
    period: "2024.09 — 현재",
    role: "COO · CTO (운영 총괄 이사)",
    company: "㈜트라이업 (Triup) · 병의원 SaaS / AI 마케팅",
    type: "리더십",
    summary:
      "비비지 네트워크(톡스앤필) 계열 병의원 솔루션 기업. 영업·마케팅·고객관리·개발 4개 부문(50명)을 통합 운영하며 AI 마케팅 자동화와 SaaS 제품을 총괄.",
    highlights: [
      "GPT·RAG 기반 마케팅 자동화 솔루션 Motion AD 기획·운영 — 콘텐츠 프로세스 80% 단축",
      "Motion Series(차트·사이니지·챗봇·매출분석) 통합 아키텍처로 운영 효율 40% 향상",
      "LLM·RAG 상담 챗봇 도입으로 사용자 전환율 20% 증가, 상담 인건비 50% 절감",
      "클라우드 인프라 최적화 + CI/CD로 연간 1.2억 원 비용 절감",
    ],
    tags: ["LLM/RAG", "LangChain", "Node.js", "Next.js", "AWS", "Leadership"],
  },
  {
    period: "2023.03 — 2024.07",
    role: "개발 운영 이사 (Team Leader)",
    company: "㈜Tenetus (구 M2S Korea) · 의료 AI / VR",
    type: "리더십",
    summary:
      "VR 기반 시각 측정 장비에 AI를 접목해 뇌병변을 판별하는 의료 장비 기업. AI 진단 서비스의 연구→상용화 전 과정을 총괄.",
    highlights: [
      "VR 안과·신경과 검사 장비 VigoRight 개발 총괄, 대학병원·개원가 진입으로 약 3억 원 매출",
      "RANSAC 기하 정합 + CNN 회귀로 안구 토션 각도 정량화, Grad-CAM XAI로 임상 신뢰도 확보",
      "고려대 의료진과 협업해 시야 데이터 기반 뇌병변 판별 AI(NDI) 설계",
      "ChatGPT·RAG·Fine-tuning 기반 의료용 챗봇 개발",
    ],
    tags: ["AI/ML", "Computer Vision", "Django", "PyTorch", "XAI", "의료 AI"],
  },
  {
    period: "2018.08 — 2022.11",
    role: "Senior Developer · ML Engineer",
    company: "ONYX Insight (BP Group) · 풍력 예측 유지보수",
    type: "글로벌",
    summary:
      "에너지 그룹 BP가 100% 투자한 영국계 예측 유지보수 기업. 풍력 SCADA 데이터를 분석하는 ML 모델과 풀스택 시스템을 개발.",
    highlights: [
      "Lost Energy 예측 모델로 풍력발전 에너지 손실을 사전 감지 — 연간 2억 원 원가 절감",
      "NLP 기반 Case Management System(AI-Hub) 및 문서 자동분류 추천 시스템 구축",
      "FieldPro(풍력단지 관리) Front/Back/iOS 전 영역 개발 및 광산 산업으로 확장",
      "영국 본사와 실시간 글로벌 협업 및 기술 커뮤니케이션",
    ],
    tags: ["Machine Learning", "NLP", "Python", "React", "GraphQL", "AWS"],
  },
  {
    period: "2016.12 — 2018.08",
    role: "Technical Leader (Front-End)",
    company: "트루라이트 (Truelight) · 실리콘밸리 / 차량관리",
    type: "글로벌",
    summary:
      "차량 관리 시스템(FleetUp)의 프론트엔드 기술 리더로서 UI/UX 고도화와 서버리스 아키텍처 전환을 주도.",
    highlights: [
      "AWS Lambda·Node.js 서버리스로 Salesforce 연동 e-commerce 셀프서비스 구현",
      "Frontend-Backend 디커플링 및 대시보드 시각화로 렌더링 성능 향상",
      "Oracle 대용량 쿼리 튜닝으로 응답속도 개선",
    ],
    tags: ["TypeScript", "AngularJS", "AWS Serverless", "Node.js"],
  },
  {
    period: "2013.08 — 2016.11",
    role: "Web개발 선임 (PL)",
    company: "미라콤아이앤씨 · 삼성전자 프로젝트",
    type: "재직",
    summary:
      "통합생산관리시스템 전문 기업에서 삼성전자 제조 인프라 포탈과 하이브리드 앱 개발을 주도.",
    highlights: [
      "삼성전자 제조 인프라 포탈 & 하이브리드 앱 개발 (Spring/Java)",
      "삼성전자 PenUp 모바일 웹앱, 다국어 Online Help 개발",
      "대용량 데이터 쿼리 튜닝 및 현장 업무 효율 개선",
    ],
    tags: ["Spring", "Java", "jQuery Mobile", "HTML5"],
  },
  {
    period: "2010.10 — 2013.07",
    role: "DRM 개발 (대리)",
    company: "디지캡 (DigiCAP) · 방송 보안",
    type: "재직",
    summary:
      "유료방송 CAS·N-Screen 솔루션 기업에서 DRM 및 모바일 보안 모듈을 개발하며 엔지니어 커리어를 시작.",
    highlights: [
      "OMA 1.0 기반 DRM Packager/Depackager 구현 (KT uCloud)",
      "Mobile TV DRM HTTPS 보안 전환, 멀티 디바이스 키 관리",
      "ARM TrustZone DRM 및 SKT DRM(Android/iOS/eBook) 개발",
    ],
    tags: ["C/C++", "Objective-C", "Java JNI", "Security"],
  },
];

/* ------------------------------------------------------------------
 * 프로젝트 비주얼 (저작권 안전 — 코드로 생성한 SVG)
 * ------------------------------------------------------------------
 * 외부 이미지를 검색해 가져오면 저작권 문제가 있으므로, 각 제품의 컨셉을
 * 표현하는 추상 SVG를 직접 생성한다. accent별 색상은 thumb-* 와 통일.
 * makeVisual(accent, body) → 16:9 그라데이션 배경 + 컨셉 그래픽.
 */
const VIS_ACCENT = {
  violet: { a: "#8fa3bd", b: "#a8b8cd", glow: "#7e93b0" },
  blue: { a: "#7fa0c4", b: "#9bb4d1", glow: "#6b8fb8" },
  cyan: { a: "#84a8b5", b: "#9dbcc6", glow: "#6f9aa8" },
};

function makeVisual(accent, inner) {
  const c = VIS_ACCENT[accent] || VIS_ACCENT.violet;
  // id 충돌 방지를 위해 accent를 접미사로
  const gid = "g_" + accent;
  return (
    `<svg viewBox="0 0 640 320" role="img" aria-hidden="true" preserveAspectRatio="xMidYMid slice" xmlns="http://www.w3.org/2000/svg">` +
    `<defs>` +
    `<linearGradient id="${gid}" x1="0" y1="0" x2="1" y2="1">` +
    `<stop offset="0" stop-color="#0d1326"/><stop offset="1" stop-color="#070a16"/>` +
    `</linearGradient>` +
    `<radialGradient id="${gid}_glow" cx="0.5" cy="0.4" r="0.7">` +
    `<stop offset="0" stop-color="${c.glow}" stop-opacity="0.40"/>` +
    `<stop offset="1" stop-color="${c.glow}" stop-opacity="0"/>` +
    `</radialGradient>` +
    `</defs>` +
    `<rect width="640" height="320" fill="url(#${gid})"/>` +
    `<rect width="640" height="320" fill="url(#${gid}_glow)"/>` +
    inner(c) +
    `</svg>`
  );
}

// 프로젝트 / 제품 (대표작)
// detail 필드(period/company/role/work/results)는 이력서 [담당 업무]·[업무성과]가 단일 출처.
// hero 필드(SVG)는 코드 생성 비주얼 — 저작권 안전.
const PROJECTS = [
  {
    title: "Motion-O (AI 오케스트레이션 플랫폼)",
    blurb:
      "Motion-W(웹)·Motion-AD(마케팅)·Motion-E(EMR)로 분리 운영되던 제품군을 하나의 AI 축에서 제어하는 오케스트레이션 플랫폼. 마케팅 성과 분석 → 이벤트 생성 → 문의 응대 → 예약 → 차트 연동까지 End-to-End 자동화를 설계 중.",
    tags: ["Claude (AI Agent)", "자체 harness", "Next.js", "NestJS"],
    links: { live: "", repo: "" },
    accent: "cyan",
    // 컨셉: 3개 제품(W·AD·E)이 중앙 AI 오케스트레이터로 수렴 → 자동화 루프로 순환
    hero: makeVisual("cyan", (c) =>
      // 중앙 오케스트레이터로 모이는 연결선
      `<g stroke="${c.a}" stroke-width="2" fill="none" stroke-opacity="0.5">` +
      `<path d="M170 110 C 250 130, 280 145, 320 160"/>` +
      `<path d="M170 250 C 250 230, 280 180, 320 165"/>` +
      `<path d="M530 180 C 470 180, 400 172, 350 165"/>` +
      `</g>` +
      // 자동화 순환 루프
      `<circle cx="335" cy="160" r="86" fill="none" stroke="${c.b}" stroke-width="1.5"
        stroke-opacity="0.35" stroke-dasharray="6 8"/>` +
      // 제품 노드 3개
      `<g font-family="Space Grotesk, sans-serif" text-anchor="middle" font-size="13">` +
      `<g><rect x="100" y="88" width="72" height="42" rx="10" fill="#0d1326"
        stroke="${c.a}" stroke-width="1.5"/>` +
      `<text x="136" y="114" fill="${c.b}">Motion-W</text></g>` +
      `<g><rect x="100" y="228" width="72" height="42" rx="10" fill="#0d1326"
        stroke="${c.a}" stroke-width="1.5"/>` +
      `<text x="136" y="254" fill="${c.b}">Motion-E</text></g>` +
      `<g><rect x="520" y="158" width="76" height="42" rx="10" fill="#0d1326"
        stroke="${c.a}" stroke-width="1.5"/>` +
      `<text x="558" y="184" fill="${c.b}">Motion-AD</text></g>` +
      `</g>` +
      // 중앙 AI 코어
      `<g><circle cx="335" cy="160" r="46" fill="${c.glow}" fill-opacity="0.16"
        stroke="${c.b}" stroke-width="2"/>` +
      `<text x="335" y="156" text-anchor="middle" font-family="Space Grotesk, sans-serif"
        font-size="20" font-weight="700" fill="${c.b}">AI</text>` +
      `<text x="335" y="176" text-anchor="middle" font-family="Space Grotesk, sans-serif"
        font-size="11" fill="${c.b}" fill-opacity="0.8">Orchestrator</text></g>` +
      // 순환 흐름 표식
      `<g fill="${c.b}" fill-opacity="0.75">` +
      `<circle cx="335" cy="74" r="4"/><circle cx="421" cy="160" r="4"/>` +
      `<circle cx="335" cy="246" r="4"/><circle cx="249" cy="160" r="4"/></g>`
    ),
    detail: {
      period: "2026.05 — 현재 (진행 중)",
      company: "㈜트라이업",
      role: "아키텍처 설계 · 총괄",
      stack: ["Claude (AI Agent)", "자체 harness 프레임워크", "Node.js", "Next.js", "NestJS", "LLM·RAG", "Naver Cloud"],
      work: [
        "Motion-W(웹)·Motion-AD(마케팅)·Motion-E(EMR/CRM)로 분리 운영되던 제품군을 하나의 축에서 제어하는 오케스트레이션 아키텍처 설계",
        "제품 전반의 데이터를 AI가 통합 판단하는 구조 설계 — 마케팅 성과를 분석해 이벤트를 자동 생성하고, 신규 문의 발생 시 자동 응대·예약까지 처리",
        "예약 데이터를 차트(EMR)까지 연동하는 End-to-End 자동화 파이프라인 설계",
        "AI 에이전트(Claude) 기반 개발을 위한 자체 harness 프레임워크 직접 설계·구축",
      ],
      results: [
        "제품 통합(진행 중): 개별 판매되던 제품군을 하나의 AI 오케스트레이션 축으로 정렬하는 신규 성장 축 구축 추진",
        "AI 기반 업무 전환(진행 중): 사람이 개입하던 마케팅 판단·고객 응대·예약·차트 입력 과정을 AI 주도 구조로 재설계 중",
      ],
      // harness에 직접 설계·구축한 AI 에이전트 스킬 (Motion 워크스페이스 SoT)
      lineupHeading: "AI 에이전트 스킬",
      lineup: [
        { name: "harness", label: "phase/step 자동 실행 프레임워크", desc: "task를 자기완결적 step으로 쪼개 가드레일(PRD·ARCHITECTURE·ADR)을 주입하고, AC 검증 실패 시 3회 자가교정하는 실행기. 3개 앱에 공통 배치." },
        { name: "run-stack", label: "3앱 dev 스택 일괄 기동", desc: "admin-api(4000)·web-admin(3100)·w-front(3000)와 docker(mysql·redis)를 한 번에 백그라운드 기동하고 HTTP healthcheck로 확인한다." },
        { name: "make-issue", label: "이슈 → Jira 자동 등록", desc: "새 작업·버그를 앱별 규격에 맞는 이슈 파일로 작성하면, 커밋 시 jira-sync 훅이 해당 앱 에픽 아래 Jira task를 자동 생성한다." },
        { name: "handoff", label: "세션 간 작업 인계", desc: "세션 종료 시 다음 세션이 끊김 없이 이어받도록 핸드오프 메모와 인덱스를 남긴다. resume 스킬과 짝을 이루는 컨텍스트 연속성 장치." },
      ],
    },
  },
  {
    title: "Motion AD",
    blurb:
      "GPT·Midjourney·n8n 기반 병의원 마케팅 자동화 SaaS. 콘텐츠 기획·생성·배포를 자동화해 운영 프로세스를 80% 단축하고 신규 수익 모델로 제품화.",
    tags: ["ChatGPT/GPTs", "Midjourney", "n8n", "Notion API"],
    links: { live: "", repo: "" },
    accent: "violet",
    // 컨셉: GPT→이미지→배포로 흐르는 자동화 파이프라인 (노드 + 흐름선)
    hero: makeVisual("violet", (c) =>
      `<g fill="none" stroke="${c.a}" stroke-width="2">` +
      `<path d="M150 160 C 230 90, 320 90, 400 160 S 570 230, 540 160" stroke-opacity="0.55"/>` +
      `<path d="M150 160 C 230 230, 320 230, 400 160 S 570 90, 540 160" stroke-opacity="0.35"/>` +
      `</g>` +
      `<g font-family="Space Grotesk, sans-serif" text-anchor="middle">` +
      `<g><circle cx="150" cy="160" r="34" fill="#0d1326" stroke="${c.a}" stroke-width="2"/>` +
      `<text x="150" y="166" fill="${c.b}" font-size="22" font-weight="700">GPT</text></g>` +
      `<g><circle cx="400" cy="160" r="30" fill="#0d1326" stroke="${c.b}" stroke-width="2"/>` +
      `<text x="400" y="167" fill="${c.b}" font-size="20">🎨</text></g>` +
      `<g><circle cx="540" cy="160" r="26" fill="#0d1326" stroke="${c.a}" stroke-width="2"/>` +
      `<text x="540" y="167" fill="${c.b}" font-size="18">n8n</text></g>` +
      `</g>` +
      `<g fill="${c.b}">` +
      `<circle cx="270" cy="120" r="4"/><circle cx="270" cy="200" r="4"/>` +
      `<circle cx="470" cy="160" r="4"/></g>`
    ),
    detail: {
      period: "2025.06 — 현재",
      company: "㈜트라이업",
      role: "기획 · 구축 총괄",
      stack: ["ChatGPT (GPTs)", "Claude", "Midjourney", "n8n", "Notion API"],
      work: [
        "병의원 전용 마케팅 솔루션 기획 및 구축",
        "GPT 기반 콘텐츠 기획 자동화 도구 개발",
        "Midjourney를 활용한 마케팅 이미지 자동 생성 파이프라인 구성",
        "n8n 기반 콘텐츠 제작·배포 워크플로우 자동화",
      ],
      results: [
        "GPTs 커스텀 에이전트로 콘텐츠 기획 소요 시간 80% 단축, 운영 인력 2인 축소 효과",
        "Midjourney API 연동으로 디자이너 투입 없이 콘텐츠 이미지 생산",
        "사내 마케팅 프로세스를 SaaS 솔루션으로 제품화 → 신규 수익 모델 창출",
      ],
      shots: [
        { src: "assets/projects/motion-ad-marketing.png", alt: "모션AD 마케팅 서비스 구성", fit: true,
          caption: "모션AD 서비스 구성. 개원의 마케팅 · 블로그 마케팅 · 네이버 플레이스 SEO 세 축으로 나누고, 전환 키워드 발굴부터 콘텐츠 발행·리뷰 관리까지 구독형으로 제공한다." },
        { src: "assets/projects/motion-ad-n8n-workflow.png", alt: "n8n 콘텐츠 자동화 워크플로우", wide: true,
          caption: "n8n 콘텐츠 자동화 워크플로우. 주제 추천(LLM)과 본문 생성을 웹훅 두 갈래로 분리하고, 팩트 시트 조회·매칭을 거쳐 서브 워크플로우로 생성을 위임한다. 재생성 분기와 에러 응답·로그 기록까지 파이프라인에 포함했다." },
      ],
    },
  },
  {
    title: "Motion Series",
    blurb:
      "마케팅·홈페이지 예약·전자차트·챗봇을 하나로 잇는 의원급 올인원 솔루션. 모션E(전자차트)·모션K(홈페이지)·카톡 챗봇·모션Ad를 통합해 병원을 하나의 관리자로 운영하게 했습니다.",
    tags: ["전자차트(EMR)", "홈페이지 빌더", "카톡 챗봇", "Naver Cloud"],
    links: { live: "https://motionecosystem.com", repo: "" },
    accent: "blue",
    // 컨셉: 차트·사이니지·챗봇·매출분석 4개 모듈을 하나로 묶은 대시보드
    hero: makeVisual("blue", (c) =>
      `<g stroke="${c.a}" stroke-opacity="0.5" stroke-width="1.5" fill="#0d1326">` +
      `<rect x="120" y="80" width="180" height="70" rx="10"/>` +
      `<rect x="340" y="80" width="180" height="70" rx="10"/>` +
      `<rect x="120" y="170" width="180" height="70" rx="10"/>` +
      `<rect x="340" y="170" width="180" height="70" rx="10"/></g>` +
      // 차트 막대
      `<g fill="${c.b}"><rect x="140" y="118" width="12" height="22" rx="2"/>` +
      `<rect x="158" y="106" width="12" height="34" rx="2"/><rect x="176" y="96" width="12" height="44" rx="2"/>` +
      `<rect x="194" y="112" width="12" height="28" rx="2"/></g>` +
      // 챗봇 모듈: 대화 말풍선
      `<g>` +
      `<rect x="360" y="95" width="62" height="26" rx="9" fill="#11203a" stroke="${c.b}" stroke-opacity="0.6"/>` +
      `<path d="M372 121 l0 10 l12 -10 z" fill="#11203a" stroke="${c.b}" stroke-opacity="0.6"/>` +
      `<rect x="430" y="100" width="80" height="26" rx="9" fill="${c.glow}" fill-opacity="0.18" stroke="${c.b}" stroke-opacity="0.5"/>` +
      `<g fill="${c.b}"><circle cx="375" cy="108" r="2.5"/><circle cx="384" cy="108" r="2.5"/><circle cx="393" cy="108" r="2.5"/>` +
      `<rect x="440" y="106" width="42" height="3.5" rx="1.7" opacity="0.7"/><rect x="440" y="114" width="28" height="3.5" rx="1.7" opacity="0.5"/></g>` +
      `</g>` +
      // 매출 라인
      `<polyline points="360,210 390,195 420,205 450,182 480,190 505,172" fill="none" stroke="${c.b}" stroke-width="2.5"/>` +
      `<g font-family="Space Grotesk" font-size="13" fill="${c.b}" fill-opacity="0.85">` +
      `<text x="135" y="100">📊 Chart</text><text x="360" y="90">🤖 Chatbot</text>` +
      `<text x="142" y="190">📺 Signage</text><text x="356" y="160">📈 Sales</text></g>`
    ),
    detail: {
      period: "2024.09 — 현재",
      company: "㈜트라이업",
      role: "통합 관리 · 고도화 총괄",
      stack: ["Naver Cloud", "Node.js", "Next.js", "NestJS", "Flutter", "Claude", "AWS"],
      // 브로셔 "의원급 올인원 솔루션" 제품 구성 (모션 브로셔 SoT)
      lineup: [
        { name: "모션E", label: "CRM 특화 전자차트(EMR/OCS)", desc: "미용·성형의원에 특화된 차트. 대시보드·대기현황판, 티켓·멤버십, 매출·예약 통계, 펜차트, 사전문진표·고객만족도까지 통합." },
        { name: "모션K", label: "홈페이지 자동구축 솔루션", desc: "월 구독형 병의원 전용 홈페이지. 관리자 페이지로 손쉬운 커스텀, 다국어 템플릿, CRM과 예약 데이터 실시간 연동." },
        { name: "카톡 챗봇", label: "카카오 채널 예약 서비스", desc: "홈페이지·카톡 채널로 들어온 예약이 EMR로 자동 연동. 하나의 관리자로 통합 예약 관리." },
        { name: "모션Ad", label: "ONE-STOP 마케팅 솔루션", desc: "국내(네이버 중심)부터 글로벌까지 의료·뷰티 통합 마케팅. 콘텐츠 제작·타겟팅·인플루언서·개원 초기 전략." },
      ],
      work: [
        "병의원 차트 시스템 개발 및 유지보수",
        "고객 응대용 챗봇 개발 및 개선",
        "병의원 디지털 광고용 사이니지 시스템 구축",
        "고객 유입·매출 분석을 위한 데이터 분석 도구 개발",
      ],
      results: [
        "서버 자원 재설계로 매달 약 1,000만 원 비용 절감",
        "홈페이지·챗봇으로 인입된 예약을 EMR로 자동 연동해 외부 컨택 포인트 축소·원내 업무 효율화",
        "Backend/Frontend 분리 및 CI/CD로 유지보수·확장성·릴리스 안정성 향상",
        "기존 챗봇에 LLM·RAG 적용, 맞춤형 응대로 고객 유입률 20% 증가",
      ],
      shots: [
        { src: "assets/projects/motion-series-e.jpg", alt: "모션E — CRM이 특화된 전자차트", tall: true,
          caption: "모션E — 미용·성형의원에 특화된 EMR 차트. 네이버 클라우드 기반으로 안정성을 확보하고, 타 차트 데이터 이관과 고시 변경 자동 반영을 지원한다. EMR·CRM·연동 세 축으로 기능을 묶었다." },
        { src: "assets/projects/motion-series-t.jpg", alt: "모션T — 태블릿 펜차트 앱", tall: true,
          caption: "모션T — 모션E와 연동되는 펜차트. 사전문진표·원내 고객 접수부터 시술동의서·각종동의서 서명까지 태블릿에서 처리하고, 작성한 차트가 모션E로 그대로 기록된다." },
        { src: "assets/projects/motion-series-w.jpg", alt: "모션W — 병의원 홈페이지 자동구축 솔루션", tall: true,
          caption: "모션W — 누구나 손쉽게 만들고 관리하는 병·의원 전용 홈페이지. CRM과 예약 데이터가 실시간 연동되는 월 구독형 구축 솔루션으로, 제작부터 운영까지 관리자에서 처리한다." },
        { src: "assets/projects/motion-series-k.jpg", alt: "모션K — 카톡 채널 챗봇 예약 서비스", tall: true,
          caption: "모션K — 홈페이지 데이터와 연동된 카카오톡 챗봇 예약. 홈페이지와 동일한 데이터로 별도 세팅 없이 예약을 받고, 하나의 관리자에서 카카오톡 예약까지 한 번에 관리한다." },
        { src: "assets/projects/motion-series-ad.jpg", alt: "모션Ad — 구독형 퍼포먼스 마케팅", tall: true,
          caption: "모션Ad — 환자와 병·의원의 접점 마케팅. 개원 마케팅·블로그 마케팅·네이버 플레이스 SEO 세 축으로 나누고, 타겟 전환 키워드 발굴부터 콘텐츠 발행·리뷰 관리까지 구독형으로 운영한다." },
      ],
    },
  },
  {
    title: "상담 어시스턴트 챗봇",
    blurb:
      "LangChain·LangGraph·Vector DB 기반 병의원 상담 챗봇. 예약~결제까지 자동화하고 사용자 전환율 20% 증가, 상담 인건비 50% 절감.",
    tags: ["FastAPI", "LangChain", "LangGraph", "Vector DB"],
    links: { live: "", repo: "" },
    accent: "cyan",
    // 컨셉: 챗봇 인터페이스 — 봇 아바타 + 대화 버블 + 타이핑 + LangGraph 노드
    hero: makeVisual("cyan", (c) =>
      // 봇 아바타
      `<g>` +
      `<circle cx="150" cy="120" r="26" fill="${c.glow}" fill-opacity="0.18" stroke="${c.b}" stroke-width="2"/>` +
      `<rect x="138" y="110" width="24" height="18" rx="5" fill="none" stroke="${c.b}" stroke-width="2"/>` +
      `<circle cx="145" cy="119" r="2.5" fill="${c.b}"/><circle cx="155" cy="119" r="2.5" fill="${c.b}"/>` +
      `<line x1="150" y1="110" x2="150" y2="103" stroke="${c.b}" stroke-width="2"/><circle cx="150" cy="101" r="2.5" fill="${c.b}"/>` +
      `</g>` +
      // 봇 답변 버블
      `<rect x="190" y="100" width="170" height="42" rx="14" fill="#11203a" stroke="${c.a}" stroke-opacity="0.55"/>` +
      `<g fill="${c.b}"><rect x="204" y="115" width="120" height="4" rx="2" opacity="0.7"/><rect x="204" y="125" width="80" height="4" rx="2" opacity="0.5"/></g>` +
      // 사용자 질문 버블 (우측 정렬)
      `<rect x="370" y="158" width="160" height="40" rx="14" fill="${c.glow}" fill-opacity="0.2" stroke="${c.b}" stroke-opacity="0.6"/>` +
      `<g fill="${c.b}"><rect x="384" y="172" width="110" height="4" rx="2" opacity="0.65"/><rect x="384" y="182" width="70" height="4" rx="2" opacity="0.45"/></g>` +
      // 타이핑 인디케이터 버블
      `<rect x="190" y="212" width="74" height="38" rx="14" fill="#11203a" stroke="${c.a}" stroke-opacity="0.5"/>` +
      `<g fill="${c.b}"><circle cx="212" cy="231" r="4"/><circle cx="227" cy="231" r="4" opacity="0.7"/><circle cx="242" cy="231" r="4" opacity="0.4"/></g>` +
      // LangGraph 노드 (대화 플로우 엔진)
      `<g stroke="${c.a}" stroke-width="1.5" stroke-opacity="0.5" fill="none">` +
      `<path d="M470 130 L540 130 L540 200"/></g>` +
      `<g fill="#0d1326" stroke="${c.b}" stroke-width="2">` +
      `<circle cx="470" cy="130" r="9"/><circle cx="540" cy="130" r="9"/><circle cx="540" cy="200" r="9"/></g>` +
      `<text x="490" y="232" font-family="Space Grotesk" font-size="11" fill="${c.b}" fill-opacity="0.8">LangGraph</text>`
    ),
    detail: {
      period: "2024.11 — 현재",
      company: "㈜트라이업",
      role: "기획 · 개발",
      stack: ["FastAPI", "LangChain", "LangGraph", "LangSmith", "Vector DB", "Dialogflow"],
      work: [
        "병의원 고객 상담을 돕는 챗봇 개발 및 챗봇 인프라 구축",
        "LangChain·LangGraph·LangSmith 기반 대화 플로우 설계",
        "세션 로깅 / 디버깅 체계 적용",
      ],
      results: [
        "상담사 업무를 대체·보조하는 시스템 구축으로 상담 인건비 50% 절감(예상)",
        "챗봇·차트 시스템 연계로 병원 운영 효율성 극대화",
        "예약~결제 프로세스 자동화로 환자 편의성·병원 수익 구조 최적화",
      ],
      shots: [
        { src: "assets/projects/motion-chatbot-translate.jpg", alt: "다국어 상담 번역·답변 화면", wide: true,
          caption: "다국어 상담 화면. 외국인 문의(일본어)를 상담사가 읽을 한국어로 번역해 띄우고, 시술 후 주의사항에 맞는 답변을 다시 원문 언어로 돌려준다. 응답 지연(3.3초)까지 함께 기록해 품질을 관리한다." },
      ],
    },
  },
  {
    title: "AI 얼굴 분석",
    blurb:
      "병의원 상담을 돕는 AI 얼굴·피부 분석 기능. 아이디어 발의와 제품 방향성을 직접 정의하고, 개발팀과 함께 시술 추천·고객 응대 흐름에 녹여낸 기획·총괄 프로젝트.",
    tags: ["AI 기획", "Computer Vision", "병의원 SaaS", "제품 총괄"],
    links: { live: "", repo: "" },
    accent: "blue",
    // 컨셉: 안면 랜드마크 메시 + 분석 포인트
    hero: makeVisual("blue", (c) =>
      // 얼굴 윤곽
      `<path d="M320 90 C 250 90 235 145 240 185 C 244 220 270 250 320 258 C 370 250 396 220 400 185 C 405 145 390 90 320 90 Z" ` +
      `fill="#0d1326" stroke="${c.a}" stroke-width="1.6" stroke-opacity="0.7"/>` +
      // 랜드마크 메시 라인
      `<g stroke="${c.a}" stroke-width="1" stroke-opacity="0.35">` +
      `<path d="M270 150 L320 168 L370 150"/><path d="M270 150 L300 200 L320 168 L340 200 L370 150"/>` +
      `<path d="M300 200 L320 220 L340 200"/><path d="M285 130 L355 130"/></g>` +
      // 랜드마크 점
      `<g fill="${c.b}">` +
      `<circle cx="270" cy="150" r="3.5"/><circle cx="370" cy="150" r="3.5"/>` +
      `<circle cx="320" cy="168" r="3.5"/><circle cx="300" cy="200" r="3"/><circle cx="340" cy="200" r="3"/>` +
      `<circle cx="320" cy="220" r="3"/><circle cx="285" cy="130" r="3"/><circle cx="355" cy="130" r="3"/>` +
      `<circle cx="295" cy="148" r="2.5"/><circle cx="345" cy="148" r="2.5"/></g>` +
      // 스캔 라인
      `<line x1="232" y1="174" x2="408" y2="174" stroke="${c.b}" stroke-width="1.5" stroke-dasharray="6 5" stroke-opacity="0.6"/>` +
      // 분석 결과 패널
      `<g font-family="Space Grotesk" font-size="12" fill="${c.b}">` +
      `<rect x="450" y="120" width="120" height="90" rx="8" fill="#11203a" stroke="${c.a}" stroke-opacity="0.4"/>` +
      `<text x="464" y="144">▹ 얼굴형</text><text x="464" y="166">▹ 피부 상태</text>` +
      `<text x="464" y="188">▹ 시술 추천</text></g>` +
      `<line x1="400" y1="160" x2="450" y2="160" stroke="${c.a}" stroke-width="1.5" stroke-opacity="0.5"/>`
    ),
    detail: {
      period: "2025 — 현재",
      company: "㈜트라이업",
      role: "기획 · 방향성 총괄 (아이디어 발의 · 개발은 개발팀)",
      stack: ["Computer Vision", "Next.js", "NestJS", "Flutter", "AI 제품 기획"],
      work: [
        "AI 얼굴·피부 분석 기능의 아이디어 발의 및 제품 컨셉 정의",
        "상담·시술 추천 흐름에 분석 결과를 연결하는 방향성 설계",
        "개발팀과 협업하여 기능 범위·우선순위 조율 및 총괄",
      ],
      results: [
        "상담 단계에서 고객 맞춤 시술 추천을 보조하는 분석 기능으로 제품화",
        "차트·챗봇 등 기존 Motion 솔루션과 연계 가능한 방향으로 설계",
      ],
      shots: [
        { src: "assets/projects/motion-e-ai-diagnosis.png", alt: "모션E PRO의 AI 진단 화면", tall: true,
          caption: "모션E PRO 고객 차트에 들어간 AI 진단 탭. 촬영과 비교를 두 갈래로 나눠, 시술 전·후 사진을 같은 기준으로 남기고 상담 때 바로 꺼내 보도록 설계했다. (고객 정보는 마스킹 처리)" },
        { src: "assets/projects/motion-e-ai-face-landmark.jpg", alt: "AI 얼굴 랜드마크 인식 화면", fit: true,
          caption: "촬영 화면의 실시간 얼굴 인식. 눈·눈썹·코·입술·윤곽을 랜드마크로 잡아 가이드에 맞추고, 라이트닝·정면 각도·얼굴 위치·거리 네 항목을 즉시 판정해 나쁜 입력을 촬영 단계에서 걸러낸다. (예시 이미지는 AI 생성)" },
        { src: "assets/projects/motion-e-ai-face-compare.jpg", alt: "시술 전·후 사진 비교 화면", wide: true,
          caption: "시술 전·후 비교. 슬라이더·분할·오버레이 세 방식으로 같은 기준에서 겹쳐 보고, 기미·잡티, 모공, 수분, 다크서클 등 항목별로 전환해 상담 근거로 제시한다. (예시 이미지는 AI 생성)" },
        { src: "assets/projects/motion-e-ai-face-guide.jpg", alt: "AI 얼굴 분석 촬영 가이드", fit: true,
          caption: "촬영 가이드라인. 분석 정확도는 입력 사진 품질이 좌우하므로, 정면·선명·머리 넘김을 권장 예시로 제시하고 측면·머리카락 가림·과도한 역광은 배제하도록 설계했다. (예시 이미지는 AI 생성)" },
      ],
    },
  },
  {
    title: "VigoRight (의료 AI/VR)",
    blurb:
      "VR 안과·신경과 검사 장비. RANSAC 기하 정합 + CNN 회귀로 안구 토션을 정량화하고 Grad-CAM XAI로 검증. 대학병원·개원가 진입으로 약 3억 원 매출.",
    tags: ["Django", "PyTorch", "Computer Vision", "XAI"],
    links: { live: "", repo: "" },
    accent: "violet",
    // 컨셉: VR 아이트래킹 — 눈동자 + 토션 각도 측정 + Grad-CAM 히트맵
    hero: makeVisual("violet", (c) =>
      // 눈 외곽
      `<path d="M210 160 Q 320 70 430 160 Q 320 250 210 160 Z" fill="#0d1326" stroke="${c.a}" stroke-width="2"/>` +
      // 홍채 + Grad-CAM 동심원
      `<circle cx="320" cy="160" r="46" fill="none" stroke="${c.b}" stroke-opacity="0.35" stroke-width="10"/>` +
      `<circle cx="320" cy="160" r="34" fill="none" stroke="${c.a}" stroke-opacity="0.55" stroke-width="8"/>` +
      `<circle cx="320" cy="160" r="18" fill="${c.b}"/>` +
      `<circle cx="320" cy="160" r="7" fill="#070a16"/>` +
      // 토션 각도 표시 (점선 + 호)
      `<g stroke="${c.b}" stroke-width="1.6" fill="none" stroke-opacity="0.8">` +
      `<line x1="320" y1="160" x2="392" y2="118" stroke-dasharray="4 4"/>` +
      `<line x1="320" y1="160" x2="396" y2="160" stroke-dasharray="4 4"/>` +
      `<path d="M380 160 A 60 60 0 0 0 366 132"/></g>` +
      `<text x="404" y="150" font-family="Space Grotesk" font-size="15" fill="${c.b}">θ°</text>` +
      // VR 코너 프레임
      `<g stroke="${c.a}" stroke-width="2" stroke-opacity="0.4" fill="none">` +
      `<path d="M150 95 h-30 v30"/><path d="M490 95 h30 v30"/><path d="M150 225 h-30 v-30"/><path d="M490 225 h30 v-30"/></g>`
    ),
    detail: {
      period: "2023.03 — 2024.07",
      company: "㈜Tenetus",
      role: "개발 운영 이사 · 개발 총괄",
      stack: ["Python (Django)", "Node.js", "MongoDB", "PyTorch", "Unity", "AWS"],
      work: [
        "안과·신경과 고식적 검사를 VR 환경으로 구현",
        "HMD Eye Tracker의 시선·토션(torsion) 데이터 실시간 분석",
        "RANSAC 기반 기하 정합으로 안구 회전 각도(°) 정량화",
        "CNN 회귀로 회전 각도 예측 + Grad-CAM XAI로 학습 집중 영역 시각 검증",
      ],
      results: [
        "VR 기반 의료 진단 장비 개발 총괄, 전통적 검사 방식의 디지털 전환 선도",
        "라벨 없는 환경에서도 RANSAC으로 토션 각도 추정 → 분석 자동화",
        "Grad-CAM XAI로 모델 해석 가능성·임상 신뢰도 향상",
        "대학병원·개원가 시장 진입, 약 3억 원 매출 달성",
      ],
      shots: [
        { src: "assets/projects/vror_v200_1.png", alt: "VigoRight 검사 장비 구성", fit: true,
          caption: "VigoRight 검사 장비 구성. 이동형 카트에 검사자용 모니터와 VR HMD를 통합해 안진·안구운동·온도안진 검사를 한 자리에서 수행." },
        { src: "assets/projects/vror_v300.png", alt: "임상 현장 적용 모습", fit: true,
          caption: "임상 현장 적용 모습. 피검자는 HMD를 착용하고, 검사자는 별도 화면으로 실시간 시선·동공 데이터를 확인한다." },
        { src: "assets/projects/vror_7_ocular_torsion.png", alt: "OcularTorsion 회선 검사 화면", fit: true,
          caption: "OcularTorsion(회선) 검사 화면. 좌우 안구 적외선 영상에서 동공 경계를 추적해 회전 각도를 정량화 — RANSAC 기하 정합과 CNN 회귀가 적용된 핵심 검사." },
        { src: "assets/projects/vror_6_visual_field.png", alt: "Visual Field 시야 검사 화면", fit: true,
          caption: "Visual Field(시야) 검사 화면. 중심 주시 상태에서 주변 자극 인지 여부를 기록하며, 이 시야 데이터가 뇌병변 판별 AI(NDI)의 입력이 된다." },
        { src: "assets/projects/vror_3_rapd.png", alt: "RAPD 상대구심성 동공결손 검사 화면", fit: true,
          caption: "RAPD(상대구심성 동공결손) 검사 화면. 한쪽 눈에 광자극을 주고 양안 동공 반응을 동시에 추적해 좌우 비대칭을 판정." },
        { src: "assets/projects/vror_v200_2.png", alt: "검사용 VR HMD", fit: true,
          caption: "검사에 사용되는 VR HMD. 내장 Eye Tracker로 시선·동공·토션 데이터를 실시간 수집한다." },
      ],
    },
  },
  {
    title: "NDI (뇌병변 국소화 AI)",
    blurb:
      "눈동자 움직임을 다각도로 측정해 뇌병변 위치를 판별하는 의료 AI. 고려대 의료진과 협업해 시야 데이터만으로 뇌병변을 국소화 → 검사 복잡도와 비용을 낮춘다.",
    tags: ["Computer Vision", "Medical AI", "Eye Tracking", "PyTorch"],
    links: { live: "", repo: "" },
    accent: "violet",
    // 컨셉: 다각도 시선 벡터가 한 점(병변)으로 수렴 + 뇌 윤곽 + 국소화 표적
    hero: makeVisual("violet", (c) =>
      // 뇌 윤곽
      `<path d="M250 110 Q 200 100 196 150 Q 170 165 185 200 Q 185 240 235 240 Q 260 258 300 246 Q 350 256 372 222 Q 410 212 398 168 Q 410 128 360 116 Q 320 92 290 108 Q 268 100 250 110 Z" fill="#0d1326" stroke="${c.a}" stroke-width="2" stroke-opacity="0.7"/>` +
      // 뇌 주름
      `<g stroke="${c.a}" stroke-width="1.4" stroke-opacity="0.35" fill="none">` +
      `<path d="M230 140 Q 260 160 240 185"/><path d="M300 125 Q 320 160 300 195"/><path d="M345 150 Q 360 180 335 205"/></g>` +
      // 병변 표적 (국소화 포인트)
      `<circle cx="318" cy="182" r="22" fill="none" stroke="${c.b}" stroke-opacity="0.4" stroke-width="2"/>` +
      `<circle cx="318" cy="182" r="12" fill="none" stroke="${c.b}" stroke-opacity="0.7" stroke-width="2"/>` +
      `<circle cx="318" cy="182" r="4" fill="${c.b}"/>` +
      // 눈 + 다각도 시선 벡터가 병변으로 수렴
      `<g stroke="${c.b}" stroke-width="1.6" stroke-opacity="0.85" stroke-dasharray="4 4">` +
      `<line x1="120" y1="130" x2="318" y2="182"/>` +
      `<line x1="120" y1="182" x2="318" y2="182"/>` +
      `<line x1="120" y1="234" x2="318" y2="182"/></g>` +
      // 눈 아이콘
      `<g transform="translate(96 182)">` +
      `<path d="M-32 0 Q 0 -26 32 0 Q 0 26 -32 0 Z" fill="#0d1326" stroke="${c.a}" stroke-width="2"/>` +
      `<circle cx="0" cy="0" r="11" fill="none" stroke="${c.b}" stroke-width="2"/>` +
      `<circle cx="0" cy="0" r="4.5" fill="${c.b}"/></g>` +
      // 각도 라벨
      `<text x="150" y="120" font-family="Space Grotesk" font-size="13" fill="${c.b}" fill-opacity="0.85">multi-angle gaze</text>`
    ),
    detail: {
      period: "2023.03 — 2024.07",
      company: "㈜Tenetus",
      role: "개발 운영 이사 · AI 개발 총괄",
      stack: ["Python", "PyTorch", "Computer Vision", "Eye Tracking", "XAI", "Unity"],
      work: [
        "눈동자의 움직임을 다각도로 측정해 뇌병변을 측정하는 검사 방식 설계",
        "고려대 의료진과 협업해 시야 데이터 기반 뇌병변 판별 AI(NDI) 설계 총괄",
        "뇌병변 국소화 모델을 위한 의료 데이터 수집 및 가공 파이프라인 구축",
        "시야 검사 데이터만으로 병변 위치를 추정하는 알고리즘 연구",
      ],
      results: [
        "시야 검사만으로 뇌병변 판별이 가능한 알고리즘 개발",
        "기존 대비 검사 복잡도 감소 및 검사 비용 절감",
        "VR 시각 측정 장비(VigoRight)와 연계한 AI 진단 방향성 정립",
      ],
      shots: [
        { src: "assets/projects/ndi-m2s-vr-brain-lesion.png", alt: "VR 기반 뇌병변 진단 장비", fit: true,
          caption: "VR 기반 뇌병변 진단 장비. HMD로 수집한 시선·시야 데이터를 콘솔에서 분석해 3D 뇌 모델 위에 병변 추정 위치를 표시한다. (국내 최초 VR 기반 뇌병변 진단 의료기기 인증)" },
      ],
    },
  },
  {
    title: "Lost Energy Intel",
    blurb:
      "풍력발전 SCADA 데이터 기반 에너지 손실 예측 시스템. 설비 이상을 사전 감지해 연간 2억 원 원가 절감을 달성한 상용 ML 모델.",
    tags: ["Python", "TensorFlow", "Scikit-learn", "Time-Series"],
    links: { live: "", repo: "" },
    accent: "blue",
    // 컨셉: 풍력 터빈 + 시계열 예측 곡선 + 이상 탐지 포인트
    hero: makeVisual("blue", (c) =>
      // 터빈
      `<g stroke="${c.a}" stroke-width="3" stroke-linecap="round">` +
      `<line x1="150" y1="120" x2="150" y2="250"/>` +
      `<g stroke="${c.b}">` +
      `<line x1="150" y1="120" x2="150" y2="72"/>` +
      `<line x1="150" y1="120" x2="192" y2="144"/>` +
      `<line x1="150" y1="120" x2="108" y2="144"/></g></g>` +
      `<circle cx="150" cy="120" r="6" fill="${c.b}"/>` +
      // 시계열 예측 곡선
      `<polyline points="240,210 280,190 320,200 360,165 400,175 440,140 480,150 520,110" ` +
      `fill="none" stroke="${c.b}" stroke-width="2.5"/>` +
      // 예측 구간 점선
      `<polyline points="440,140 480,150 520,110 560,95" fill="none" stroke="${c.a}" stroke-width="2" stroke-dasharray="5 4" stroke-opacity="0.7"/>` +
      // 이상 탐지 포인트
      `<circle cx="360" cy="165" r="9" fill="none" stroke="${c.b}" stroke-width="2"/>` +
      `<circle cx="360" cy="165" r="3.5" fill="${c.b}"/>` +
      `<text x="372" y="158" font-family="Space Grotesk" font-size="12" fill="${c.b}" fill-opacity="0.85">anomaly</text>` +
      // 베이스라인
      `<line x1="240" y1="248" x2="560" y2="248" stroke="${c.a}" stroke-opacity="0.25"/>`
    ),
    detail: {
      period: "2022.01 — 2022.11",
      company: "ONYX Insight (BP Group)",
      role: "Senior Developer · ML Engineer",
      stack: ["Python (Django)", "R", "Keras", "TensorFlow", "Scikit-learn"],
      work: [
        "Generator·Pitch·Yaw Misalignment 등 SCADA 센서 데이터 기반 Lost Energy 예측",
        "각 설비 상태를 분석하는 모델 개발",
        "데이터 상관관계 분석 및 이상 탐지",
        "현장 엔지니어와 협업해 문제 해결 및 성능 검증",
      ],
      results: [
        "풍력발전기 Lost Energy 사전 예측으로 연간 2억 원 원가 절감",
        "설비 이상을 사전 감지해 운영 효율성 극대화",
      ],
      shots: [
        { src: "assets/projects/wind-engineers-inspecting-blade-failure.jpg", alt: "현장 엔지니어의 블레이드 결함 점검",
          caption: "현장 엔지니어의 블레이드 결함 점검. 모델이 사전 감지한 이상을 현장에서 검증하며 성능을 함께 다듬었다." },
      ],
    },
  },
  {
    title: "AI-Hub (NLP)",
    blurb:
      "FastText·Word2Vec 기반 문서/이슈 자동 분류 및 추천 시스템. 수동 분류를 자동화하고 GraphQL·React로 반응형 케이스 관리 UI 구현.",
    tags: ["NLP", "React", "GraphQL", "Gensim"],
    links: { live: "", repo: "" },
    accent: "cyan",
    // 컨셉: 문서들이 임베딩되어 카테고리로 분류·추천되는 NLP 파이프라인
    hero: makeVisual("cyan", (c) =>
      // 입력 문서들
      `<g fill="#0d1326" stroke="${c.a}" stroke-opacity="0.55" stroke-width="1.5">` +
      `<rect x="100" y="100" width="48" height="60" rx="6"/>` +
      `<rect x="100" y="135" width="48" height="60" rx="6"/>` +
      `<rect x="100" y="170" width="48" height="60" rx="6"/></g>` +
      `<g stroke="${c.b}" stroke-opacity="0.5" stroke-width="1.5"><line x1="110" y1="185" x2="138" y2="185"/>` +
      `<line x1="110" y1="195" x2="132" y2="195"/></g>` +
      // 임베딩 노드
      `<circle cx="320" cy="160" r="40" fill="none" stroke="${c.a}" stroke-opacity="0.4" stroke-width="1.5"/>` +
      `<text x="320" y="156" text-anchor="middle" font-family="Space Grotesk" font-size="13" fill="${c.b}">word2vec</text>` +
      `<text x="320" y="174" text-anchor="middle" font-family="Space Grotesk" font-size="13" fill="${c.b}">/ fastText</text>` +
      // 연결선
      `<g stroke="${c.a}" stroke-width="1.5" stroke-opacity="0.5"><line x1="148" y1="160" x2="282" y2="160"/>` +
      `<line x1="358" y1="140" x2="470" y2="110"/><line x1="358" y1="160" x2="470" y2="160"/>` +
      `<line x1="358" y1="180" x2="470" y2="210"/></g>` +
      // 분류 카테고리
      `<g font-family="Space Grotesk" font-size="13" text-anchor="middle">` +
      `<g><rect x="470" y="92" width="90" height="34" rx="17" fill="${c.glow}" fill-opacity="0.18" stroke="${c.b}"/><text x="515" y="114" fill="${c.b}">Class A</text></g>` +
      `<g><rect x="470" y="143" width="90" height="34" rx="17" fill="${c.glow}" fill-opacity="0.18" stroke="${c.b}"/><text x="515" y="165" fill="${c.b}">Class B</text></g>` +
      `<g><rect x="470" y="194" width="90" height="34" rx="17" fill="${c.glow}" fill-opacity="0.18" stroke="${c.b}"/><text x="515" y="216" fill="${c.b}">Class C</text></g>` +
      `</g>`
    ),
    detail: {
      period: "2020.03 — 2022.11",
      company: "ONYX Insight (BP Group)",
      role: "Senior Developer · ML Engineer",
      stack: ["Python (Django)", "ReactJS", "GraphQL", "Apollo", "Gensim", "Scikit-learn"],
      work: [
        "이슈/히스토리 관리를 위한 Case Management System 개발",
        "React Hook·Material UI·GraphQL 기반 반응형 웹페이지 제작",
        "FastText·Word2Vec 기반 Issue History Classification 제작",
        "사용자·Case 정보를 매핑한 Recommendation System 구축",
      ],
      results: [
        "기존 수동 분류 이슈를 자동화하여 처리 속도 향상",
        "사용자 직급·단지 정보 기반 맞춤형 Case 추천",
        "장비별 데이터 확인·이슈 공유로 협업 강화",
      ],
      shots: [
        { src: "assets/projects/case-management-two-screens-onyx.jpg", alt: "AI-Hub Case Management 화면", fit: true,
          caption: "AI-Hub 운영 화면. Monitoring Case Summary 대시보드와 Case Management 테이블로 단지별 이슈를 한 화면에서 추적한다." },
      ],
    },
  },
  {
    title: "FieldPro (풍력단지 관리 SaaS)",
    blurb:
      "풍력단지 현장 점검·데이터 관리 산업용 SaaS. Web·iOS 전 영역을 개발하고 서버리스 미들웨어로 재설계했으며, 광산 산업까지 서비스를 확장했다.",
    tags: ["AngularJS2", "Swift", "AWS Lambda", "PostgreSQL"],
    links: { live: "", repo: "" },
    accent: "blue",
    // 컨셉: 풍력단지 맵 + 점검 체크리스트 카드 + 모바일 동기화
    hero: makeVisual("blue", (c) =>
      // 단지 맵 그리드
      `<g stroke="${c.a}" stroke-opacity="0.18" stroke-width="1">` +
      `<line x1="90" y1="110" x2="560" y2="110"/><line x1="90" y1="170" x2="560" y2="170"/>` +
      `<line x1="90" y1="230" x2="560" y2="230"/></g>` +
      // 터빈 2기 (점검 대상)
      `<g stroke="${c.a}" stroke-width="2.5" stroke-linecap="round">` +
      `<line x1="140" y1="150" x2="140" y2="232"/><line x1="140" y1="150" x2="140" y2="120"/>` +
      `<line x1="140" y1="150" x2="166" y2="166"/><line x1="140" y1="150" x2="114" y2="166"/>` +
      `<line x1="228" y1="150" x2="228" y2="232"/><line x1="228" y1="150" x2="228" y2="120"/>` +
      `<line x1="228" y1="150" x2="254" y2="166"/><line x1="228" y1="150" x2="202" y2="166"/></g>` +
      `<circle cx="140" cy="150" r="4.5" fill="${c.b}"/><circle cx="228" cy="150" r="4.5" fill="${c.b}"/>` +
      // 점검 체크리스트 카드
      `<rect x="330" y="96" width="200" height="140" rx="10" fill="#0d1326" stroke="${c.a}" stroke-width="2"/>` +
      `<text x="348" y="122" font-family="Space Grotesk" font-size="13" fill="${c.b}">Inspection</text>` +
      `<g stroke="${c.b}" stroke-width="2" fill="none" stroke-linecap="round">` +
      `<path d="M350 145 l7 7 l13 -14"/><path d="M350 175 l7 7 l13 -14"/><path d="M350 205 l7 7 l13 -14"/></g>` +
      `<g stroke="${c.a}" stroke-opacity="0.45" stroke-width="2" stroke-linecap="round">` +
      `<line x1="382" y1="150" x2="508" y2="150"/><line x1="382" y1="180" x2="508" y2="180"/>` +
      `<line x1="382" y1="210" x2="474" y2="210"/></g>` +
      // 동기화 화살표
      `<g stroke="${c.b}" stroke-width="2" fill="none" stroke-opacity="0.75" stroke-dasharray="5 4">` +
      `<path d="M262 166 h 52"/></g>` +
      `<text x="264" y="156" font-family="Space Grotesk" font-size="12" fill="${c.b}" fill-opacity="0.85">sync</text>`
    ),
    detail: {
      period: "2018.08 — 2021.03",
      company: "ONYX Insight (BP Group)",
      role: "Senior Developer",
      stack: ["AngularJS2", "JSP", "PostgreSQL", "Swift 3", "AWS Lambda", "Node.js"],
      work: [
        "풍력단지 데이터 관리 시스템 FieldPro Front-end·Back-end 개발 및 운영",
        "FieldPro iOS Application v2 개발 — Data Sync 및 사용자 UI 개선",
        "AWS API Gateway + Lambda 기반 Serverless Middleware 재개발, 영국 본사 Live Report와 연동",
        "풍력단지용 서비스를 광산 산업에 맞게 커스터마이징(FieldPro Mining), Fleet Monitor 데이터 연계·차트 시각화",
      ],
      results: [
        "풍력 → 광산 산업으로 서비스 확장",
        "Serverless 설계로 관리 리소스 절감 및 안정성 강화",
        "iOS 다운로드/업로드 기능 강화로 현장 데이터 동기화 개선",
        "서비스 안정화·성능 개선으로 사용자 만족도 향상",
      ],
      shots: [
        { src: "assets/projects/onyx-insight-fieldpro-two-phones.jpg", alt: "FieldPro 모바일 점검 앱", fit: true,
          caption: "FieldPro 모바일 앱. 현장 엔지니어가 Inspection Checklist와 Drivetrain·Gearbox 점검 항목을 단말에서 바로 기록한다." },
        { src: "assets/projects/fieldpro-desktop-application-punch-list-screenshot-1024x566.jpg", alt: "FieldPro 데스크톱 Issue Punch List", fit: true,
          caption: "FieldPro 데스크톱의 Issue Punch List. 현장에서 올라온 이슈를 단지 단위로 모아 상태별로 관리한다." },
      ],
    },
  },
  {
    title: "FleetUp (차량 관리 시스템)",
    blurb:
      "실리콘밸리 스타트업의 차량 관리 SaaS. Front-end Technical Leader로 Spring 기반 레거시를 프론트-백엔드 분리 구조로 개편하고, e-commerce는 AWS Serverless로 재구축했다.",
    tags: ["AngularJS2", "TypeScript", "AWS Lambda", "Spring"],
    links: { live: "", repo: "" },
    accent: "cyan",
    // 컨셉: 차량 텔레메트리 — 경로 위 차량 + 대시보드 카드 + 서버리스 노드
    hero: makeVisual("cyan", (c) =>
      // 주행 경로
      `<path d="M100 250 C 190 250, 210 150, 300 150 S 420 200, 520 130" fill="none" ` +
      `stroke="${c.a}" stroke-width="2.5" stroke-opacity="0.55" stroke-dasharray="8 7"/>` +
      // 경로 위 위치 핀 3개
      `<g fill="${c.b}"><circle cx="150" cy="248" r="5"/><circle cx="300" cy="150" r="5"/>` +
      `<circle cx="520" cy="130" r="5"/></g>` +
      // 차량 아이콘 (경로 위)
      `<g><rect x="272" y="118" width="56" height="24" rx="7" fill="#0d1326" stroke="${c.b}" stroke-width="2"/>` +
      `<rect x="284" y="110" width="30" height="12" rx="4" fill="#0d1326" stroke="${c.b}" stroke-width="1.6"/>` +
      `<circle cx="288" cy="144" r="5" fill="#0d1326" stroke="${c.b}" stroke-width="1.8"/>` +
      `<circle cx="314" cy="144" r="5" fill="#0d1326" stroke="${c.b}" stroke-width="1.8"/></g>` +
      // 텔레메트리 대시보드 카드
      `<rect x="380" y="180" width="176" height="96" rx="10" fill="#0d1326" stroke="${c.a}" stroke-width="2"/>` +
      `<text x="398" y="204" font-family="Space Grotesk" font-size="12" fill="${c.b}" fill-opacity="0.85">Fleet Dashboard</text>` +
      `<g fill="${c.b}"><rect x="398" y="238" width="14" height="22" rx="2"/>` +
      `<rect x="418" y="226" width="14" height="34" rx="2"/><rect x="438" y="216" width="14" height="44" rx="2"/>` +
      `<rect x="458" y="232" width="14" height="28" rx="2" opacity="0.6"/></g>` +
      `<polyline points="486,252 502,238 518,244 536,222" fill="none" stroke="${c.b}" stroke-width="2" stroke-opacity="0.8"/>` +
      // Serverless 노드 체인
      `<g stroke="${c.a}" stroke-width="1.5" stroke-opacity="0.5" fill="none">` +
      `<path d="M120 110 h 60 M212 110 h 60"/></g>` +
      `<g fill="#0d1326" stroke="${c.b}" stroke-width="2">` +
      `<circle cx="110" cy="110" r="10"/><circle cx="196" cy="110" r="10"/></g>` +
      `<text x="96" y="88" font-family="Space Grotesk" font-size="11" fill="${c.b}" fill-opacity="0.8">API GW → Lambda</text>`
    ),
    detail: {
      period: "2016.12 — 2018.08",
      company: "트루라이트 (Truelight) · 실리콘밸리",
      role: "Senior Developer · Front-end Technical Leader",
      stack: ["AngularJS2", "TypeScript", "Node.js", "Spring", "Java", "Oracle", "AWS Lambda", "AWS S3"],
      work: [
        "FleetUp Front-end Technical Leader — 기술 문제 해결, 사용 환경·성능 향상, 서비스 운영 개선 총괄",
        "Spring 기반 FleetUp 서버 관리 및 Application 추가 개발, 대용량 데이터 쿼리 튜닝",
        "기존 Web Page를 AngularJS·Bootstrap 기반 UI로 개편하고, UI 4.0에서 Frontend-Backend Decoupling 및 대시보드 시각화 차트 개발",
        "AWS API Gateway·Lambda·S3 Serverless 구조로 e-commerce 페이지 구축, Salesforce(고객 관리 시스템) 연동",
      ],
      results: [
        "Oracle DB 성능 향상 및 응답속도 개선",
        "소스 모듈화로 렌더링 성능 향상, 독립 빌드·운영이 가능한 구조로 개선",
        "Salesforce에서 처리하던 작업을 사용자가 직접 처리하는 시스템으로 개선",
        "Node.js로 Lambda Turn-on Time 최적화",
      ],
    },
  },
  {
    title: "삼성전자 PenUp Mobile Web App",
    blurb:
      "삼성전자 드로잉 SNS PenUp의 모바일 웹앱. MVC 구조와 템플릿·뷰 위젯 체계를 도입하고 애니메이션·페이지 전환을 개선해 Android 버전까지 확장했다.",
    tags: ["JavaScript", "jQuery", "HTML5", "Hybrid App"],
    links: { live: "", repo: "" },
    accent: "violet",
    // 컨셉: 모바일 단말 + 드로잉 캔버스 + 카드 그리드 + 페이지 전환
    hero: makeVisual("violet", (c) =>
      // 단말 프레임
      `<rect x="240" y="60" width="170" height="220" rx="20" fill="#0d1326" stroke="${c.a}" stroke-width="2"/>` +
      `<rect x="300" y="72" width="50" height="6" rx="3" fill="${c.a}" fill-opacity="0.5"/>` +
      // 드로잉 스트로크 (펜)
      `<path d="M264 190 C 292 138, 320 226, 348 158 S 384 118, 392 148" fill="none" ` +
      `stroke="${c.b}" stroke-width="3" stroke-linecap="round"/>` +
      // 펜촉
      `<g stroke="${c.b}" stroke-width="2" fill="#0d1326">` +
      `<path d="M392 148 l16 -22 l10 8 l-18 20 z"/></g>` +
      // 카드 그리드 (갤러리)
      `<g fill="none" stroke="${c.a}" stroke-opacity="0.55" stroke-width="1.6">` +
      `<rect x="258" y="208" width="62" height="48" rx="7"/><rect x="330" y="208" width="62" height="48" rx="7"/></g>` +
      `<g fill="${c.b}" fill-opacity="0.45">` +
      `<circle cx="278" cy="228" r="7"/><path d="M266 250 l16 -16 l14 14 l10 -8 v10 z"/>` +
      `<circle cx="350" cy="228" r="7"/><path d="M338 250 l16 -16 l14 14 l10 -8 v10 z"/></g>` +
      // 페이지 전환 표식 (좌우 슬라이드)
      `<g stroke="${c.b}" stroke-width="2.5" fill="none" stroke-linecap="round" stroke-opacity="0.8">` +
      `<path d="M180 170 l-22 0 M166 160 l-12 10 l12 10"/>` +
      `<path d="M470 170 l22 0 M486 160 l12 10 l-12 10"/></g>` +
      // 뷰 위젯 스택 (좌측)
      `<g fill="#0d1326" stroke="${c.a}" stroke-opacity="0.5" stroke-width="1.5">` +
      `<rect x="100" y="96" width="90" height="20" rx="5"/><rect x="108" y="122" width="90" height="20" rx="5"/>` +
      `<rect x="116" y="148" width="90" height="20" rx="5"/></g>` +
      `<text x="100" y="86" font-family="Space Grotesk" font-size="11" fill="${c.b}" fill-opacity="0.8">View Widgets</text>`
    ),
    detail: {
      period: "2014.02 — 2015.02",
      company: "미라콤아이앤씨 · 삼성전자 프로젝트",
      role: "모바일2팀 선임 · Web 개발",
      stack: ["JavaScript", "jQuery", "HTML5", "CSS"],
      work: [
        "MVC 모델을 적용한 Hybrid App 개발",
        "Template 구조화 및 View-Widget 구현",
        "Animation 및 Page 전환 개선",
      ],
      results: [
        "성능 향상 및 사용자 경험 개선",
        "Post Blog Android Version으로 확장",
      ],
    },
  },
  {
    title: "DRM · 콘텐츠 보안 모듈",
    blurb:
      "유료방송·음원·클라우드 콘텐츠를 보호하는 DRM 모듈. Melon Player 4.0의 멀티 디바이스 키 관리와 유니코드 지원을 맡았고, KT uCloud 패키저와 Mobile TV 보안 서버까지 담당했다.",
    tags: ["C / Objective-C", "OMA DRM", "암·복호화", "iOS"],
    links: { live: "", repo: "" },
    accent: "blue",
    // 컨셉: 자물쇠(암호화) + 키 + 멀티 디바이스 배포
    hero: makeVisual("blue", (c) =>
      // 중앙 자물쇠 (보호되는 콘텐츠)
      `<g>` +
      `<path d="M296 148 v-18 a24 24 0 0 1 48 0 v18" fill="none" stroke="${c.b}" stroke-width="3.5" stroke-linecap="round"/>` +
      `<rect x="282" y="148" width="76" height="62" rx="10" fill="${c.glow}" fill-opacity="0.16" ` +
      `stroke="${c.b}" stroke-width="2.5"/>` +
      `<circle cx="320" cy="174" r="6" fill="${c.b}"/>` +
      `<rect x="317" y="178" width="6" height="16" rx="3" fill="${c.b}"/></g>` +
      // 암호화 스트림 (좌측 → 자물쇠)
      `<g font-family="Space Grotesk" font-size="12" fill="${c.a}" fill-opacity="0.6">` +
      `<text x="120" y="140">01001</text><text x="120" y="166">11010</text><text x="120" y="192">10110</text></g>` +
      `<g stroke="${c.a}" stroke-width="1.5" stroke-opacity="0.45" fill="none">` +
      `<path d="M186 136 h 76"/><path d="M186 162 h 76"/><path d="M186 188 h 76"/></g>` +
      // 멀티 디바이스 (우측): 폰 · 태블릿 · TV
      `<g fill="#0d1326" stroke="${c.a}" stroke-width="2">` +
      `<rect x="424" y="96" width="38" height="60" rx="7"/>` +
      `<rect x="480" y="88" width="56" height="76" rx="7"/>` +
      `<rect x="424" y="186" width="112" height="66" rx="8"/></g>` +
      `<g stroke="${c.b}" stroke-width="2" stroke-opacity="0.7"><line x1="452" y1="252" x2="508" y2="252"/></g>` +
      // 자물쇠 → 디바이스 키 전달선
      `<g stroke="${c.b}" stroke-width="1.8" stroke-opacity="0.6" fill="none" stroke-dasharray="5 5">` +
      `<path d="M362 162 C 396 150, 400 128, 420 124"/>` +
      `<path d="M362 182 C 396 196, 400 214, 420 218"/></g>` +
      // 키 아이콘
      `<g stroke="${c.b}" stroke-width="2" fill="none">` +
      `<circle cx="392" cy="252" r="8"/><path d="M400 252 h 30 M424 252 v 8 M414 252 v 8"/></g>` +
      `<text x="416" y="80" font-family="Space Grotesk" font-size="11" fill="${c.b}" fill-opacity="0.8">Multi Device</text>`
    ),
    detail: {
      period: "2010.10 — 2013.07",
      company: "디지캡 (DigiCAP)",
      role: "DRM 개발팀 · 대리",
      stack: ["C", "Objective-C", "C#", "Java JNI", "iOS", "OMA DRM 1.0"],
      work: [
        "Melon Player 4.0 Multi Device & Unicode — 멀티 디바이스 Key 관리 및 유니코드 지원 (2012.01~2012.05)",
        "KT uCloud Storage Broker Service Framework — OMA 1.0 규격 기반 DRM Packager / Repackager / Depackager 구현",
        "Mobile TV DRM Local Secure Server — QuickTime Player로 전송되는 M3U8 내 Encrypted Key 복호화 및 HTTPS 구현",
        "SKT DRM(Android·iOS·eBook) 및 ARM TrustZone DRM, SKB Smart TV UI Application 개발",
      ],
      results: [
        "Melon Player 다중 단말 지원 및 다국어 콘텐츠 호환성 확보",
        "사용자 ID 기반 암·복호화 처리로 보안성 강화 및 안전한 업로드 환경 구축",
        "HTTP → HTTPS 전환으로 통신 보안 강화",
      ],
    },
  },
];

// 업무상 강점 (이력서 "□ 업무상 강점" 6개 항목이 단일 출처 — 임의 생성 금지)
const STRENGTHS = [
  {
    icon: "📈",
    title: "AI·데이터 기반 마케팅 혁신 & Growth Enablement",
    summary:
      "GPT·RAG 마케팅 자동화(Motion AD)부터 의료용 챗봇, 풍력 설비 이상 예측까지 — AI 기술을 매출과 비용 절감으로 직결시킨 실무형 Data-driven Growth 리더십.",
    proof: "마케팅 80% 단축 · 연 2억 절감",
  },
  {
    icon: "🧩",
    title: "플랫폼·SaaS 제품 운영 & 기술 리더십",
    summary:
      "병의원 통합 플랫폼(Motion Series)부터 산업용 SaaS(ONYX FieldPro)까지 다양한 도메인에서 Django·Node·React 기반 제품을 설계·운영. Frontend/Backend/Infra 전 영역 Full-Stack 아키텍처 능력.",
    proof: "운영 효율 40%↑",
  },
  {
    icon: "🤖",
    title: "AI·데이터 엔지니어링 & 분석",
    summary:
      "Python 기반 ML/DL(TensorFlow·PyTorch·scikit-learn) 모델 구축. NLP·Computer Vision·시계열 분석을 설비 이상 탐지·고객 반응 분석 등 실제 서비스에 적용하고 데이터 파이프라인까지 설계.",
    proof: "NLP · CV · 시계열 상용화",
  },
  {
    icon: "🧭",
    title: "경영 & 조직 운영 리더십",
    summary:
      "트라이업 COO로 전략·기획·재무·인력관리를 통합 운영. KPI 기반 성과관리 체계와 협업 인프라(Monday·Notion·GitHub)를 도입해 조직 투명성과 생산성을 끌어올림.",
    proof: "생산성 2배 향상",
  },
  {
    icon: "🌏",
    title: "글로벌 프로젝트 & 커뮤니케이션",
    summary:
      "영국계 본사(ONYX Insight)와 실시간 협업하며 글로벌 프로젝트를 운영. 영문 문서·미팅을 주도한 기술 커뮤니케이션과 Cross-functional 리더십 보유.",
    proof: "영국·실리콘밸리 협업",
  },
  {
    icon: "⚡",
    title: "비용 효율화 & 기술 최적화",
    summary:
      "클라우드 인프라 최적화(AWS·Naver Cloud)와 자동화 배포 파이프라인으로 비용을 절감하고 운영 리스크를 제거. 데이터 기반 리소스 분석으로 ROI를 개선.",
    proof: "연 1.2억 절감 · 운영 리스크 0%",
  },
];

// 기술 스택 (카테고리별) — note: 카드 상단 한 줄 맥락(강점과 연결)
const SKILLS = [
  {
    category: "AI / ML",
    note: "LLM·RAG로 매출을 만들고, ML로 비용을 줄입니다",
    items: ["LLM · RAG", "LangChain / LangGraph", "PyTorch / TensorFlow", "NLP · CV · 시계열", "Vector DB · Prompt Eng."],
  },
  {
    category: "Frontend",
    note: "실리콘밸리·삼성 프로젝트에서 다진 UI 엔지니어링",
    items: ["JavaScript / TypeScript", "React", "Next.js", "Angular", "HTML5 / CSS3"],
  },
  {
    category: "Backend",
    note: "CRM·SaaS를 설계·운영한 멀티 스택 서버 경험",
    items: ["Node.js / NestJS", "Python (Django)", "FastAPI", "Spring / Java", "Express"],
  },
  {
    category: "Infra / Data",
    note: "인프라 최적화로 연 1.2억 절감을 이끈 데이터 파이프라인",
    items: ["AWS", "Naver Cloud", "Serverless (Lambda)", "CI/CD", "MySQL · MongoDB · PostgreSQL"],
  },
  {
    category: "Leadership",
    note: "코드와 사업의 경계에서 50명 조직을 운영하는 COO·CTO",
    items: ["기술 전략 / 로드맵", "조직 운영 (COO)", "KPI 성과관리", "Cross-functional 리딩"],
  },
];

// 전역으로 노출
window.PORTFOLIO_DATA = { PROFILE, STATS, CAREER, PROJECTS, SKILLS, STRENGTHS };
