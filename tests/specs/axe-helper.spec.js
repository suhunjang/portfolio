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

// step 34 — axe baseline projection (설계 §6.2 step 34): PROJECTION_FIELDS · projectEntry ·
// compareCollectedBaseline · CLI --check-baseline-match
import { PROJECTION_FIELDS, projectEntry, compareCollectedBaseline } from '../helpers/axe.js';

const S34_KEY_A = 'page:desktop-dark:aria-allowed-attr';
const S34_KEY_B = 'page:desktop-dark:color-contrast';
const T_EXTRA = 'color-contrast::#about::About';
// 같은 entry 2개 기준 baseline(§6.4 strict fix 포함) = FIXTURE_OK ∪ FIXTURE_RULE_COLOR(css-rule → rcc true/false 모두 유효).
const S34_BASELINE = [...FIXTURE_OK, ...FIXTURE_RULE_COLOR];
const s34Collected = (b = S34_BASELINE) => b.map((e) => projectEntry(e));
const S34_EMPTY = { ok: true, missingEntries: [], extraEntries: [], missingTargets: [], extraTargets: [], fieldMismatches: [] };
const s34Result = (over) => ({ ...S34_EMPTY, ok: false, ...over });

let s34Seq = 0;
function s34Dir() {
  s34Seq += 1;
  const rel = `tests/.tmp/axe-helper-s34-${process.pid}-${s34Seq}`;
  fs.mkdirSync(path.join(S32_REPO, rel), { recursive: true });
  return rel;
}

