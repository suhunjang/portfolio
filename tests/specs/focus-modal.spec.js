// compact step 8 — focus-overlays (설계 compact §C6 trapFocus, 원 §6.1 focus trap, resume r28·r29)
import { readFileSync } from 'node:fs';
import { expect } from '@playwright/test';
import { test } from '../helpers/theme.js';
import { gridCard, closeVia, expectFocused, findProjectWithShots } from '../helpers/modal.js';

const baseline = JSON.parse(readFileSync(new URL('../fixtures/baseline-data.json', import.meta.url), 'utf8'));
const MODAL = '#projectModal';
const DIALOG = '#projectModal .modal-dialog';
const LIGHTBOX = '.lightbox[role="dialog"]';
const CLOSE_METHODS = ['button', 'backdrop', 'esc'];
const FEATURED = [1, 5, 7];

function featuredCard(page, N) {
  return page.locator('#heroFeatured .featured-card[data-project="' + N + '"]');
}

// 문서·요소에 등록된 keydown listener를 추적한다(EventTarget 단위 활성 개수).
function installKeydownProbe() {
  const active = new Map();
  const origAdd = EventTarget.prototype.addEventListener;
  const origRemove = EventTarget.prototype.removeEventListener;
  const label = (t) =>
    t === document ? 'document' : t === window ? 'window' : t instanceof Element ? t.className || t.tagName : 'other';
  EventTarget.prototype.addEventListener = function (type, fn, opts) {
    if (type === 'keydown' && fn) {
      let set = active.get(this);
      if (!set) active.set(this, (set = new Set()));
      set.add(fn);
    }
    return origAdd.call(this, type, fn, opts);
  };
  EventTarget.prototype.removeEventListener = function (type, fn, opts) {
    if (type === 'keydown' && fn && active.has(this)) active.get(this).delete(fn);
    return origRemove.call(this, type, fn, opts);
  };
  window.__keydownProbe = () => {
    const out = {};
    for (const [t, set] of active) {
      const k = label(t);
      out[k] = (out[k] || 0) + set.size;
    }
    return out;
  };
  window.__keydownOn = (sel) => {
    const el = document.querySelector(sel);
    const set = el && active.get(el);
    return set ? set.size : 0;
  };
}

// root 안의 보이는 tab 순서 후보와 activeElement의 위치
async function focusState(page, rootSel) {
  return page.evaluate((sel) => {
    const FOCUSABLE =
      'a[href], button:not([disabled]), input:not([disabled]), select:not([disabled]), textarea:not([disabled]), [tabindex]:not([tabindex="-1"])';
    const root = document.querySelector(sel);
    const items = root
      ? Array.from(root.querySelectorAll(FOCUSABLE)).filter(
          (el) => el.getClientRects().length > 0 && getComputedStyle(el).visibility !== 'hidden'
        )
      : [];
    return { n: items.length, index: items.indexOf(document.activeElement) };
  }, rootSel);
}

// 현재 focus 위치에서 Tab(또는 Shift+Tab)을 cycles × n번 눌러 한 칸씩 순환하는지 확인한다.
async function expectCycle(page, rootSel, { cycles = 1, shift = false } = {}) {
  const start = await focusState(page, rootSel);
  expect(start.n, `${rootSel} focusable`).toBeGreaterThan(0);
  expect(start.index, `${rootSel} 시작 focus가 안에 있어야 함`).toBeGreaterThanOrEqual(0);
  let idx = start.index;
  for (let i = 0; i < start.n * cycles + 1; i++) {
    await page.keyboard.press(shift ? 'Shift+Tab' : 'Tab');
    idx = shift ? (idx - 1 + start.n) % start.n : (idx + 1) % start.n;
    const now = await focusState(page, rootSel);
    expect(now.index, `${shift ? 'Shift+' : ''}Tab #${i + 1} (n=${start.n})`).toBe(idx);
  }
}

