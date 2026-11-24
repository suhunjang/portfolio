// step 17 — 색 토큰 위치 키 중복(규칙 0)·보존(규칙 1~3)과 checkColors (설계 §11.4).
// 순수 함수: 입력을 바꾸지 않는다. 위치 키 = (file, chain, selectors, name).
import { customPropertyDefs, colorTokenSet, isColorValue } from './color-vocab.js';
import { checkColorRules } from './design-guard-color-rules.js';

const keyOf = (d) => JSON.stringify([d.file, d.chain, d.selectors, d.name]);

// 키별 정의 묶음(첫 등장 순 Map).
function groupDefs(rules) {
  const groups = new Map();
  for (const d of customPropertyDefs(rules)) {
    const k = keyOf(d);
    if (!groups.has(k)) groups.set(k, []);
    groups.get(k).push(d);
  }
  return groups;
}

const dupLabel = (d, n) => {
  const chain = d.chain.length ? d.chain.join(' > ') : '-';
  return `색 토큰 중복 정의: ${d.name} @ ${d.file} ${chain} ${d.selectors.join(', ')} (count=${n})`;
};

export function checkColorTokens({ baseRules, currentRules, colorTokens }) {
  const out = [];
  const seen = new Set();
  const push = (s) => { if (!seen.has(s)) { seen.add(s); out.push(s); } };

  const cur = groupDefs(currentRules);
  const excluded = new Set();

  // 규칙 0: 현재 키 첫 등장 순.
  for (const [k, defs] of cur) {
    if (defs.length < 2) continue;
    const name = defs[0].name;
    if (colorTokens.has(name) || defs.some((d) => isColorValue(d.value, colorTokens))) {
      excluded.add(k);
      push(dupLabel(defs[0], defs.length));
    }
  }

  const count = (k) => (cur.get(k) ?? []).length;
  const baseDefs = customPropertyDefs(baseRules);
  const baseKeys = new Set(baseDefs.map(keyOf));

  // 규칙 1: BASE color token 정의, BASE 순.
  for (const d of baseDefs) {
    if (!colorTokens.has(d.name)) continue;
    const k = keyOf(d);
    if (excluded.has(k)) continue;
    const n = count(k);
    if (n === 0) push(`color-token-removed:${d.name}`);
    else if (n === 1 && cur.get(k)[0].value !== d.value) push(`color-token-changed:${d.name}`);
  }

  // 규칙 2: BASE에 없는 키, 현재 정확히 하나, 현재 순.
  for (const [k, defs] of cur) {
    if (baseKeys.has(k) || excluded.has(k) || defs.length !== 1) continue;
    const { name, value } = defs[0];
    if (colorTokens.has(name)) push(`color-token-redefined:${name}`);
    else if (isColorValue(value, colorTokens)) push(`color-token-added:${name}`);
  }

  // 규칙 3: BASE 비색 custom property가 현재 정확히 하나이고 색 값으로, BASE 순.
  for (const d of baseDefs) {
    if (colorTokens.has(d.name)) continue;
    const k = keyOf(d);
    if (excluded.has(k) || count(k) !== 1) continue;
    if (isColorValue(cur.get(k)[0].value, colorTokens)) push(`color-token-added:${d.name}`);
  }
  return out;
}

export function checkColors({ baseRules, currentRules }) {
  const colorTokens = colorTokenSet(baseRules);
  return [
    ...checkColorRules({ baseRules, currentRules, colorTokens }),
    ...checkColorTokens({ baseRules, currentRules, colorTokens }),
  ];
}
