// step 27 — ui-regression (설계 §2·§4·§5): 테마 토글·모바일 메뉴·스크롤스파이·typing·reduced-motion 회귀
import { readFileSync } from 'node:fs';
import { expect } from '@playwright/test';
import { test } from '../helpers/theme.js';

const baseline = JSON.parse(readFileSync(new URL('../fixtures/baseline-data.json', import.meta.url), 'utf8'));
const ROLES = baseline.PROFILE.roles;
const MAIN_JS = readFileSync(new URL('../../js/main.js', import.meta.url), 'utf8');
const THEME_KEY = MAIN_JS.match(/\bTHEME_KEY\s*=\s*["']([^"']+)["']/)[1];
const OPEN = /(^|\s)open(\s|$)/;

const projectTheme = (testInfo) => testInfo.project.name.match(/-(dark|light)$/)[1];
const isDevice = (testInfo, device) => testInfo.project.name.startsWith(`${device}-`);
const storedTheme = (page) => page.evaluate((key) => window.localStorage.getItem(key), THEME_KEY);

test.describe('step 27 ui-regression', () => {
  test('테마 토글: data-theme·THEME_KEY 전환 후 새로고침에도 유지', async ({ page }, testInfo) => {
    const theme = projectTheme(testInfo);
    const other = theme === 'dark' ? 'light' : 'dark';
    const html = page.locator('html');
    await page.goto('/');
    await expect(html).toHaveAttribute('data-theme', theme);
    expect(await storedTheme(page)).toBe(theme);

    await page.locator('#themeToggle').click();
    await expect(html).toHaveAttribute('data-theme', other);
    expect(await storedTheme(page)).toBe(other);

    await page.reload();
    await expect(html).toHaveAttribute('data-theme', other);
    expect(await storedTheme(page)).toBe(other);

    await page.locator('#themeToggle').click();
    await expect(html).toHaveAttribute('data-theme', theme);
    await page.reload();
    await expect(html).toHaveAttribute('data-theme', theme);
    expect(await storedTheme(page)).toBe(theme);
  });

  test('mobile 메뉴: 열면 #navLinks.open·aria-expanded=true, 링크 클릭 후 닫힘', async ({ page }, testInfo) => {
    test.skip(!isDevice(testInfo, 'mobile'), 'mobile 전용');
    await page.goto('/');
    const toggle = page.locator('#menuToggle');
    const nav = page.locator('#navLinks');
    await expect(toggle).toBeVisible();
    await expect(toggle).toHaveAttribute('aria-expanded', 'false');
    await expect(nav).not.toHaveClass(OPEN);

    await toggle.click();
    await expect(nav).toHaveClass(OPEN);
    await expect(toggle).toHaveAttribute('aria-expanded', 'true');

    const link = page.locator('#navLinks .nav-link[href="#projects"]');
    await expect(link).toBeVisible();
    await link.click();
    await expect(nav).not.toHaveClass(OPEN);
    await expect(toggle).toHaveAttribute('aria-expanded', 'false');
  });

  test('desktop 스크롤스파이: projects 링크 클릭 → active', async ({ page }, testInfo) => {
    test.skip(!isDevice(testInfo, 'desktop'), 'desktop 전용');
    await page.goto('/');
    const link = page.locator('.nav-link[href="#projects"]');
    await link.click();
    await expect(link).toHaveClass(/active/);
  });

  test('typing: #typed 텍스트가 roles 접두사로 계속 변한다', async ({ page }) => {
    await page.goto('/');
    const typed = page.locator('#typed');
    const seen = new Set();
    await expect
      .poll(
        async () => {
          seen.add(await typed.textContent());
          return seen.size;
        },
        { timeout: 10_000, intervals: [50] },
      )
      .toBeGreaterThanOrEqual(3);
    for (const text of seen) {
      expect(ROLES.some((r) => r.startsWith(text)), `prefix of a role: ${JSON.stringify(text)}`).toBe(true);
    }
  });

  test.describe('reduced-motion', () => {
    test.use({ reducedMotion: 'reduce' });

    test('#typed = roles[0] 고정, .reveal 즉시 .in', async ({ page }) => {
      await page.goto('/');
      const counts = await page.evaluate(() => ({
        total: document.querySelectorAll('.reveal').length,
        notIn: document.querySelectorAll('.reveal:not(.in)').length,
      }));
      expect(counts.total).toBeGreaterThan(0);
      expect(counts.notIn).toBe(0);
      const typed = page.locator('#typed');
      await expect(typed).toHaveText(ROLES[0]);
      await page.waitForTimeout(500);
      await expect(typed).toHaveText(ROLES[0]);
    });
  });
});