async function openGrid(page, N) {
  await gridCard(page, N).click();
  await expect(page.locator(MODAL)).toBeVisible();
}

// 모달이 닫힌 뒤 Tab은 페이지로 나가야 한다(trap이 남아 있지 않음).
async function expectNotTrapped(page) {
  await page.keyboard.press('Tab');
  const inModal = await page.evaluate((sel) => document.querySelector(sel).contains(document.activeElement), MODAL);
  expect(inModal, '닫힌 뒤 Tab이 모달 안으로 가면 안 됨').toBe(false);
  const inLightbox = await page.evaluate(() => {
    const lb = document.querySelector('.lightbox');
    return !!lb && lb.contains(document.activeElement);
  });
  expect(inLightbox, '닫힌 뒤 Tab이 lightbox 안으로 가면 안 됨').toBe(false);
}

test.describe('compact step 8 focus-modal', () => {
  test.beforeEach(async ({ page }) => {
    await page.addInitScript(installKeydownProbe);
    await page.goto('/');
  });

  test('modal: Tab·Shift+Tab이 modal 안에서 한 칸씩 순환한다', async ({ page }) => {
    await openGrid(page, 0);
    await expectFocused(page.locator(`${MODAL} .modal-close[data-modal-close]`));
    await expectCycle(page, DIALOG, { cycles: 2 });
    await expectCycle(page, DIALOG, { cycles: 2, shift: true });
  });

  test('modal: shots 프로젝트(.shot-zoom 포함)에서도 순환한다', async ({ page }) => {
    const idx = await findProjectWithShots(page);
    expect(idx).not.toBeNull();
    await openGrid(page, idx);
    await expectCycle(page, DIALOG, { cycles: 1 });
    await expectCycle(page, DIALOG, { cycles: 1, shift: true });
  });

  for (const how of CLOSE_METHODS) {
    test(`grid trigger: Tab 순환 뒤 ${how} 닫기 → trigger 복귀, trap 해제`, async ({ page }) => {
      await openGrid(page, 0);
      await expectCycle(page, DIALOG, { cycles: 1 });
      await closeVia(page, how);
      await expect(page.locator(MODAL)).toBeHidden();
      await expectFocused(gridCard(page, 0));
      await expectNotTrapped(page);
    });

    test(`featured trigger: Tab 순환 뒤 ${how} 닫기 → trigger 복귀, trap 해제`, async ({ page }) => {
      for (const N of FEATURED) {
        const card = featuredCard(page, N);
        await card.focus();
        await card.press('Enter');
        await expect(page.locator(MODAL)).toBeVisible();
        await expectCycle(page, DIALOG, { cycles: 1 });
        await closeVia(page, how);
        await expect(page.locator(MODAL)).toBeHidden();
        await expectFocused(card);
      }
      await expectNotTrapped(page);
    });
  }

  test('modal: 두 번 열고 닫은 뒤에도 Tab이 한 칸씩 이동한다', async ({ page }) => {
    for (const how of ['button', 'esc']) {
      await openGrid(page, 0);
      await closeVia(page, how);
      await expect(page.locator(MODAL)).toBeHidden();
    }
    await openGrid(page, 0);
    await expectCycle(page, DIALOG, { cycles: 2 });
    await expectCycle(page, DIALOG, { cycles: 1, shift: true });
  });

  test.describe('lightbox (desktop)', () => {
    test.beforeEach(async ({}, testInfo) => {
      test.skip(!testInfo.project.name.startsWith('desktop-'), 'lightbox는 desktop project만');
    });

    test('lightbox 안 순환 → Esc 1회 lightbox만 닫고 .shot-zoom 복귀·modal 순환 재개 → Esc 2회 modal 닫고 trigger 복귀', async ({ page }) => {
      const idx = await findProjectWithShots(page);
      expect(idx).not.toBeNull();
      expect(baseline.PROJECTS[idx].detail.shots.length).toBeGreaterThan(0);
      await openGrid(page, idx);
      const zoom = page.locator(`${MODAL} .shot-zoom`).first();
      await zoom.focus();
      await zoom.press('Enter');
      const lb = page.locator(LIGHTBOX);
      await expect(lb).toBeVisible();
      await expectFocused(lb.locator('.modal-close'));
      await expectCycle(page, '.lightbox', { cycles: 2 });
      await expectCycle(page, '.lightbox', { cycles: 1, shift: true });

      await page.keyboard.press('Escape');
      await expect(lb).toBeHidden();
      await expect(page.locator(MODAL)).toBeVisible();
      await expectFocused(zoom);
      await expectCycle(page, DIALOG, { cycles: 1 });
      await expectCycle(page, DIALOG, { cycles: 1, shift: true });

      await page.keyboard.press('Escape');
      await expect(page.locator(MODAL)).toBeHidden();
      await expectFocused(gridCard(page, idx));
      await expectNotTrapped(page);
    });

    test('release 반복에도 안전: lightbox·modal을 여러 경로로 반복 개폐해도 stack이 어긋나지 않는다', async ({ page }) => {
      const idx = await findProjectWithShots(page);
      expect(idx).not.toBeNull();
      const lb = page.locator(LIGHTBOX);
      for (let round = 0; round < 2; round++) {
        await openGrid(page, idx);
        const zoom = page.locator(`${MODAL} .shot-zoom`).first();
        // 버튼 click 닫기 → Esc(이미 닫힌 lightbox는 다시 release되지 않음) 순서
        await zoom.click();
        await expect(lb).toBeVisible();
        await lb.locator('.modal-close').click();
        await expect(lb).toBeHidden();
        await expectFocused(zoom);
        await zoom.click();
        await expect(lb).toBeVisible();
        await page.keyboard.press('Escape');
        await expect(lb).toBeHidden();
        await expectCycle(page, DIALOG, { cycles: 1 });
        await closeVia(page, round === 0 ? 'button' : 'esc');
        await expect(page.locator(MODAL)).toBeHidden();
        await expectFocused(gridCard(page, idx));
        await expectNotTrapped(page);
      }
    });

    test('document trap handler는 1개이고 개폐를 반복해도 늘지 않으며, lightbox 개별 keydown listener는 없다', async ({ page }) => {
      const idx = await findProjectWithShots(page);
      expect(idx).not.toBeNull();
      const lb = page.locator(LIGHTBOX);
      await openGrid(page, idx);
      await page.locator(`${MODAL} .shot-zoom`).first().click();
      await expect(lb).toBeVisible();
      const first = await page.evaluate(() => window.__keydownProbe());
      await page.keyboard.press('Escape');
      await page.keyboard.press('Escape');
      for (let i = 0; i < 3; i++) {
        await openGrid(page, idx);
        await page.locator(`${MODAL} .shot-zoom`).first().click();
        await expect(lb).toBeVisible();
        await page.keyboard.press('Escape');
        await closeVia(page, 'button');
        await expect(page.locator(MODAL)).toBeHidden();
      }
      const after = await page.evaluate(() => window.__keydownProbe());
      expect(after.document, 'document keydown listener 수 불변').toBe(first.document);
      expect(await page.evaluate(() => window.__keydownOn('.lightbox'))).toBe(0);
    });
  });

  test('Tab으로 도달한 modal 요소의 :focus-visible outline-style은 none이 아니다', async ({ page }) => {
    await openGrid(page, 0);
    const { n } = await focusState(page, DIALOG);
    for (let i = 0; i < n; i++) {
      await page.keyboard.press('Tab');
      const st = await page.evaluate(() => {
        const el = document.activeElement;
        return { focusVisible: el.matches(':focus-visible'), outline: getComputedStyle(el).outlineStyle, tag: el.outerHTML.slice(0, 60) };
      });
      expect(st.focusVisible, st.tag).toBe(true);
      expect(st.outline, st.tag).not.toBe('none');
    }
  });
});