test.describe('step 34 axe-baseline-projection', () => {
  let before;
  const made = [];
  const dir = () => {
    const d = s34Dir();
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

  test('PROJECTION_FIELDS·projectEntry: 정확히 7필드, fixes·fixFiles·requiresColorChange 없음', () => {
    expect(PROJECTION_FIELDS).toEqual(['key', 'scenario', 'project', 'ruleId', 'impact', 'targets', 'selectors']);
    expect(validateBaseline(S34_BASELINE)).toEqual([]);
    const snapshot = clone(S34_BASELINE);
    const p = projectEntry(S34_BASELINE[1]);
    expect(Object.keys(p)).toEqual(PROJECTION_FIELDS);
    expect(p).not.toHaveProperty('fixes');
    expect(p).not.toHaveProperty('fixFiles');
    expect(p).not.toHaveProperty('requiresColorChange');
    expect(JSON.stringify(p)).not.toContain('requiresColorChange');
    expect(p).toEqual({
      key: S34_KEY_B,
      scenario: 'page',
      project: 'desktop-dark',
      ruleId: 'color-contrast',
      impact: 'serious',
      targets: [T_CAREER],
      selectors: ['#career .section-kicker'],
    });
    expect(S34_BASELINE).toEqual(snapshot);
    // targets·selectors 정렬·중복 제거, 입력 불변
    const messy = { ...p, targets: [T_PROJECTS, T_CAREER, T_PROJECTS], selectors: ['b', 'a', 'b'] };
    const messySnap = clone(messy);
    expect(projectEntry(messy)).toEqual({ ...p, targets: [T_CAREER, T_PROJECTS], selectors: ['a', 'b'] });
    expect(messy).toEqual(messySnap);
    // 누락·key 불일치 throw
    for (const f of PROJECTION_FIELDS) {
      const e = clone(p);
      delete e[f];
      expect(() => projectEntry(e), f).toThrow();
    }
    expect(() => projectEntry({ ...p, key: 'page:desktop-light:color-contrast' })).toThrow();
    expect(() => projectEntry(null)).toThrow();
  });

  test('compareCollectedBaseline: 같음 ok·다섯 []; requiresColorChange true↔false만 바꿔도 동일', () => {
    const collected = s34Collected();
    const cSnap = clone(collected);
    const bSnap = clone(S34_BASELINE);
    expect(compareCollectedBaseline(collected, S34_BASELINE)).toEqual(S34_EMPTY);
    expect(collected).toEqual(cSnap);
    expect(S34_BASELINE).toEqual(bSnap);
    const flipped = clone(S34_BASELINE);
    expect(flipped[1].fixes[0].requiresColorChange).toBe(true);
    flipped[1].fixes[0].requiresColorChange = false;
    expect(validateBaseline(flipped)).toEqual([]);
    expect(compareCollectedBaseline(collected, flipped)).toEqual(S34_EMPTY);
    expect(compareCollectedBaseline(collected, S34_BASELINE)).toEqual(compareCollectedBaseline(collected, flipped));
  });

  test('compareCollectedBaseline 불일치 5종·중복 throw', () => {
    const collected = s34Collected();
    // collected에만 entry
    expect(compareCollectedBaseline(collected, S34_BASELINE.slice(1))).toEqual(s34Result({ missingEntries: [S34_KEY_A] }));
    // baseline에만 entry
    expect(compareCollectedBaseline(collected.slice(1), S34_BASELINE)).toEqual(s34Result({ extraEntries: [S34_KEY_A] }));
    // collected target 추가
    const cMore = clone(collected);
    cMore[1].targets.push(T_EXTRA);
    expect(compareCollectedBaseline(cMore, S34_BASELINE)).toEqual(
      s34Result({ missingTargets: [{ key: S34_KEY_B, target: T_EXTRA }] }),
    );
    // baseline target 추가
    const bMore = clone(S34_BASELINE);
    bMore[1].targets.push(T_EXTRA);
    expect(compareCollectedBaseline(collected, bMore)).toEqual(
      s34Result({ extraTargets: [{ key: S34_KEY_B, target: T_EXTRA }] }),
    );
    // impact 다름
    const cImpact = clone(collected);
    cImpact[0].impact = 'critical';
    expect(compareCollectedBaseline(cImpact, S34_BASELINE)).toEqual(
      s34Result({ fieldMismatches: [{ key: S34_KEY_A, field: 'impact' }] }),
    );
    // selectors 다름
    const cSel = clone(collected);
    cSel[1].selectors = ['#career'];
    expect(compareCollectedBaseline(cSel, S34_BASELINE)).toEqual(
      s34Result({ fieldMismatches: [{ key: S34_KEY_B, field: 'selectors' }] }),
    );
    // key 중복 throw
    expect(() => compareCollectedBaseline([...collected, collected[0]], S34_BASELINE)).toThrow();
    expect(() => compareCollectedBaseline(collected, [...S34_BASELINE, S34_BASELINE[1]])).toThrow();
  });

  test('CLI --check-baseline-match: 일치 0, 5종 불일치 1·정확한 줄, 파일 없음·JSON 오류 1', async () => {
    const d = dir();
    const write = (f, data) => {
      const rel = `${d}/${f}`;
      fs.writeFileSync(path.join(S32_REPO, rel), typeof data === 'string' ? data : JSON.stringify(data, null, 2) + '\n');
      return rel;
    };
    const base = write('baseline.json', S34_BASELINE);
    const run = (collected, baseline = base) =>
      s32Cli(['--check-baseline-match', '--collected', collected, '--baseline', baseline]);

    const ok = await run(write('ok.json', s34Collected()));
    expect(ok.code).toBe(0);
    expect(ok.stdout).toBe('baseline-match: OK\n');
    expect(ok.stderr).toBe('');

    const flippedBase = clone(S34_BASELINE);
    flippedBase[1].fixes[0].requiresColorChange = false;
    const flippedRun = await run(write('ok2.json', s34Collected()), write('flipped.json', flippedBase));
    expect(flippedRun.code).toBe(0);
    expect(flippedRun.stdout).toBe('baseline-match: OK\n');

    const collected = s34Collected();
    const cMore = clone(collected);
    cMore[1].targets.push(T_EXTRA);
    const bMore = clone(S34_BASELINE);
    bMore[1].targets.push(T_EXTRA);
    const cImpact = clone(collected);
    cImpact[0].impact = 'critical';
    const cSel = clone(collected);
    cSel[1].selectors = ['#career'];
    const cases = [
      ['missing-entry', collected, S34_BASELINE.slice(1), `missing-entry:${S34_KEY_A}\n`],
      ['extra-entry', collected.slice(1), S34_BASELINE, `extra-entry:${S34_KEY_A}\n`],
      ['missing-target', cMore, S34_BASELINE, `missing-target:${S34_KEY_B}|${T_EXTRA}\n`],
      ['extra-target', collected, bMore, `extra-target:${S34_KEY_B}|${T_EXTRA}\n`],
      ['field-mismatch-impact', cImpact, S34_BASELINE, `field-mismatch:${S34_KEY_A}|impact\n`],
      ['field-mismatch-selectors', cSel, S34_BASELINE, `field-mismatch:${S34_KEY_B}|selectors\n`],
    ];
    for (const [name, c, b, line] of cases) {
      const r = await run(write(`${name}-c.json`, c), write(`${name}-b.json`, b));
      expect(r.code, name).toBe(1);
      expect(r.stderr, name).toBe(line);
      expect(r.stdout, name).toBe('');
    }

    // 여러 종류가 섞이면 missing-entry → extra-entry → missing-target → extra-target → field-mismatch 순서
    const mixC = [
      { ...collected[0], key: 'page:mobile-dark:aria-allowed-attr', project: 'mobile-dark' },
      { ...collected[1], targets: [T_EXTRA], selectors: ['#x'] },
    ];
    const mix = await run(write('mix-c.json', mixC), base);
    expect(mix.code).toBe(1);
    expect(mix.stderr).toBe(
      [
        'missing-entry:page:mobile-dark:aria-allowed-attr',
        `extra-entry:${S34_KEY_A}`,
        `missing-target:${S34_KEY_B}|${T_EXTRA}`,
        `extra-target:${S34_KEY_B}|${T_CAREER}`,
        `field-mismatch:${S34_KEY_B}|selectors`,
        '',
      ].join('\n'),
    );

    // collected 없음·baseline JSON 오류 → 1
    const missing = await run(`${d}/nope.json`);
    expect(missing.code).toBe(1);
    expect(missing.stdout).toBe('');
    const broken = await run(write('c3.json', s34Collected()), write('broken.json', '[{'));
    expect(broken.code).toBe(1);
    expect(broken.stdout).toBe('');
  });
});

// step 35 — axe-remediation-plan-schema (§6.2 step 35·§6.5)
import { GROUP_ID_RE, loadPlan, requiredBlockReason, validateRemediationPlan } from '../helpers/axe.js';

const S35_KEY_OK = 'page:desktop-dark:aria-allowed-attr';
const S35_KEY_CC = 'page:desktop-dark:color-contrast';
const S35_KEY_TS = 'page:desktop-dark:target-size';
const R_COLOR = 'color change excluded (HOO-81 §16.3)';
const R_TEXT = 'text change excluded';
const R_BOTH = `${R_TEXT}; ${R_COLOR}`;
const pt = (key, target) => ({ key, target });
const group = (over) => ({
  id: 'g',
  targets: [],
  fixFiles: [],
  difficulty: 'low',
  estMinutes: 6,
  blocked: false,
  reason: '',
  ...over,
});
const PLAN_OK = {
  groups: [group({ id: 'hero-featured-aria', targets: [pt(S35_KEY_OK, T_HERO)], fixFiles: ['index.html'] })],
};
const planOkWith = (fn) => {
  const p = clone(PLAN_OK);
  fn(p.groups[0], p);
  return p;
};
const themesPlan = (blocked, reason) => ({
  groups: [
    group({
      id: 'career-kicker-contrast',
      targets: [pt(S35_KEY_CC, T_CAREER)],
      fixFiles: ['css/themes.css'],
      estMinutes: 5,
      blocked,
      reason,
    }),
  ],
});
const rulePlainPlan = (blocked, reason) => ({
  groups: [group({ id: 'theme-toggle-size', targets: [pt(S35_KEY_TS, T_TOGGLE)], fixFiles: ['css/style.css'], blocked, reason })],
});
const ruleColorPlan = (blocked, reason) => ({
  groups: [
    group({
      id: 'career-kicker-rule',
      targets: [pt(S35_KEY_CC, T_CAREER)],
      fixFiles: ['css/style.css'],
      estMinutes: 5,
      blocked,
      reason,
    }),
  ],
});
const mixedPlan = (blocked, reason) => ({
  groups: [
    group({
      id: 'kicker-mixed',
      targets: [pt(S35_KEY_CC, T_CAREER), pt(S35_KEY_CC, T_PROJECTS)],
      fixFiles: ['css/style.css'],
      blocked,
      reason,
    }),
  ],
});

let s35Seq = 0;
function s35Dir() {
  s35Seq += 1;
  const rel = `tests/.tmp/axe-helper-s35-${process.pid}-${s35Seq}`;
  fs.mkdirSync(path.join(S32_REPO, rel), { recursive: true });
  return rel;
}

test.describe('step 35 axe-remediation-plan-schema', () => {
  let before;
  const made = [];
  const dir = () => {
    const d = s35Dir();
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

  test('fixture 상수는 모두 validateBaseline → []', () => {
    for (const b of [FIXTURE_OK, FIXTURE_THEMES, FIXTURE_RULE_PLAIN, FIXTURE_RULE_COLOR, FIXTURE_MIXED, FIXTURE_COLOR_PLAIN]) {
      expect(validateBaseline(b)).toEqual([]);
    }
  });

  test('requiredBlockReason: 조각·순서·무시·입력 불변', () => {
    expect(requiredBlockReason([pt(S35_KEY_OK, T_HERO)], FIXTURE_OK)).toBe('');
    expect(requiredBlockReason([pt(S35_KEY_CC, T_CAREER)], FIXTURE_THEMES)).toBe(R_COLOR);
    expect(requiredBlockReason([pt(S35_KEY_TS, T_TOGGLE)], FIXTURE_RULE_PLAIN)).toBe('');
    expect(requiredBlockReason([pt(S35_KEY_CC, T_CAREER)], FIXTURE_RULE_COLOR)).toBe(R_COLOR);
    expect(requiredBlockReason([pt(S35_KEY_CC, T_CAREER), pt(S35_KEY_CC, T_PROJECTS)], FIXTURE_MIXED)).toBe(R_BOTH);
    // 입력 순서가 달라도 조각 순서는 text → color
    expect(requiredBlockReason([pt(S35_KEY_CC, T_PROJECTS), pt(S35_KEY_CC, T_CAREER)], FIXTURE_MIXED)).toBe(R_BOTH);
    expect(requiredBlockReason([pt(S35_KEY_CC, T_PROJECTS)], FIXTURE_MIXED)).toBe(R_TEXT);
    expect(requiredBlockReason([pt(S35_KEY_CC, T_CAREER)], FIXTURE_MIXED)).toBe(R_COLOR);
    expect(requiredBlockReason([pt(S35_KEY_TS, T_TOGGLE)], FIXTURE_COLOR_PLAIN)).toBe('');
    expect(requiredBlockReason([], FIXTURE_MIXED)).toBe('');
    // baseline에 없는 target 무시
    expect(requiredBlockReason([pt(S35_KEY_CC, 'color-contrast::#about::About')], FIXTURE_MIXED)).toBe('');
    expect(requiredBlockReason([pt(S35_KEY_OK, T_HERO)], FIXTURE_THEMES)).toBe('');
    expect(requiredBlockReason([pt(S35_KEY_OK, T_HERO), pt(S35_KEY_CC, T_CAREER)], FIXTURE_THEMES)).toBe(R_COLOR);
    // 입력 불변
    const gts = [pt(S35_KEY_CC, T_PROJECTS), pt(S35_KEY_CC, T_CAREER)];
    const gSnap = clone(gts);
    const bSnap = clone(FIXTURE_MIXED);
    requiredBlockReason(gts, FIXTURE_MIXED);
    expect(gts).toEqual(gSnap);
    expect(FIXTURE_MIXED).toEqual(bSnap);
  });

  test('FIXTURE_OK: 정상·오류 예·id·중복·정렬·PlanTarget·필드 값 오류', () => {
    const v = (plan, opts) => validateRemediationPlan(plan, FIXTURE_OK, opts);
    const planSnap = clone(PLAN_OK);
    const baseSnap = clone(FIXTURE_OK);
    expect(v(PLAN_OK)).toEqual([]);
    expect(v(PLAN_OK, { coverage: true })).toEqual([]);
    expect(PLAN_OK).toEqual(planSnap);
    expect(FIXTURE_OK).toEqual(baseSnap);
    // §6.5 오류 예 2종
    expect(v(planOkWith((g) => (g.targets[0] = T_HERO)))).toEqual(['groups[0].targets[0]: not-object']);
    expect(v(planOkWith((g) => (g.blocked = true)))).toEqual(['groups[0]: reason-required']);

    // GROUP_ID_RE·id
    expect(GROUP_ID_RE.source).toBe('^[a-z0-9]+(?:-[a-z0-9]+)*$');
    for (const id of ['color-token-1', 'a', 'x2']) {
      expect(GROUP_ID_RE.test(id), id).toBe(true);
      expect(v(planOkWith((g) => (g.id = id))), id).toEqual([]);
    }
    for (const id of ['Group-1', 'a--b', '-a', 'a-', 'a_b', '']) {
      expect(GROUP_ID_RE.test(id), id).toBe(false);
      expect(v(planOkWith((g) => (g.id = id))), id).toEqual(['groups[0]: bad-id']);
    }

    // plan 수준: 중복 id·정렬(두 번째 그룹은 targets 빈 배열)
    const g0 = PLAN_OK.groups[0];
    const twoGroups = (ids) => ({ groups: ids.map((id, i) => ({ ...clone(g0), id, targets: i === 0 ? clone(g0.targets) : [] })) });
    expect(v(twoGroups(['a', 'a']))).toEqual(['groups[1]: targets empty', 'plan: duplicate-id a']);
    expect(v(twoGroups(['b', 'a']))).toEqual(['groups[1]: targets empty', 'plan: groups unsorted']);

    // PlanTarget 여분·누락 필드
    expect(v(planOkWith((g) => (g.targets[0].x = 1)))).toEqual(['groups[0].targets[0]: fields missing=[] extra=[x]']);
    expect(v(planOkWith((g) => delete g.targets[0].target))).toEqual([
      'groups[0].targets[0]: fields missing=[target] extra=[]',
    ]);
    // unknown-target
    expect(v(planOkWith((g) => (g.targets[0].target = 'aria-allowed-attr::#nope::x')))).toEqual([
      'groups[0].targets[0]: unknown-target',
    ]);
    expect(v(planOkWith((g) => (g.targets[0].key = 'page:desktop-light:aria-allowed-attr')))).toEqual([
      'groups[0].targets[0]: unknown-target',
    ]);
    // 그룹 내 중복·정렬
    expect(v(planOkWith((g) => g.targets.push(clone(g.targets[0]))))).toEqual(['groups[0]: targets duplicate']);
    const unsorted = mixedPlan(true, R_BOTH);
    unsorted.groups[0].targets.reverse();
    expect(validateRemediationPlan(unsorted, FIXTURE_MIXED)).toEqual(['groups[0]: targets unsorted']);
    // 두 그룹 중복
    const multi = { groups: [clone(g0), { ...clone(g0), id: 'hero-featured-aria-2' }] };
    expect(v(multi)).toEqual([`plan: target-in-multiple-groups ${S35_KEY_OK}|${T_HERO}`]);

    // 필드 값 오류
    expect(v(planOkWith((g) => (g.fixFiles = ['css/style.css'])))).toEqual(['groups[0]: fixFiles-mismatch']);
    expect(v(planOkWith((g) => (g.fixFiles = [])))).toEqual(['groups[0]: fixFiles-mismatch']);
    expect(v(planOkWith((g) => (g.difficulty = 'easy')))).toEqual(['groups[0]: bad-difficulty']);
    for (const m of [0, 21, 1.5, '6']) {
      expect(v(planOkWith((g) => (g.estMinutes = m))), String(m)).toEqual(['groups[0]: bad-estMinutes']);
    }
    for (const m of [1, 20]) expect(v(planOkWith((g) => (g.estMinutes = m))), String(m)).toEqual([]);
    expect(v(planOkWith((g) => (g.blocked = 'false')))).toEqual(['groups[0]: bad-blocked']);
    expect(v(planOkWith((g) => (g.reason = 'x')))).toEqual(['groups[0]: reason-must-be-empty']);
    expect(v(planOkWith((g) => (g.targets = [])))).toEqual(['groups[0]: targets empty']);
    expect(v(planOkWith((g) => (g.note = 'x')))).toEqual(['groups[0]: fields missing=[] extra=[note]']);
    expect(v({ groups: [null] })).toEqual(['groups[0]: not-object']);

    // plan 형태
    expect(v(null)).toEqual(['plan: not-object']);
    expect(v([])).toEqual(['plan: not-object']);
    expect(v({ groups: [], x: 1 })).toEqual(['plan: fields missing=[] extra=[x]']);
    expect(v({})).toEqual(['plan: fields missing=[groups] extra=[]']);
    expect(v({ groups: {} })).toEqual(['plan: groups not-array']);

    // coverage·requireEmpty
    expect(v({ groups: [] })).toEqual([]);
    expect(v({ groups: [] }, { coverage: true })).toEqual([
      'plan: uncovered page:desktop-dark:aria-allowed-attr|aria-allowed-attr::#heroFeatured::대표 프로젝트',
    ]);
    expect(v({ groups: [] }, { requireEmpty: true })).toEqual([]);
    expect(v(PLAN_OK, { requireEmpty: true })).toEqual(['groups: expected empty, got 1']);
    expect(PLAN_OK).toEqual(planSnap);
  });

  test('FIXTURE_THEMES·RULE_PLAIN·RULE_COLOR·MIXED: blocked·reason', () => {
    const v = validateRemediationPlan;
    expect(v(themesPlan(false, ''), FIXTURE_THEMES)).toEqual(['groups[0]: blocked-required']);
    expect(v(themesPlan(true, R_COLOR), FIXTURE_THEMES)).toEqual([]);
    expect(v(themesPlan(true, R_COLOR), FIXTURE_THEMES, { coverage: true })).toEqual([]);
    expect(v(themesPlan(true, 'x'), FIXTURE_THEMES)).toEqual(['groups[0]: reason-mismatch']);
    expect(v(themesPlan(true, ''), FIXTURE_THEMES)).toEqual(['groups[0]: reason-required']);

    expect(v(rulePlainPlan(false, ''), FIXTURE_RULE_PLAIN)).toEqual([]);
    expect(v(rulePlainPlan(true, 'manual hold'), FIXTURE_RULE_PLAIN)).toEqual([]);
    expect(v(rulePlainPlan(true, ''), FIXTURE_RULE_PLAIN)).toEqual(['groups[0]: reason-required']);

    expect(v(ruleColorPlan(false, ''), FIXTURE_RULE_COLOR)).toEqual(['groups[0]: blocked-required']);
    expect(v(ruleColorPlan(true, R_COLOR), FIXTURE_RULE_COLOR)).toEqual([]);

    expect(v(mixedPlan(true, R_BOTH), FIXTURE_MIXED)).toEqual([]);
    expect(v(mixedPlan(true, R_BOTH), FIXTURE_MIXED, { coverage: true })).toEqual([]);
    expect(v(mixedPlan(true, R_COLOR), FIXTURE_MIXED)).toEqual(['groups[0]: reason-mismatch']);
    expect(v(mixedPlan(false, ''), FIXTURE_MIXED)).toEqual(['groups[0]: blocked-required']);

    // FIXTURE_COLOR_PLAIN: 두 그룹, target-size 그룹은 blocked 불필요
    const cp = { groups: [...ruleColorPlan(true, R_COLOR).groups, ...rulePlainPlan(false, '').groups] };
    expect(v(cp, FIXTURE_COLOR_PLAIN, { coverage: true })).toEqual([]);
    expect(v(rulePlainPlan(false, ''), FIXTURE_COLOR_PLAIN, { coverage: true })).toEqual([
      `plan: uncovered ${S35_KEY_CC}|${T_CAREER}`,
    ]);
  });

  test('loadPlan·CLI --check-plan', async () => {
    const d = dir();
    const write = (name, data) => {
      const rel = `${d}/${name}`;
      fs.writeFileSync(path.join(S32_REPO, rel), typeof data === 'string' ? data : JSON.stringify(data, null, 2));
      return rel;
    };
    const run = (plan, baseline, extra = []) => s32Cli(['--check-plan', '--plan', plan, '--baseline', baseline, ...extra]);

    expect(loadPlan(write('lp.json', PLAN_OK))).toEqual(PLAN_OK);
    expect(() => loadPlan(`${d}/nope.json`)).toThrow();
    expect(() => loadPlan(write('lp-broken.json', '{'))).toThrow();

    const ok = await run(write('ok.json', PLAN_OK), write('b-ok.json', FIXTURE_OK));
    expect(ok.code).toBe(0);
    expect(ok.stdout).toBe('check-plan: OK\n');
    expect(ok.stderr).toBe('');
    expect((await run(`${d}/ok.json`, `${d}/b-ok.json`, ['--coverage'])).code).toBe(0);

    const bad = await run(write('bad.json', planOkWith((g) => (g.blocked = true))), `${d}/b-ok.json`);
    expect(bad.code).toBe(1);
    expect(bad.stderr).toBe('groups[0]: reason-required\n');
    expect(bad.stdout).toBe('');

    const themes = await run(write('themes.json', themesPlan(false, '')), write('b-themes.json', FIXTURE_THEMES));
    expect(themes.code).toBe(1);
    expect(themes.stderr).toBe('groups[0]: blocked-required\n');

    const rc = await run(write('rc.json', ruleColorPlan(false, '')), write('b-rc.json', FIXTURE_RULE_COLOR));
    expect(rc.code).toBe(1);
    expect(rc.stderr).toBe('groups[0]: blocked-required\n');

    const rp = await run(write('rp.json', rulePlainPlan(false, '')), write('b-rp.json', FIXTURE_RULE_PLAIN));
    expect(rp.code).toBe(0);
    expect(rp.stdout).toBe('check-plan: OK\n');

    const empty = await run(write('empty.json', { groups: [] }), `${d}/b-ok.json`, ['--require-empty']);
    expect(empty.code).toBe(0);
    const notEmpty = await run(`${d}/ok.json`, `${d}/b-ok.json`, ['--require-empty']);
    expect(notEmpty.code).toBe(1);
    expect(notEmpty.stderr).toBe('groups: expected empty, got 1\n');
    const uncovered = await run(`${d}/empty.json`, `${d}/b-ok.json`, ['--coverage']);
    expect(uncovered.code).toBe(1);
    expect(uncovered.stderr).toBe(`plan: uncovered ${S35_KEY_OK}|${T_HERO}\n`);

    const missing = await run(`${d}/nope.json`, `${d}/b-ok.json`);
    expect(missing.code).toBe(1);
    expect(missing.stdout).toBe('');
    const broken = await run(write('broken.json', '{"groups": ['), `${d}/b-ok.json`);
    expect(broken.code).toBe(1);
    expect(broken.stdout).toBe('');
  });
});

// step 36 — axe-plan-executable (§6.2 step 36)
import { validateRemediationExecutable } from '../helpers/axe.js';

const S36_HEAD = 'Harness 재계획 필요: 실행 불가 remediation 그룹';
// text-change 하나뿐인 baseline(requiresColorChange false, fixFiles [])
const FIXTURE_TEXT_ONLY = [
  {
    key: S35_KEY_CC,
    scenario: 'page',
    project: 'desktop-dark',
    ruleId: 'color-contrast',
    impact: 'serious',
    targets: [T_PROJECTS],
    selectors: ['#projects .section-kicker'],
    fixes: [{ target: T_PROJECTS, fixKind: 'text-change', fixFiles: [], requiresColorChange: false }],
    fixFiles: [],
  },
];
const textOnlyPlan = () => ({
  groups: [
    group({ id: 'projects-kicker-text', targets: [pt(S35_KEY_CC, T_PROJECTS)], fixFiles: [], blocked: true, reason: R_TEXT }),
  ],
});
const colorPlainPlan = () => ({ groups: [...ruleColorPlan(true, R_COLOR).groups, ...rulePlainPlan(false, '').groups] });

let s36Seq = 0;
function s36Dir() {
  s36Seq += 1;
  const rel = `tests/.tmp/axe-helper-s36-${process.pid}-${s36Seq}`;
  fs.mkdirSync(path.join(S32_REPO, rel), { recursive: true });
  return rel;
}

test.describe('step 36 axe-plan-executable', () => {
  let before;
  const made = [];
  const dir = () => {
    const d = s36Dir();
    made.push(d);
    return d;
  };
  // 전제: 모든 입력은 먼저 validateRemediationPlan → []
  const exec = (plan, baseline) => {
    expect(validateBaseline(baseline)).toEqual([]);
    expect(validateRemediationPlan(plan, baseline)).toEqual([]);
    return validateRemediationExecutable(plan, baseline);
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

  test('실행 가능 → [], blocked 그룹만 거부, 입력 불변', () => {
    expect(exec({ groups: [] }, FIXTURE_OK)).toEqual([]);
    expect(exec(PLAN_OK, FIXTURE_OK)).toEqual([]);
    expect(exec(rulePlainPlan(false, ''), FIXTURE_RULE_PLAIN)).toEqual([]);

    expect(exec(themesPlan(true, R_COLOR), FIXTURE_THEMES)).toEqual(['blocked-group:career-kicker-contrast']);
    expect(exec(ruleColorPlan(true, R_COLOR), FIXTURE_RULE_COLOR)).toEqual(['blocked-group:career-kicker-rule']);
    expect(exec(rulePlainPlan(true, 'manual hold'), FIXTURE_RULE_PLAIN)).toEqual(['blocked-group:theme-toggle-size']);

    expect(exec(textOnlyPlan(), FIXTURE_TEXT_ONLY)).toEqual([
      'blocked-group:projects-kicker-text',
      `text-change:projects-kicker-text:${S35_KEY_CC}:${T_PROJECTS}`,
      'empty-fixfiles:projects-kicker-text',
    ]);

    // 혼합: 한 그룹 안의 color+text → blocked·text-change만(fixFiles 있음)
    expect(exec(mixedPlan(true, R_BOTH), FIXTURE_MIXED)).toEqual([
      'blocked-group:kicker-mixed',
      `text-change:kicker-mixed:${S35_KEY_CC}:${T_PROJECTS}`,
    ]);
    // 혼합: 실행 가능 그룹 + blocked 그룹 → blocked 그룹 관련만
    expect(exec(colorPlainPlan(), FIXTURE_COLOR_PLAIN)).toEqual(['blocked-group:career-kicker-rule']);

    const inputs = [
      [textOnlyPlan(), FIXTURE_TEXT_ONLY],
      [mixedPlan(true, R_BOTH), FIXTURE_MIXED],
      [colorPlainPlan(), FIXTURE_COLOR_PLAIN],
    ];
    for (const [plan, baseline] of inputs) {
      const ps = clone(plan);
      const bs = clone(baseline);
      validateRemediationExecutable(plan, baseline);
      expect(plan).toEqual(ps);
      expect(baseline).toEqual(bs);
    }
  });

  test('CLI --check-executable·--check-plan 체인', async () => {
    const d = dir();
    const write = (name, data) => {
      const rel = `${d}/${name}`;
      fs.writeFileSync(path.join(S32_REPO, rel), typeof data === 'string' ? data : JSON.stringify(data, null, 2));
      return rel;
    };
    const run = (plan, baseline) => s32Cli(['--check-executable', '--plan', plan, '--baseline', baseline]);

    const bOk = write('b-ok.json', FIXTURE_OK);
    const empty = await run(write('empty.json', { groups: [] }), bOk);
    expect(empty).toEqual({ code: 0, stdout: 'check-executable: OK\n', stderr: '' });
    const ok = await run(write('ok.json', PLAN_OK), bOk);
    expect(ok).toEqual({ code: 0, stdout: 'check-executable: OK\n', stderr: '' });

    const bThemes = write('b-themes.json', FIXTURE_THEMES);
    const themes = await run(write('themes.json', themesPlan(true, R_COLOR)), bThemes);
    expect(themes.code).toBe(1);
    expect(themes.stdout).toBe('');
    expect(themes.stderr).toBe(`${S36_HEAD}\nblocked-group:career-kicker-contrast\n`);

    const text = await run(write('text.json', textOnlyPlan()), write('b-text.json', FIXTURE_TEXT_ONLY));
    expect(text.code).toBe(1);
    expect(text.stderr.split('\n')[0]).toBe(S36_HEAD);
    expect(text.stderr).toBe(
      `${S36_HEAD}\nblocked-group:projects-kicker-text\ntext-change:projects-kicker-text:${S35_KEY_CC}:${T_PROJECTS}\nempty-fixfiles:projects-kicker-text\n`,
    );

    const missing = await run(`${d}/nope.json`, bOk);
    expect(missing.code).toBe(1);
    expect(missing.stdout).toBe('');
    const brokenBaseline = await run(`${d}/ok.json`, write('b-broken.json', '[{'));
    expect(brokenBaseline.code).toBe(1);
    expect(brokenBaseline.stdout).toBe('');

    // 잘못 분류(RULE_COLOR + blocked false): --check-plan이 먼저 exit 1 → 체인은 executable 전에 멈춤
    const rcPlan = write('rc.json', ruleColorPlan(false, ''));
    const bRc = write('b-rc.json', FIXTURE_RULE_COLOR);
    const plan = await s32Cli(['--check-plan', '--plan', rcPlan, '--baseline', bRc]);
    expect(plan.code).toBe(1);
    expect(plan.stderr).toBe('groups[0]: blocked-required\n');
    const chain = await new Promise((resolve) => {
      const cmd =
        `"${process.execPath}" "${S32_AXE}" --check-plan --plan "${rcPlan}" --baseline "${bRc}"` +
        ` && echo EXEC-REACHED && "${process.execPath}" "${S32_AXE}" --check-executable --plan "${rcPlan}" --baseline "${bRc}"`;
      execFile('/bin/sh', ['-c', cmd], { cwd: S32_REPO }, (err, stdout, stderr) => {
        resolve({ code: err ? (typeof err.code === 'number' ? err.code : 1) : 0, stdout, stderr });
      });
    });
    expect(chain.code).toBe(1);
    expect(chain.stdout).toBe('');
    expect(chain.stderr).toBe('groups[0]: blocked-required\n');
  });
});
