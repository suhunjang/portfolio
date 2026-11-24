// step 21 — browser smoke + §THEME tests/helpers/theme.js (설계 §8.3), 6 project 전부 실행
import { readFileSync } from 'node:fs';
import { expect } from '@playwright/test';
import { test, installProjectTheme, collectConsoleErrors } from '../helpers/theme.js';

const THEME_KEY = readFileSync(new URL('../../js/main.js', import.meta.url), 'utf8')
  .match(/\bTHEME_KEY\s*=\s*["']([^"']+)["']/)[1];

const suffixOf = (testInfo) => testInfo.project.name.match(/-(dark|light)$/)[1];
const opposite = (theme) => (theme === 'dark' ? 'light' : 'dark');

test.describe('step 21 smoke', () => {
  test('(a) 기본 page: html[data-theme] = project suffix, heroName 보임', async ({ page }, testInfo) => {
    await page.goto('/');
    await expect(page.locator('html')).toHaveAttribute('data-theme', suffixOf(testInfo));
    await expect(page.locator('#heroName')).toBeVisible();
  });

  test('(b) context.newPage()도 테마 상속', async ({ context }, testInfo) => {
    const p2 = await context.newPage();
    await p2.goto('/');
    await expect(p2.locator('html')).toHaveAttribute('data-theme', suffixOf(testInfo));
    await p2.close();
  });

  test('(c) 비-null 저장값은 덮어쓰지 않는다', async ({ context }, testInfo) => {
    const other = opposite(suffixOf(testInfo));
    const seed = await context.newPage();
    await seed.goto('/');
    await seed.evaluate(([k, v]) => localStorage.setItem(k, v), [THEME_KEY, other]);
    await seed.close();

    const p = await context.newPage();
    await p.goto('/');
    expect(await p.evaluate((k) => localStorage.getItem(k), THEME_KEY)).toBe(other);
    await expect(p.locator('html')).toHaveAttribute('data-theme', other);
    await p.close();
  });

  test('installProjectTheme: suffix 없는 project name → throw, addInitScript 정확히 1회', async () => {
    const calls = [];
    const fake = { addInitScript: async (...args) => { calls.push(args); } };

    for (const name of ['desktop', 'desktop-dim', 'dark-desktop', '']) {
      await expect(installProjectTheme(fake, { project: { name } })).rejects.toThrow();
    }
    expect(calls).toHaveLength(0);

    await installProjectTheme(fake, { project: { name: 'tablet-light' } });
    expect(calls).toHaveLength(1);
  });

  test('collectConsoleErrors: 정상 페이지 [] · 비동기 throw → pageErrors 1건', async ({ page }) => {
    const c1 = collectConsoleErrors(page);
    await page.goto('/');
    const r1 = await c1.finish();
    expect(r1.pageErrors).toEqual([]);
    expect(r1.consoleErrors).toEqual([]);

    const c2 = collectConsoleErrors(page);
    await page.evaluate(() => { setTimeout(() => { throw new Error('smoke-async-boom'); }, 0); });
    await page.waitForTimeout(50);
    const r2 = await c2.finish();
    expect(r2.pageErrors).toHaveLength(1);
    expect(String(r2.pageErrors[0])).toContain('smoke-async-boom');
  });
});
