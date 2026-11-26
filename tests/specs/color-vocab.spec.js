// step 14 — tests/helpers/color-vocab.js 색 어휘·COLOR_PROPS·양방향 token 그래프 (설계 §11.4, node 전용, desktop-dark에서만 실행)
import { test, expect } from '@playwright/test';
import { parseCssRules } from '../helpers/css-parse.js';
import {
  NAMED_COLORS,
  COLOR_LITERAL_RE,
  COLOR_PROPS,
  valueIdentifiers,
  varRefs,
  isColorLiteralValue,
  isColorDecl,
  customPropertyDefs,
  colorTokenSet,
  isColorValue,
} from '../helpers/color-vocab.js';

const STYLE = ':root{--card:#fff;--accent:var(--brand);--pad:16px;--alias:var(--accent);--ring:var(--pad);--p3:color(display-p3 1 0 0)} .a{background:var(--card)} .b{color:var(--alias)}';
const THEMES = ':root{--brand:#3355ff}';
const rulesOf = (style, themes) => [
  ...parseCssRules(style, 'css/style.css'),
  ...parseCssRules(themes, 'css/themes.css'),
];
const sorted = (set) => [...set].sort();

test.describe('step 14 color-vocab', () => {
  test.beforeEach(({}, testInfo) => {
    test.skip(testInfo.project.name !== 'desktop-dark', 'node 전용 검사는 desktop-dark에서만 실행');
  });

  test('NAMED_COLORS 149개(148 + transparent)', () => {
    expect(NAMED_COLORS.size).toBe(149);
    expect(NAMED_COLORS.has('navy')).toBe(true);
    expect(NAMED_COLORS.has('rebeccapurple')).toBe(true);
    expect(NAMED_COLORS.has('transparent')).toBe(true);
    expect(isColorLiteralValue('RebeccaPurple')).toBe(true);
  });

  test('COLOR_LITERAL_RE 설계 그대로', () => {
    expect(COLOR_LITERAL_RE.source).toBe(
      '#[0-9a-fA-F]{3,8}\\b|(?<![A-Za-z0-9_-])(?:rgb|rgba|hsl|hsla|hwb|lab|lch|oklab|oklch|color|color-mix)\\s*\\(',
    );
    expect(COLOR_LITERAL_RE.flags).toBe('i');
  });

  test('isColorLiteralValue true', () => {
    for (const v of [
      '#fff', '#0d0f12', 'rgb(0 0 0)', 'hsla(0,0%,0%,.5)', 'color-mix(in srgb, red, blue)',
      'navy', 'NAVY', 'currentColor', '1px solid red',
      'color(display-p3 1 0 0)', 'CoLoR(display-p3 1 0 0)',
      'color(from rgb(255 0 0) srgb r g b)', 'color(from color(display-p3 1 0 0) srgb r g b / .5)',
      'RGB (0 0 0)',
    ]) {
      expect(isColorLiteralValue(v), v).toBe(true);
    }
  });

  test('isColorLiteralValue false', () => {
    for (const v of [
      '16px', 'var(--navy)', 'url(navy.png)', '"navy"', 'none',
      'mycolor(display-p3 1 0 0)', '"color(display-p3 1 0 0)"', 'url(color(display-p3 1 0 0).png)',
      'x-rgb(1 2 3)',
    ]) {
      expect(isColorLiteralValue(v), v).toBe(false);
    }
  });

  test('valueIdentifiers: 문자열·url()·var() 인자 제외', () => {
    const ids = valueIdentifiers('1px solid red "navy" url(blue.png) var(--green, teal)');
    expect(ids).toContain('solid');
    expect(ids).toContain('red');
    expect(ids).not.toContain('navy');
    expect(ids).not.toContain('blue');
    expect(ids).not.toContain('teal');
    expect(ids).not.toContain('px');
  });

  test('COLOR_PROPS 설계 집합', () => {
    const expected = 'color, background, background-color, background-image, border, border-top, border-right, border-bottom, border-left, border-color, border-top-color, border-right-color, border-bottom-color, border-left-color, border-block, border-block-start, border-block-end, border-block-color, border-block-start-color, border-block-end-color, border-inline, border-inline-start, border-inline-end, border-inline-color, border-inline-start-color, border-inline-end-color, outline, outline-color, column-rule, column-rule-color, text-decoration, text-decoration-color, text-emphasis, text-emphasis-color, -webkit-text-fill-color, -webkit-text-stroke, -webkit-text-stroke-color, fill, stroke, stop-color, flood-color, lighting-color, box-shadow, text-shadow, caret-color, accent-color, scrollbar-color'.split(', ');
    expect(sorted(COLOR_PROPS)).toEqual([...expected].sort());
    for (const p of [
      'border-top-color', 'border-right-color', 'border-bottom-color', 'border-left-color',
      'border-block-start-color', 'border-inline-end-color', '-webkit-text-fill-color',
      'text-emphasis-color', 'scrollbar-color', 'stop-color',
    ]) expect(COLOR_PROPS.has(p), p).toBe(true);
    for (const p of ['padding', 'font-size', 'transform']) expect(COLOR_PROPS.has(p), p).toBe(false);
  });

  test('varRefs 중첩 fallback 포함', () => {
    expect(varRefs('var(--a)')).toEqual(['--a']);
    expect(varRefs('var(--a, var(--b))')).toEqual(['--a', '--b']);
    expect(varRefs('16px')).toEqual([]);
  });

  test('isColorDecl', () => {
    const x = 'var(--x)';
    for (const d of [
      ['color', x], ['fill', x], ['border', '1px solid var(--x)'], ['border-top-color', 'var(--x)'],
      ['border-left-color', 'transparent'], ['border-inline-start-color', 'var(--x)'],
      ['-webkit-text-fill-color', 'var(--x)'], ['scrollbar-color', 'auto'],
      ['text-decoration', 'underline var(--x)'],
    ]) expect(isColorDecl(d), d.join(':')).toBe(true);
    for (const d of [
      ['border', '0'], ['border', 'none'], ['border-top', 'none'], ['outline', 'none'],
      ['text-decoration', 'none'], ['padding', '16px'], ['--card', '#fff'],
    ]) expect(isColorDecl(d), d.join(':')).toBe(false);
  });

  test('customPropertyDefs', () => {
    const defs = customPropertyDefs(parseCssRules(':root{--a:#fff;color:red} @media (x){.b{--c:var(--a)}}', 'css/style.css'));
    expect(defs).toEqual([
      { file: 'css/style.css', chain: [], selectors: [':root'], name: '--a', value: '#fff' },
      { file: 'css/style.css', chain: ['@media (x)'], selectors: ['.b'], name: '--c', value: 'var(--a)' },
    ]);
  });

  test('colorTokenSet 양방향 고정점', () => {
    const set = colorTokenSet(rulesOf(STYLE, THEMES));
    expect(sorted(set)).toEqual(['--accent', '--alias', '--brand', '--card', '--p3']);

    const set2 = colorTokenSet(rulesOf(`${STYLE} .c{border-top-color:var(--ring2)}`, `${THEMES} :root{--ring2:var(--pad)}`));
    expect(sorted(set2)).toEqual(['--accent', '--alias', '--brand', '--card', '--p3', '--pad', '--ring', '--ring2']);

    expect(isColorValue('var(--alias)', set)).toBe(true);
    expect(isColorValue('var(--p3)', set)).toBe(true);
    expect(isColorValue('var(--pad)', set)).toBe(false);
  });

  test('입력 불변', () => {
    const rules = rulesOf(STYLE, THEMES);
    const before = structuredClone(rules);
    customPropertyDefs(rules);
    colorTokenSet(rules);
    expect(rules).toEqual(before);
    const decl = ['border', 'none'];
    isColorDecl(decl);
    expect(decl).toEqual(['border', 'none']);
  });
});
