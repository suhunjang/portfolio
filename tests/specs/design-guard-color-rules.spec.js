// step 16 — tests/helpers/design-guard-color-rules.js 색 선언 규칙 4~8·checkColorRules 순서·중복 제거 (설계 §11.4, node 전용, desktop-dark에서만 실행)
import { test, expect } from '@playwright/test';
import { parseCssRules } from '../helpers/css-parse.js';
import { checkColorRules } from '../helpers/design-guard-color-rules.js';

const ROOT = ':root{--card:#fff;--accent:#3355ff}';
const PC = '.project-card{background:var(--card);padding:16px}';
const NAV = '@media (max-width: 768px){.nav-link{color:var(--accent)}}';
const STRIPE = '.strength-card::before{background:var(--accent)}';
const DUP1 = '.dup{color:var(--card)}';
const DUP2 = '.dup{color:var(--accent)}';
const BTN = '.btn{border-color:var(--accent)}';
const PAIR = '.pair{color:var(--card);color:var(--accent)}';
const PARTS = [ROOT, PC, NAV, STRIPE, DUP1, DUP2, BTN, PAIR];
const BASE = PARTS.join(' ');

const FILE = 'css/style.css';
const COLOR_TOKENS = new Set(['--card', '--accent']);
const rules = (text) => parseCssRules(text, FILE);
const variant = (fn) => fn([...PARTS]).filter((p) => p !== null).join(' ');
const set = (i, text) => variant((p) => { p[i] = text; return p; });
const append = (text) => `${BASE} ${text}`;
const check = (currentText) => checkColorRules({
  baseRules: rules(BASE),
  currentRules: rules(currentText),
  colorTokens: COLOR_TOKENS,
});

test.describe('step 16 design-guard-color-rules', () => {
  test.beforeEach(({}, testInfo) => {
    test.skip(testInfo.project.name !== 'desktop-dark', 'node 전용 검사는 desktop-dark에서만 실행');
  });

  test('허용 변경은 []', () => {
    const cases = [
      BASE,
      append(ROOT),
      set(0, ':root{--card:#fff;--accent:#3355ff;--card2:#000}'),
      set(1, '.project-card, .featured-card{background:var(--card);padding:16px}'),
      set(3, null),
      set(1, '.project-card{background:var(--card);padding:16px;margin:4px;transition:transform .2s}'),
      set(1, '.project-card{padding:16px;background:var(--card)}'),
      set(7, '.pair{margin:0;color:var(--card);gap:4px;color:var(--accent)}'),
      append('.z{gap:24px}'),
      append(':focus-visible{outline:2px solid var(--accent)}'),
    ];
    for (const c of cases) expect(check(c), c).toEqual([]);
  });

  test('짝 있는 Rule 규칙 4~6', () => {
    expect(check(set(7, '.pair{color:var(--accent);color:var(--card)}'))).toEqual(['color-decl-reordered:.pair']);
    expect(check(set(1, '.project-card{background:var(--accent);padding:16px}')))
      .toEqual(['color-decl-changed:.project-card', 'color-decl-new:.project-card']);
    expect(check(set(1, '.project-card{background:currentColor;padding:16px}')))
      .toEqual(['color-decl-changed:.project-card', 'color-decl-new:.project-card']);
    expect(check(set(1, '.project-card{background:var(--card);padding:16px;background:var(--accent)}')))
      .toEqual(['color-decl-new:.project-card']);
    expect(check(set(2, '@media (max-width: 768px){.nav-link{color:var(--accent);color:var(--card)}}')))
      .toEqual(['color-decl-new:.nav-link']);
    expect(check(set(6, '.btn{border-color:var(--accent);border-color:var(--card)}'))).toEqual(['color-decl-new:.btn']);
    expect(check(set(1, '.project-card{background:var(--card);padding:16px;border-top-color:var(--accent)}')))
      .toEqual(['color-decl-new:.project-card']);
    expect(check(set(1, '.project-card{background:var(--card);padding:16px;outline-color:navy}')))
      .toEqual(['color-decl-new:.project-card']);
    expect(check(set(1, '.project-card{background:var(--card);padding:16px;margin:currentColor}')))
      .toEqual(['color-decl-new:.project-card']);
  });

  test('짝 없는 Rule 규칙 7~8과 pairs 결과 결합', () => {
    expect(check(set(1, '.card{background:var(--card);padding:16px}')))
      .toEqual(['color-rule-missing:|.project-card', 'color-decl-new:.card']);
    expect(check(set(2, '@media (max-width: 900px){.nav-link{color:var(--accent)}}')))
      .toEqual(['color-rule-missing:@media (max-width: 768px)|.nav-link', 'color-decl-new:.nav-link']);
    expect(check(variant((p) => { [p[6], p[7]] = [p[7], p[6]]; return p; }))).toEqual(['color-rule-reordered:.btn|.pair']);
    expect(check(append('.x{color:var(--card)}'))).toEqual(['color-decl-new:.x']);
    expect(check(append('.x{border-left:2px solid navy}'))).toEqual(['color-decl-new:.x']);
    expect(check(append('.x{border-bottom-color:var(--card)}'))).toEqual(['color-decl-new:.x']);
    expect(check(append('.y{margin:currentColor}'))).toEqual(['color-decl-new:.y']);
    expect(check(append(':focus-visible{outline:2px solid #000}'))).toEqual(['color-decl-new::focus-visible']);
  });

  test('결합 진단 순서·중복 제거', () => {
    const combined = variant((p) => {
      p[1] = '.card{background:var(--card);padding:16px}';
      p[4] = '.dup{color:var(--accent)}';
      p[7] = '.pair{color:var(--accent);color:var(--card)}';
      p.push('.x{color:var(--card)}');
      return p;
    });
    expect(check(combined)).toEqual([
      'color-rule-missing:|.project-card',
      'color-decl-changed:.dup',
      'color-decl-new:.dup',
      'color-decl-reordered:.pair',
      'color-decl-new:.card',
      'color-decl-new:.x',
    ]);
  });

  test('입력 불변', () => {
    const baseRules = rules(BASE);
    const currentRules = rules(variant((p) => {
      p[1] = '.card{background:var(--card);padding:16px}';
      p[7] = '.pair{color:var(--accent);color:var(--card)}';
      p.push('.x{color:var(--card)}');
      return p;
    }));
    const colorTokens = new Set(COLOR_TOKENS);
    const before = JSON.stringify({ baseRules, currentRules, tokens: [...colorTokens] });
    checkColorRules({ baseRules, currentRules, colorTokens });
    expect(JSON.stringify({ baseRules, currentRules, tokens: [...colorTokens] })).toBe(before);
  });
});
