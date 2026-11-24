// step 14 — 색 어휘·COLOR_PROPS·양방향 token 그래프 (설계 §11.4). 순수 함수, fs·Git 없음, 입력을 바꾸지 않는다.

// CSS Color 4 named colors 148개 + transparent (소문자).
export const NAMED_COLORS = new Set([
  'aliceblue', 'antiquewhite', 'aqua', 'aquamarine', 'azure', 'beige', 'bisque', 'black',
  'blanchedalmond', 'blue', 'blueviolet', 'brown', 'burlywood', 'cadetblue', 'chartreuse', 'chocolate',
  'coral', 'cornflowerblue', 'cornsilk', 'crimson', 'cyan', 'darkblue', 'darkcyan', 'darkgoldenrod',
  'darkgray', 'darkgreen', 'darkgrey', 'darkkhaki', 'darkmagenta', 'darkolivegreen', 'darkorange', 'darkorchid',
  'darkred', 'darksalmon', 'darkseagreen', 'darkslateblue', 'darkslategray', 'darkslategrey', 'darkturquoise', 'darkviolet',
  'deeppink', 'deepskyblue', 'dimgray', 'dimgrey', 'dodgerblue', 'firebrick', 'floralwhite', 'forestgreen',
  'fuchsia', 'gainsboro', 'ghostwhite', 'gold', 'goldenrod', 'gray', 'green', 'greenyellow',
  'grey', 'honeydew', 'hotpink', 'indianred', 'indigo', 'ivory', 'khaki', 'lavender',
  'lavenderblush', 'lawngreen', 'lemonchiffon', 'lightblue', 'lightcoral', 'lightcyan', 'lightgoldenrodyellow', 'lightgray',
  'lightgreen', 'lightgrey', 'lightpink', 'lightsalmon', 'lightseagreen', 'lightskyblue', 'lightslategray', 'lightslategrey',
  'lightsteelblue', 'lightyellow', 'lime', 'limegreen', 'linen', 'magenta', 'maroon', 'mediumaquamarine',
  'mediumblue', 'mediumorchid', 'mediumpurple', 'mediumseagreen', 'mediumslateblue', 'mediumspringgreen', 'mediumturquoise', 'mediumvioletred',
  'midnightblue', 'mintcream', 'mistyrose', 'moccasin', 'navajowhite', 'navy', 'oldlace', 'olive',
  'olivedrab', 'orange', 'orangered', 'orchid', 'palegoldenrod', 'palegreen', 'paleturquoise', 'palevioletred',
  'papayawhip', 'peachpuff', 'peru', 'pink', 'plum', 'powderblue', 'purple', 'rebeccapurple',
  'red', 'rosybrown', 'royalblue', 'saddlebrown', 'salmon', 'sandybrown', 'seagreen', 'seashell',
  'sienna', 'silver', 'skyblue', 'slateblue', 'slategray', 'slategrey', 'snow', 'springgreen',
  'steelblue', 'tan', 'teal', 'thistle', 'tomato', 'turquoise', 'violet', 'wheat',
  'white', 'whitesmoke', 'yellow', 'yellowgreen',
  'transparent',
]);

// hex 또는 바깥 색 함수 토큰(함수명 대소문자 무시, identifier 경계, 함수명 뒤 선택적 공백).
export const COLOR_LITERAL_RE = /#[0-9a-fA-F]{3,8}\b|(?<![A-Za-z0-9_-])(?:rgb|rgba|hsl|hsla|hwb|lab|lch|oklab|oklch|color|color-mix)\s*\(/i;

export const COLOR_PROPS = new Set([
  'color', 'background', 'background-color', 'background-image',
  'border', 'border-top', 'border-right', 'border-bottom', 'border-left',
  'border-color', 'border-top-color', 'border-right-color', 'border-bottom-color', 'border-left-color',
  'border-block', 'border-block-start', 'border-block-end',
  'border-block-color', 'border-block-start-color', 'border-block-end-color',
  'border-inline', 'border-inline-start', 'border-inline-end',
  'border-inline-color', 'border-inline-start-color', 'border-inline-end-color',
  'outline', 'outline-color', 'column-rule', 'column-rule-color',
  'text-decoration', 'text-decoration-color', 'text-emphasis', 'text-emphasis-color',
  '-webkit-text-fill-color', '-webkit-text-stroke', '-webkit-text-stroke-color',
  'fill', 'stroke', 'stop-color', 'flood-color', 'lighting-color',
  'box-shadow', 'text-shadow', 'caret-color', 'accent-color', 'scrollbar-color',
]);

// 값이 `0`·`none`이면 색이 아닌 shorthand.
const NONE_SHORTHANDS = new Set([
  'border', 'border-top', 'border-right', 'border-bottom', 'border-left',
  'border-block', 'border-block-start', 'border-block-end',
  'border-inline', 'border-inline-start', 'border-inline-end',
  'outline', 'column-rule', 'text-decoration', 'text-emphasis', '-webkit-text-stroke',
]);

const IDENT_CHAR = /[A-Za-z0-9_-]/;

