// compact step 4 — section-structure (설계 compact §C1, 원 §4·§5 예외 (2)~(5))
import { execFileSync } from 'node:child_process';
import { readFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import { expect } from '@playwright/test';
import { test } from '../helpers/theme.js';
import { GUARD_BASE } from '../helpers/design-guard.js';
import { applyColorAllow } from '../helpers/design-guard-color-rules.js';

const baseline = JSON.parse(readFileSync(new URL('../fixtures/baseline-data.json', import.meta.url), 'utf8'));

// 원 §4 FINAL 표 그대로
const FINAL_SECTIONS = [
  { id: 'hero', cls: 'hero', kicker: null, heading: 'H1#heroName' },
  { id: 'career', cls: 'section', kicker: '01 — Career', heading: 'H2:경력 & 창업' },
  { id: 'projects', cls: 'section section-alt', kicker: '02 — Projects', heading: 'H2:프로젝트 & 제품' },
  { id: 'strengths', cls: 'section', kicker: '03 — Strengths', heading: 'H2:업무상 강점' },
  { id: 'about', cls: 'section section-alt', kicker: '04 — About', heading: 'H2:소개' },
  { id: 'contact', cls: 'section', kicker: '05 — Contact', heading: 'H2:연락처' },
];
const NAV_ORDER = ['#career', '#projects', '#strengths', '#about', '#contact'];

async function openMenuIfCollapsed(page) {
  const toggle = page.locator('#menuToggle');
  if (await toggle.isVisible()) {
    await toggle.click();
    await expect(page.locator('#navLinks')).toHaveClass(/(^|\s)open(\s|$)/);
  }
}

test.describe('compact step 4 final-contract: section-structure', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/');
  });

  test('섹션 id·class·kicker·heading이 FINAL 표와 정확히 같다', async ({ page }) => {
    const sections = await page.$$eval('main > section', (els) => {
      const n = (s) => String(s).replace(/\s+/g, ' ').trim();
      return els.map((s) => {
        const kickers = s.querySelectorAll('.section-kicker');
        let heading;
        if (s.id === 'hero') {
          const h1 = s.querySelector('h1');
          heading = h1 ? 'H1#' + h1.id : null;
        } else {
          const h2s = s.querySelectorAll('h2.section-title');
          heading = h2s.length === 1 ? 'H2:' + n(h2s[0].textContent) : 'h2-count:' + h2s.length;
        }
        return {
          id: s.id,
          cls: s.className,
          kicker: kickers.length === 0 ? null : kickers.length === 1 ? n(kickers[0].textContent) : 'many',
          heading,
        };
      });
    });
    expect(sections).toEqual(FINAL_SECTIONS);
    // strengths section-sub 유지
    await expect(page.locator('#strengths .section-head .section-sub')).toHaveCount(1);
  });

  test('about: 본문 뒤 h3.subsection-title 기술 스택 1개, 그 뒤 #skillsGrid, skill-group 제목은 h3', async ({ page }) => {
    await expect(page.locator('h3.subsection-title')).toHaveCount(1);
    await expect(page.locator('#about h3.subsection-title')).toHaveText('기술 스택');
    await expect(page.locator('#about #skillsGrid')).toHaveCount(1);
    const order = await page.evaluate(() => {
      const body = document.querySelector('#about .about-grid');
      const h3 = document.querySelector('#about h3.subsection-title');
      const grid = document.getElementById('skillsGrid');
      const after = (a, b) => !!(a && b) && (a.compareDocumentPosition(b) & Node.DOCUMENT_POSITION_FOLLOWING) !== 0;
      return { h3AfterBody: after(body, h3), gridAfterH3: after(h3, grid) };
    });
    expect(order).toEqual({ h3AfterBody: true, gridAfterH3: true });
    const groups = page.locator('#skillsGrid .skill-group');
    await expect(groups).toHaveCount(baseline.SKILLS.length);
    await expect(page.locator('#skillsGrid .skill-group > h3')).toHaveText(baseline.SKILLS.map((g) => g.category));
    await expect(page.locator('#skillsGrid h4')).toHaveCount(0);
  });

  test('contact: .contact-card와 h3 함께 만들어요 유지, 기술 스택은 없음', async ({ page }) => {
    await expect(page.locator('#contact .contact-card')).toHaveCount(1);
    await expect(page.locator('#contact .contact-card h3')).toHaveText('함께 만들어요');
    await expect(page.locator('#contact #skillsGrid')).toHaveCount(0);
  });

  test('nav 순서: career, projects, strengths, about, contact', async ({ page }) => {
    const hrefs = await page.$$eval('#navLinks .nav-link', (els) => els.map((e) => e.getAttribute('href')));
    expect(hrefs).toEqual(NAV_ORDER);
  });

  test('스크롤스파이: projects', async ({ page }) => {
    await openMenuIfCollapsed(page);
    const link = page.locator('.nav-link[href="#projects"]');
    await link.click();
    await expect(link).toHaveClass(/active/);
  });

  test('스크롤스파이: about', async ({ page }) => {
    await openMenuIfCollapsed(page);
    const link = page.locator('.nav-link[href="#about"]');
    await link.click();
    await expect(link).toHaveClass(/active/);
  });

  test('.scroll-hint href는 #career', async ({ page }) => {
    await expect(page.locator('.scroll-hint')).toHaveCount(1);
    await expect(page.locator('.scroll-hint')).toHaveAttribute('href', '#career');
  });

  test('heading 계층: h1 1개, 단계 건너뜀 없음', async ({ page }) => {
    await expect(page.locator('h1')).toHaveCount(1);
    const levels = await page.$$eval('main h1, main h2, main h3, main h4, main h5, main h6', (els) =>
      els.map((e) => Number(e.tagName.slice(1))),
    );
    expect(levels[0]).toBe(1);
    const skips = levels.flatMap((l, i) => (i > 0 && l > levels[i - 1] + 1 ? [`${levels[i - 1]}->${l}@${i}`] : []));
    expect(skips).toEqual([]);
    // 각 섹션(hero 제외)의 h2는 정확히 1개
    for (const s of FINAL_SECTIONS.slice(1)) {
      await expect(page.locator(`#${s.id} h2`), s.id).toHaveCount(1);
    }
  });

  test('#heroFeatured 유지: #heroStats 바로 다음, 대표 카드 1·5·7', async ({ page }) => {
    const prev = await page.$eval('#heroFeatured', (el) => (el.previousElementSibling ? el.previousElementSibling.id : null));
    expect(prev).toBe('heroStats');
    const idx = await page.$$eval('#heroFeatured button.featured-card', (els) => els.map((e) => e.dataset.project));
    expect(idx).toEqual(['1', '5', '7']);
  });

  test('#projectGrid에 PROJECTS 13개가 data.js 순서로 렌더된다', async ({ page }) => {
    const cards = page.locator('#projectGrid .project-card');
    await expect(cards).toHaveCount(13);
    const idx = await cards.evaluateAll((els) => els.map((e) => e.dataset.project));
    expect(idx).toEqual(baseline.PROJECTS.map((_, i) => String(i)));
    await expect(page.locator('#projectGrid .project-card .project-title')).toHaveText(baseline.PROJECTS.map((p) => p.title));
  });
});

