// compact step 1 — featured-cards (설계 compact §C1·§C6, 원 §3)
import { readFileSync } from 'node:fs';
import { expect } from '@playwright/test';
import { test } from '../helpers/theme.js';
import { readLiveData, norm } from '../helpers/content.js';
import { gridCard, closeVia, expectFocused, modalTitle } from '../helpers/modal.js';

const baseline = JSON.parse(readFileSync(new URL('../fixtures/baseline-data.json', import.meta.url), 'utf8'));
const FEATURED = [1, 5, 7];
const MODAL = '#projectModal';
const MODAL_OPEN = /(^|\s)modal-open(\s|$)/;
const CLOSE_METHODS = ['button', 'backdrop', 'esc'];

function featuredCard(page, N) {
  return page.locator('#heroFeatured .featured-card[data-project="' + N + '"]');
}

async function expectOpen(page, idx) {
  await expect(page.locator(MODAL)).toBeVisible();
  await expect(page.locator('body')).toHaveClass(MODAL_OPEN);
  await expect(modalTitle(page)).toHaveText(baseline.PROJECTS[idx].title);
}

async function expectClosed(page) {
  await expect(page.locator(MODAL)).toBeHidden();
  await expect(page.locator('body')).not.toHaveClass(MODAL_OPEN);
}

