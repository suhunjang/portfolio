// compact step 10 — screenshot (설계 compact §C7): COMPACT_RUN_ID가 있을 때만, desktop-dark 하나에서 단일 실행 주체로 15장을 찍는다.
import { createHash } from 'node:crypto';
import { existsSync, lstatSync, mkdirSync, readdirSync, readFileSync, writeFileSync } from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { expect, test } from '@playwright/test';
import config from '../playwright.config.js';
import { installProjectTheme } from '../helpers/theme.js';
import { prepareForAxe } from '../helpers/axe-prepare.js';

const RUN_ID = process.env.COMPACT_RUN_ID;
const RUN_ID_RE = /^[a-z0-9][a-z0-9-]{2,40}$/;
const REPO_ROOT = fileURLToPath(new URL('../..', import.meta.url));
const COORDINATOR = 'desktop-dark';
const PROJECT_NAMES = ['mobile-dark', 'mobile-light', 'tablet-dark', 'tablet-light', 'desktop-dark', 'desktop-light'];
const MODAL_PROJECTS = [1, 5, 7];
const MODAL_THEMES = ['desktop-dark', 'desktop-light'];

const EXPECTED_FILES = [
  ...PROJECT_NAMES.map((p) => `page-${p}.png`),
  ...MODAL_PROJECTS.flatMap((n) => MODAL_THEMES.map((p) => `modal-project-${n}-${p}.png`)),
  'menu-open-mobile-dark.png',
  'lightbox-desktop-dark.png',
  'print-desktop-light.png',
].sort();

const relDir = () => `tests/screenshots/compact-${RUN_ID}`;
const absDir = () => path.join(REPO_ROOT, relDir());
const manifestPath = () => path.join(REPO_ROOT, `tests/.tmp/compact/screenshots-${RUN_ID}.json`);

// suite 공유 상태(serial)
const state = { projects: null, taken: [], lightboxProject: null, files: null };

async function shoot(page, name, { fullPage = false } = {}) {
  const file = path.join(absDir(), name);
  expect(existsSync(file), `${name} 중복`).toBe(false);
  await page.screenshot({ path: file, fullPage, animations: 'disabled' });
  state.taken.push(name);
}

// 모달 SVG text는 Space Grotesk(첫 family)여야 한다.
async function expectModalSvgFont(page, label) {
  const fams = await page.$$eval('#projectModal svg text', (els) => els.map((e) => getComputedStyle(e).fontFamily));
  expect(fams.length, `${label} svg text 개수`).toBeGreaterThan(0);
  const first = fams.map((f) => f.split(',')[0].trim().replace(/^["']|["']$/g, ''));
  expect(first, `${label} svg text font`).toEqual(fams.map(() => 'Space Grotesk'));
}

async function withPage(context, fn) {
  const page = await context.newPage();
  try {
    await page.goto('/');
    await fn(page);
  } finally {
    await page.close();
  }
}

test.describe.serial('compact step 10 screenshots', () => {
  test.skip(!RUN_ID, 'COMPACT_RUN_ID 없음');

  test.beforeEach(({}, testInfo) => {
    test.skip(testInfo.project.name !== COORDINATOR, `${COORDINATOR} 전용 coordinator`);
  });

  test('1. ID 검사', () => {
    expect(RUN_ID).toMatch(RUN_ID_RE);
  });

  test('2. 출력 디렉터리가 없음을 확인하고 만든다', () => {
    expect(existsSync(absDir()), `${relDir()} 이미 있음`).toBe(false);
    mkdirSync(absDir(), { recursive: true });
    expect(lstatSync(absDir()).isDirectory()).toBe(true);
  });

  test('3. config에서 6개 project를 읽는다', () => {
    const projects = config.projects.map((p) => ({
      name: p.name,
      viewport: p.use.viewport,
      colorScheme: p.use.colorScheme,
      theme: p.metadata.theme,
      baseURL: p.use.baseURL ?? config.use.baseURL,
    }));
    expect(projects.map((p) => p.name).sort()).toEqual([...PROJECT_NAMES].sort());
    for (const p of projects) {
      expect(p.viewport, p.name).toBeTruthy();
      expect(p.colorScheme, p.name).toBe(p.theme);
      expect(p.baseURL, p.name).toBeTruthy();
    }
    state.projects = projects;
  });

  test('4. project마다 context를 만들고 테마를 적용해 15장을 찍는다', async ({ browser }) => {
    test.setTimeout(300000);
    expect(state.projects).not.toBeNull();
    for (const p of state.projects) {
      const context = await browser.newContext({ baseURL: p.baseURL, viewport: p.viewport, colorScheme: p.colorScheme });
      try {
        await installProjectTheme(context, { project: { name: p.name } });

        await withPage(context, async (page) => {
          await prepareForAxe(page, { scenario: 'page' });
          await expect(page.locator('html')).toHaveAttribute('data-theme', p.theme);
          await shoot(page, `page-${p.name}.png`, { fullPage: true });
        });

        if (MODAL_THEMES.includes(p.name)) {
          for (const n of MODAL_PROJECTS) {
            await withPage(context, async (page) => {
              await prepareForAxe(page, { scenario: 'modal', projectIndex: n });
              await expectModalSvgFont(page, `modal ${n} ${p.name}`);
              await shoot(page, `modal-project-${n}-${p.name}.png`);
            });
          }
        }

        if (p.name === 'mobile-dark') {
          await withPage(context, async (page) => {
            await prepareForAxe(page, { scenario: 'page' });
            await page.locator('#menuToggle').click();
            await expect(page.locator('#navLinks')).toHaveClass(/(^|\s)open(\s|$)/);
            await expect(page.locator('#menuToggle')).toHaveAttribute('aria-expanded', 'true');
            await shoot(page, 'menu-open-mobile-dark.png');
          });
        }

        if (p.name === 'desktop-dark') {
          await withPage(context, async (page) => {
            const res = await prepareForAxe(page, { scenario: 'lightbox' });
            expect(Number.isInteger(res.projectIndex)).toBe(true);
            state.lightboxProject = res.projectIndex;
            await shoot(page, 'lightbox-desktop-dark.png');
          });
        }

        if (p.name === 'desktop-light') {
          await withPage(context, async (page) => {
            await prepareForAxe(page, { scenario: 'page' });
            await page.emulateMedia({ media: 'print' });
            await shoot(page, 'print-desktop-light.png', { fullPage: true });
          });
        }
      } finally {
        await context.close();
      }
    }
  });

  test('5. 결과 목록: 15개 exact, 누락·중복·초과 없음', () => {
    expect([...state.taken].sort()).toEqual(EXPECTED_FILES);
    const onDisk = readdirSync(absDir()).sort();
    expect(onDisk).toEqual(EXPECTED_FILES);
    state.files = onDisk.map((name) => {
      const rel = `${relDir()}/${name}`;
      const abs = path.join(REPO_ROOT, rel);
      const st = lstatSync(abs);
      expect(st.isFile() && st.size > 0, rel).toBe(true);
      return { path: rel, sha256: createHash('sha256').update(readFileSync(abs)).digest('hex') };
    });
  });

  test('6. manifest를 기록한다', () => {
    expect(state.files).toHaveLength(15);
    expect(state.lightboxProject).not.toBeNull();
    mkdirSync(path.dirname(manifestPath()), { recursive: true });
    const manifest = { runId: RUN_ID, files: state.files, lightboxProject: state.lightboxProject };
    writeFileSync(manifestPath(), JSON.stringify(manifest, null, 2) + '\n', { flag: 'wx' });
  });
});
