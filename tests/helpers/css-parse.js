// step 13 — 순수 CSS 파서 (설계 §11.4). fs·Git·외부 파서 없음, 입력을 바꾸지 않는다.
// Rule = { file, chain, selectors, decls, atRule, prelude, index }
//   chain    : 바깥 at-rule prelude 목록(공백 정규화, 예 '@media (max-width: 768px)')
//   selectors: 최상위 쉼표로 분리·공백 정규화한 선택자 목록(at-rule Rule은 [])
//   decls    : [prop, value] 등장 순(prop 소문자, custom property 원문; value normalizeValue)
//   atRule   : 일반 규칙 null, 그 밖 '@import'·'@charset'·'@font-face' 등
//   prelude  : 일반 규칙·@font-face null, @import·@charset 등은 at-keyword 뒤~';' 앞 정규화
//   index    : file 안 등장 순서(중첩 포함, 0부터)

// 이 at-rule 블록은 Rule이 아니라 chain 단계로 재귀한다.
const NESTING_AT_RULES = new Set(['@media', '@supports', '@layer', '@container', '@scope', '@starting-style', '@document']);
const isNesting = (name) => NESTING_AT_RULES.has(name) || /^@(-[a-z]+-)?keyframes$/.test(name);

const WS = /\s/;

// text[i]가 따옴표면 문자열 끝 다음 위치(이스케이프 포함, 닫히지 않으면 end)를 반환.
function skipString(text, i, end) {
  const q = text[i];
  let j = i + 1;
  while (j < end) {
    const c = text[j];
    if (c === '\\') { j += 2; continue; }
    if (c === q) return j + 1;
    j += 1;
  }
  return end;
}

// text[i..]가 식별자 경계의 `url(`이면 true.
function isUrlStart(text, i) {
  if (text.slice(i, i + 4).toLowerCase() !== 'url(') return false;
  return i === 0 || !/[A-Za-z0-9_-]/.test(text[i - 1]);
}

// `url(` 시작 위치에서 닫는 `)` 다음 위치를 반환(따옴표·이스케이프 고려).
function skipUrl(text, i, end) {
  let j = i + 4;
  while (j < end) {
    const c = text[j];
    if (c === '\\') { j += 2; continue; }
    if (c === '"' || c === "'") { j = skipString(text, j, end); continue; }
    if (c === ')') return j + 1;
    j += 1;
  }
  return end;
}

// 주석을 공백 하나로 바꾼 새 문자열(문자열·url() 내용은 원문).
function stripComments(text) {
  let out = '';
  let i = 0;
  const end = text.length;
  while (i < end) {
    const c = text[i];
    if (c === '\\') { out += text.slice(i, i + 2); i += 2; continue; }
    if (c === '"' || c === "'") { const j = skipString(text, i, end); out += text.slice(i, j); i = j; continue; }
    if (isUrlStart(text, i)) { const j = skipUrl(text, i, end); out += text.slice(i, j); i = j; continue; }
    if (c === '/' && text[i + 1] === '*') {
      const close = text.indexOf('*/', i + 2);
      i = close < 0 ? end : close + 2;
      out += ' ';
      continue;
    }
    out += c;
    i += 1;
  }
  return out;
}

// [i, end)에서 괄호·대괄호·중괄호 깊이 0인 stops 문자의 첫 위치(없으면 end).
// stops에 없는 '{'는 깊이를 올리고, 깊이 0의 '}'가 stops에 있으면 그 위치를 반환한다.
function findTopLevel(text, i, end, stops) {
  let paren = 0;
  let brace = 0;
  while (i < end) {
    const c = text[i];
    if (c === '\\') { i += 2; continue; }
    if (c === '"' || c === "'") { i = skipString(text, i, end); continue; }
    if (isUrlStart(text, i)) { i = skipUrl(text, i, end); continue; }
    if (paren === 0 && brace === 0 && stops.includes(c)) return i;
    if (c === '(' || c === '[') paren += 1;
    else if ((c === ')' || c === ']') && paren > 0) paren -= 1;
    else if (c === '{') brace += 1;
    else if (c === '}' && brace > 0) brace -= 1;
    i += 1;
  }
  return end;
}