test.describe('compact step 1 featured-cards', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/');
  });

  test('data: featured === true는 정확히 index 1·5·7, PROJECTS 13개 순서·title 불변', async ({ page }) => {
    const live = await readLiveData(page);
    expect(live.PROJECTS).toHaveLength(13);
    expect(live.PROJECTS.map((p) => p.title)).toEqual(baseline.PROJECTS.map((p) => p.title));
    const featured = live.PROJECTS.flatMap((p, i) => (p.featured === true ? [i] : []));
    expect(featured).toEqual(FEATURED);
    const withKey = live.PROJECTS.flatMap((p, i) => ('featured' in p ? [i] : []));
    expect(withKey).toEqual(FEATURED);
  });

  test('#heroFeatured 구조: div[role=region][aria-label=대표 프로젝트], #heroStats 바로 다음 형제', async ({ page }) => {
    const info = await page.evaluate(() => {
      const el = document.getElementById('heroFeatured');
      if (!el) return null;
      return {
        count: document.querySelectorAll('#heroFeatured').length,
        tag: el.tagName,
        role: el.getAttribute('role'),
        label: el.getAttribute('aria-label'),
        prevId: el.previousElementSibling ? el.previousElementSibling.id : null,
        parentIsHeroInner: el.parentElement ? el.parentElement.classList.contains('hero-inner') : false,
        childCount: el.children.length,
      };
    });
    expect(info).not.toBeNull();
    expect(info).toEqual({
      count: 1,
      tag: 'DIV',
      role: 'region',
      label: '대표 프로젝트',
      prevId: 'heroStats',
      parentIsHeroInner: true,
      childCount: 3,
    });
  });

  test('카드 3개: button[type=button], data-project 1·5·7, span 2개(block), interactive 자손 0, background-image none', async ({ page }) => {
    const cards = await page.evaluate(() =>
      Array.from(document.querySelectorAll('#heroFeatured > *')).map((el) => {
        const spans = Array.from(el.children);
        return {
          tag: el.tagName,
          type: el.getAttribute('type'),
          className: el.className,
          featuredAttr: el.hasAttribute('data-featured-card'),
          project: el.getAttribute('data-project'),
          childTags: spans.map((s) => s.tagName),
          descendantCount: el.querySelectorAll('*').length,
          spanClasses: spans.map((s) => s.className),
          spanTexts: spans.map((s) => s.textContent),
          spanDisplays: spans.map((s) => getComputedStyle(s).display),
          interactive: el.querySelectorAll(
            'a, button, input, select, textarea, iframe, summary, [href], [tabindex], [contenteditable], [role="button"], [role="link"]'
          ).length,
          backgroundImage: getComputedStyle(el).backgroundImage,
        };
      })
    );
    expect(cards).toHaveLength(3);
    expect(cards.map((c) => c.project)).toEqual(['1', '5', '7']);
    cards.forEach((c, i) => {
      const p = baseline.PROJECTS[FEATURED[i]];
      expect(c.tag).toBe('BUTTON');
      expect(c.type).toBe('button');
      expect(c.className).toBe('featured-card');
      expect(c.featuredAttr).toBe(true);
      expect(c.childTags).toEqual(['SPAN', 'SPAN']);
      expect(c.descendantCount).toBe(2);
      expect(c.spanClasses).toEqual(['featured-title', 'featured-blurb']);
      expect(c.spanTexts).toEqual([p.title, p.blurb]);
      expect(c.spanDisplays).toEqual(['block', 'block']);
      expect(c.interactive).toBe(0);
      expect(c.backgroundImage).toBe('none');
    });
  });

  for (const N of FEATURED) {
    test(`click 열기(data-project ${N}) → 제목 일치`, async ({ page }) => {
      await featuredCard(page, N).click();
      await expectOpen(page, N);
    });

    test(`Enter 열기(data-project ${N}) → 제목 일치`, async ({ page }) => {
      const card = featuredCard(page, N);
      await card.focus();
      await card.press('Enter');
      await expectOpen(page, N);
    });
  }

  for (const how of CLOSE_METHODS) {
    test(`click 열기 → ${how} 닫기: featured trigger로 focus 복귀`, async ({ page }) => {
      for (const N of FEATURED) {
        const card = featuredCard(page, N);
        await card.click();
        await expectOpen(page, N);
        await closeVia(page, how);
        await expectClosed(page);
        await expectFocused(card);
      }
    });

    test(`Enter 열기 → ${how} 닫기: featured trigger로 focus 복귀`, async ({ page }) => {
      for (const N of FEATURED) {
        const card = featuredCard(page, N);
        await card.focus();
        await card.press('Enter');
        await expectOpen(page, N);
        await closeVia(page, how);
        await expectClosed(page);
        await expectFocused(card);
      }
    });
  }

  test('.featured-card 색 3속성 = 같은 data-project의 #projectGrid .project-card', async ({ page }) => {
    await page.mouse.move(0, 0);
    for (const N of FEATURED) {
      await expect(featuredCard(page, N)).toHaveCount(1);
      await expect(gridCard(page, N)).toHaveCount(1);
      await expect
        .poll(async () =>
          page.evaluate((n) => {
            const pick = (el) => {
              const cs = getComputedStyle(el);
              return { color: cs.color, backgroundColor: cs.backgroundColor, borderColor: cs.borderColor };
            };
            const f = document.querySelector('#heroFeatured .featured-card[data-project="' + n + '"]');
            const g = document.querySelector('#projectGrid .project-card[data-project="' + n + '"]');
            const a = pick(f);
            const b = pick(g);
            return a.color === b.color && a.backgroundColor === b.backgroundColor && a.borderColor === b.borderColor
              ? 'same'
              : JSON.stringify({ featured: a, grid: b });
          }, N)
        )
        .toBe('same');
    }
  });
});

// compact step 2 — hero-first-screen (설계 compact Step 2, 원 §3·§7)
const MAIN_JS_SRC = readFileSync(new URL('../../js/main.js', import.meta.url), 'utf8');
const STAT_ITEM = '#heroStats > li';
const STAT_VALUE = '.stat-value';
const STAT_LABEL = '.stat-label';
const HERO_CHILDREN = [
  { tag: 'P', id: null, cls: 'hero-eyebrow' },
  { tag: 'H1', id: 'heroName', cls: 'hero-name' },
  { tag: 'P', id: 'heroTagline', cls: 'hero-tagline' },
  { tag: 'H2', id: null, cls: 'hero-role' },
  { tag: 'P', id: 'heroSummary', cls: 'hero-summary' },
  { tag: 'DIV', id: null, cls: 'hero-cta' },
  { tag: 'UL', id: 'heroStats', cls: 'hero-stats' },
  { tag: 'DIV', id: 'heroFeatured', cls: null },
];
const STATS_ROWS = { 375: [2, 2], 768: [4], 1280: [4] };
const FEATURED_ROWS = { 375: [1, 1, 1], 768: [2, 1], 1280: [3] };

