// step 31 — axe prepare lightbox (설계 §6.3): prepareLightbox · prepareOverlay · prepareForAxe
import { expect } from '@playwright/test';
import { test } from '../helpers/theme.js';
import { findProjectWithShots } from '../helpers/modal.js';
import { prepareLightbox, prepareOverlay, prepareForAxe } from '../helpers/axe-prepare.js';

const PROJECTS_RUN = ['desktop-dark', 'desktop-light'];
const PNG = 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNkYAAAAAYAAjCB0C8AAAAASUVORK5CYII=';

// 합성 fixture(§6.3): 동작 모달 fixture(window.__opens·__closes·__clicks) + 최소 lightbox.
// grid 0·1 카드, 대표 버튼(data-featured-card) 하나, shotAt 카드의 모달에만 .shot-zoom.
// lightboxContent: 'img'(정상 data: png) | 'broken'(없는 src) | 'svg0'(0×0 svg).
function lightboxFixture({ shotAt = null, featured = 0, lightboxContent = 'img' } = {}) {
  const projects = [0, 1].map((n) => (n === shotAt ? { title: `p${n}`, detail: { shots: [{ src: PNG }] } } : { title: `p${n}`, detail: {} }));
  return `<!doctype html><html><body>
    <button type="button" class="featured-open" data-featured-card data-project="${featured}">대표</button>
    <div id="projectGrid">
      <article class="project-card has-detail" data-project="0" tabindex="0" role="button">grid 0</article>
      <article class="project-card has-detail" data-project="1" tabindex="0" role="button">grid 1</article>
    </div>
    <div class="modal" id="projectModal" hidden>
      <div class="modal-backdrop" data-modal-close></div>
      <div class="modal-dialog" role="dialog" aria-modal="true" aria-labelledby="modalTitle">
        <button class="modal-close" type="button" data-modal-close aria-label="닫기">x</button>
        <div class="modal-body" id="modalBody"></div>
      </div>
    </div>
    <script>(() => {
      window.PROJECTS = ${JSON.stringify(projects)};
      window.__opens = 0; window.__closes = 0; window.__clicks = { grid: 0, featured: 0 };
      const SHOT_AT = ${JSON.stringify(shotAt)};
      const LB = ${JSON.stringify(lightboxContent)};
      const modal = document.getElementById('projectModal');
      let lightbox = null;
      function open(n) {
        const shot = n === SHOT_AT
          ? '<div class="modal-section"><h4>화면</h4><button type="button" class="shot-zoom" aria-label="확대"><img alt="샷" src="${PNG}"></button></div>'
          : '';
        document.getElementById('modalBody').innerHTML =
          '<h3 id="modalTitle">제목 ' + n + '</h3><p class="modal-blurb">본문 ' + n + '</p>' + shot;
        modal.hidden = false; document.body.classList.add('modal-open'); window.__opens += 1;
      }
      function close() {
        if (lightbox) lightbox.hidden = true;
        modal.hidden = true; document.body.classList.remove('modal-open'); window.__closes += 1;
      }
      document.querySelectorAll('#projectGrid [data-project]').forEach((el) =>
        el.addEventListener('click', () => { window.__clicks.grid += 1; open(Number(el.dataset.project)); }));
      document.querySelectorAll('[data-featured-card]').forEach((el) =>
        el.addEventListener('click', () => { window.__clicks.featured += 1; open(Number(el.dataset.project)); }));
      modal.addEventListener('click', (e) => {
        const zoom = e.target.closest('.shot-zoom');
        if (zoom) {
          lightbox = document.createElement('div');
          lightbox.className = 'lightbox';
          lightbox.setAttribute('role', 'dialog');
          const media = LB === 'svg0' ? '<svg width="0" height="0"></svg>'
            : '<img alt="샷" src="' + (LB === 'broken' ? '/__missing__.png' : zoom.querySelector('img').src) + '">';
          lightbox.innerHTML = '<button class="modal-close" type="button" aria-label="닫기">x</button>' + media;
          document.body.appendChild(lightbox);
          lightbox.querySelector('.modal-close').focus();
          return;
        }
        if (e.target.closest('[data-modal-close]')) close();
      });
      document.addEventListener('keydown', (e) => {
        if (e.key !== 'Escape') return;
        if (lightbox && !lightbox.hidden) { lightbox.hidden = true; return; }
        if (!modal.hidden) close();
      });
    })();</script>
  </body></html>`;
}

async function codeOf(promise) {
  const err = await promise.then(() => null, (e) => e);
  expect(err).toBeInstanceOf(Error);
  expect(err.message).toBe('prepareForAxe: ' + err.code);
  return err.code;
}

async function counters(page) {
  return page.evaluate(() => ({ opens: window.__opens, closes: window.__closes, clicks: window.__clicks }));
}

