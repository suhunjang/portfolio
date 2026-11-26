// compact step 4 — section-structure (설계 compact §C1, 원 §4·§5 예외 (2)~(5))
import { readFileSync } from 'node:fs';
import { expect } from '@playwright/test';
import { test } from '../helpers/theme.js';

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

  test('about: 본문 뒤 h3.subsection-title 기술 스택 1개, 그 뒤 #skillsGrid, skill-group 제목은 h4', async ({ page }) => {
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
    await expect(page.locator('#skillsGrid .skill-group > h4')).toHaveText(baseline.SKILLS.map((g) => g.category));
    await expect(page.locator('#skillsGrid h3')).toHaveCount(0);
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