// 요소 bbox top(반올림)으로 묶은 행별 개수(위→아래).
async function rowCounts(page, selector) {
  return page.evaluate((sel) => {
    const rows = new Map();
    for (const el of document.querySelectorAll(sel)) {
      const top = Math.round(el.getBoundingClientRect().top);
      rows.set(top, (rows.get(top) || 0) + 1);
    }
    return Array.from(rows.entries()).sort((a, b) => a[0] - b[0]).map((e) => e[1]);
  }, selector);
}

test.describe('compact step 2 hero-first-screen', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/');
  });

  test('.hero-inner 직계 자식 정확히 8개, 원 §3 순서', async ({ page }) => {
    const kids = await page.evaluate(() =>
      Array.from(document.querySelector('#hero > .hero-inner').children).map((el) => ({
        tag: el.tagName,
        id: el.id || null,
        classes: Array.from(el.classList),
      }))
    );
    expect(kids).toHaveLength(HERO_CHILDREN.length);
    kids.forEach((k, i) => {
      const want = HERO_CHILDREN[i];
      expect(k.tag, `child ${i}`).toBe(want.tag);
      expect(k.id, `child ${i}`).toBe(want.id);
      if (want.cls) expect(k.classes, `child ${i}`).toContain(want.cls);
    });
  });

  test('tagline: #heroTagline 텍스트 = PROFILE.tagline, main.js에 정확한 setText 1줄', async ({ page }) => {
    const live = await readLiveData(page);
    expect(live.PROFILE.tagline).toBe(baseline.PROFILE.tagline);
    await expect(page.locator('#heroTagline')).toHaveText(baseline.PROFILE.tagline);
    const lines = MAIN_JS_SRC.split('\n').filter((l) => l.includes('heroTagline'));
    expect(lines.map((l) => l.trim())).toEqual(["setText('heroTagline', PROFILE.tagline);"]);
  });

  test('eyebrow·typed·CTA·#heroFeatured role/label 유지', async ({ page }) => {
    await expect(page.locator('#hero .hero-eyebrow')).toHaveText('👋 안녕하세요, 저는');
    await expect(page.locator('#hero .hero-role > #typed.typed')).toHaveCount(1);
    await expect(page.locator('#hero .hero-role > .caret[aria-hidden="true"]')).toHaveCount(1);
    const cta = await page.evaluate(() =>
      Array.from(document.querySelectorAll('#hero .hero-cta > *')).map((a) => ({
        tag: a.tagName,
        cls: a.className,
        href: a.getAttribute('href'),
        text: a.textContent.trim(),
      }))
    );
    expect(cta).toEqual([
      { tag: 'A', cls: 'btn btn-primary', href: '#projects', text: '프로젝트 보기' },
      { tag: 'A', cls: 'btn btn-ghost', href: '#contact', text: '연락하기' },
    ]);
    const region = page.locator('#heroFeatured');
    await expect(region).toHaveAttribute('role', 'region');
    await expect(region).toHaveAttribute('aria-label', '대표 프로젝트');
  });

  test('STATS: 375 2×2, 768·1280 4×1', async ({ page }) => {
    const width = page.viewportSize().width;
    await expect(page.locator(STAT_ITEM)).toHaveCount(4);
    await expect.poll(() => rowCounts(page, STAT_ITEM)).toEqual(STATS_ROWS[width]);
  });

  test('#heroFeatured: 375/768/1280에서 1/2/3열', async ({ page }) => {
    const width = page.viewportSize().width;
    await expect(page.locator('#heroFeatured > .featured-card')).toHaveCount(3);
    await expect.poll(() => rowCounts(page, '#heroFeatured > .featured-card')).toEqual(FEATURED_ROWS[width]);
  });

  test('첫 화면 AC(1280×800): 이름·tagline·STATS 4개·대표 제목 3개가 화면 안에 완전히 보인다', async ({ page }, testInfo) => {
    test.skip(!['desktop-dark', 'desktop-light'].includes(testInfo.project.name), 'desktop 1280×800 전용');
    expect(page.viewportSize()).toEqual({ width: 1280, height: 800 });
    await page.evaluate(() => document.fonts.ready.then(() => true));
    expect(await page.evaluate(() => window.scrollY)).toBe(0);

    const items = page.locator(STAT_ITEM);
    await expect(items).toHaveCount(4);
    const targets = [page.locator('#heroName'), page.locator('#heroTagline'), page.locator('#heroStats')];
    const titles = page.locator('#heroFeatured .featured-title');
    await expect(titles).toHaveCount(3);
    for (let i = 0; i < 3; i++) targets.push(titles.nth(i));
    for (let i = 0; i < 4; i++) {
      const item = items.nth(i);
      const value = item.locator(STAT_VALUE);
      const label = item.locator(STAT_LABEL);
      expect(norm(await value.textContent())).toBe(norm(baseline.STATS[i].value));
      expect(norm(await label.textContent())).toBe(norm(baseline.STATS[i].label));
      targets.push(item, value, label);
    }

    for (const loc of targets) {
      await expect(loc).toBeVisible();
      await expect
        .poll(() =>
          loc.evaluate((el) => {
            const bad = [];
            for (let n = el; n && n.nodeType === 1; n = n.parentElement) {
              const cs = getComputedStyle(n);
              if (cs.visibility !== 'visible' || cs.opacity !== '1') bad.push(n.tagName + '.' + n.className);
            }
            return bad;
          })
        )
        .toEqual([]);
      const box = await loc.boundingBox();
      expect(box).not.toBeNull();
      expect(box.width).toBeGreaterThan(0);
      expect(box.height).toBeGreaterThan(0);
      expect(box.x).toBeGreaterThanOrEqual(0);
      expect(box.y).toBeGreaterThanOrEqual(0);
      expect(box.x + box.width).toBeLessThanOrEqual(1280);
      expect(box.y + box.height).toBeLessThanOrEqual(800);
    }
  });
});