// compact step 5 — section-layout (원 §7·§11.2, tokens: tests/fixtures/claude-design-intake.json)
const intake = JSON.parse(readFileSync(new URL('../fixtures/claude-design-intake.json', import.meta.url), 'utf8'));
const TOKENS = intake.tokens;
const LAYOUT_SECTIONS = FINAL_SECTIONS.slice(1).map((s) => s.id);
const EXPECTED_COLUMNS = { 375: 1, 768: 2, 1280: 3 };

function viewportKey(page) {
  const w = page.viewportSize().width;
  if (!(String(w) in TOKENS.sectionPaddingPx)) throw new Error(`layout: unexpected viewport width ${w}`);
  return String(w);
}

test.describe('compact step 5 final-contract: section-layout', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/');
    await page.evaluate(() => document.fonts.ready);
  });

  test('가로 스크롤이 없다', async ({ page }) => {
    const overflow = await page.evaluate(() => document.documentElement.scrollWidth - document.documentElement.clientWidth);
    expect(overflow).toBe(0);
  });

  test('섹션 padding-top·bottom이 tokens.sectionPaddingPx[viewport]와 같다', async ({ page }) => {
    const want = TOKENS.sectionPaddingPx[viewportKey(page)];
    const pads = await page.$$eval('main > section', (els, ids) =>
      els.filter((s) => ids.includes(s.id)).map((s) => {
        const cs = getComputedStyle(s);
        return { id: s.id, top: cs.paddingTop, bottom: cs.paddingBottom };
      }), LAYOUT_SECTIONS);
    expect(pads).toEqual(LAYOUT_SECTIONS.map((id) => ({ id, top: `${want}px`, bottom: `${want}px` })));
  });

  test('#heroFeatured·#projectGrid·#strengthsGrid의 row·column gap이 tokens.cardGapPx', async ({ page }) => {
    const gaps = await page.evaluate(() =>
      ['heroFeatured', 'projectGrid', 'strengthsGrid'].map((id) => {
        const cs = getComputedStyle(document.getElementById(id));
        return { id, row: cs.rowGap, column: cs.columnGap };
      }),
    );
    const g = `${TOKENS.cardGapPx}px`;
    expect(gaps).toEqual(['heroFeatured', 'projectGrid', 'strengthsGrid'].map((id) => ({ id, row: g, column: g })));
  });

  test('#projectGrid·#strengthsGrid 열 수가 375=1, 768=2, 1280=3', async ({ page }) => {
    const want = EXPECTED_COLUMNS[viewportKey(page)];
    const cols = await page.evaluate(() =>
      ['projectGrid', 'strengthsGrid'].map((id) => {
        const v = getComputedStyle(document.getElementById(id)).gridTemplateColumns;
        return { id, n: v === 'none' ? 0 : v.trim().split(/\s+/).length };
      }),
    );
    expect(cols).toEqual([{ id: 'projectGrid', n: want }, { id: 'strengthsGrid', n: want }]);
  });

  test('Career: 375 세로, 768·1280 가로(top 차 < 24px)', async ({ page }) => {
    const horizontal = viewportKey(page) !== '375';
    const items = await page.$$eval('#timeline .timeline-item', (els) =>
      els.map((el) => {
        const p = el.querySelector('.timeline-period').getBoundingClientRect();
        const c = el.querySelector('.timeline-card').getBoundingClientRect();
        return { pTop: p.top, pBottom: p.bottom, pRight: p.right, cTop: c.top, cLeft: c.left };
      }),
    );
    expect(items.length).toBeGreaterThan(0);
    for (const [i, it] of items.entries()) {
      if (horizontal) {
        expect(Math.abs(it.cTop - it.pTop), `item ${i} top diff`).toBeLessThan(24);
        expect(it.cLeft, `item ${i} card right of period`).toBeGreaterThanOrEqual(it.pRight);
      } else {
        expect(it.cTop, `item ${i} card below period`).toBeGreaterThanOrEqual(it.pBottom);
      }
    }
  });

  test('375에서 Career highlights가 보인다', async ({ page }) => {
    test.skip(viewportKey(page) !== '375', '375 전용');
    const lists = page.locator('#timeline .timeline-highlights');
    expect(await lists.count()).toBeGreaterThan(0);
    for (let i = 0; i < (await lists.count()); i++) {
      await lists.nth(i).scrollIntoViewIfNeeded();
      await expect(lists.nth(i)).toBeVisible();
      const box = await lists.nth(i).boundingBox();
      expect(box.x).toBeGreaterThanOrEqual(0);
      expect(box.x + box.width).toBeLessThanOrEqual(375);
    }
  });

  test('.subsection-title은 h2보다 위계가 낮다(weight ≤ h2, size < h2)', async ({ page }) => {
    const t = await page.evaluate(() => {
      const h2 = getComputedStyle(document.querySelector('#about h2.section-title'));
      const h3 = getComputedStyle(document.querySelector('#about h3.subsection-title'));
      return {
        h2w: Number(h2.fontWeight), h3w: Number(h3.fontWeight),
        h2s: parseFloat(h2.fontSize), h3s: parseFloat(h3.fontSize),
      };
    });
    expect(t.h3w).toBeLessThanOrEqual(t.h2w);
    expect(t.h3s).toBeLessThan(t.h2s);
  });
});