test.describe('step 31 axe-prepare-lightbox', () => {
  test.beforeEach(async ({}, testInfo) => {
    test.skip(!PROJECTS_RUN.includes(testInfo.project.name), 'desktop-dark·desktop-light 전용');
  });

  test('prepareForAxe page → include body·projectIndex null', async ({ page }) => {
    await page.goto('/');
    const res = await prepareForAxe(page, { scenario: 'page' });
    expect(res).toEqual({ include: 'body', projectIndex: null });
    expect(await page.evaluate(() => document.querySelectorAll('.reveal:not(.in)').length)).toBe(0);
    await expect(page.locator('#projectModal')).toBeHidden();
  });

  test('prepareForAxe modal → include #projectModal·modal-open', async ({ page }) => {
    await page.goto('/');
    const res = await prepareForAxe(page, { scenario: 'modal' });
    expect(res).toEqual({ include: '#projectModal', projectIndex: 0 });
    await expect(page.locator('#projectModal')).toBeVisible();
    expect(await page.evaluate(() => document.body.classList.contains('modal-open'))).toBe(true);
  });

  test('prepareForAxe lightbox → include .lightbox·img 로딩·포커스 내부', async ({ page }) => {
    await page.goto('/');
    const expected = await findProjectWithShots(page);
    expect(expected).not.toBeNull();
    const res = await prepareForAxe(page, { scenario: 'lightbox' });
    expect(res).toEqual({ include: '.lightbox', projectIndex: expected });
    const lb = page.locator('.lightbox');
    await expect(lb).toBeVisible();
    expect(await lb.locator('img').evaluate((img) => img.complete && img.naturalWidth > 0)).toBe(true);
    expect(await page.evaluate(() => !!document.activeElement && !!document.activeElement.closest('.lightbox'))).toBe(true);
    expect(await page.evaluate(() => document.body.classList.contains('modal-open'))).toBe(true);
  });

  test('prepareOverlay modal·lightbox 위임, projectIndex 지정', async ({ page }) => {
    await page.goto('/');
    expect(await prepareOverlay(page, { scenario: 'lightbox', projectIndex: 1 })).toEqual({ include: '.lightbox', projectIndex: 1 });
    await expect(page.locator('#projectModal #modalTitle')).toHaveText(await page.evaluate(() => PROJECTS[1].title)); // eslint-disable-line no-undef
  });

  test('shots 없는 index → lightbox-not-open', async ({ page }) => {
    await page.goto('/');
    const n = await page.evaluate(() => PROJECTS.findIndex((p) => !(p.detail && p.detail.shots && p.detail.shots.length))); // eslint-disable-line no-undef
    expect(n).toBeGreaterThanOrEqual(0);
    expect(await codeOf(prepareLightbox(page, { projectIndex: n, timeoutMs: 1000 }))).toBe('lightbox-not-open');
  });

  test('이미지 abort → content-not-loaded:img', async ({ page }) => {
    await page.route(/\.(png|jpe?g|webp|gif|avif)(\?.*)?$/i, (route) => route.abort());
    await page.goto('/');
    expect(await codeOf(prepareForAxe(page, { scenario: 'lightbox', timeoutMs: 1000 }))).toBe('content-not-loaded:img');
  });

  test("scenario 'x'·prepareOverlay({ scenario: 'page' }) → unknown-scenario", async ({ page }) => {
    await page.setContent(lightboxFixture());
    expect(await codeOf(prepareForAxe(page, { scenario: 'x' }))).toBe('unknown-scenario');
    expect(await codeOf(prepareOverlay(page, { scenario: 'page' }))).toBe('unknown-scenario');
    expect(await codeOf(prepareOverlay(page, {}))).toBe('unknown-scenario');
    expect((await counters(page)).opens).toBe(0);
  });

  test('no-shots fixture(grid 0·1 + 대표 0) → findProjectWithShots null·opens/closes 2·대표 0·no-shots-project', async ({ page }) => {
    await page.setContent(lightboxFixture({ shotAt: null, featured: 0 }));
    expect(await findProjectWithShots(page)).toBeNull();
    expect(await codeOf(prepareLightbox(page, { timeoutMs: 1000 }))).toBe('no-shots-project');
    const c = await counters(page);
    expect(c.opens).toBe(2);
    expect(c.closes).toBe(2);
    expect(c.clicks.featured).toBe(0);
    expect(c.clicks.grid).toBe(2);
    await expect(page.locator('#projectModal')).toBeHidden();
  });

  test('shots fixture(1에만 .shot-zoom + 대표 1) → 1·opens/closes 2·대표 0', async ({ page }) => {
    await page.setContent(lightboxFixture({ shotAt: 1, featured: 1 }));
    expect(await findProjectWithShots(page)).toBe(1);
    const res = await prepareLightbox(page, { timeoutMs: 1000 });
    expect(res).toEqual({ include: '.lightbox', projectIndex: 1 });
    // 0은 열고 닫음, 1은 연 채로 lightbox까지 — 재오픈 없음
    let c = await counters(page);
    expect(c.opens).toBe(2);
    expect(c.closes).toBe(1);
    expect(c.clicks.featured).toBe(0);
    await expect(page.locator('.lightbox')).toBeVisible();
    expect(await page.evaluate(() => !!document.activeElement.closest('.lightbox'))).toBe(true);
    await page.keyboard.press('Escape');
    await page.keyboard.press('Escape');
    c = await counters(page);
    expect(c.opens).toBe(2);
    expect(c.closes).toBe(2);
  });

  test('fixture lightbox 깨진 img → content-not-loaded:img, 0×0 svg → content-not-loaded:svg', async ({ page }) => {
    await page.setContent(lightboxFixture({ shotAt: 1, lightboxContent: 'broken' }));
    expect(await codeOf(prepareLightbox(page, { projectIndex: 1, timeoutMs: 500 }))).toBe('content-not-loaded:img');
    await page.setContent(lightboxFixture({ shotAt: 1, lightboxContent: 'svg0' }));
    expect(await codeOf(prepareLightbox(page, { projectIndex: 1, timeoutMs: 500 }))).toBe('content-not-loaded:svg');
  });
});
