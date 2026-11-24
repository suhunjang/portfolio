// step 15 — 색 Rule 대응·featured/stripe 예외·color-rule-reordered (설계 §11.4 규칙 1~3).
// 순수 함수: 입력 Rule 배열을 바꾸지 않는다. custom property 선언과 선언 내용 비교는 다루지 않는다.
import { isColorDecl } from './color-vocab.js';

const PROJECT_CARD = /\.project-card(?![A-Za-z0-9_-])/g;
const STRIPE = '.strength-card::before';

// `.project-card` 클래스를 모두 `.featured-card`로 바꾼 선택자, 없으면 null.
export function featuredCounterpart(selector) {
  const s = String(selector);
  if (!s.match(PROJECT_CARD)) return null;
  return s.replace(PROJECT_CARD, '.featured-card');
}

const sameChain = (a, b) => a.length === b.length && a.every((x, i) => x === b[i]);
const groupKey = (rule) => JSON.stringify([rule.file, rule.chain, rule.selectors]);
const isColorRule = (rule) => rule.decls.some((d) => isColorDecl(d));
const label = (rule) => `${rule.chain.join(' > ')}|${rule.selectors.join(', ')}`;

// BASE 색 Rule을 (file, index) 순으로.
function baseColorRules(baseRules) {
  return baseRules
    .filter(isColorRule)
    .slice()
    .sort((a, b) => (a.file < b.file ? -1 : a.file > b.file ? 1 : a.index - b.index));
}

// [{ base, current|null }]: 같은 file·chain에서 current.selectors ⊇ base.selectors,
// 같은 file·chain·selectors BASE 색 Rule 여럿이면 후보와 등장 순 1:1.
export function pairColorRules(baseRules, currentRules) {
  const seen = new Map();
  return baseColorRules(baseRules).map((base) => {
    const key = groupKey(base);
    const k = seen.get(key) ?? 0;
    seen.set(key, k + 1);
    const candidates = currentRules
      .filter((cur) => cur.file === base.file
        && sameChain(cur.chain, base.chain)
        && base.selectors.every((s) => cur.selectors.includes(s)))
      .slice()
      .sort((a, b) => a.index - b.index);
    return { base, current: candidates[k] ?? null };
  });
}

export function checkColorRulePairs({ baseRules, currentRules }) {
  const out = [];
  const seen = new Set();
  const push = (s) => { if (!seen.has(s)) { seen.add(s); out.push(s); } };
  const pairs = pairColorRules(baseRules, currentRules);

  // 규칙 1→2: BASE 색 Rule (file, index) 순.
  for (const { base, current } of pairs) {
    if (current === null) {
      if (!base.selectors.every((s) => s === STRIPE)) push(`color-rule-missing:${label(base)}`);
      continue;
    }
    const allowed = new Set(base.selectors.map(featuredCounterpart).filter((s) => s !== null));
    const extra = current.selectors.filter((s) => !base.selectors.includes(s));
    if (extra.some((s) => !allowed.has(s))) push(`selector-extended:${current.selectors.join(', ')}`);
  }

  // 규칙 3: file별, 짝 있는 BASE 색 Rule을 BASE index 순으로 인접 비교.
  const files = [];
  for (const { base } of pairs) if (!files.includes(base.file)) files.push(base.file);
  for (const file of files) {
    const paired = pairs.filter((p) => p.base.file === file && p.current !== null);
    for (let i = 1; i < paired.length; i += 1) {
      const P = paired[i - 1];
      const Q = paired[i];
      if (Q.current.index < P.current.index) {
        push(`color-rule-reordered:${P.base.selectors.join(', ')}|${Q.base.selectors.join(', ')}`);
      }
    }
  }
  return out;
}