// compact step 3 — hero-two-column (설계 compact Step 3, 원 §7·§11.2)
const TOKENS = JSON.parse(readFileSync(new URL('../fixtures/claude-design-intake.json', import.meta.url), 'utf8')).tokens;
const HERO_KIDS_SEL = '#hero > .hero-inner > *';

// .hero-inner 레이아웃 측정: content-box, computed grid, 직계 자식 8개 bbox.
async function heroLayout(page) {
  return page.evaluate((sel) => {
    const inner = document.querySelector('#hero > .hero-inner');
    const cs = getComputedStyle(inner);
    const rect = inner.getBoundingClientRect();
    const padL = parseFloat(cs.paddingLeft);
    const padR = parseFloat(cs.paddingRight);
    const rectOf = (el) => {
      const r = el.getBoundingClientRect();
      return { left: r.left, right: r.right, top: r.top, width: r.width };
    };
    const cols = (cs.gridTemplateColumns.match(/-?\d+(\.\d+)?px/g) || []).map(parseFloat);
    return {
      display: cs.display,
      areas: cs.gridTemplateAreas,
      columnGap: cs.columnGap,
      cols,
      W: inner.clientWidth - padL - padR,
      contentLeft: rect.left + parseFloat(cs.borderLeftWidth) + padL,
      kids: Array.from(document.querySelectorAll(sel)).map(rectOf),
      name: rectOf(document.getElementById('heroName')),
      summary: rectOf(document.getElementById('heroSummary')),
      cta: rectOf(document.querySelector('#hero .hero-cta')),
      stats: rectOf(document.getElementById('heroStats')),
      featured: rectOf(document.getElementById('heroFeatured')),
      scrollW: document.documentElement.scrollWidth,
      clientW: document.documentElement.clientWidth,
    };
  }, HERO_KIDS_SEL);
}

