// step 26 — 모달·lightbox 회귀 helper (설계 §5)
import { expect } from '@playwright/test';

export const GRID_CARD = '#projectGrid .project-card';
const MODAL_ROOT = '#projectModal';
const CLOSE_BUTTON = '#projectModal .modal-close[data-modal-close]';
const BACKDROP = '#projectModal .modal-backdrop[data-modal-close]';

export function gridCard(page, N) {
  return page.locator('#projectGrid .project-card[data-project="' + N + '"]');
}

async function waitOpen(page) {
  await expect(page.locator(MODAL_ROOT)).toBeVisible();
}

export async function openFirstProjectByClick(page) {
  await gridCard(page, 0).click();
  await waitOpen(page);
}

export async function openFirstProjectByEnter(page) {
  const card = gridCard(page, 0);
  await card.focus();
  await card.press('Enter');
  await waitOpen(page);
}

export async function closeVia(page, how) {
  if (how === 'button') {
    await page.locator(CLOSE_BUTTON).click();
  } else if (how === 'backdrop') {
    await page.locator(BACKDROP).click({ position: { x: 5, y: 5 } });
  } else if (how === 'esc') {
    await page.keyboard.press('Escape');
  } else {
    throw new Error(`modal: unknown close method: ${JSON.stringify(how)}`);
  }
}

export async function expectFocused(locator) {
  await expect(locator).toBeFocused();
}

export function modalTitle(page) {
  return page.locator('#projectModal #modalTitle');
}

// #projectGrid 카드(DOM 순서) 중 detail.shots가 있는 첫 프로젝트 index, 없으면 null.
export async function findProjectWithShots(page) {
  return page.evaluate((sel) => {
    for (const card of document.querySelectorAll(sel)) {
      const n = Number(card.getAttribute('data-project'));
      const p = PROJECTS[n]; // eslint-disable-line no-undef
      if (p && p.detail && Array.isArray(p.detail.shots) && p.detail.shots.length > 0) return n;
    }
    return null;
  }, GRID_CARD);
}
