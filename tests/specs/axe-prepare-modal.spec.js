// step 30 — axe prepare modal (설계 §6.3): MODAL_ROOT · MODAL_BODY_TEXT · assertContentLoaded · prepareModal
import { expect } from '@playwright/test';
import { test } from '../helpers/theme.js';
import { MODAL_ROOT, MODAL_BODY_TEXT, assertContentLoaded, prepareModal } from '../helpers/axe-prepare.js';

const PROJECTS_RUN = ['desktop-dark', 'desktop-light'];

// 합성 fixture(§6.3): 동작 모달 fixture는 window.__opens·__closes·__clicks를 기록한다.
function modalFixture({ handler = true, gridProject = 1, featured = true, content = 'full' } = {}) {
  const grid = gridProject === null
    ? '<div id="projectGrid"></div>'
    : `<div id="projectGrid"><article class="project-card has-detail" data-project="${gridProject}" tabindex="0" role="button">grid ${gridProject}</article></div>`;
  const feat = featured
    ? `<button type="button" class="featured-open" data-featured-card data-project="${gridProject ?? 3}">대표</button>`
    : '';
  const outside = gridProject === null ? '<article class="project-card" data-project="3">outside 3</article>' : '';
  const body = content === 'full'
    ? '<h3 id="modalTitle">합성 제목</h3><p class="modal-blurb">합성 본문</p><div class="modal-section"><h4>섹션</h4></div>'
    : '<h3 id="modalTitle">합성 제목</h3><p class="modal-blurb">  </p>';
  const script = handler
    ? `<script>
        window.__opens = 0; window.__closes = 0; window.__clicks = { grid: 0, featured: 0 };
        const modal = document.getElementById('projectModal');
        function open() {
          document.getElementById('modalBody').innerHTML = ${JSON.stringify(body)};
          modal.hidden = false; document.body.classList.add('modal-open'); window.__opens += 1;
        }
        document.querySelectorAll('#projectGrid [data-project]').forEach((el) =>
          el.addEventListener('click', () => { window.__clicks.grid += 1; open(); }));
        document.querySelectorAll('[data-featured-card]').forEach((el) =>
          el.addEventListener('click', () => { window.__clicks.featured += 1; open(); }));
        modal.addEventListener('click', (e) => {
          if (e.target.closest('[data-modal-close]')) {
            modal.hidden = true; document.body.classList.remove('modal-open'); window.__closes += 1;
          }
        });
      </script>`
    : '';
  return `<!doctype html><html><body>
    ${feat}${outside}${grid}
    <div class="modal" id="projectModal" hidden>
      <div class="modal-backdrop" data-modal-close></div>
      <div class="modal-dialog" role="dialog" aria-modal="true" aria-labelledby="modalTitle">
        <button class="modal-close" type="button" data-modal-close aria-label="닫기">x</button>
        <div class="modal-body" id="modalBody"></div>
      </div>
    </div>
    ${script}
  </body></html>`;
}

async function codeOf(promise) {
  const err = await promise.then(() => null, (e) => e);
  expect(err).toBeInstanceOf(Error);
  expect(err.message).toBe('prepareForAxe: ' + err.code);
  return err.code;
}

test.describe('step 30 axe-prepare-modal', () => {
  test.beforeEach(async ({}, testInfo) => {
    test.skip(!PROJECTS_RUN.includes(testInfo.project.name), 'desktop-dark·desktop-light 전용');
  });

  test('상수: MODAL_ROOT·MODAL_BODY_TEXT', () => {
    expect(MODAL_ROOT).toBe('#projectModal');
    expect(MODAL_BODY_TEXT).toBe('#modalBody .modal-blurb, #modalBody .modal-section');
  });

  test('prepareModal(page): 실제 페이지 → include #projectModal·modal-open·제목 PROJECTS[0].title·본문', async ({ page }) => {
    await page.goto('/');
    const res = await prepareModal(page);
    expect(res.include).toBe('#projectModal');
    await expect(page.locator(MODAL_ROOT)).toBeVisible();
    expect(await page.evaluate(() => document.body.classList.contains('modal-open'))).toBe(true);
    const title = await page.evaluate(() => PROJECTS[0].title); // eslint-disable-line no-undef
    await expect(page.locator('#projectModal #modalTitle')).toHaveText(title);
    const texts = await page.locator(MODAL_BODY_TEXT).allTextContents();
    expect(texts.some((t) => t.trim().length > 0)).toBe(true);
  });

  test('동작 fixture: 대표 버튼과 grid data-project="1" 공존 → grid만 1회 click·__opens === 1', async ({ page }) => {
    await page.setContent(modalFixture());
    const res = await prepareModal(page, { projectIndex: 1 });
    expect(res.include).toBe(MODAL_ROOT);
    const st = await page.evaluate(() => ({ opens: window.__opens, clicks: window.__clicks }));
    expect(st.clicks.grid).toBe(1);
    expect(st.clicks.featured).toBe(0);
    expect(st.opens).toBe(1);
  });

  test('grid 밖에만 data-project="3" → project-card-not-found:3', async ({ page }) => {
    await page.setContent(modalFixture({ gridProject: null }));
    expect(await codeOf(prepareModal(page, { projectIndex: 3 }))).toBe('project-card-not-found:3');
    expect(await page.evaluate(() => window.__opens)).toBe(0);
  });

  test('handler 없음 + 500ms → modal-not-open', async ({ page }) => {
    await page.setContent(modalFixture({ handler: false, featured: false }));
    expect(await codeOf(prepareModal(page, { projectIndex: 1, timeoutMs: 500 }))).toBe('modal-not-open');
  });

  test('.modal-blurb 빈·.modal-section 0 → content-not-loaded:text', async ({ page }) => {
    await page.setContent(modalFixture({ content: 'empty' }));
    expect(await codeOf(prepareModal(page, { projectIndex: 1, timeoutMs: 500 }))).toBe('content-not-loaded:text');
  });

  test('assertContentLoaded: 텍스트 없는 div + textLocator null 통과, 지정 시 text 실패', async ({ page }) => {
    await page.setContent('<!doctype html><html><body><div id="empty"></div></body></html>');
    const div = page.locator('#empty');
    await expect(assertContentLoaded(div, 500)).resolves.toBeUndefined();
    await expect(assertContentLoaded(div, 500, { textLocator: null })).resolves.toBeUndefined();
    expect(await codeOf(assertContentLoaded(div, 500, { textLocator: div }))).toBe('content-not-loaded:text');
  });

  test('assertContentLoaded: 깨진 img → content-not-loaded:img, 빈 svg → content-not-loaded:svg', async ({ page }) => {
    await page.setContent('<!doctype html><html><body><div id="i"><img alt="x" src="/__missing__.png"></div><div id="s"><svg></svg></div></body></html>');
    expect(await codeOf(assertContentLoaded(page.locator('#i'), 500))).toBe('content-not-loaded:img');
    await page.evaluate(() => { document.querySelector('#s svg').setAttribute('width', '0'); document.querySelector('#s svg').setAttribute('height', '0'); });
    expect(await codeOf(assertContentLoaded(page.locator('#s'), 500))).toBe('content-not-loaded:svg');
  });
});
