// step 17 — tests/helpers/design-guard-color.js 색 토큰 위치 키 중복(규칙 0)·보존(1~3)·checkColors (설계 §11.4, node 전용, desktop-dark에서만 실행)
import { test, expect } from '@playwright/test';
import { parseCssRules } from '../helpers/css-parse.js';
import { colorTokenSet } from '../helpers/color-vocab.js';
import { checkColorTokens, checkColors } from '../helpers/design-guard-color.js';

const ROOT = ':root{--card:#fff;--accent:var(--brand);--pad:16px}';
const PC = '.project-card{background:var(--card);padding:var(--pad)}';
const NAV = '@media (max-width: 768px){.nav-link{color:var(--accent)}}';
const STRIPE = '.strength-card::before{background:var(--accent)}';
const PARTS = [ROOT, PC, NAV, STRIPE];
const BASE = PARTS.join(' ');
const BASE_THEMES = ':root{--brand:#3355ff}';

const STYLE = 'css/style.css';
const THEMES = 'css/themes.css';
const rules = (style, themes = BASE_THEMES) => [...parseCssRules(style, STYLE), ...parseCssRules(themes, THEMES)];
const BASE_RULES = rules(BASE);
const COLOR_TOKENS = colorTokenSet(BASE_RULES);

const variant = (fn) => fn([...PARTS]).filter((p) => p !== null).join(' ');
const set = (i, text) => variant((p) => { p[i] = text; return p; });
const append = (text) => `${BASE} ${text}`;
const root = (body) => set(0, `:root{${body}}`);

const tokens = (style, themes) => checkColorTokens({
  baseRules: rules(BASE),
  currentRules: rules(style, themes),
  colorTokens: COLOR_TOKENS,
});
const colors = (style, themes) => checkColors({ baseRules: rules(BASE), currentRules: rules(style, themes) });

const DUP_CARD = '색 토큰 중복 정의: --card @ css/style.css - :root (count=2)';

