// step 19 — tests/helpers/design-guard-css.js checkTypeAndAssets·checkCss (설계 §11.4, node 전용, desktop-dark에서만 실행)
import { test, expect } from '@playwright/test';
import { parseCssRules } from '../helpers/css-parse.js';
import { checkTypeAndAssets, checkCss } from '../helpers/design-guard-css.js';

const IMPORT = '@import url("a.css") screen and (min-width: 10px);';
const BODY = 'body{font-family:"Pretendard",sans-serif;font-weight:400}';
const H2 = 'h2{font-weight:700}';
const PC = '.project-card{font:500 1rem/1.5 "Pretendard",sans-serif}';
const ROOT = ':root{--pad:16px}';
const BRAND = '.brand{color:var(--brand)}';
const PARTS = [IMPORT, BODY, H2, PC, ROOT, BRAND];
const BASE = PARTS.join(' ');
const THEMES = ':root{--brand:#3355ff}';

const STYLE = 'css/style.css';
const THEME_FILE = 'css/themes.css';
const rulesOf = (style, themes = THEMES) => [...parseCssRules(style, STYLE), ...parseCssRules(themes, THEME_FILE)];
const variant = (fn) => fn([...PARTS]).filter((p) => p !== null).join(' ');
const plus = (extra) => `${BASE} ${extra}`;
const check = (style, themes = THEMES) => checkTypeAndAssets({ baseRules: rulesOf(BASE), currentRules: rulesOf(style, themes) });

test.describe('step 19 design-guard-css', () => {
  test.beforeEach(({}, testInfo) => {
    test.skip(testInfo.project.name !== 'desktop-dark', 'node 전용 검사는 desktop-dark에서만 실행');
  });

  test('checkTypeAndAssets 허용 변경은 []', () => {
    const cases = [
      BASE,
      plus('.y{border-color:var(--brand)}'),
      variant((p) => { p[0] = '@import url("a.css")   screen and (min-width:   10px);'; return p; }),
      variant((p) => { p[0] = null; return p; }),
      plus('.x{font-weight:700;font-size:1.25rem;letter-spacing:.01em}'),
      plus('.y{content:none}'),
      plus('.z{padding:var(--pad)}'),
      plus(':root{--gap:24px} .g{gap:var(--gap)}'),
      variant((p) => { p[4] = '.z{padding:var(--pad)}'; return p; }),
      variant((p) => { p[3] = '.project-card, .featured-card{font:500 1rem/1.5 "Pretendard",sans-serif}'; return p; }),
    ];
    for (const style of cases) expect(check(style), style).toEqual([]);
  });

  test('checkTypeAndAssets 정확한 진단', () => {
    const cases = [
      [variant((p) => { p[0] = '@import url("b.css") screen and (min-width: 10px);'; return p; }), ['asset:@import']],
      [variant((p) => { p[0] = '@import url("a.css") screen and (min-width: 20px);'; return p; }), ['asset:@import']],
      [variant((p) => { p.splice(1, 0, '@import url(f.css);'); return p; }), ['asset:@import']],
      [plus('@font-face{font-family:X;src:url(x.woff2)}'), ['font-asset:@font-face', 'asset:@font-face']],
      [plus('.x{font-weight:800}'), ['font-weight:800']],
      [plus('.x{background-image:url(a.png)}'), ['asset:.x']],
      [plus(".x::after{content:'★'}"), ['content:.x::after']],
      [plus('.x{margin:var(--nope)}'), ['unknown-token:--nope']],
      [plus('.x{color:var(--brand);margin:var(--nope)}'), ['unknown-token:--nope']],
      [plus(':root{--a:1px} .x{margin:var(--a, var(--nope))}'), ['unknown-token:--nope']],
      [plus('.x{margin:var(--nope)} .w{padding:var(--nope)}'), ['unknown-token:--nope']],
      [variant((p) => { p[1] = 'body{font-weight:400}'; p.push('.x{font-weight:800}'); return p; }),
        ['font-decl-missing:|body|font-family', 'font-weight:800']],
      [plus('.x{font-weight:800;font-family:Inter}'), ['font-asset:.x', 'font-weight:800']],
    ];
    for (const [style, want] of cases) expect(check(style), style).toEqual(want);
  });

  test('checkCss', () => {
    const run = (currentCss, currentThemes = THEMES) => checkCss({ baseCss: BASE, currentCss, baseThemes: THEMES, currentThemes });
    expect(run(BASE)).toEqual([]);
    const img = run(plus('.x{background-image:url(a.png)}'));
    expect(img).toContain('asset:.x');
    expect(img).toContain('color-decl-new:.x');
    expect(run(BASE, ':root{--brand:#3355ff} ')).toContain('themes-changed');
    expect(run(variant((p) => { p[1] = 'body{font-weight:400}'; return p; }))).toContain('font-decl-missing:|body|font-family');
    expect(run(variant((p) => { p[0] = '@import url("b.css") screen and (min-width: 10px);'; return p; }))).toContain('asset:@import');
    const dup = run(BASE, ':root{--brand:#3355ff} :root{--brand:#3355ff}');
    expect(dup).toContain('색 토큰 중복 정의: --brand @ css/themes.css - :root (count=2)');
    expect(dup).toContain('themes-changed');
  });

  test('입력 불변', () => {
    const baseRules = rulesOf(BASE);
    const currentRules = rulesOf(plus('@font-face{font-family:X;src:url(x.woff2)} .x{margin:var(--nope);content:"a"}'));
    const b = JSON.stringify(baseRules);
    const c = JSON.stringify(currentRules);
    checkTypeAndAssets({ baseRules, currentRules });
    expect(JSON.stringify(baseRules)).toBe(b);
    expect(JSON.stringify(currentRules)).toBe(c);
  });
});
