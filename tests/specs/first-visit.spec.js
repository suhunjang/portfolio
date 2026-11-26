// step 27 — first-visit (설계 §8.3): installProjectTheme 없는 별도 context에서 최초 방문 테마 = colorScheme
import { readFileSync } from 'node:fs';
import { test, expect } from '@playwright/test';

const MAIN_JS = readFileSync(new URL('../../js/main.js', import.meta.url), 'utf8');
const THEME_KEY = MAIN_JS.match(/\bTHEME_KEY\s*=\s*["']([^"']+)["']/)[1];

test.describe('step 27 first-visit', () => {
  for (const colorScheme of ['light', 'dark']) {
    test(`저장값 없는 최초 방문은 colorScheme ${colorScheme}을 따른다`, async ({ browser }, testInfo) => {
      test.skip(testInfo.project.name !== 'desktop-dark', 'desktop-dark 전용');
      const context = await browser.newContext({
        baseURL: testInfo.project.use.baseURL,
        viewport: testInfo.project.use.viewport,
        colorScheme,
      });
      try {
        const page = await context.newPage();
        await page.goto('/');
        await expect(page.locator('html')).toHaveAttribute('data-theme', colorScheme);
        expect(await page.evaluate((key) => window.localStorage.getItem(key), THEME_KEY)).toBeNull();
      } finally {
        await context.close();
      }
    });
  }
});
