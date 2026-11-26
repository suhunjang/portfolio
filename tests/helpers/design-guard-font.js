// step 18 — font-family·font 선언 보존·신규 판정 (설계 §11.4, atRule null 선언 규칙만; at-rule은 step 19).
// 순수 함수: 입력 Rule 배열을 바꾸지 않는다. 결과는 정렬하지 않는다.
import { featuredCounterpart } from './design-guard-color-pairs.js';

const FONT_PROPS = new Set(['font-family', 'font']);
const sameChain = (a, b) => a.length === b.length && a.every((x, i) => x === b[i]);
const isDeclRule = (rule) => rule.atRule === null;
const fontDecls = (rule) => rule.decls.filter(([prop]) => FONT_PROPS.has(prop));
const hasDecl = (rule, prop, value) => rule.decls.some(([p, v]) => p === prop && v === value);

// 같은 file·chain, base selectors ⊆ current, current에만 있는 선택자는 모두 base 선택자의 featuredCounterpart.
export function matchesBaseRule(baseRule, currentRule) {
  if (baseRule.file !== currentRule.file || !sameChain(baseRule.chain, currentRule.chain)) return false;
  if (!baseRule.selectors.every((s) => currentRule.selectors.includes(s))) return false;
  const allowed = new Set(baseRule.selectors.map(featuredCounterpart).filter((s) => s !== null));
  return currentRule.selectors
    .filter((s) => !baseRule.selectors.includes(s))
    .every((s) => allowed.has(s));
}

export function checkFontDecls({ baseRules, currentRules }) {
  const out = [];
  const seen = new Set();
  const push = (s) => { if (!seen.has(s)) { seen.add(s); out.push(s); } };
  const bases = baseRules.filter(isDeclRule);
  const currents = currentRules.filter(isDeclRule);

  // (1) 보존: BASE 순.
  for (const base of bases) {
    for (const [prop, value] of fontDecls(base)) {
      if (!currents.some((cur) => matchesBaseRule(base, cur) && hasDecl(cur, prop, value))) {
        push(`font-decl-missing:${base.chain.join(' > ')}|${base.selectors.join(', ')}|${prop}`);
      }
    }
  }
  // (2) 신규: 현재 순·선언 순.
  for (const cur of currents) {
    for (const [prop, value] of fontDecls(cur)) {
      if (!bases.some((base) => matchesBaseRule(base, cur) && hasDecl(base, prop, value))) {
        push(`font-asset:${cur.selectors.join(', ')}`);
      }
    }
  }
  return out;
}
