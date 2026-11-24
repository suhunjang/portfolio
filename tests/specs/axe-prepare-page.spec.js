// step 29 — axe prepare page (설계 §6.3): PREPARE_PREFIX · prepareError · withPrepareCode · preparePage
import { expect } from '@playwright/test';
import { test } from '../helpers/theme.js';
import { PREPARE_PREFIX, prepareError, withPrepareCode, preparePage } from '../helpers/axe-prepare.js';

const PROJECTS = ['desktop-dark', 'desktop-light', 'mobile-dark'];

async function envState(page) {
  return page.evaluate(() => ({
    theme: document.documentElement.getAttribute('data-theme'),
    reduce: window.matchMedia('(prefers-reduced-motion: reduce)').matches,
  }));
}

test.describe('step 29 axe-prepare-page', () => {
  test.beforeEach(async ({}, testInfo) => {
    test.skip(!PROJECTS.includes(testInfo.project.name), 'desktop-dark·desktop-light·mobile-dark 전용');
  });

  test('PREPARE_PREFIX·prepareError: message·code·cause', () => {
    expect(PREPARE_PREFIX).toBe('prepareForAxe: ');
    const e = prepareError('x');
    expect(e).toBeInstanceOf(Error);
    expect(e.message).toBe('prepareForAxe: x');
    expect(e.code).toBe('x');
    const cause = new Error('c');
    expect(prepareError('y', cause).cause).toBe(cause);
  });

  test('withPrepareCode: 일반 오류는 code로 감싸고 prepareError는 그대로 통과', async () => {
    await expect(withPrepareCode('ok', async () => 42)).resolves.toBe(42);
    const boom = new Error('boom');
    const err = await withPrepareCode('fonts-not-ready', () => Promise.reject(boom)).catch((e) => e);
    expect(err.message).toBe('prepareForAxe: fonts-not-ready');
    expect(err.code).toBe('fonts-not-ready');
    expect(err.cause).toBe(boom);
    const inner = await withPrepareCode('a', () => Promise.reject(prepareError('b'))).catch((e) => e);
    expect(inner.code).toBe('b');
    expect(inner.message).toBe('prepareForAxe: b');
  });

  test('preparePage: 모든 .reveal이 .in·scrollY 0·scrollSteps ≥ 1·테마/reduced-motion 불변', async ({ page }) => {
    await page.goto('/');
    const before = await envState(page);
    const res = await preparePage(page);
    expect(res.revealChecked).toBeGreaterThan(0);
    expect(res.scrollSteps).toBeGreaterThanOrEqual(1);
    const state = await page.evaluate(() => ({
      total: document.querySelectorAll('.reveal').length,
      hidden: document.querySelectorAll('.reveal:not(.in)').length,
      y: window.scrollY,
    }));
    expect(state.total).toBe(res.revealChecked);
    expect(state.hidden).toBe(0);
    expect(state.y).toBe(0);
    expect(await envState(page)).toEqual(before);
  });

  test('preparePage: .in이 붙지 않는 .reveal 1개 → reveal-hidden:1', async ({ page }) => {
    await page.goto('/');
    const before = await envState(page);
    await page.evaluate(() => {
      const el = document.createElement('div');
      el.className = 'reveal';
      el.textContent = 'never revealed';
      document.body.appendChild(el);
    });
    const err = await preparePage(page, { timeoutMs: 500 }).catch((e) => e);
    expect(err).toBeInstanceOf(Error);
    expect(err.message).toBe('prepareForAxe: reveal-hidden:1');
    expect(err.code).toBe('reveal-hidden:1');
    expect(await envState(page)).toEqual(before);
  });
});
