// step 21 — §THEME (설계 §8.3): installProjectTheme · test fixture · collectConsoleErrors
import { createHash } from 'node:crypto';
import { existsSync, mkdirSync, readFileSync, renameSync, writeFileSync } from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
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

// 외부 Google Fonts 요청은 간헐적으로 응답이 멈춰 page.goto 'load'를 30초 넘게 막는다(2026-11-26 확인).
// 실제 글꼴(Inter·Space Grotesk)은 유지해야 geometry 검사(첫 화면·hit target·3줄 높이)의 의미가 같다.
// 그래서 막지 않고, 처음 한 번 받은 응답을 tests/.tmp/font-cache(gitignore)에 저장해 이후에는 로컬에서 응답한다.
// 받지 못하면 대체 글꼴로 조용히 통과하지 않도록 fixture가 테스트를 실패시킨다. index.html은 그대로다.
const FONT_CACHE = fileURLToPath(new URL('../.tmp/font-cache/', import.meta.url));
const GOOGLE_FONTS_RE = /^https:\/\/fonts\.(googleapis|gstatic)\.com\//;

export async function serveGoogleFontsFromCache(context, failures) {
  mkdirSync(FONT_CACHE, { recursive: true });
  await context.route(GOOGLE_FONTS_RE, async (route) => {
    const url = route.request().url();
    const key = createHash('sha256').update(url).digest('hex');
    const bodyPath = path.join(FONT_CACHE, key);
    const metaPath = `${bodyPath}.json`;
    if (existsSync(bodyPath) && existsSync(metaPath)) {
      const meta = JSON.parse(readFileSync(metaPath, 'utf8'));
      await route.fulfill({ status: 200, headers: meta.headers, body: readFileSync(bodyPath) });
      return;
    }
    try {
      const resp = await route.fetch({ timeout: 15000 });
      if (resp.status() !== 200) throw new Error(`status ${resp.status()}`);
      const body = await resp.body();
      const headers = {
        'content-type': resp.headers()['content-type'] || 'application/octet-stream',
        'access-control-allow-origin': '*',
      };
      writeFileSync(`${bodyPath}.tmp`, body);
      renameSync(`${bodyPath}.tmp`, bodyPath);
      writeFileSync(metaPath, JSON.stringify({ url, headers }));
      await route.fulfill({ status: 200, headers, body });
    } catch (e) {
      failures.push(`${url}: ${e.message}`);
      await route.abort('failed');
    }
  });
}

export const test = base.extend({
  context: async ({ context }, use, testInfo) => {
    await installProjectTheme(context, testInfo);
    const fontFailures = [];
    await serveGoogleFontsFromCache(context, fontFailures);
    await use(context);
    if (fontFailures.length) throw new Error(`google-fonts-unavailable: ${fontFailures.join('; ')}`);
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
