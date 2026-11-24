// step 28 — axe canonical target (설계 §6.1·§6.2): ALIASES · canonicalTargetInPage · canonicalFromDescriptor · runAxe
import { test, expect } from '@playwright/test';
import { ALIASES, canonicalTargetInPage, canonicalFromDescriptor, runAxe } from '../helpers/axe.js';

const RULE = 'color-contrast';

const wrap = (body) => `<!doctype html><html lang="ko"><head><title>t</title></head><body>${body}</body></html>`;

async function keyOf(page, html, selector, ruleId = RULE) {
  await page.setContent(wrap(html));
  return canonicalTargetInPage(page, ruleId, selector);
}

test.describe('step 28 axe-canonical', () => {
  test.beforeEach(async ({}, testInfo) => {
    test.skip(testInfo.project.name !== 'desktop-dark', 'desktop-dark 전용');
  });

  test('ALIASES는 §6.1 두 alias 그대로다', () => {
    expect(ALIASES).toEqual({ '## — Stack & Contact': '## — Contact', '기술 스택 & 연락처': '연락처' });
  });

  test('canonicalFromDescriptor: anchor 우선순위·textSig fallback·숫자 #·80자', () => {
    const empty = { textContent: '', ariaLabel: null, alt: null, title: null, src: null };
    const t = (anchor, text = {}) => canonicalFromDescriptor({ ruleId: 'r', anchor, text: { ...empty, ...text } });
    expect(t({ kind: 'featured', value: '5' }, { textContent: ' A\n  b ' })).toBe('r::featured:5::A b');
    expect(t({ kind: 'project', value: '5' }, { textContent: 'x' })).toBe('r::project:5::x');
    expect(t({ kind: 'id', value: 'career' }, { textContent: 'x' })).toBe('r::#career::x');
    expect(t({ kind: 'landmark', value: 'main' }, { textContent: 'x' })).toBe('r::main::x');
    expect(t({ kind: 'document' }, { textContent: 'x' })).toBe('r::document::x');
    expect(t({ kind: 'document' }, { ariaLabel: 'Menu 2', alt: 'a', title: 't' })).toBe('r::document::Menu #');
    expect(t({ kind: 'document' }, { alt: 'Alt', title: 't' })).toBe('r::document::Alt');
    expect(t({ kind: 'document' }, { title: 'Ti' })).toBe('r::document::Ti');
    expect(t({ kind: 'document' }, { src: 'https://x.test/img/shot-12.png?v=3' })).toBe('r::document::shot-##.png');
    expect(t({ kind: 'document' }, {})).toBe('r::document::');
    expect(t({ kind: 'document' }, { textContent: 'y'.repeat(100) })).toBe(`r::document::${'y'.repeat(80)}`);
    expect(t({ kind: 'document' }, { textContent: '04 — Stack & Contact' })).toBe('r::document::## — Contact');
    expect(() => t({ kind: 'bogus' }, {})).toThrow();
  });

  test('section#career subtree 이동·h3→span·01→04는 key 같음', async ({ page }) => {
    const a = await keyOf(
      page,
      '<header><nav>n</nav></header><main><section id="career"><h3 class="t">01 — Career</h3></section><section id="x">x</section></main>',
      '.t',
    );
    const b = await keyOf(
      page,
      '<header><nav>n</nav></header><main><section id="x">x</section><div><section id="career"><span class="t">04 — Career</span></section></div></main>',
      '.t',
    );
    expect(a).toBe('color-contrast::#career::## — Career');
    expect(b).toBe(a);
  });

  test('h3만 section#career 밖으로 이동하면 key 다름', async ({ page }) => {
    const a = await keyOf(page, '<main><section id="career"><h3 class="t">01 — Career</h3></section></main>', '.t');
    const b = await keyOf(page, '<main><h3 class="t">01 — Career</h3><section id="career"></section></main>', '.t');
    expect(b).toBe('color-contrast::main::## — Career');
    expect(b).not.toBe(a);
  });

  test('[data-project=5] 안 div→p는 key 같음, 텍스트 다르면 다름', async ({ page }) => {
    const a = await keyOf(page, '<main id="m"><article data-project="5"><div class="d">Hello world</div></article></main>', '.d');
    const b = await keyOf(page, '<main id="m"><article data-project="5"><p class="d">Hello   world</p></article></main>', '.d');
    const c = await keyOf(page, '<main id="m"><article data-project="5"><p class="d">Hello there</p></article></main>', '.d');
    expect(a).toBe('color-contrast::project:5::Hello world');
    expect(b).toBe(a);
    expect(c).not.toBe(a);
  });

  test('project:5 ≠ featured:5', async ({ page }) => {
    const p = await keyOf(page, '<main><article data-project="5"><p class="d">T</p></article></main>', '.d');
    const f = await keyOf(page, '<main><article data-featured-card data-project="5"><p class="d">T</p></article></main>', '.d');
    expect(p).toBe('color-contrast::project:5::T');
    expect(f).toBe('color-contrast::featured:5::T');
    expect(p).not.toBe(f);
  });

  test('alias 적용 후 key 같음', async ({ page }) => {
    const a = await keyOf(page, '<main><section id="contact"><h2 class="t">04 — Stack &amp; Contact</h2></section></main>', '.t');
    const b = await keyOf(page, '<main><section id="contact"><h2 class="t">05 — Contact</h2></section></main>', '.t');
    expect(a).toBe('color-contrast::#contact::## — Contact');
    expect(b).toBe(a);
    const c = await keyOf(page, '<main><section id="contact"><h3 class="t">기술 스택 &amp; 연락처</h3></section></main>', '.t');
    const d = await keyOf(page, '<main><section id="contact"><h3 class="t">연락처</h3></section></main>', '.t');
    expect(c).toBe('color-contrast::#contact::연락처');
    expect(d).toBe(c);
  });

  test('canonicalTargetInPage: 없는 selector는 throw', async ({ page }) => {
    await page.setContent(wrap('<main></main>'));
    await expect(canonicalTargetInPage(page, RULE, '.nope')).rejects.toThrow(/not found/);
  });

  test('runAxe: serious/critical만, include 범위, targets·selectors 정렬', async ({ page }) => {
    await page.setContent(
      wrap('<main><section id="a"><img src="/img/p1.png"></section><section id="b"><img src="/img/p2.png"></section></main>'),
    );
    const all = await runAxe(page);
    const alt = all.find((v) => v.ruleId === 'image-alt');
    expect(alt).toBeTruthy();
    expect(['serious', 'critical']).toContain(alt.impact);
    expect(alt.targets).toEqual(['image-alt::#a::p#.png', 'image-alt::#b::p#.png']);
    expect(alt.selectors).toEqual([...alt.selectors].sort());
    expect(alt.selectors).toHaveLength(2);
    for (const v of all) expect(['serious', 'critical']).toContain(v.impact);
    const onlyB = await runAxe(page, { include: '#b' });
    expect(onlyB.find((v) => v.ruleId === 'image-alt').targets).toEqual(['image-alt::#b::p#.png']);
  });
});