// compact step 6 — component-states (원 §11.2 step 46·49·50: hit target, 비색 hover/active, blurb clamp, stripe)
// 측정 전 대상과 조상의 유한 애니메이션만 기다린다(무한 장식 .caret·.scroll-hint span은 제외, 문서 전체 대기 금지).
async function waitForFiniteAnimations(page, selector, nth = 0, timeoutMs = 5000) {
  const done = page.evaluate(
    async ([sel, i]) => {
      const el = document.querySelectorAll(sel)[i];
      if (!el) throw new Error(`missing:${sel}[${i}]`);
      const anims = [...el.getAnimations({ subtree: true })];
      for (let a = el.parentElement; a; a = a.parentElement) anims.push(...a.getAnimations());
      const finite = anims.filter(
        (x) => x.effect && x.effect.getComputedTiming().iterations !== Infinity && ['running', 'pending'].includes(x.playState),
      );
      await Promise.all(finite.map((x) => x.finished.catch(() => null)));
    },
    [selector, nth],
  );
  let timer;
  const timeout = new Promise((_, reject) => {
    timer = setTimeout(() => reject(new Error(`animation-timeout:${selector}`)), timeoutMs);
  });
  try {
    await Promise.race([done, timeout]);
  } finally {
    clearTimeout(timer);
  }
}

