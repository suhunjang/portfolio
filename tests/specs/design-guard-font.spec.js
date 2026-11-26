// step 18 — tests/helpers/design-guard-font.js matchesBaseRule·checkFontDecls (설계 §11.4, node 전용, desktop-dark에서만 실행)
import { test, expect } from '@playwright/test';
import { parseCssRules } from '../helpers/css-parse.js';
import { matchesBaseRule, checkFontDecls } from '../helpers/design-guard-font.js';

const BODY = 'body{font-family:"Pretendard",sans-serif;font-weight:400}';
const H2 = 'h2{font-weight:700}';
const PC = '.project-card{font:500 1rem/1.5 "Pretendard",sans-serif}';
const PARTS = [BODY, H2, PC];
const BASE = PARTS.join(' ');

const FILE = 'css/style.css';
const rules = (text, file = FILE) => parseCssRules(text, file);
const variant = (fn) => fn([...PARTS]).filter((p) => p !== null).join(' ');
const check = (currentText) => checkFontDecls({ baseRules: rules(BASE), currentRules: rules(currentText) });
const only = (text, file = FILE) => {
  const r = rules(text, file).filter((x) => x.atRule === null);
  expect(r.length).toBe(1);
  return r[0];
};

test.describe('step 18 design-guard-font', () => {
  test.beforeEach(({}, testInfo) => {
    test.skip(testInfo.project.name !== 'desktop-dark', 'node 전용 검사는 desktop-dark에서만 실행');
  });

  test('matchesBaseRule', () => {
    const base = only(PC);
    expect(matchesBaseRule(base, only(PC))).toBe(true);
    expect(matchesBaseRule(base, only('.project-card, .featured-card{font:500 1rem/1.5 "Pretendard",sans-serif}'))).toBe(true);
    expect(matchesBaseRule(base, only('.project-card, .hero-name{font:500 1rem/1.5 "Pretendard",sans-serif}'))).toBe(false);
    expect(matchesBaseRule(base, only('.card{font:500 1rem/1.5 "Pretendard",sans-serif}'))).toBe(false);
    expect(matchesBaseRule(base, only(`@media (min-width: 1024px){${PC}}`))).toBe(false);
    expect(matchesBaseRule(base, only(PC, 'css/themes.css'))).toBe(false);
  });

  test('허용 변경은 []', () => {
    const cases = [
      BASE,
      variant((p) => { p[2] = '.project-card, .featured-card{font:500 1rem/1.5 "Pretendard",sans-serif}'; return p; }),
      variant((p) => { p.push('.x{font-weight:700;font-size:1.25rem;letter-spacing:.01em}'); return p; }),
      variant((p) => { p.push('@font-face{font-family:X}'); return p; }),
    ];
    for (const c of cases) expect(check(c), c).toEqual([]);
  });

  test('정확한 진단', () => {
    const BODY_PATH = 'font-decl-missing:|body|font-family';
    expect(check(variant((p) => { p[0] = 'body{font-weight:400}'; return p; }))).toEqual([BODY_PATH]);
    expect(check(variant((p) => { p[0] = 'body{font-weight:400}'; p.unshift('html{font-family:"Pretendard",sans-serif}'); return p; })))
      .toEqual([BODY_PATH, 'font-asset:html']);
    expect(check(variant((p) => {
      p[0] = 'body{font-weight:400}';
      p.push('@media (min-width: 1024px){body{font-family:"Pretendard",sans-serif}}');
      return p;
    }))).toEqual([BODY_PATH, 'font-asset:body']);
    expect(check(variant((p) => { p[0] = 'body{font-family:"Inter",sans-serif;font-weight:400}'; return p; })))
      .toEqual([BODY_PATH, 'font-asset:body']);
    expect(check(variant((p) => { p[2] = '.project-card{}'; return p; })))
      .toEqual(['font-decl-missing:|.project-card|font']);
    expect(check(variant((p) => { p[2] = '.project-card, .hero-name{font:500 1rem/1.5 "Pretendard",sans-serif}'; return p; })))
      .toEqual(['font-decl-missing:|.project-card|font', 'font-asset:.project-card, .hero-name']);
    expect(check(variant((p) => { p[2] = '.card{font:500 1rem/1.5 "Pretendard",sans-serif}'; return p; })))
      .toEqual(['font-decl-missing:|.project-card|font', 'font-asset:.card']);
    expect(check(variant((p) => { p.push('.x{font-family:Inter}'); return p; }))).toEqual(['font-asset:.x']);
    expect(check(variant((p) => { p[0] = 'body{font-weight:400}'; p.push('.x{font-family:Inter}'); return p; })))
      .toEqual([BODY_PATH, 'font-asset:.x']);
  });

  test('입력 불변', () => {
    const baseRules = rules(BASE);
    const currentRules = rules(variant((p) => { p[0] = 'body{font-weight:400}'; p.push('.x{font-family:Inter}'); return p; }));
    const before = JSON.stringify({ baseRules, currentRules });
    matchesBaseRule(baseRules[0], currentRules[0]);
    checkFontDecls({ baseRules, currentRules });
    expect(JSON.stringify({ baseRules, currentRules })).toBe(before);
  });
});