// 문자열·url() 밖의 연속 공백을 한 칸으로 줄이고 trim한다(그 안의 내용은 원문).
export function normalizeValue(value) {
  const text = String(value);
  const end = text.length;
  let out = '';
  let i = 0;
  while (i < end) {
    const c = text[i];
    if (c === '\\') { out += text.slice(i, i + 2); i += 2; continue; }
    if (c === '"' || c === "'") { const j = skipString(text, i, end); out += text.slice(i, j); i = j; continue; }
    if (isUrlStart(text, i)) { const j = skipUrl(text, i, end); out += text.slice(i, j); i = j; continue; }
    if (WS.test(c)) {
      while (i < end && WS.test(text[i])) i += 1;
      out += ' ';
      continue;
    }
    out += c;
    i += 1;
  }
  return out.trim();
}

// 최상위 쉼표로만 분리(`:is(a, b)`·`[data-x="a,b"]` 유지), 각 선택자 공백 정규화, 빈 항목 제외.
export function splitSelectors(text) {
  const src = String(text);
  const parts = [];
  let i = 0;
  while (i <= src.length) {
    const j = findTopLevel(src, i, src.length, ',');
    parts.push(normalizeValue(src.slice(i, j)));
    i = j + 1;
  }
  return parts.filter((s) => s !== '');
}

function parseDecls(text, start, end) {
  const decls = [];
  let i = start;
  while (i < end) {
    const j = findTopLevel(text, i, end, ';');
    const piece = text.slice(i, j);
    const colon = piece.indexOf(':');
    if (colon > 0) {
      const rawProp = piece.slice(0, colon).trim();
      if (rawProp !== '') {
        const prop = rawProp.startsWith('--') ? rawProp : rawProp.toLowerCase();
        decls.push([prop, normalizeValue(piece.slice(colon + 1))]);
      }
    }
    i = j + 1;
  }
  return decls;
}

function parseBlock(text, start, end, chain, ctx) {
  let i = start;
  while (i < end) {
    while (i < end && WS.test(text[i])) i += 1;
    if (i >= end) break;
    const c = text[i];
    if (c === '}' || c === ';') { i += 1; continue; }

    if (c === '@') {
      const m = /^@[-A-Za-z0-9_]+/.exec(text.slice(i, Math.min(end, i + 256)));
      const name = (m ? m[0] : '@').toLowerCase();
      const afterName = i + (m ? m[0].length : 1);
      const stop = findTopLevel(text, afterName, end, '{;}');
      const rawPrelude = text.slice(afterName, stop);
      if (stop >= end || text[stop] !== '{') {
        // 문(statement) at-rule: @import·@charset 등
        const prelude = normalizeValue(rawPrelude);
        ctx.rules.push(makeRule(ctx, chain, [], [], name, prelude === '' ? null : prelude));
        i = stop + (stop < end && text[stop] === ';' ? 1 : 0);
        continue;
      }
      const close = findTopLevel(text, stop + 1, end, '}');
      if (isNesting(name)) {
        parseBlock(text, stop + 1, close, [...chain, normalizeValue(`${name} ${rawPrelude}`)], ctx);
      } else {
        // 선언 블록 at-rule: @font-face(prelude null), @page 등
        const norm = normalizeValue(rawPrelude);
        const prelude = name === '@font-face' || norm === '' ? null : norm;
        ctx.rules.push(makeRule(ctx, chain, [], parseDecls(text, stop + 1, close), name, prelude));
      }
      i = close + 1;
      continue;
    }

    const stop = findTopLevel(text, i, end, '{;}');
    if (stop >= end || text[stop] !== '{') {
      // 블록 없는 조각(잘못된 선언 등)은 건너뛴다.
      i = stop + 1;
      continue;
    }
    const close = findTopLevel(text, stop + 1, end, '}');
    ctx.rules.push(makeRule(ctx, chain, splitSelectors(text.slice(i, stop)), parseDecls(text, stop + 1, close), null, null));
    i = close + 1;
  }
}

function makeRule(ctx, chain, selectors, decls, atRule, prelude) {
  return { file: ctx.file, chain: [...chain], selectors, decls, atRule, prelude, index: ctx.rules.length };
}

export function parseCssRules(text, file) {
  const src = stripComments(String(text ?? ''));
  const ctx = { file, rules: [] };
  parseBlock(src, 0, src.length, [], ctx);
  return ctx.rules;
}