async function measureState(page, selector, nth = 0) {
  await waitForFiniteAnimations(page, selector, nth);
  return page.evaluate(
    ([sel, i]) => {
      const cs = getComputedStyle(document.querySelectorAll(sel)[i]);
      return {
        color: cs.color,
        backgroundColor: cs.backgroundColor,
        borderColor: cs.borderColor,
        transform: cs.transform,
        opacity: cs.opacity,
      };
    },
    [selector, nth],
  );
}

const COLOR_KEYS = ['color', 'backgroundColor', 'borderColor'];
const pickColors = (s) => Object.fromEntries(COLOR_KEYS.map((k) => [k, s[k]]));

// 대상마다 새 page: default → hover → active(mouse.down 직후). mouse.up은 하지 않는다(이동·모달 열기 방지).
async function measureStateSequence(context, selector, nth, { baseCss = null } = {}) {
  const page = await context.newPage();
  try {
    if (baseCss !== null) {
      await page.route('**/css/style.css', (route) => route.fulfill({ status: 200, contentType: 'text/css', body: baseCss }));
    }
    await page.goto('/');
    await page.evaluate(() => document.fonts.ready);
    const loc = page.locator(selector).nth(nth);
    await loc.scrollIntoViewIfNeeded();
    // 등장(.reveal → .in) 전환이 시작된 뒤에 기다려야 default가 등장 도중 값이 아니다.
    await page.waitForFunction(([sel, i]) => {
      const r = document.querySelectorAll(sel)[i].closest('.reveal');
      return !r || r.classList.contains('in');
    }, [selector, nth]);
    await waitForFiniteAnimations(page, selector, nth);
    await page.mouse.move(0, 0);
    const def = await measureState(page, selector, nth);
    await loc.hover();
    const hover = await measureState(page, selector, nth);
    await page.mouse.down();
    const active = await measureState(page, selector, nth);
    return { default: def, hover, active };
  } finally {
    await page.close();
  }
}

const HIT_SINGLE = ['#themeToggle'];
const HIT_ALL = ['.nav-link', '.hero-cta .btn', '.featured-card', '#projectGrid .project-card', '#contactActions a'];
const HIT_IF_VISIBLE = ['#menuToggle', '.scroll-hint'];
const HIT_COUNTS = { '.featured-card': 3, '#projectGrid .project-card': 13 };

