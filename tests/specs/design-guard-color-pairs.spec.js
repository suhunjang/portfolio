// step 15 — tests/helpers/design-guard-color-pairs.js 색 Rule 대응·featured/stripe 예외·color-rule-reordered (설계 §11.4, node 전용, desktop-dark에서만 실행)
import { test, expect } from '@playwright/test';
import { parseCssRules } from '../helpers/css-parse.js';
import { featuredCounterpart, pairColorRules, checkColorRulePairs } from '../helpers/design-guard-color-pairs.js';

const A = '.a{color:red}';
const B = '.b{color:blue}';
const PC = '.project-card{background:var(--card);padding:16px}';
const NAV = '@media (max-width: 768px){.nav-link{color:var(--accent)}}';
const STRIPE = '.strength-card::before{background:var(--accent)}';
const DUP1 = '.dup{color:var(--card)}';
const DUP2 = '.dup{color:var(--accent)}';
const ROOT = ':root{--card:#fff}';
const PARTS = [A, B, PC, NAV, STRIPE, DUP1, DUP2, ROOT];
const BASE = PARTS.join(' ');

const FILE = 'css/style.css';
const rules = (text) => parseCssRules(text, FILE);
const variant = (fn) => fn([...PARTS]).filter((p) => p !== null).join(' ');
const check = (currentText) => {
  const baseRules = rules(BASE);
  const currentRules = rules(currentText);
  return checkColorRulePairs({ baseRules, currentRules });
};

test.describe('step 15 design-guard-color-pairs', () => {
  test.beforeEach(({}, testInfo) => {
    test.skip(testInfo.project.name !== 'desktop-dark', 'node 전용 검사는 desktop-dark에서만 실행');
  });

  test('featuredCounterpart', () => {
    expect(featuredCounterpart('#projectGrid .project-card:hover')).toBe('#projectGrid .featured-card:hover');
    expect(featuredCounterpart('.project-card .project-card-x')).toBe('.featured-card .project-card-x');
    expect(featuredCounterpart('.nav-link')).toBe(null);
  });

  test('pairColorRules: 색 Rule만, 같은 selectors는 등장 순 1:1', () => {
    const baseRules = rules(BASE);
    const pairs = pairColorRules(baseRules, rules(BASE));
    expect(pairs.map((p) => p.base.selectors.join(', '))).toEqual([
      '.a', '.b', '.project-card', '.nav-link', '.strength-card::before', '.dup', '.dup',
    ]);
    for (const p of pairs) expect(p.current.index).toBe(p.base.index);
    expect(pairs.some((p) => p.base.selectors.includes(':root'))).toBe(false);

    const dropped = pairColorRules(baseRules, rules(variant((p) => { p[6] = null; return p; })));
    const dups = dropped.filter((p) => p.base.selectors[0] === '.dup');
    expect(dups[0].current.decls).toEqual([['color', 'var(--card)']]);
    expect(dups[1].current).toBe(null);
  });

  test('허용 변경은 []', () => {
    const cases = [
      BASE,
      variant((p) => { p[2] = '.project-card, .featured-card{background:var(--card);padding:16px}'; return p; }),
      variant((p) => { p[4] = null; return p; }),
      variant((p) => { p.splice(1, 0, '.z{gap:1px}'); return p; }),
      variant((p) => { p[0] = '.a{color:green}'; return p; }),
      variant((p) => { p[2] = '.project-card{padding:16px;margin:0;background:var(--card)}'; return p; }),
    ];
    for (const c of cases) expect(check(c), c).toEqual([]);
  });

  test('정확한 진단', () => {
    const swap = (p) => { [p[0], p[1]] = [p[1], p[0]]; return p; };
    const card = (p) => { p[2] = '.card{background:var(--card);padding:16px}'; return p; };
    expect(check(variant(swap))).toEqual(['color-rule-reordered:.a|.b']);
    expect(check(variant((p) => { const [pc] = p.splice(2, 1); p.unshift(pc); return p; })))
      .toEqual(['color-rule-reordered:.b|.project-card']);
    expect(check(variant(card))).toEqual(['color-rule-missing:|.project-card']);
    expect(check(variant((p) => { p[2] = '.project-card, .hero-name{background:var(--card);padding:16px}'; return p; })))
      .toEqual(['selector-extended:.project-card, .hero-name']);
    expect(check(variant((p) => { p[3] = '@media (max-width: 900px){.nav-link{color:var(--accent)}}'; return p; })))
      .toEqual(['color-rule-missing:@media (max-width: 768px)|.nav-link']);
    expect(check(variant((p) => { p[6] = null; return p; }))).toEqual(['color-rule-missing:|.dup']);
    expect(check(variant((p) => card(swap(p)))))
      .toEqual(['color-rule-missing:|.project-card', 'color-rule-reordered:.a|.b']);
  });

  test('입력 불변', () => {
    const baseRules = rules(BASE);
    const currentRules = rules(variant((p) => { [p[0], p[1]] = [p[1], p[0]]; p[6] = null; return p; }));
    const before = JSON.stringify({ baseRules, currentRules });
    pairColorRules(baseRules, currentRules);
    checkColorRulePairs({ baseRules, currentRules });
    expect(JSON.stringify({ baseRules, currentRules })).toBe(before);
  });
});
