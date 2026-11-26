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

// compact step 9 (설계 §C6) — color-contrast 수정 선언 단위 예외. 원소 {file, chain, selector, occurrence, prop, base, to},
// (file, chain, selector, occurrence, prop) 순 정렬. occurrence = 같은 file·chain·selector BASE Rule 중 순번(0부터).
export const HOO81_COLOR_V52_ALLOW = [
  { file: 'css/style.css', chain: [], selector: '.about-avatar', occurrence: 0, prop: 'color', base: '#fff', to: 'var(--bg-elev)' },
  { file: 'css/style.css', chain: [], selector: '.about-meta dt', occurrence: 0, prop: 'color', base: 'var(--text-faint)', to: 'var(--text-muted)' },
  { file: 'css/style.css', chain: [], selector: '.brand-mark', occurrence: 0, prop: 'color', base: '#fff', to: 'var(--bg-elev)' },
  { file: 'css/style.css', chain: [], selector: '.btn-primary', occurrence: 0, prop: 'color', base: '#fff', to: 'var(--bg-elev)' },
  { file: 'css/style.css', chain: [], selector: '.footer-inner', occurrence: 0, prop: 'color', base: 'var(--text-faint)', to: 'var(--text-muted)' },
  { file: 'css/style.css', chain: [], selector: '.stat-label', occurrence: 0, prop: 'color', base: 'var(--text-faint)', to: 'var(--text-muted)' },
];

// BASE Rule이 같은 file·chain·selector BASE Rule 중 몇 번째인가(0부터).
const occurrenceOf = (baseRules, rule) => baseRules.filter((b) => b.file === rule.file
  && sameList(b.chain, rule.chain)
  && selectorsLabel(b) === selectorsLabel(rule)
  && b.index < rule.index).length;

// 짝 base·current의 비-custom 선언: 허용 항목과 정확히 맞는 선언 하나만 값 `to`를 `base`로 읽는다.
function allowedDecls(base, current, baseRules, allow) {
  const decls = current.decls.filter((d) => !isCustom(d));
  const occ = occurrenceOf(baseRules, base);
  for (const e of allow) {
    if (e.file !== base.file || !sameList(e.chain, base.chain) || e.selector !== selectorsLabel(base)
      || e.occurrence !== occ || !hasDecl(base.decls, [e.prop, e.base])) continue;
    const i = decls.findIndex((d) => d[0] === e.prop && d[1] === e.to);
    if (i >= 0) decls[i] = [e.prop, e.base];
  }
  return decls;
}

export function checkColorRules({ baseRules, currentRules, colorTokens, allow = HOO81_COLOR_V52_ALLOW }) {
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
    const curDecls = allowedDecls(base, current, baseRules, allow);
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

// compact step 9 (설계 §C6, 2026-11-26 대표 결정) — BASE css에 HOO81_COLOR_V52_ALLOW 선언만 base→to로 적용한다.
// 다른 선언은 바이트 그대로 둔다. 최상위(chain []) rule만, 주석 없는 블록만, 정확히 선언 경계로 1개 일치할 때만 바꾸고 아니면 throw한다.
export function applyColorAllow(css, allow = HOO81_COLOR_V52_ALLOW) {
  const esc = (t) => t.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
  const depthAt = (text, pos) => {
    let d = 0;
    for (let k = 0; k < pos; k += 1) { if (text[k] === '{') d += 1; else if (text[k] === '}') d -= 1; }
    return d;
  };
  let out = css;
  for (const e of allow) {
    if (e.file !== 'css/style.css' || e.chain.length !== 0) throw new Error(`unsupported allow entry: ${e.selector}`);
    const starts = [];
    const re = new RegExp(`^${esc(e.selector)} \\{`, 'gm');
    for (let m; (m = re.exec(out)); ) if (depthAt(out, m.index) === 0) starts.push(m.index);
    const s = starts[e.occurrence];
    if (s === undefined) throw new Error(`rule not found: ${e.selector}#${e.occurrence}`);
    const open = out.indexOf('{', s);
    const end = out.indexOf('}', open);
    const body = out.slice(open + 1, end);
    if (body.includes('/*') || body.includes('{')) throw new Error(`unsupported block: ${e.selector}`);
    const declRe = new RegExp(`(^|;)(\\s*)${esc(e.prop)}\\s*:\\s*${esc(e.base)}\\s*(?=;)`, 'g');
    const hits = [...body.matchAll(declRe)];
    if (hits.length !== 1) throw new Error(`decl not unique: ${e.selector} ${e.prop}: ${e.base} (${hits.length})`);
    const h = hits[0];
    const at = open + 1 + h.index + h[1].length + h[2].length;
    const len = h[0].length - h[1].length - h[2].length;
    out = out.slice(0, at) + `${e.prop}: ${e.to}` + out.slice(at + len);
  }
  return out;
}