test.describe('compact step 6 final-contract: component-states', () => {
  test('hit target: 기본 상태 대상 bbox w·h ≥ 44px', async ({ page }) => {
    await page.goto('/');
    await page.evaluate(() => document.fonts.ready);
    const sizes = [];
    const measureAll = async (sel) => {
      const n = await page.locator(sel).count();
      for (let i = 0; i < n; i++) {
        await waitForFiniteAnimations(page, sel, i);
        const r = await page.evaluate(([s, k]) => {
          const b = document.querySelectorAll(s)[k].getBoundingClientRect();
          return { w: b.width, h: b.height };
        }, [sel, i]);
        sizes.push({ target: `${sel}[${i}]`, ...r });
      }
      return n;
    };
    for (const sel of HIT_SINGLE) expect(await measureAll(sel), sel).toBe(1);
    for (const sel of HIT_ALL) {
      const n = await measureAll(sel);
      if (sel in HIT_COUNTS) expect(n, sel).toBe(HIT_COUNTS[sel]);
      else if (sel !== '#contactActions a') expect(n, sel).toBeGreaterThan(0);
    }
    for (const sel of HIT_IF_VISIBLE) {
      if (await page.locator(sel).isVisible()) await measureAll(sel);
    }
    const small = sizes.filter((s) => s.w < 44 || s.h < 44).map((s) => `${s.target} ${s.w.toFixed(1)}x${s.h.toFixed(1)}`);
    expect(small).toEqual([]);
  });

  test('hover·active: transform 또는 opacity가 바뀌고 색 3속성은 BASE(+§C6 허용 선언) 그대로', async ({ context }, testInfo) => {
    test.skip(!/^desktop-(dark|light)$/.test(testInfo.project.name), 'desktop-dark·desktop-light 전용');
    test.setTimeout(120000);
    // step 9 color-contrast 수정(HOO81_COLOR_V52_ALLOW)만 기준에 반영한다. 그 밖의 색 변화는 계속 실패.
    const baseCss = applyColorAllow(execFileSync('git', ['show', `${GUARD_BASE}:css/style.css`], {
      cwd: fileURLToPath(new URL('../..', import.meta.url)),
      encoding: 'utf8',
    }));
    const targets = [
      { name: 'hero-cta-btn-0', sel: '.hero-cta .btn', nth: 0 },
      { name: 'hero-cta-btn-1', sel: '.hero-cta .btn', nth: 1 },
      { name: 'grid-card-0', sel: '#projectGrid .project-card', nth: 0 },
      { name: 'grid-card-1', sel: '#projectGrid .project-card', nth: 1 },
    ];
    const cur = {};
    for (const t of targets) {
      cur[t.name] = await measureStateSequence(context, t.sel, t.nth);
      const base = await measureStateSequence(context, t.sel, t.nth, { baseCss });
      for (const st of ['default', 'hover', 'active']) {
        expect(pickColors(cur[t.name][st]), `${t.name} ${st} colors = BASE`).toEqual(pickColors(base[st]));
      }
    }
    // 첫 .featured-card(data-project 1)는 grid-card-1과 같은 상태 색
    const featured = await measureStateSequence(context, '.featured-card', 0);
    for (const st of ['default', 'hover', 'active']) {
      expect(pickColors(featured[st]), `featured-card-0 ${st} colors = grid-card-1`).toEqual(pickColors(cur['grid-card-1'][st]));
    }
    cur['featured-card-0'] = featured;
    const unchanged = [];
    for (const [name, s] of Object.entries(cur)) {
      for (const st of ['hover', 'active']) {
        if (s[st].transform === s.default.transform && s[st].opacity === s.default.opacity) unchanged.push(`${name}:${st}`);
      }
    }
    expect(unchanged).toEqual([]);
  });

  test('blurb clamp: 대표 3 + grid 13은 line-clamp 3, 전문 유지, 모달은 none', async ({ page }) => {
    await page.goto('/');
    const blurbs = await page.$$eval('#heroFeatured .featured-blurb, #projectGrid .project-card .project-blurb', (els) =>
      els.map((el) => ({
        project: Number(el.closest('[data-project]').dataset.project),
        clamp: getComputedStyle(el).webkitLineClamp,
        text: el.textContent,
        featured: el.classList.contains('featured-blurb'),
        height: el.getBoundingClientRect().height,
        maxHeight: parseFloat(getComputedStyle(el).lineHeight) * 3 + 1,
      })),
    );
    expect(blurbs).toHaveLength(16);
    for (const b of blurbs) {
      expect(b.clamp, `project ${b.project}`).toBe('3');
      // span은 display: block 계약이라 line-clamp가 그려지지 않는다 → 대표 카드 blurb는 화면 높이도 3줄 이하
      if (b.featured) expect(b.height, `featured ${b.project} 화면에서 3줄 이하`).toBeLessThanOrEqual(b.maxHeight);
      expect(b.text, `project ${b.project}`).toBe(baseline.PROJECTS[b.project].blurb);
    }
    await page.locator('#projectGrid .project-card[data-project="0"]').click();
    await expect(page.locator('#projectModal')).toBeVisible();
    const modal = await page.$eval('#projectModal .modal-blurb', (el) => ({ clamp: getComputedStyle(el).webkitLineClamp, text: el.textContent }));
    expect(modal).toEqual({ clamp: 'none', text: baseline.PROJECTS[0].blurb });
  });

  test('stripe: .strength-card::before 없음(content none) 또는 크기 0, 카드 6개 순서·내용 = STRENGTHS', async ({ page }) => {
    await page.goto('/');
    const cards = await page.$$eval('#strengthsGrid .strength-card', (els) =>
      els.map((el) => {
        const b = getComputedStyle(el, '::before');
        const q = (s) => (el.querySelector(s) ? el.querySelector(s).textContent : null);
        return {
          stripe: b.content === 'none' || parseFloat(b.width) === 0 || parseFloat(b.height) === 0,
          icon: q('.strength-icon'),
          title: q('.strength-title'),
          summary: q('.strength-summary'),
          proof: q('.strength-proof'),
        };
      }),
    );
    expect(cards.map((c) => c.stripe)).toEqual(baseline.STRENGTHS.map(() => true));
    expect(cards.map(({ stripe, ...rest }) => rest)).toEqual(
      baseline.STRENGTHS.map((s) => ({ icon: s.icon || '◆', title: s.title, summary: s.summary, proof: s.proof || null })),
    );
  });
});

