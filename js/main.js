/**
 * main.js — 테마, 네비게이션, 애니메이션, 콘텐츠 렌더링
 */
(function () {
  "use strict";

  const data = window.PORTFOLIO_DATA;
  if (!data) return;
  const { PROFILE, STATS, CAREER, PROJECTS, SKILLS, STRENGTHS } = data;

  const $ = (sel, root = document) => root.querySelector(sel);
  const $$ = (sel, root = document) => Array.from(root.querySelectorAll(sel));

  /* ----------------------------------------------------------------
     1) 테마 — localStorage > 시스템 선호 (HTML은 기본 dark로 시작)
  ---------------------------------------------------------------- */
  const root = document.documentElement;
  const THEME_KEY = "portfolio-theme";

  function applyTheme(theme) {
    root.setAttribute("data-theme", theme);
  }

  (function initTheme() {
    const stored = localStorage.getItem(THEME_KEY);
    if (stored === "light" || stored === "dark") {
      applyTheme(stored);
    } else if (window.matchMedia("(prefers-color-scheme: light)").matches) {
      applyTheme("light");
    } else {
      applyTheme("dark");
    }
  })();

  const themeToggle = $("#themeToggle");
  if (themeToggle) {
    themeToggle.addEventListener("click", () => {
      const next = root.getAttribute("data-theme") === "dark" ? "light" : "dark";
      applyTheme(next);
      localStorage.setItem(THEME_KEY, next);
    });
  }

  /* ----------------------------------------------------------------
     2) 프로필 텍스트 채우기
  ---------------------------------------------------------------- */
  function setText(id, value) {
    const el = document.getElementById(id);
    if (el && value != null) el.textContent = value;
  }
  setText("brandMark", PROFILE.initials);
  setText("brandName", PROFILE.name);
  setText("heroName", PROFILE.name);
  setText("heroSummary", PROFILE.summary);
  setText("aboutSummary", PROFILE.summary);
  setText("aboutAvatar", PROFILE.initials);
  setText("aboutLocation", PROFILE.location);
  setText("footerName", "© " + PROFILE.name);
  document.title = PROFILE.name + " · COO · CTO · Full-Stack & AI Leader";

  /* ----------------------------------------------------------------
     3) Hero 통계
  ---------------------------------------------------------------- */
  const heroStats = $("#heroStats");
  if (heroStats) {
    heroStats.innerHTML = STATS.map(
      (s) =>
        `<li><span class="stat-value">${esc(s.value)}</span><span class="stat-label">${esc(
          s.label
        )}</span></li>`
    ).join("");
  }

  /* ----------------------------------------------------------------
     4) 타이핑 애니메이션 (roles 순환)
  ---------------------------------------------------------------- */
  const typedEl = $("#typed");
  const reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  if (typedEl && PROFILE.roles && PROFILE.roles.length) {
    if (reduceMotion) {
      typedEl.textContent = PROFILE.roles[0];
      const caret = $(".caret");
      if (caret) caret.style.display = "none";
    } else {
      runTyping(typedEl, PROFILE.roles);
    }
  }

  function runTyping(el, words) {
    let wi = 0;
    let ci = 0;
    let deleting = false;

    function tick() {
      const word = words[wi];
      ci += deleting ? -1 : 1;
      el.textContent = word.slice(0, ci);

      let delay = deleting ? 45 : 90;
      if (!deleting && ci === word.length) {
        delay = 1500; // 단어 완성 후 대기
        deleting = true;
      } else if (deleting && ci === 0) {
        deleting = false;
        wi = (wi + 1) % words.length;
        delay = 350;
      }
      setTimeout(tick, delay);
    }
    tick();
  }

  /* ----------------------------------------------------------------
     4.5) 업무상 강점 렌더링
  ---------------------------------------------------------------- */
  const strengthsGrid = $("#strengthsGrid");
  if (strengthsGrid && Array.isArray(STRENGTHS)) {
    strengthsGrid.innerHTML = STRENGTHS.map(
      (s) => `
        <article class="strength-card reveal">
          <span class="strength-icon" aria-hidden="true">${esc(s.icon || "◆")}</span>
          <h3 class="strength-title">${esc(s.title)}</h3>
          <p class="strength-summary">${esc(s.summary)}</p>
          ${s.proof ? `<span class="strength-proof">${esc(s.proof)}</span>` : ""}
        </article>`
    ).join("");
  }

  /* ----------------------------------------------------------------
     5) 경력 타임라인 렌더링
  ---------------------------------------------------------------- */
  const timeline = $("#timeline");
  if (timeline) {
    timeline.innerHTML = CAREER.map((c) => {
      const highlights = (c.highlights || [])
        .map((h) => `<li>${esc(h)}</li>`)
        .join("");
      const tags = (c.tags || [])
        .map((t) => `<span class="tag">${esc(t)}</span>`)
        .join("");
      return `
        <li class="timeline-item reveal">
          <span class="timeline-period">${esc(c.period)}</span>
          <div class="timeline-card">
            <div class="timeline-role">
              ${esc(c.role)}
              ${c.type ? `<span class="timeline-badge">${esc(c.type)}</span>` : ""}
            </div>
            <div class="timeline-company">${esc(c.company)}</div>
            <p class="timeline-summary">${esc(c.summary)}</p>
            <ul class="timeline-highlights">${highlights}</ul>
            <div class="timeline-tags">${tags}</div>
          </div>
        </li>`;
    }).join("");
  }

  /* ----------------------------------------------------------------
     6) 프로젝트 렌더링
  ---------------------------------------------------------------- */
  const projectGrid = $("#projectGrid");
  if (projectGrid) {
    projectGrid.innerHTML = PROJECTS.map((p, idx) => {
      const tags = (p.tags || [])
        .map((t) => `<span class="tag">${esc(t)}</span>`)
        .join("");
      const links = [];
      if (p.links && p.links.live)
        links.push(
          `<a href="${esc(p.links.live)}" target="_blank" rel="noopener">↗ Live</a>`
        );
      if (p.links && p.links.repo)
        links.push(
          `<a href="${esc(p.links.repo)}" target="_blank" rel="noopener">⌥ Code</a>`
        );
      const thumbClass = "thumb-" + (p.accent || "violet");
      const initials = (p.title || "?").slice(0, 2).toUpperCase();
      // hero SVG가 있으면 비주얼로, 없으면 이니셜 fallback
      const thumbInner = p.hero
        ? `<div class="project-visual">${p.hero}</div>`
        : esc(initials);
      const hasDetail = !!p.detail;
      const moreBtn = hasDetail
        ? `<button class="project-more" type="button" data-project="${idx}" aria-label="${esc(
            p.title
          )} 자세히 보기">자세히 →</button>`
        : "";
      return `
        <article class="project-card reveal${hasDetail ? " has-detail" : ""}"${
        hasDetail ? ` data-project="${idx}" tabindex="0" role="button" aria-label="${esc(p.title)} 자세히 보기"` : ""
      }>
          <div class="project-thumb ${thumbClass}${p.hero ? " has-visual" : ""}">${thumbInner}</div>
          <h3 class="project-title">${esc(p.title)}</h3>
          <p class="project-blurb">${esc(p.blurb)}</p>
          <div class="project-tags">${tags}</div>
          <div class="project-foot">
            <div class="project-links">${links.join("")}</div>
            ${moreBtn}
          </div>
        </article>`;
    }).join("");
  }

  /* ----------------------------------------------------------------
     6.5) 프로젝트 상세 모달
  ---------------------------------------------------------------- */
  const modal = $("#projectModal");
  const modalBody = $("#modalBody");
  let lastFocused = null;

  function listBlock(label, items) {
    if (!items || !items.length) return "";
    const lis = items.map((i) => `<li>${esc(i)}</li>`).join("");
    return `<div class="modal-section"><h4>${esc(label)}</h4><ul>${lis}</ul></div>`;
  }

  function lineupBlock(items, heading) {
    if (!items || !items.length) return "";
    const cards = items
      .map(
        (it) => `
        <div class="lineup-item">
          <span class="lineup-name">${esc(it.name)}</span>
          <span class="lineup-label">${esc(it.label)}</span>
          <p class="lineup-desc">${esc(it.desc)}</p>
        </div>`
      )
      .join("");
    return `<div class="modal-section"><h4>${esc(heading || "제품 구성")}</h4><div class="lineup-grid">${cards}</div></div>`;
  }

  function shotsBlock(items) {
    if (!items || !items.length) return "";
    const figs = items
      .map(
        (s) => `
        <figure class="shot${s.wide ? " wide" : ""}${s.fit ? " fit" : ""}${s.tall ? " tall" : ""}">
          <img src="${esc(s.src)}" alt="${esc(s.alt || "")}" loading="lazy">
          <figcaption>${esc(s.caption)}</figcaption>
        </figure>`
      )
      .join("");
    return `<div class="modal-section"><h4>화면 · 현장</h4><div class="shot-grid">${figs}</div></div>`;
  }

  function openProjectModal(idx) {
    const p = PROJECTS[idx];
    if (!p || !p.detail || !modal || !modalBody) return;
    const d = p.detail;
    const meta = [d.period, d.company, d.role].filter(Boolean);
    const metaHtml = meta
      .map((m) => `<span>${esc(m)}</span>`)
      .join('<span class="modal-dot">·</span>');
    const stack = (d.stack || [])
      .map((t) => `<span class="tag">${esc(t)}</span>`)
      .join("");
    const modalThumb = p.hero
      ? `<div class="modal-visual thumb-${esc(p.accent || "violet")}">${p.hero}</div>`
      : `<span class="modal-thumb thumb-${esc(p.accent || "violet")}">${esc(
          (p.title || "?").slice(0, 2).toUpperCase()
        )}</span>`;
    modalBody.innerHTML = `
      ${modalThumb}
      <h3 id="modalTitle" class="modal-title">${esc(p.title)}</h3>
      <div class="modal-meta">${metaHtml}</div>
      <p class="modal-blurb">${esc(p.blurb)}</p>
      ${lineupBlock(d.lineup, d.lineupHeading)}
      ${listBlock("담당 업무", d.work)}
      ${listBlock("주요 성과", d.results)}
      ${shotsBlock(d.shots)}
      ${stack ? `<div class="modal-section"><h4>기술 스택</h4><div class="modal-stack">${stack}</div></div>` : ""}
    `;
    lastFocused = document.activeElement;
    modal.hidden = false;
    document.body.classList.add("modal-open");
    const closeBtn = $(".modal-close", modal);
    if (closeBtn) closeBtn.focus();
  }

  function closeProjectModal() {
    if (!modal || modal.hidden) return;
    modal.hidden = true;
    document.body.classList.remove("modal-open");
    if (lastFocused && typeof lastFocused.focus === "function") lastFocused.focus();
  }

  if (projectGrid && modal) {
    projectGrid.addEventListener("click", (e) => {
      const card = e.target.closest("[data-project]");
      if (!card) return;
      openProjectModal(Number(card.getAttribute("data-project")));
    });
    projectGrid.addEventListener("keydown", (e) => {
      if (e.key !== "Enter" && e.key !== " ") return;
      const card = e.target.closest(".project-card.has-detail");
      if (!card) return;
      e.preventDefault();
      openProjectModal(Number(card.getAttribute("data-project")));
    });
    modal.addEventListener("click", (e) => {
      if (e.target.hasAttribute("data-modal-close")) closeProjectModal();
    });
    document.addEventListener("keydown", (e) => {
      if (e.key === "Escape") closeProjectModal();
    });
  }

  /* ----------------------------------------------------------------
     7) 스킬 렌더링
  ---------------------------------------------------------------- */
  const skillsGrid = $("#skillsGrid");
  if (skillsGrid) {
    skillsGrid.innerHTML = SKILLS.map((g) => {
      const items = (g.items || [])
        .map((i) => `<span>${esc(i)}</span>`)
        .join("");
      const note = g.note
        ? `<p class="skill-note">${esc(g.note)}</p>`
        : "";
      return `
        <div class="skill-group reveal">
          <h3>${esc(g.category)}</h3>
          ${note}
          <div class="skill-list">${items}</div>
        </div>`;
    }).join("");
  }

  /* ----------------------------------------------------------------
     8) 연락처 버튼
  ---------------------------------------------------------------- */
  const contactActions = $("#contactActions");
  if (contactActions) {
    const btns = [];
    if (PROFILE.email)
      btns.push(
        `<span class="contact-info">✉ ${esc(PROFILE.email)}</span>`
      );
    if (PROFILE.phone)
      btns.push(
        `<span class="contact-info">☎ ${esc(PROFILE.phone)}</span>`
      );
    const s = PROFILE.social || {};
    if (s.github)
      btns.push(
        `<a class="btn btn-ghost" href="${esc(s.github)}" target="_blank" rel="noopener">GitHub</a>`
      );
    if (s.linkedin)
      btns.push(
        `<a class="btn btn-ghost" href="${esc(s.linkedin)}" target="_blank" rel="noopener">LinkedIn</a>`
      );
    if (s.website)
      btns.push(
        `<a class="btn btn-ghost" href="${esc(s.website)}" target="_blank" rel="noopener">Website</a>`
      );
    contactActions.innerHTML = btns.join("");
  }

  /* ----------------------------------------------------------------
     9) 네비게이션 — 스크롤 효과 + 모바일 메뉴 + 스크롤스파이
  ---------------------------------------------------------------- */
  const navbar = $("#navbar");
  const menuToggle = $("#menuToggle");
  const navLinks = $("#navLinks");

  function onScroll() {
    if (navbar) navbar.classList.toggle("scrolled", window.scrollY > 20);
  }
  window.addEventListener("scroll", onScroll, { passive: true });
  onScroll();

  if (menuToggle && navLinks) {
    menuToggle.addEventListener("click", () => {
      const open = navLinks.classList.toggle("open");
      menuToggle.setAttribute("aria-expanded", String(open));
      menuToggle.setAttribute("aria-label", open ? "메뉴 닫기" : "메뉴 열기");
    });
    // 링크 클릭 시 모바일 메뉴 닫기
    $$(".nav-link", navLinks).forEach((link) =>
      link.addEventListener("click", () => {
        navLinks.classList.remove("open");
        menuToggle.setAttribute("aria-expanded", "false");
      })
    );
  }

  // 스크롤스파이 — 현재 섹션 메뉴 하이라이트
  const sections = ["about", "strengths", "career", "projects", "contact"]
    .map((id) => document.getElementById(id))
    .filter(Boolean);
  const linkFor = {};
  $$(".nav-link").forEach((l) => {
    const href = l.getAttribute("href");
    if (href) linkFor[href.slice(1)] = l;
  });
  if (sections.length && "IntersectionObserver" in window) {
    const spy = new IntersectionObserver(
      (entries) => {
        entries.forEach((e) => {
          if (e.isIntersecting) {
            $$(".nav-link").forEach((l) => l.classList.remove("active"));
            const active = linkFor[e.target.id];
            if (active) active.classList.add("active");
          }
        });
      },
      { rootMargin: "-45% 0px -50% 0px" }
    );
    sections.forEach((s) => spy.observe(s));
  }

  /* ----------------------------------------------------------------
     10) Reveal 애니메이션 (IntersectionObserver)
  ---------------------------------------------------------------- */
  const revealEls = $$(".reveal");
  if (reduceMotion || !("IntersectionObserver" in window)) {
    revealEls.forEach((el) => el.classList.add("in"));
  } else {
    const io = new IntersectionObserver(
      (entries, obs) => {
        entries.forEach((e) => {
          if (e.isIntersecting) {
            e.target.classList.add("in");
            obs.unobserve(e.target);
          }
        });
      },
      { threshold: 0.12, rootMargin: "0px 0px -40px 0px" }
    );
    revealEls.forEach((el) => io.observe(el));
  }

  /* ----------------------------------------------------------------
     유틸 — HTML 이스케이프
  ---------------------------------------------------------------- */
  function esc(str) {
    return String(str)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;")
      .replace(/'/g, "&#39;");
  }
})();