// step 32 — axe collect tooling (설계 §6.1 entry key·§6.2 step 32): makeEntryKey · COLLECT_DIR · EXPECTED_FILES ·
// resolveCollectDir · resetCollected · writeCollected · mergeCollected · CLI --reset / --merge
import { execFile } from 'node:child_process';
import { createHash } from 'node:crypto';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import {
  makeEntryKey,
  COLLECT_DIR,
  EXPECTED_FILES,
  resolveCollectDir,
  resetCollected,
  writeCollected,
  mergeCollected,
  violationsToEntries,
} from '../helpers/axe.js';

const S32_REPO = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '../..');
const S32_AXE = path.join(S32_REPO, 'tests/helpers/axe.js');
const S32_FIXTURE_OUT = path.join(S32_REPO, 'tests/fixtures/axe-collected.json');
const S32_REAL_DIR = path.join(S32_REPO, COLLECT_DIR);
const S32_PAIRS = [
  ...['mobile', 'tablet', 'desktop'].flatMap((v) => ['dark', 'light'].map((t) => ['page', `${v}-${t}`])),
  ['modal', 'desktop-dark'],
  ['modal', 'desktop-light'],
  ['lightbox', 'desktop-dark'],
  ['lightbox', 'desktop-light'],
];

let s32Seq = 0;
function s32Dir() {
  s32Seq += 1;
  return `tests/.tmp/axe-helper-test-${process.pid}-${s32Seq}`;
}
const s32Abs = (rel) => path.join(S32_REPO, rel);

// 실제 COLLECT_DIR·fixtures 파일의 상태(존재·내용 hash)를 기록한다.
function s32State() {
  const out = {};
  for (const p of [S32_FIXTURE_OUT, S32_REAL_DIR]) {
    let st = null;
    try {
      st = fs.lstatSync(p);
    } catch {
      out[p] = null;
      continue;
    }
    if (st.isDirectory()) {
      out[p] = fs
        .readdirSync(p)
        .sort()
        .map((f) => [f, createHash('sha256').update(fs.readFileSync(path.join(p, f))).digest('hex')]);
    } else {
      out[p] = createHash('sha256').update(fs.readFileSync(p)).digest('hex');
    }
  }
  return out;
}

