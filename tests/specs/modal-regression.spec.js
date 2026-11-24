// step 26 — modal-regression (설계 §5): 모달·lightbox 회귀, 6 project 전부 실행(lightbox는 desktop만)
import { readFileSync } from 'node:fs';
import { expect } from '@playwright/test';
import { test } from '../helpers/theme.js';
import {
  GRID_CARD,
  gridCard,
  openFirstProjectByClick,
  openFirstProjectByEnter,
  closeVia,
  expectFocused,
  modalTitle,
  findProjectWithShots,
} from '../helpers/modal.js';

const baseline = JSON.parse(readFileSync(new URL('../fixtures/baseline-data.json', import.meta.url), 'utf8'));
const MODAL = '#projectModal';
const LIGHTBOX = '.lightbox[role="dialog"]';
const MODAL_OPEN = /(^|\s)modal-open(\s|$)/;

async function expectOpen(page, idx) {
  await expect(page.locator(MODAL)).toBeVisible();
  await expect(page.locator('body')).toHaveClass(MODAL_OPEN);
  await expect(modalTitle(page)).toHaveText(baseline.PROJECTS[idx].title);
}

async function expectClosed(page) {
  await expect(page.locator(MODAL)).toBeHidden();
  await expect(page.locator('body')).not.toHaveClass(MODAL_OPEN);
}

test.describe('step 26 modal-regression', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/');
  });

  test('helper 상수·gridCard 셀렉터', async ({ page }) => {
    expect(GRID_CARD).toBe('#projectGrid .project-card');
    await expect(page.locator(GRID_CARD)).toHaveCount(baseline.PROJECTS.length);
    await expect(gridCard(page, 0)).toHaveCount(1);
    await expect(gridCard(page, 0)).toHaveAttribute('data-project', '0');
    await expect(gridCard(page, 12)).toHaveAttribute('data-project', '12');
  });

  for (const how of ['button', 'backdrop', 'esc']) {
    test(`click 열기 → ${how} 닫기: 트리거 포커스 복귀·modal-open 해제`, async ({ page }) => {
      await openFirstProjectByClick(page);
      await expectOpen(page, 0);
      await expectFocused(page.locator(`${MODAL} .modal-close[data-modal-close]`));
      await closeVia(page, how);
      await expectClosed(page);
      await expectFocused(gridCard(page, 0));
    });

    test(`Enter 열기 → ${how} 닫기: 트리거 포커스 복귀·modal-open 해제`, async ({ page }) => {
      await openFirstProjectByEnter(page);
      await expectOpen(page, 0);
      await closeVia(page, how);
      await expectClosed(page);
      await expectFocused(gridCard(page, 0));
    });
  }

  test('closeVia: 알 수 없는 방식 → throw', async ({ page }) => {
    await expect(closeVia(page, 'nope')).rejects.toThrow();
  });

  test('desktop lightbox: .shot-zoom 열기, Esc 1회 lightbox만·2회 모달', async ({ page }, testInfo) => {
    test.skip(!testInfo.project.name.startsWith('desktop-'), 'lightbox는 desktop project만');
    const idx = await findProjectWithShots(page);
    expect(idx).not.toBeNull();
    expect(baseline.PROJECTS[idx].detail.shots.length).toBeGreaterThan(0);

    // 모달 탐색(열기→닫기) 뒤에도 lightbox는 열리지 않는다
    await gridCard(page, idx).click();
    await expectOpen(page, idx);
    await closeVia(page, 'button');
    await expectClosed(page);
    await expect(page.locator(LIGHTBOX)).toHaveCount(0);

    await gridCard(page, idx).click();
    await expectOpen(page, idx);
    await expect(page.locator(LIGHTBOX)).toHaveCount(0);
    const zoom = page.locator(`${MODAL} .shot-zoom`).first();
    await zoom.click();
    const lb = page.locator(LIGHTBOX);
    await expect(lb).toBeVisible();
    await expect(lb.locator('img')).toHaveAttribute('src', /.+/);
    await expectFocused(lb.locator('.modal-close'));

    await page.keyboard.press('Escape');
    await expect(lb).toBeHidden();
    await expect(page.locator(MODAL)).toBeVisible();
    await expect(page.locator('body')).toHaveClass(MODAL_OPEN);
    await expectFocused(zoom);

    await page.keyboard.press('Escape');
    await expectClosed(page);
    await expectFocused(gridCard(page, idx));
  });
});
