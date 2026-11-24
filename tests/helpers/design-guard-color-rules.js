// step 16 — 색 선언 규칙 4~8과 checkColorRules 진단 순서·중복 제거 (설계 §11.4).
// 순수 함수: 입력을 바꾸지 않는다. custom property 선언은 다루지 않는다(token 판정은 step 17).
import {
  NAMED_COLORS, isColorDecl, isColorValue, isColorLiteralValue, valueIdentifiers, varRefs,
} from './color-vocab.js';
import { pairColorRules, checkColorRulePairs } from './design-guard-color-pairs.js';

const isCustom = ([prop]) => prop.startsWith('--');
const sameDecl = (a, b) => a[0] === b[0] && a[1] === b[1];
const hasDecl = (decls, d) => decls.some((x) => sameDecl(x, d));
const sameList = (a, b) => a.length === b.length && a.every((x, i) => x === b[i]);
const selectorsLabel = (rule) => rule.selectors.join(', ');

// BASE 색 선언 배열: 비-custom 색 선언 등장 순.
const colorDecls = (rule) => rule.decls.filter((d) => !isCustom(d) && isColorDecl(d));

// 값에 currentColor·named color 식별자가 있는가.
const hasKeywordColor = (value) => valueIdentifiers(value).some((id) => {
  const lower = id.toLowerCase();
  return lower === 'currentcolor' || NAMED_COLORS.has(lower);
});

// 규칙 7 예외: selectors 모두 :focus-visible, 선언이 outline·outline-offset뿐, 리터럴 없음, varRefs ⊆ colorTokens.
function isFocusOutlineException(rule, colorTokens) {
  if (rule.selectors.length === 0 || !rule.selectors.every((s) => s.includes(':focus-visible'))) return false;
  const decls = rule.decls.filter((d) => !isCustom(d));
  if (decls.length === 0) return false;
  return decls.every(([prop, value]) => (prop === 'outline' || prop === 'outline-offset')
    && !isColorLiteralValue(value)
    && varRefs(value).every((n) => colorTokens.has(n)));
}

export function checkColorRules({ baseRules, currentRules, colorTokens }) {
  const out = [];
  const seen = new Set();
  const push = (s) => { if (!seen.has(s)) { seen.add(s); out.push(s); } };
  for (const s of checkColorRulePairs({ baseRules, currentRules })) push(s);

  const pairs = pairColorRules(baseRules, currentRules);
  const paired = new Set();

  // 규칙 4→5→6: 짝 있는 BASE 색 Rule, BASE 순.
  for (const { base, current } of pairs) {
    if (current === null) continue;
    paired.add(current);
    const label = selectorsLabel(base);
    const baseArr = colorDecls(base);
    const curDecls = current.decls.filter((d) => !isCustom(d));
    let changed = false;
    for (const d of baseArr) {
      if (!hasDecl(curDecls, d)) { changed = true; push(`color-decl-changed:${label}`); }
    }
    if (!changed) {
      const sub = curDecls.filter((d) => hasDecl(baseArr, d));
      const same = sub.length === baseArr.length && sub.every((d, i) => sameDecl(d, baseArr[i]));
      if (!same) push(`color-decl-reordered:${label}`);
    }
    for (const d of curDecls) {
      if (hasDecl(base.decls, d)) continue;
      if (isColorDecl(d) || isColorValue(d[1], colorTokens)) push(`color-decl-new:${label}`);
    }
  }

  // 규칙 7→8: 짝 없는 현재 Rule, 현재 순·선언 순.
  for (const rule of currentRules) {
    if (paired.has(rule)) continue;
    const label = selectorsLabel(rule);
    const decls = rule.decls.filter((d) => !isCustom(d));
    if (!isFocusOutlineException(rule, colorTokens)) {
      for (const d of decls) {
        if (isColorDecl(d) || isColorValue(d[1], colorTokens)) push(`color-decl-new:${label}`);
      }
    }
    for (const d of decls) {
      if (isColorDecl(d) || !hasKeywordColor(d[1])) continue;
      const inBase = baseRules.some((b) => b.file === rule.file
        && sameList(b.chain, rule.chain)
        && sameList(b.selectors, rule.selectors)
        && hasDecl(b.decls, d));
      if (!inBase) push(`color-decl-new:${label}`);
    }
  }
  return out;
}