function s32Cli(args) {
  return new Promise((resolve) => {
    execFile(process.execPath, [S32_AXE, ...args], { cwd: S32_REPO }, (err, stdout, stderr) => {
      resolve({ code: err ? (typeof err.code === 'number' ? err.code : 1) : 0, stdout, stderr });
    });
  });
}

const V = (ruleId, targets, selectors = [], impact = 'serious') => ({ ruleId, impact, targets, selectors });

test.describe('step 32 axe-collect-tooling', () => {
  let before;
  const made = [];
  const dir = () => {
    const d = s32Dir();
    made.push(d);
    return d;
  };

  test.beforeEach(async ({}, testInfo) => {
    test.skip(testInfo.project.name !== 'desktop-dark', 'desktop-dark 전용');
    before = s32State();
  });

  test.afterEach(async ({}, testInfo) => {
    if (testInfo.project.name !== 'desktop-dark') return;
    for (const d of made.splice(0)) fs.rmSync(s32Abs(d), { recursive: true, force: true });
    expect(s32State()).toEqual(before);
  });

  test('makeEntryKey: `${scenario}:${project}:${ruleId}`, 빈 값·`:` throw', () => {
    expect(makeEntryKey({ scenario: 'page', project: 'desktop-dark', ruleId: 'color-contrast' })).toBe(
      'page:desktop-dark:color-contrast',
    );
    expect(makeEntryKey({ scenario: 'lightbox', project: 'desktop-light', ruleId: 'image-alt' })).toBe(
      'lightbox:desktop-light:image-alt',
    );
    for (const bad of [
      { scenario: '', project: 'desktop-dark', ruleId: 'r' },
      { scenario: 'page', project: '', ruleId: 'r' },
      { scenario: 'page', project: 'desktop-dark', ruleId: '' },
      { project: 'desktop-dark', ruleId: 'r' },
      { scenario: 'page', project: 'desktop-dark', ruleId: 'a:b' },
      { scenario: 'pa:ge', project: 'desktop-dark', ruleId: 'r' },
      { scenario: 'page', project: 'desktop:dark', ruleId: 'r' },
    ]) {
      expect(() => makeEntryKey(bad)).toThrow();
    }
  });

  test('COLLECT_DIR·EXPECTED_FILES 10개', () => {
    expect(COLLECT_DIR).toBe('tests/.tmp/axe-collected');
    expect(EXPECTED_FILES).toHaveLength(10);
    expect(new Set(EXPECTED_FILES).size).toBe(10);
    expect(EXPECTED_FILES).toEqual([...EXPECTED_FILES].sort());
    for (const [s, p] of S32_PAIRS) expect(EXPECTED_FILES).toContain(`${s}--${p}.json`);
  });

  test('같은 ruleId 2개·중복 target → entry 1개, targets·selectors 정렬·고유', () => {
    const input = [
      V('image-alt', ['image-alt::#b::y', 'image-alt::#a::x'], ['#b img', '#a img']),
      V('image-alt', ['image-alt::#a::x', 'image-alt::#c::z'], ['#a img', '#c img'], 'critical'),
    ];
    const snapshot = structuredClone(input);
    const entries = violationsToEntries('page', 'desktop-dark', input);
    expect(input).toEqual(snapshot);
    expect(entries).toEqual([
      {
        key: 'page:desktop-dark:image-alt',
        scenario: 'page',
        project: 'desktop-dark',
        ruleId: 'image-alt',
        impact: 'critical',
        targets: ['image-alt::#a::x', 'image-alt::#b::y', 'image-alt::#c::z'],
        selectors: ['#a img', '#b img', '#c img'],
      },
    ]);
  });

  test('page desktop-dark/light → 2 entry, page/modal → 2 entry', () => {
    const v = [V('color-contrast', ['color-contrast::#career::## — Career'], ['#career .section-kicker'])];
    const d = dir();
    resetCollected(d);
    for (const [s, p] of S32_PAIRS) writeCollected(s, p, s === 'page' && p.startsWith('desktop') ? v : [], { dir: d });
    expect(mergeCollected({ collectDir: d }).map((e) => e.key)).toEqual([
      'page:desktop-dark:color-contrast',
      'page:desktop-light:color-contrast',
    ]);
    resetCollected(d);
    for (const [s, p] of S32_PAIRS) writeCollected(s, p, p === 'desktop-dark' && s !== 'lightbox' ? v : [], { dir: d });
    expect(mergeCollected({ collectDir: d }).map((e) => e.key)).toEqual([
      'modal:desktop-dark:color-contrast',
      'page:desktop-dark:color-contrast',
    ]);
  });

  test('resolveCollectDir: 인자 > AXE_COLLECT_DIR > COLLECT_DIR, tests/.tmp 밖 거부', () => {
    const saved = process.env.AXE_COLLECT_DIR;
    try {
      delete process.env.AXE_COLLECT_DIR;
      expect(resolveCollectDir()).toBe(S32_REAL_DIR);
      process.env.AXE_COLLECT_DIR = 'tests/.tmp/axe-helper-test-env';
      expect(resolveCollectDir()).toBe(s32Abs('tests/.tmp/axe-helper-test-env'));
      expect(resolveCollectDir('tests/.tmp/axe-helper-test-arg')).toBe(s32Abs('tests/.tmp/axe-helper-test-arg'));
      expect(resolveCollectDir(s32Abs('tests/.tmp/axe-helper-test-abs'))).toBe(s32Abs('tests/.tmp/axe-helper-test-abs'));
      process.env.AXE_COLLECT_DIR = 'tests/fixtures';
      expect(() => resolveCollectDir()).toThrow(/outside tests\/\.tmp/);
      delete process.env.AXE_COLLECT_DIR;
      for (const bad of ['tests/fixtures', 'tests/.tmp', 'tests/.tmp/../fixtures', '/tmp/x', 'tests', '.', '']) {
        expect(() => resolveCollectDir(bad)).toThrow();
      }
    } finally {
      if (saved === undefined) delete process.env.AXE_COLLECT_DIR;
      else process.env.AXE_COLLECT_DIR = saved;
    }
  });

  test('resetCollected: 기존 파일 제거 후 빈 디렉터리', () => {
    const d = dir();
    fs.mkdirSync(s32Abs(d), { recursive: true });
    fs.writeFileSync(path.join(s32Abs(d), 'stale.json'), '[]');
    const abs = resetCollected(d);
    expect(abs).toBe(s32Abs(d));
    expect(fs.readdirSync(abs)).toEqual([]);
    const fresh = dir();
    resetCollected(fresh);
    expect(fs.readdirSync(s32Abs(fresh))).toEqual([]);
    expect(() => resetCollected('tests/fixtures')).toThrow();
  });

  test('writeCollected: 10개 파일, 잘못된 scenario·조합 throw', () => {
    const d = dir();
    resetCollected(d);
    for (const [s, p] of S32_PAIRS) writeCollected(s, p, [V('image-alt', [`image-alt::#a::${s}`])], { dir: d });
    expect(fs.readdirSync(s32Abs(d)).sort()).toEqual(EXPECTED_FILES);
    const one = JSON.parse(fs.readFileSync(path.join(s32Abs(d), 'modal--desktop-dark.json'), 'utf8'));
    expect(one).toEqual({
      scenario: 'modal',
      project: 'desktop-dark',
      entries: [
        {
          key: 'modal:desktop-dark:image-alt',
          scenario: 'modal',
          project: 'desktop-dark',
          ruleId: 'image-alt',
          impact: 'serious',
          targets: ['image-alt::#a::modal'],
          selectors: [],
        },
      ],
    });
    expect(() => writeCollected('dialog', 'desktop-dark', [], { dir: d })).toThrow(/scenario/);
    expect(() => writeCollected('page', 'desktop-blue', [], { dir: d })).toThrow(/project/);
    expect(() => writeCollected('modal', 'mobile-dark', [], { dir: d })).toThrow(/unexpected/);
    expect(fs.readdirSync(s32Abs(d))).toHaveLength(10);
  });

  test('mergeCollected: 성공(key 정렬 7필드)·9개 missing·여분 extra', () => {
    const d = dir();
    resetCollected(d);
    for (const [s, p] of S32_PAIRS) {
      const vs =
        s === 'page' && p.startsWith('desktop')
          ? [V('image-alt', ['image-alt::#a::x'], ['#a img']), V('color-contrast', ['color-contrast::#career::x'], ['.k'])]
          : [];
      writeCollected(s, p, vs, { dir: d });
    }
    const out = `${d}/merged.json`;
    const merged = mergeCollected({ collectDir: d, out });
    expect(merged.map((e) => e.key)).toEqual([
      'page:desktop-dark:color-contrast',
      'page:desktop-dark:image-alt',
      'page:desktop-light:color-contrast',
      'page:desktop-light:image-alt',
    ]);
    for (const e of merged) {
      expect(Object.keys(e)).toEqual(['key', 'scenario', 'project', 'ruleId', 'impact', 'targets', 'selectors']);
    }
    expect(fs.readFileSync(s32Abs(out), 'utf8')).toBe(JSON.stringify(merged, null, 2) + '\n');
    fs.rmSync(s32Abs(out));

    fs.writeFileSync(path.join(s32Abs(d), 'page--extra-dark.json'), '{}');
    expect(() => mergeCollected({ collectDir: d })).toThrow(/extra:page--extra-dark\.json/);
    fs.rmSync(path.join(s32Abs(d), 'page--extra-dark.json'));

    fs.rmSync(path.join(s32Abs(d), 'lightbox--desktop-light.json'));
    let err;
    try {
      mergeCollected({ collectDir: d, out: `${d}/never.json` });
    } catch (e) {
      err = e;
    }
    expect(err).toBeTruthy();
    expect(err.problems).toEqual(['missing:lightbox--desktop-light.json']);
    expect(fs.existsSync(s32Abs(`${d}/never.json`))).toBe(false);
  });

  test('CLI: --reset 0, --merge 0, 9개 1, --dir tests/fixtures 1', async () => {
    const d = dir();
    const r0 = await s32Cli(['--reset', '--dir', d]);
    expect(r0.code).toBe(0);
    expect(fs.readdirSync(s32Abs(d))).toEqual([]);
    for (const [s, p] of S32_PAIRS) writeCollected(s, p, [], { dir: d });
    const out = `${d}/merged.json`;
    const m0 = await s32Cli(['--merge', '--dir', d, '--out', out]);
    expect(m0.code).toBe(0);
    expect(fs.readFileSync(s32Abs(out), 'utf8')).toBe('[]\n');
    fs.rmSync(s32Abs(out));
    fs.rmSync(path.join(s32Abs(d), 'page--mobile-dark.json'));
    const m1 = await s32Cli(['--merge', '--dir', d, '--out', out]);
    expect(m1.code).toBe(1);
    expect(m1.stderr).toContain('missing:page--mobile-dark.json');
    expect(fs.existsSync(s32Abs(out))).toBe(false);
    const f1 = await s32Cli(['--merge', '--dir', 'tests/fixtures', '--out', out]);
    expect(f1.code).toBe(1);
    const f2 = await s32Cli(['--reset', '--dir', 'tests/fixtures']);
    expect(f2.code).toBe(1);
    const u = await s32Cli(['--bogus']);
    expect(u.code).toBe(1);
  });
});