// compact step 7 — print (원 §7 인쇄: A 기본 상태, B lightbox 열린 상태, clamp 해제, PDF 조건)
// `/Type` 다음에 오는 `/Page`만 센다(`/Pages` 제외).
const pdfPageCount = (buf) => (buf.toString('latin1').match(/\/Type\s*\/Page\b/g) || []).length;

const PRINT_HIDDEN = ['#themeToggle', '#menuToggle', '#navLinks', '.scroll-hint', '#projectModal'];
const PRINT_VISIBLE = ['#hero', '#heroFeatured', '#career', '#projects', '#strengths', '#about', '#contact'];

async function expectPdfOk(page) {
  const buf = await page.pdf();
  expect(buf.length, 'pdf bytes').toBeGreaterThan(10240);
  expect(pdfPageCount(buf), 'pdf pages').toBeGreaterThanOrEqual(1);
}

test.describe('compact step 7 final-contract: print', () => {
  test('pdfPageCount fixture 4개', () => {
    const cases = [
      ['/Type /Page', 1],
      ['/Type/Page', 1],
      ['/Type /Pages', 0],
      ['/Page', 0],
    ];
    expect(cases.map(([s]) => pdfPageCount(Buffer.from(s, 'latin1')))).toEqual(cases.map(([, n]) => n));
  });

  test('A 기본 상태: 본문·대표 visible·opacity 1, reveal 비어 있지 않음, interaction·modal 숨김, lightbox 없음/none, clamp 해제, PDF', async ({ page }, testInfo) => {
    test.skip(!/^desktop-(dark|light)$/.test(testInfo.project.name), 'desktop-dark·desktop-light 전용');
    await page.goto('/');
    await page.evaluate(() => document.fonts.ready);
    await page.emulateMedia({ media: 'print' });
    for (const sel of PRINT_VISIBLE) {
      await expect(page.locator(sel), sel).toBeVisible();
      expect(await page.$eval(sel, (el) => getComputedStyle(el).opacity), `${sel} opacity`).toBe('1');
    }
    const reveals = await page.$$eval('.reveal', (els) =>
      els
        .filter((el) => getComputedStyle(el).display !== 'none')
        .map((el, i) => ({
          i,
          cls: el.className,
          opacity: getComputedStyle(el).opacity,
          empty: el.textContent.trim() === '' && el.children.length === 0,
        })),
    );
    expect(reveals.length).toBeGreaterThan(0);
    expect(reveals.filter((r) => r.opacity !== '1' || r.empty)).toEqual([]);
    for (const sel of PRINT_HIDDEN) await expect(page.locator(sel).first(), sel).toBeHidden();
    const lb = await page.$$eval('.lightbox', (els) => els.map((el) => getComputedStyle(el).display));
    expect(lb.every((d) => d === 'none'), `lightbox ${JSON.stringify(lb)}`).toBe(true);
    const clamps = await page.$$eval('#heroFeatured .featured-blurb, #projectGrid .project-blurb', (els) =>
      els.map((el) => getComputedStyle(el).webkitLineClamp),
    );
    expect(clamps).toHaveLength(16);
    expect(clamps.filter((c) => c !== 'none' && c !== 'unset')).toEqual([]);
    await expectPdfOk(page);
  });

  test('C 인쇄 대비: 흰 종이 위 step 9 변경 글자(.stat-label·.about-meta dt·.footer-inner) 대비 4.5 이상', async ({ page }, testInfo) => {
    test.skip(!/^desktop-(dark|light)$/.test(testInfo.project.name), 'desktop-dark·desktop-light 전용');
    await page.goto('/');
    await page.evaluate(() => document.fonts.ready);
    await page.emulateMedia({ media: 'print' });
    const ratios = await page.$$eval('.stat-label, .about-meta dt, .footer-inner', (els) => {
      const lum = (c) => {
        const [r, g, b] = c.match(/[\d.]+/g).slice(0, 3).map(Number).map((v) => {
          const x = v / 255;
          return x <= 0.03928 ? x / 12.92 : ((x + 0.055) / 1.055) ** 2.4;
        });
        return 0.2126 * r + 0.7152 * g + 0.0722 * b;
      };
      const paper = 'rgb(255, 255, 255)';
      return els.map((el) => {
        const a = lum(getComputedStyle(el).color);
        const b = lum(paper);
        return { sel: el.className || el.tagName, ratio: (Math.max(a, b) + 0.05) / (Math.min(a, b) + 0.05) };
      });
    });
    expect(ratios.length).toBeGreaterThan(0);
    expect(ratios.filter((r) => r.ratio < 4.5)).toEqual([]);
  });

  test('B lightbox 열린 상태: print에서 .lightbox·#projectModal none, PDF', async ({ page }, testInfo) => {
    test.skip(!/^desktop-(dark|light)$/.test(testInfo.project.name), 'desktop-dark·desktop-light 전용');
    await page.goto('/');
    await page.locator('#projectGrid .project-card[data-project="0"]').click();
    await expect(page.locator('#projectModal')).toBeVisible();
    await page.locator('#projectModal .shot-zoom').first().click();
    await expect(page.locator('.lightbox')).toBeVisible();
    await page.emulateMedia({ media: 'print' });
    const disp = await page.evaluate(() => ({
      lightbox: getComputedStyle(document.querySelector('.lightbox')).display,
      modal: getComputedStyle(document.getElementById('projectModal')).display,
    }));
    expect(disp).toEqual({ lightbox: 'none', modal: 'none' });
    await expectPdfOk(page);
  });
});

