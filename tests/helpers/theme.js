// step 21 — §THEME (설계 §8.3): installProjectTheme · test fixture · collectConsoleErrors
import { readFileSync } from 'node:fs';
import { test as base } from '@playwright/test';

const MAIN_JS = new URL('../../js/main.js', import.meta.url);
const THEME_KEY_RE = /\bTHEME_KEY\s*=\s*["']([^"']+)["']/;
const PROJECT_THEME_RE = /-(dark|light)$/;
const GOOGLE_FONTS_DOMAINS = ['fonts.googleapis.com', 'fonts.gstatic.com'];

function readThemeKey() {
  const m = readFileSync(MAIN_JS, 'utf8').match(THEME_KEY_RE);
  if (!m) throw new Error('theme: THEME_KEY not found in js/main.js');
  return m[1];
}

// 문서 origin의 저장값이 null일 때만 프로젝트 테마를 저장한다(비-null 값은 그대로 둔다).
function nullOnlyThemeInit({ key, theme }) {
  try {
    if (window.localStorage.getItem(key) === null) window.localStorage.setItem(key, theme);
  } catch {
    // about:blank 등 localStorage 접근 불가 문서는 건너뛴다.
  }
}

export async function installProjectTheme(context, testInfo) {
  const name = testInfo?.project?.name;
  const m = typeof name === 'string' ? name.match(PROJECT_THEME_RE) : null;
  if (!m) throw new Error(`theme: project name must end with -dark or -light: ${JSON.stringify(name)}`);
  const key = readThemeKey();
  await context.addInitScript(nullOnlyThemeInit, { key, theme: m[1] });
}

export const test = base.extend({
  context: async ({ context }, use, testInfo) => {
    await installProjectTheme(context, testInfo);
    await use(context);
  },
});

function isGoogleFonts(msg) {
  const text = msg.text() || '';
  const url = msg.location()?.url || '';
  return GOOGLE_FONTS_DOMAINS.some((d) => text.includes(d) || url.includes(d));
}

export function collectConsoleErrors(page) {
  const pageErrors = [];
  const consoleErrors = [];
  const onPageError = (err) => pageErrors.push(err);
  const onConsole = (msg) => {
    if (msg.type() === 'error' && !isGoogleFonts(msg)) consoleErrors.push(msg.text());
  };
  page.on('pageerror', onPageError);
  page.on('console', onConsole);
  return {
    async finish() {
      await page.waitForLoadState('networkidle');
      page.off('pageerror', onPageError);
      page.off('console', onConsole);
      return { pageErrors: [...pageErrors], consoleErrors: [...consoleErrors] };
    },
  };
}