// step 33 — axe baseline·regression (설계 §6.2 step 33·§6.4·§6.5 fixture)
import {
  BASELINE_PATH,
  COLLECTED_PATH,
  PLAN_PATH,
  FIX_FILES_BY_KIND,
  baselineExists,
  loadBaseline,
  resolveBaselineMode,
  validateBaseline,
  checkRegression,
  assertEmptyFile,
} from '../helpers/axe.js';

const T_CAREER = 'color-contrast::#career::## — Career';
const T_PROJECTS = 'color-contrast::#projects::## — Projects';
const T_HERO = 'aria-allowed-attr::#heroFeatured::대표 프로젝트';
const T_TOGGLE = 'target-size::#themeToggle::#';

const FIXTURE_OK = [
  {
    key: 'page:desktop-dark:aria-allowed-attr',
    scenario: 'page',
    project: 'desktop-dark',
    ruleId: 'aria-allowed-attr',
    impact: 'serious',
    targets: [T_HERO],
    selectors: ['#heroFeatured'],
    fixes: [{ target: T_HERO, fixKind: 'static-markup', fixFiles: ['index.html'], requiresColorChange: false }],
    fixFiles: ['index.html'],
  },
];
const FIXTURE_THEMES = [
  {
    key: 'page:desktop-dark:color-contrast',
    scenario: 'page',
    project: 'desktop-dark',
    ruleId: 'color-contrast',
    impact: 'serious',
    targets: [T_CAREER],
    selectors: ['#career .section-kicker'],
    fixes: [{ target: T_CAREER, fixKind: 'css-token', fixFiles: ['css/themes.css'], requiresColorChange: true }],
    fixFiles: ['css/themes.css'],
  },
];
const FIXTURE_RULE_PLAIN = [
  {
    key: 'page:desktop-dark:target-size',
    scenario: 'page',
    project: 'desktop-dark',
    ruleId: 'target-size',
    impact: 'serious',
    targets: [T_TOGGLE],
    selectors: ['#themeToggle'],
    fixes: [{ target: T_TOGGLE, fixKind: 'css-rule', fixFiles: ['css/style.css'], requiresColorChange: false }],
    fixFiles: ['css/style.css'],
  },
];
const FIXTURE_RULE_COLOR = [
  {
    ...FIXTURE_THEMES[0],
    fixes: [{ target: T_CAREER, fixKind: 'css-rule', fixFiles: ['css/style.css'], requiresColorChange: true }],
    fixFiles: ['css/style.css'],
  },
];
const FIXTURE_MIXED = [
  {
    key: 'page:desktop-dark:color-contrast',
    scenario: 'page',
    project: 'desktop-dark',
    ruleId: 'color-contrast',
    impact: 'serious',
    targets: [T_CAREER, T_PROJECTS],
    selectors: ['#career .section-kicker', '#projects .section-kicker'],
    fixes: [
      { target: T_CAREER, fixKind: 'css-rule', fixFiles: ['css/style.css'], requiresColorChange: true },
      { target: T_PROJECTS, fixKind: 'text-change', fixFiles: [], requiresColorChange: false },
    ],
    fixFiles: ['css/style.css'],
  },
];
const FIXTURE_COLOR_PLAIN = [...FIXTURE_RULE_COLOR, ...FIXTURE_RULE_PLAIN];