// compact step 10 — visual-final-contract (§C1 bytes·콘텐츠·menu·modal). screenshot 결과에는 의존하지 않는다.
const REPO_ROOT_DIR = fileURLToPath(new URL('../..', import.meta.url));
const EVIDENCE_STEP0 = new URL('../.tmp/compact/evidence-step0.json', import.meta.url);
const FEATURED_INDEXES = [1, 5, 7];
const MODAL_CHECK_INDEXES = [0, 1, 2, 5, 7, 12];

const gitShowBytes = (rev, file) => execFileSync('git', ['show', `${rev}:${file}`], { cwd: REPO_ROOT_DIR, maxBuffer: 64 * 1024 * 1024 });

// baseline data.js에서 PROJECTS[k] title 줄 바로 다음에 `featured: true,`를 넣은 기대 bytes. title 줄은 정확히 1개여야 한다.
function expectedDataJs(baseText, titles) {
  const lines = baseText.split('\n');
  const inserts = FEATURED_INDEXES.map((k) => {
    const want = `title: ${JSON.stringify(titles[k])},`;
    const at = lines.flatMap((l, i) => (l.trim() === want ? [i] : []));
    if (at.length !== 1) throw new Error(`data.js: title line for PROJECTS[${k}] found ${at.length}x`);
    return { at: at[0], indent: lines[at[0]].match(/^\s*/)[0] };
  });
  for (const { at, indent } of [...inserts].sort((a, b) => b.at - a.at)) lines.splice(at + 1, 0, `${indent}featured: true,`);
  return lines.join('\n');
}

// 현재 bytes가 기대 bytes와 정확히 같을 때만 통과(featured: false·다른 field·형식 변경·줄 수 차이 모두 거부).
function dataJsViolations(baseBuf, curBuf, titles) {
  const want = Buffer.from(expectedDataJs(baseBuf.toString('utf8'), titles), 'utf8');
  return Buffer.compare(want, curBuf) === 0 ? [] : ['data.js: bytes != baseline + featured 3줄'];
}

