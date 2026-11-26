// compact step 1 — featured-cards (설계 compact §C1·§C6, 원 §3)
import { readFileSync } from 'node:fs';
import { expect } from '@playwright/test';
import { test } from '../helpers/theme.js';
import { readLiveData } from '../helpers/content.js';
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