const clone = (x) => structuredClone(x);
// fixture를 복제해 entry 0 / fix 0을 고친 baseline.
const themesWith = (fn) => {
  const b = clone(FIXTURE_THEMES);
  fn(b[0], b[0].fixes[0]);
  return b;
};
const okWith = (fn) => {
  const b = clone(FIXTURE_OK);
  fn(b[0], b[0].fixes[0]);
  return b;
};
const BAD_RCC = ['baseline[0].fixes[0]: bad-requiresColorChange'];

let s33Seq = 0;
function s33Dir() {
  s33Seq += 1;
  const rel = `tests/.tmp/axe-helper-s33-${process.pid}-${s33Seq}`;
  fs.mkdirSync(path.join(S32_REPO, rel), { recursive: true });
  return rel;
}

test.describe('step 33 axe-baseline-regression', () => {
  let before;
  const made = [];
  const dir = () => {
    const d = s33Dir();
    made.push(d);
    return d;
  };

  test.beforeEach(async ({}, testInfo) => {
    test.skip(testInfo.project.name !== 'desktop-dark', 'desktop-dark 전용');
    before = s32State();
  });

  test.afterEach(async ({}, testInfo) => {
    if (testInfo.project.name !== 'desktop-dark') return;
    for (const d of made.splice(0)) fs.rmSync(path.join(S32_REPO, d), { recursive: true, force: true });
    expect(s32State()).toEqual(before);
  });

  test('경로 상수·FIX_FILES_BY_KIND', () => {
    expect(BASELINE_PATH).toBe('tests/fixtures/axe-baseline.json');
    expect(COLLECTED_PATH).toBe('tests/fixtures/axe-collected.json');
    expect(PLAN_PATH).toBe('tests/fixtures/axe-remediation-plan.json');
    expect(FIX_FILES_BY_KIND).toEqual({
      'css-token': ['css/themes.css'],
      'css-rule': ['css/style.css'],
      'js-render': ['js/main.js'],
      'static-markup': ['index.html'],
      'text-change': [],
    });
    expect(Object.isFrozen(FIX_FILES_BY_KIND)).toBe(true);
  });

  test('validateBaseline 통과 []: §6.5 fixture 6개·빈 배열·text-change만 entry', () => {
    for (const b of [FIXTURE_THEMES, FIXTURE_OK, FIXTURE_RULE_PLAIN, FIXTURE_RULE_COLOR, FIXTURE_MIXED, FIXTURE_COLOR_PLAIN, []]) {
      const snapshot = clone(b);
      expect(validateBaseline(b)).toEqual([]);
      expect(b).toEqual(snapshot);
    }
    const textOnly = okWith((e, f) => {
      f.fixKind = 'text-change';
      f.fixFiles = [];
      f.requiresColorChange = false;
      e.fixFiles = [];
    });
    expect(validateBaseline(textOnly)).toEqual([]);
  });

  test('validateBaseline §6.4 오류 예 A·B·C·D·E', () => {
    expect(validateBaseline(themesWith((e) => (e.note = 'x')))).toEqual(['baseline[0]: fields missing=[] extra=[note]']);
    expect(validateBaseline(themesWith((e, f) => (f.fixKind = 'css-rule')))).toEqual([
      'baseline[0].fixes[0]: fixFiles-mismatch',
    ]);
    expect(validateBaseline(themesWith((e) => (e.fixFiles = ['css/style.css'])))).toEqual([
      'baseline[0]: fixFiles union-mismatch',
    ]);
    expect(validateBaseline(themesWith((e, f) => (f.requiresColorChange = false)))).toEqual(BAD_RCC);
    expect(validateBaseline(themesWith((e, f) => delete f.requiresColorChange))).toEqual([
      'baseline[0].fixes[0]: fields missing=[requiresColorChange] extra=[]',
    ]);
  });

  test('validateBaseline requiresColorChange 추가 사례·fix extraField', () => {
    expect(validateBaseline(themesWith((e, f) => (f.requiresColorChange = 'yes')))).toEqual(BAD_RCC);
    expect(validateBaseline(themesWith((e, f) => (f.requiresColorChange = null)))).toEqual(BAD_RCC);
    expect(validateBaseline(okWith((e, f) => (f.requiresColorChange = true)))).toEqual(BAD_RCC);
    const jsRender = okWith((e, f) => {
      f.fixKind = 'js-render';
      f.fixFiles = ['js/main.js'];
      f.requiresColorChange = true;
      e.fixFiles = ['js/main.js'];
    });
    expect(validateBaseline(jsRender)).toEqual(BAD_RCC);
    const textTrue = okWith((e, f) => {
      f.fixKind = 'text-change';
      f.fixFiles = [];
      f.requiresColorChange = true;
      e.fixFiles = [];
    });
    expect(validateBaseline(textTrue)).toEqual(BAD_RCC);
    expect(validateBaseline(themesWith((e, f) => (f.requiresColorChange = false)))).toEqual(BAD_RCC);
    expect(validateBaseline(themesWith((e, f) => (f.extraField = 1)))).toEqual([
      'baseline[0].fixes[0]: fields missing=[] extra=[extraField]',
    ]);
  });

  test('validateBaseline 그 밖 오류 각 한 항목', () => {
    expect(validateBaseline({})).toEqual(['baseline: not-array']);
    expect(validateBaseline([null])).toEqual(['baseline[0]: not-object']);
    expect(validateBaseline(themesWith((e) => delete e.impact))).toEqual([
      'baseline[0]: fields missing=[impact] extra=[]',
    ]);
    expect(validateBaseline(themesWith((e) => (e.scenario = 'dialog')))).toEqual(['baseline[0]: bad-scenario']);
    expect(validateBaseline(themesWith((e) => (e.project = 'desktop-blue')))).toEqual(['baseline[0]: bad-project']);
    expect(validateBaseline(themesWith((e) => (e.ruleId = 'a:b')))).toEqual(['baseline[0]: bad-ruleId']);
    expect(validateBaseline(themesWith((e) => (e.key = 'page:desktop-dark:image-alt')))).toEqual([
      'baseline[0]: key-mismatch',
    ]);
    expect(validateBaseline(themesWith((e) => (e.impact = 'minor')))).toEqual(['baseline[0]: bad-impact']);
    expect(
      validateBaseline(
        themesWith((e) => {
          e.targets = [];
          e.fixes = [];
          e.fixFiles = [];
        }),
      ),
    ).toEqual(['baseline[0]: targets empty']);
    expect(
      validateBaseline(
        themesWith((e, f) => {
          e.targets = [T_CAREER, T_CAREER];
          e.fixes = [f, clone(f)];
        }),
      ),
    ).toEqual(['baseline[0]: targets duplicate']);
    const unsorted = clone(FIXTURE_MIXED);
    unsorted[0].targets.reverse();
    unsorted[0].fixes.reverse();
    expect(validateBaseline(unsorted)).toEqual(['baseline[0]: targets unsorted']);
    const selUnsorted = clone(FIXTURE_MIXED);
    selUnsorted[0].selectors.reverse();
    expect(validateBaseline(selUnsorted)).toEqual(['baseline[0]: selectors unsorted']);
    expect(validateBaseline(themesWith((e) => (e.fixes = [])))).toEqual(['baseline[0]: fixes count']);
    expect(validateBaseline(themesWith((e, f) => (f.target = T_PROJECTS)))).toEqual([
      'baseline[0].fixes[0]: target-mismatch',
    ]);
    // fixKind가 유효하지 않으면 fixFiles·kind별 requiresColorChange 판정 생략
    expect(validateBaseline(themesWith((e, f) => (f.fixKind = 'css-magic')))).toEqual([
      'baseline[0].fixes[0]: bad-fixKind',
    ]);
    expect(
      validateBaseline(
        themesWith((e, f) => {
          f.fixKind = 'css-magic';
          f.requiresColorChange = false;
        }),
      ),
    ).toEqual(['baseline[0].fixes[0]: bad-fixKind']);
    expect(validateBaseline([...clone(FIXTURE_THEMES), ...clone(FIXTURE_THEMES)])).toEqual([
      'baseline: duplicate-key page:desktop-dark:color-contrast',
    ]);
    expect(validateBaseline([...clone(FIXTURE_RULE_PLAIN), ...clone(FIXTURE_RULE_COLOR)])).toEqual(['baseline: unsorted']);
  });

  test('checkRegression: 새 key·새 target 실패, 사라짐 허용, dark 전용 target → light new-key, 입력 불변', () => {
    const baseline = clone(FIXTURE_MIXED);
    const V33 = (ruleId, targets) => ({ ruleId, impact: 'serious', targets, selectors: [] });
    const violations = [V33('color-contrast', [T_CAREER]), V33('image-alt', ['image-alt::#a::x'])];
    const snapB = clone(baseline);
    const snapV = clone(violations);
    expect(checkRegression(violations, baseline, 'page', 'desktop-dark')).toEqual(['new-key:page:desktop-dark:image-alt']);
    expect(baseline).toEqual(snapB);
    expect(violations).toEqual(snapV);
    expect(
      checkRegression([V33('color-contrast', [T_CAREER, 'color-contrast::#about::x'])], baseline, 'page', 'desktop-dark'),
    ).toEqual(['new-target:page:desktop-dark:color-contrast:color-contrast::#about::x']);
    expect(checkRegression([], baseline, 'page', 'desktop-dark')).toEqual([]);
    expect(checkRegression([V33('color-contrast', [T_PROJECTS])], baseline, 'page', 'desktop-dark')).toEqual([]);
    expect(checkRegression([V33('color-contrast', [T_CAREER])], baseline, 'page', 'desktop-light')).toEqual([
      'new-key:page:desktop-light:color-contrast',
    ]);
    expect(checkRegression([V33('color-contrast', [T_CAREER])], baseline, 'modal', 'desktop-dark')).toEqual([
      'new-key:modal:desktop-dark:color-contrast',
    ]);
  });

  test('resolveBaselineMode·baselineExists·loadBaseline', () => {
    const d = dir();
    const p = (f) => `${d}/${f}`;
    const write = (f, s) => fs.writeFileSync(path.join(S32_REPO, p(f)), s);
    const opts = { baselinePath: p('baseline.json'), collectedPath: p('collected.json'), planPath: p('plan.json') };
    const saved = process.env.AXE_ALLOW_MISSING_BASELINE;
    try {
      delete process.env.AXE_ALLOW_MISSING_BASELINE;
      expect(baselineExists(opts.baselinePath)).toBe(false);
      expect(() => resolveBaselineMode(opts)).toThrow();
      process.env.AXE_ALLOW_MISSING_BASELINE = '1';
      expect(() => resolveBaselineMode(opts)).toThrow();
      delete process.env.AXE_ALLOW_MISSING_BASELINE;
      write('collected.json', '[]\n');
      expect(resolveBaselineMode(opts)).toBe('pending');
      write('plan.json', '{"groups":[]}\n');
      expect(() => resolveBaselineMode(opts)).toThrow();
      write('baseline.json', '[]\n');
      expect(baselineExists(opts.baselinePath)).toBe(true);
      expect(resolveBaselineMode(opts)).toBe('check');
    } finally {
      if (saved === undefined) delete process.env.AXE_ALLOW_MISSING_BASELINE;
      else process.env.AXE_ALLOW_MISSING_BASELINE = saved;
    }
    expect(loadBaseline(p('baseline.json'))).toEqual([]);
    write('ok.json', JSON.stringify(FIXTURE_THEMES));
    expect(loadBaseline(p('ok.json'))).toEqual(FIXTURE_THEMES);
    expect(() => loadBaseline(p('missing.json'))).toThrow();
    write('broken.json', '[{');
    expect(() => loadBaseline(p('broken.json'))).toThrow();
    write('obj.json', '{}');
    expect(() => loadBaseline(p('obj.json'))).toThrow();
  });

  test('assertEmptyFile·CLI --assert-empty: [] 0, [{}]·{}·깨짐·없음 1', async () => {
    const d = dir();
    const cases = [
      ['empty.json', '[]\n', 0],
      ['one.json', '[{}]\n', 1],
      ['obj.json', '{}\n', 1],
      ['broken.json', '[', 1],
      ['missing.json', null, 1],
    ];
    for (const [f, body, code] of cases) {
      const rel = `${d}/${f}`;
      if (body !== null) fs.writeFileSync(path.join(S32_REPO, rel), body);
      if (code === 0) expect(() => assertEmptyFile(rel)).not.toThrow();
      else expect(() => assertEmptyFile(rel)).toThrow();
      const r = await s32Cli(['--assert-empty', '--baseline', rel]);
      expect(r.code, f).toBe(code);
    }
  });
});