function expectedAreas() {
  return TOKENS.heroAreas.map((r) => '"' + r + '"').join(' ');
}

// 2열 계약(원 §11.2 열 폭 계약 + compact step 3).
async function expectTwoColumn(page) {
  await page.evaluate(() => document.fonts.ready.then(() => true));
  const L = await heroLayout(page);
  const gap = TOKENS.heroColumnGapPx;
  expect(L.display).toBe('grid');
  expect(L.areas).toBe(expectedAreas());
  expect(L.columnGap).toBe(gap + 'px');
  expect(L.cols).toHaveLength(2);
  const [a, b] = L.cols;
  expect(Math.abs(a - ((L.W - gap) * 5) / 12)).toBeLessThanOrEqual(1);
  expect(Math.abs(b - ((L.W - gap) * 7) / 12)).toBeLessThanOrEqual(1);
  expect(Math.abs(a + gap + b - L.W)).toBeLessThanOrEqual(1);
  expect(L.name.right).toBeLessThanOrEqual(L.summary.left);
  expect(Math.abs(L.cta.left - L.summary.left)).toBeLessThanOrEqual(1);
  expect(L.stats.width).toBeGreaterThanOrEqual(L.W * 0.95);
  expect(L.featured.width).toBeGreaterThanOrEqual(L.W * 0.95);
}

// 1열 계약: grid 아님 또는 px 열 ≤ 1개, 직계 자식 8개 left = content-box left ±1, top DOM 순 증가.
async function expectOneColumn(page) {
  await page.evaluate(() => document.fonts.ready.then(() => true));
  const L = await heroLayout(page);
  expect(L.display !== 'grid' || L.cols.length <= 1, `display=${L.display} cols=${L.cols}`).toBe(true);
  expect(L.kids).toHaveLength(8);
  L.kids.forEach((k, i) => {
    expect(Math.abs(k.left - L.contentLeft), `child ${i} left`).toBeLessThanOrEqual(1);
    if (i > 0) expect(k.top, `child ${i} top`).toBeGreaterThan(L.kids[i - 1].top);
  });
  return L;
}

test.describe('compact step 3 hero-two-column', () => {
  test('1280: 5:7 2열 grid, areas = tokens.heroAreas, gap 48', async ({ page }, testInfo) => {
    test.skip(!['desktop-dark', 'desktop-light'].includes(testInfo.project.name), 'desktop 1280 전용');
    await page.goto('/');
    expect(page.viewportSize().width).toBe(1280);
    await expectTwoColumn(page);
  });

  test('1023×800: 1열(left 일치, top 증가)', async ({ page }) => {
    await page.setViewportSize({ width: 1023, height: 800 });
    await page.goto('/');
    await expectOneColumn(page);
  });

  test('1024×800: 1280의 2열 계약 그대로', async ({ page }) => {
    await page.setViewportSize({ width: 1024, height: 800 });
    await page.goto('/');
    await expectTwoColumn(page);
  });

  test('375·768: 1열, 가로 스크롤 없음', async ({ page }, testInfo) => {
    const width = page.viewportSize().width;
    test.skip(![375, 768].includes(width), `375·768 전용 (${testInfo.project.name})`);
    await page.goto('/');
    const L = await expectOneColumn(page);
    expect(L.scrollW).toBeLessThanOrEqual(L.clientW);
  });
});