// text[i..]가 identifier 경계의 `name(`이면 true(대소문자 무시).
function isFuncStart(text, i, name) {
  const open = `${name}(`;
  if (text.slice(i, i + open.length).toLowerCase() !== open) return false;
  return i === 0 || !IDENT_CHAR.test(text[i - 1]);
}

// 따옴표 문자열 끝 다음 위치(이스케이프 포함).
function skipString(text, i) {
  const q = text[i];
  let j = i + 1;
  while (j < text.length) {
    if (text[j] === '\\') { j += 2; continue; }
    if (text[j] === q) return j + 1;
    j += 1;
  }
  return text.length;
}

// `url(` 시작 위치에서 닫는 `)` 다음 위치(따옴표·이스케이프 고려, 중첩 없음).
function skipUrl(text, i) {
  let j = i + 4;
  while (j < text.length) {
    const c = text[j];
    if (c === '\\') { j += 2; continue; }
    if (c === '"' || c === "'") { j = skipString(text, j); continue; }
    if (c === ')') return j + 1;
    j += 1;
  }
  return text.length;
}

// `var(` 시작 위치에서 짝 맞는 `)` 다음 위치(문자열·url() 고려).
function skipVar(text, i) {
  let depth = 0;
  let j = i + 3;
  while (j < text.length) {
    const c = text[j];
    if (c === '\\') { j += 2; continue; }
    if (c === '"' || c === "'") { j = skipString(text, j); continue; }
    if (isFuncStart(text, j, 'url')) { j = skipUrl(text, j); continue; }
    if (c === '(') depth += 1;
    else if (c === ')') { depth -= 1; if (depth === 0) return j + 1; }
    j += 1;
  }
  return text.length;
}

// 따옴표 문자열과 url(…) (그리고 dropVar면 var(…))를 공백으로 바꾼 새 문자열.
function stripOpaque(value, dropVar) {
  const text = String(value);
  let out = '';
  let i = 0;
  while (i < text.length) {
    const c = text[i];
    if (c === '\\') { out += text.slice(i, i + 2); i += 2; continue; }
    if (c === '"' || c === "'") { i = skipString(text, i); out += ' '; continue; }
    if (isFuncStart(text, i, 'url')) { i = skipUrl(text, i); out += ' '; continue; }
    if (dropVar && isFuncStart(text, i, 'var')) { i = skipVar(text, i); out += ' '; continue; }
    out += c;
    i += 1;
  }
  return out;
}

// 값의 식별자 목록(문자열·url()·var() 인자 제외, 숫자 단위·hex 조각 제외), 등장 순 원문.
export function valueIdentifiers(value) {
  return stripOpaque(value, true).match(/(?<![A-Za-z0-9_#.\\-])-?[A-Za-z_][A-Za-z0-9_-]*/g) ?? [];
}

// var() 참조 이름(중첩 fallback 포함), 등장 순. 문자열·url() 안은 제외.
export function varRefs(value) {
  const text = stripOpaque(value, false);
  return [...text.matchAll(/(?<![A-Za-z0-9_-])var\(\s*(--[A-Za-z0-9_-]+)/gi)].map((m) => m[1]);
}

export function isColorLiteralValue(value) {
  if (COLOR_LITERAL_RE.test(stripOpaque(value, false))) return true;
  return valueIdentifiers(value).some((id) => {
    const lower = id.toLowerCase();
    return lower === 'currentcolor' || NAMED_COLORS.has(lower);
  });
}

export function isColorDecl([prop, value]) {
  if (prop.startsWith('--')) return false;
  if (!COLOR_PROPS.has(prop)) return false;
  if (NONE_SHORTHANDS.has(prop)) {
    const v = String(value).replace(/!\s*important\s*$/i, '').trim().toLowerCase();
    if (v === '0' || v === 'none') return false;
  }
  return true;
}

export function customPropertyDefs(rules) {
  const defs = [];
  for (const rule of rules) {
    for (const [prop, value] of rule.decls) {
      if (!prop.startsWith('--')) continue;
      defs.push({ file: rule.file, chain: [...rule.chain], selectors: [...rule.selectors], name: prop, value });
    }
  }
  return defs;
}

// 시작 = 리터럴 정의 이름 ∪ 색 선언이 var()로 참조하는 이름; 별칭 간선(정의 이름 ↔ 값의 varRefs)을 양방향으로 따라 고정점.
export function colorTokenSet(rules) {
  const set = new Set();
  const edges = new Map();
  const link = (a, b) => {
    if (!edges.has(a)) edges.set(a, new Set());
    edges.get(a).add(b);
  };
  for (const { name, value } of customPropertyDefs(rules)) {
    if (isColorLiteralValue(value)) set.add(name);
    for (const ref of varRefs(value)) { link(name, ref); link(ref, name); }
  }
  for (const rule of rules) {
    for (const decl of rule.decls) {
      if (isColorDecl(decl)) for (const ref of varRefs(decl[1])) set.add(ref);
    }
  }
  const queue = [...set];
  while (queue.length) {
    const n = queue.pop();
    for (const m of edges.get(n) ?? []) {
      if (!set.has(m)) { set.add(m); queue.push(m); }
    }
  }
  return set;
}

export function isColorValue(value, colorTokens) {
  return isColorLiteralValue(value) || varRefs(value).some((n) => colorTokens.has(n));
}