test.describe('step 17 design-guard-color', () => {
  test.beforeEach(({}, testInfo) => {
    test.skip(testInfo.project.name !== 'desktop-dark', 'node 전용 검사는 desktop-dark에서만 실행');
  });

  test('colorTokens 전제', () => {
    for (const n of ['--card', '--accent', '--brand']) expect(COLOR_TOKENS.has(n), n).toBe(true);
    expect(COLOR_TOKENS.has('--pad')).toBe(false);
  });

  test('보존 규칙 1~3', () => {
    expect(tokens(BASE)).toEqual([]);
    expect(tokens(root('--card:#fafafa;--accent:var(--brand);--pad:16px'))).toEqual(['color-token-changed:--card']);
    expect(tokens(root('--accent:var(--brand);--pad:16px'))).toEqual(['color-token-removed:--card']);
    expect(tokens(root('--card:#fff;--accent:var(--card);--pad:16px'))).toEqual(['color-token-changed:--accent']);
    expect(tokens(append('.btn{--accent:#000}'))).toEqual(['color-token-redefined:--accent']);
    expect(tokens(root('--card:#fff;--accent:var(--brand);--pad:16px;--btn-bg: var(--brand)'))).toEqual(['color-token-added:--btn-bg']);
    expect(tokens(root('--card:#fff;--accent:var(--brand);--pad:16px;--ring: currentColor'))).toEqual(['color-token-added:--ring']);
    expect(tokens(root('--card:#fff;--accent:var(--brand);--pad:16px;--card2:#000'))).toEqual(['color-token-added:--card2']);
    expect(tokens(root('--card:#fff;--accent:var(--brand);--pad: red'))).toEqual(['color-token-added:--pad']);
    expect(tokens(root('--card:#fff;--accent:var(--brand);--pad:16px;--section-pad: 96px'))).toEqual([]);
  });

  test('color() 신규 토큰', () => {
    expect(tokens(root('--card:#fff;--accent:var(--brand);--pad:16px;--new-color: color(display-p3 1 0 0)')))
      .toEqual(['color-token-added:--new-color']);
    expect(tokens(root('--card:#fff;--accent:var(--brand);--pad:16px;--new-color: CoLoR(display-p3 1 0 0)')))
      .toEqual(['color-token-added:--new-color']);
  });

  test('위치 키 중복 정의(규칙 0 먼저, 정확히 하나일 때만 보존 검사)', () => {
    expect(tokens(root('--card:#fff;--card:#fff;--accent:var(--brand);--pad:16px'))).toEqual([DUP_CARD]);
    expect(tokens(root('--card:#fff;--card:#fafafa;--accent:var(--brand);--pad:16px'))).toEqual([DUP_CARD]);
    expect(tokens(append(':root{--card:#fff}'))).toEqual([DUP_CARD]);
    expect(tokens(append(':root{--card:#fafafa}'))).toEqual([DUP_CARD]);
    expect(tokens(`${root('--card:#fff;--card:#fff;--accent:var(--brand);--pad:16px')} :root{--card:#fff}`))
      .toEqual(['색 토큰 중복 정의: --card @ css/style.css - :root (count=3)']);
    expect(tokens(append('@media (min-width: 1024px){:root{--card:#fff;--card:#fff}}')))
      .toEqual(['색 토큰 중복 정의: --card @ css/style.css @media (min-width: 1024px) :root (count=2)']);
    expect(tokens(BASE, ':root{--brand:#3355ff;--brand:#3355ff}'))
      .toEqual(['색 토큰 중복 정의: --brand @ css/themes.css - :root (count=2)']);
    expect(tokens(root('--card:#fff;--accent:var(--brand);--pad:16px;--pad:16px'))).toEqual([]);
    expect(tokens(root('--card:#fff;--card:#fff;--accent:var(--brand);--pad:red')))
      .toEqual([DUP_CARD, 'color-token-added:--pad']);
  });

  test('checkColors 허용 []', () => {
    const cases = [
      BASE,
      set(1, '.project-card, .featured-card{background:var(--card);padding:var(--pad)}'),
      set(3, null),
      append('.z{gap:24px}'),
      root('--card:#fff;--accent:var(--brand);--pad:16px;--section-pad: 96px'),
      append(':focus-visible{outline:2px solid var(--accent)}'),
    ];
    for (const c of cases) expect(colors(c), c).toEqual([]);
  });

  test('checkColors 거부', () => {
    const both = colors(variant((p) => {
      p[0] = ':root{--card:#fafafa;--accent:var(--brand);--pad:16px}';
      p[1] = '.project-card, .x{background:var(--card);padding:var(--pad)}';
      return p;
    }));
    expect(both).toEqual(['selector-extended:.project-card, .x', 'color-token-changed:--card']);
    expect(colors(append('.x{color:var(--card)}'))).toEqual(['color-decl-new:.x']);
    expect(colors(set(1, '.project-card{background:var(--card);padding:var(--pad);border-top-color:var(--accent)}')))
      .toEqual(['color-decl-new:.project-card']);
    expect(colors(set(1, '.project-card{background:var(--card);padding:var(--pad);background:var(--accent)}')))
      .toEqual(['color-decl-new:.project-card']);
    expect(colors([ROOT, NAV, PC, STRIPE].join(' '))).toEqual(['color-rule-reordered:.project-card|.nav-link']);
    expect(colors(append(':root{--card:#fff}'))).toEqual([DUP_CARD]);
    expect(colors(root('--card:#fff;--accent:var(--brand);--pad:16px;--new-color: color(display-p3 1 0 0)')))
      .toEqual(['color-token-added:--new-color']);
  });

  test('입력 불변', () => {
    const baseRules = rules(BASE);
    const currentRules = rules(`${root('--card:#fff;--card:#fafafa;--accent:var(--card);--pad:red')} .btn{--accent:#000}`);
    const colorTokens = colorTokenSet(baseRules);
    const snap = JSON.stringify([baseRules, currentRules, [...colorTokens]]);
    checkColorTokens({ baseRules, currentRules, colorTokens });
    checkColors({ baseRules, currentRules });
    expect(JSON.stringify([baseRules, currentRules, [...colorTokens]])).toBe(snap);
  });
});