test.describe('compact step 10 final-contract: bytes·content·menu·modal', () => {
  const evidence = () => JSON.parse(readFileSync(EVIDENCE_STEP0, 'utf8'));
  const titles = baseline.PROJECTS.map((p) => p.title);

  test('js/data.js = evidence-step0 baselineHead + index 1·5·7 title 다음 featured: true, 3줄', () => {
    const head = evidence().baselineHead;
    expect(head).toMatch(/^[0-9a-f]{40}$/);
    const base = gitShowBytes(head, 'js/data.js');
    const cur = readFileSync(new URL('../../js/data.js', import.meta.url));
    expect(cur.length - base.length).toBe(3 * Buffer.byteLength('    featured: true,\n'));
    expect(dataJsViolations(base, cur, titles)).toEqual([]);
  });

  test('data.js 판정은 featured: false·다른 field·형식 변경·줄 수 차이를 거부한다', () => {
    const base = gitShowBytes(evidence().baselineHead, 'js/data.js');
    const good = expectedDataJs(base.toString('utf8'), titles);
    const mutate = (from, to) => {
      expect(good.includes(from), `fixture source: ${from}`).toBe(true);
      return Buffer.from(good.replace(from, to), 'utf8');
    };
    const motion = `title: ${JSON.stringify(titles[1])},`;
    const cases = {
      ok: Buffer.from(good, 'utf8'),
      featuredFalse: mutate(`${motion}\n    featured: true,`, `${motion}\n    featured: false,`),
      noSpace: mutate(`${motion}\n    featured: true,`, `${motion}\n    featured:true,`),
      indent: mutate(`${motion}\n    featured: true,`, `${motion}\n  featured: true,`),
      extraField: mutate(`${motion}\n    featured: true,`, `${motion}\n    featured: true,\n    pinned: true,`),
      fourthLine: mutate(`title: ${JSON.stringify(titles[0])},`, `title: ${JSON.stringify(titles[0])},\n    featured: true,`),
      missing: mutate(`${motion}\n    featured: true,\n`, `${motion}\n`),
      // featured 줄을 title 앞으로 옮긴다(줄 수·내용 같음, 위치만 다름) → title 다음 줄 계약 위반
      wrongPlace: mutate(`\n    ${motion}\n    featured: true,\n`, `\n    featured: true,\n    ${motion}\n`),
      crlf: Buffer.from(good.replace('\n', '\r\n'), 'utf8'),
      otherEdit: mutate(JSON.stringify(titles[12]), JSON.stringify(titles[12] + ' ')),
    };
    const verdict = Object.fromEntries(Object.entries(cases).map(([k, buf]) => [k, dataJsViolations(base, buf, titles).length === 0]));
    expect(verdict).toEqual({
      ok: true, featuredFalse: false, noSpace: false, indent: false, extraField: false,
      fourthLine: false, missing: false, wrongPlace: false, crlf: false, otherEdit: false,
    });
  });

  test('css/themes.css bytes = BASE d0a8a6e…', () => {
    expect(GUARD_BASE).toBe('d0a8a6e462bc1366757b1401c3ba7aeb0fbf391d');
    const base = gitShowBytes(GUARD_BASE, 'css/themes.css');
    const cur = readFileSync(new URL('../../css/themes.css', import.meta.url));
    expect(Buffer.compare(base, cur)).toBe(0);
  });

  test('PROJECTS 13개 순서·title 그대로(live data)', async ({ page }) => {
    await page.goto('/');
    const live = await page.evaluate(() => PROJECTS.map((p) => p.title)); // eslint-disable-line no-undef
    expect(titles).toHaveLength(13);
    expect(live).toEqual(titles);
  });

  test('mobile-dark: menu를 열고 닫을 수 있다', async ({ page }, testInfo) => {
    test.skip(testInfo.project.name !== 'mobile-dark', 'mobile-dark 전용');
    await page.goto('/');
    const toggle = page.locator('#menuToggle');
    const nav = page.locator('#navLinks');
    await expect(toggle).toBeVisible();
    await expect(nav).not.toHaveClass(/(^|\s)open(\s|$)/);
    await toggle.click();
    await expect(nav).toHaveClass(/(^|\s)open(\s|$)/);
    await expect(toggle).toHaveAttribute('aria-expanded', 'true');
    await expect(nav.locator('.nav-link').first()).toBeVisible();
    await toggle.click();
    await expect(nav).not.toHaveClass(/(^|\s)open(\s|$)/);
    await expect(toggle).toHaveAttribute('aria-expanded', 'false');
  });

  for (const n of MODAL_CHECK_INDEXES) {
    test(`project ${n} modal을 열고 닫을 수 있다`, async ({ page }) => {
      await page.goto('/');
      const card = page.locator(`#projectGrid .project-card[data-project="${n}"]`);
      await card.scrollIntoViewIfNeeded();
      await card.click();
      const modal = page.locator('#projectModal');
      await expect(modal).toBeVisible();
      await expect(page.locator('body')).toHaveClass(/(^|\s)modal-open(\s|$)/);
      await expect(page.locator('#projectModal #modalTitle')).toHaveText(titles[n]);
      await page.locator('#projectModal .modal-close[data-modal-close]').click();
      await expect(modal).toBeHidden();
      await expect(page.locator('body')).not.toHaveClass(/(^|\s)modal-open(\s|$)/);
      await expect(card).toBeFocused();
    });
  }
});
