// step 19 — 서체·asset·content·weight·unknown-token 판정과 checkCss (설계 §11.4).
// 순수 함수: 입력 Rule 배열을 바꾸지 않는다. 결과는 정렬하지 않는다.
import { parseCssRules } from './css-parse.js';
import { varRefs, customPropertyDefs } from './color-vocab.js';
import { checkColors } from './design-guard-color.js';
import { checkFontDecls, matchesBaseRule } from './design-guard-font.js';

const STYLE_FILE = 'css/style.css';
const THEMES_FILE = 'css/themes.css';
const ALLOWED_CONTENT = new Set(['none', "''", '""', 'normal']);
const URL_RE = /url\(/i;

const sameChain = (a, b) => a.length === b.length && a.every((x, i) => x === b[i]);
const sameDecls = (a, b) => a.length === b.length && a.every(([p, v], i) => p === b[i][0] && v === b[i][1]);
const isCustom = (prop) => prop.startsWith('--');
const hasDecl = (rule, prop, value) => rule.decls.some(([p, v]) => p === prop && v === value);

// 같은 위치(matchesBaseRule)의 BASE Rule에 같은 (prop, value)가 없으면 새 선언.
const isNewDecl = (bases, cur, prop, value) =>
  !bases.some((base) => matchesBaseRule(base, cur) && hasDecl(base, prop, value));

export function checkTypeAndAssets({ baseRules, currentRules }) {
  const out = [];
  const seen = new Set();
  const push = (s) => { if (!seen.has(s)) { seen.add(s); out.push(s); } };

  // 서체 결과 선행.
  for (const s of checkFontDecls({ baseRules, currentRules })) push(s);

  const baseDeclRules = baseRules.filter((r) => r.atRule === null);
  const baseWeights = new Set(
    baseRules
      .filter((r) => r.atRule === null && r.file === STYLE_FILE)
      .flatMap((r) => r.decls.filter(([p]) => p === 'font-weight').map(([, v]) => v)),
  );
  const known = new Set([...customPropertyDefs(baseRules), ...customPropertyDefs(currentRules)].map((d) => d.name));

  for (const cur of currentRules) {
    if (cur.atRule === '@import') {
      const same = baseRules.some((b) => b.atRule === '@import' && b.file === cur.file
        && sameChain(b.chain, cur.chain) && b.prelude === cur.prelude);
      if (!same) push('asset:@import');
      continue;
    }
    if (cur.atRule === '@font-face') {
      const same = baseRules.some((b) => b.atRule === '@font-face' && b.file === cur.file
        && sameChain(b.chain, cur.chain) && sameDecls(b.decls, cur.decls));
      if (!same) {
        push('font-asset:@font-face');
        if (cur.decls.some(([, v]) => URL_RE.test(v))) push('asset:@font-face');
      }
    }
    for (const [prop, value] of cur.decls) {
      if (cur.atRule === null) {
        const selectors = cur.selectors.join(', ');
        if (prop === 'font-weight' && !baseWeights.has(value)) push(`font-weight:${value}`);
        if (URL_RE.test(value) && isNewDecl(baseDeclRules, cur, prop, value)) push(`asset:${selectors}`);
        if (prop === 'content' && !ALLOWED_CONTENT.has(value) && isNewDecl(baseDeclRules, cur, prop, value)) {
          push(`content:${selectors}`);
        }
      }
      if (!isCustom(prop)) {
        for (const name of varRefs(value)) {
          if (!known.has(name)) push(`unknown-token:${name}`);
        }
      }
    }
  }
  return out;
}

export function checkCss({ baseCss, currentCss, baseThemes, currentThemes }) {
  const baseRules = [...parseCssRules(baseCss, STYLE_FILE), ...parseCssRules(baseThemes, THEMES_FILE)];
  const currentRules = [...parseCssRules(currentCss, STYLE_FILE), ...parseCssRules(currentThemes, THEMES_FILE)];
  const out = [...checkColors({ baseRules, currentRules }), ...checkTypeAndAssets({ baseRules, currentRules })];
  if (currentThemes !== baseThemes) out.push('themes-changed');
  return out;
}
