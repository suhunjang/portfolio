// step 28 — axe canonical target (설계 §6.1·§6.2): ALIASES · canonicalTargetInPage · canonicalFromDescriptor · runAxe
import AxeBuilder from '@axe-core/playwright';
import { norm } from './content.js';

// 숫자를 `#`로 바꾼 뒤 적용하는 textSig alias (§6.1).
export const ALIASES = Object.freeze({
  '## — Stack & Contact': '## — Contact',
  '기술 스택 & 연락처': '연락처',
});

const TEXT_SIG_MAX = 80;
const AXE_TAGS = ['wcag2a', 'wcag2aa'];
const KEPT_IMPACTS = new Set(['serious', 'critical']);
const LANDMARK_SELECTOR = [
  'header',
  'nav',
  'main',
  'footer',
  'aside',
  'form',
  '[role="banner"]',
  '[role="navigation"]',
  '[role="main"]',
  '[role="contentinfo"]',
  '[role="complementary"]',
  '[role="region"]',
  '[role="search"]',
  '[role="form"]',
].join(', ');

function srcFileName(src) {
  const path = String(src).split(/[?#]/)[0];
  const parts = path.split('/');
  return parts[parts.length - 1];
}

function textSig(text) {
  const candidates = [text.textContent, text.ariaLabel, text.alt, text.title];
  let sig = '';
  for (const c of candidates) {
    const v = c == null ? '' : norm(c);
    if (v) {
      sig = v;
      break;
    }
  }
  if (!sig && text.src) sig = norm(srcFileName(text.src));
  sig = sig.replace(/[0-9]/g, '#');
  for (const [from, to] of Object.entries(ALIASES)) sig = sig.split(from).join(to);
  return sig.slice(0, TEXT_SIG_MAX);
}

function anchorSig(anchor) {
  switch (anchor?.kind) {
    case 'featured':
      return `featured:${anchor.value}`;
    case 'project':
      return `project:${anchor.value}`;
    case 'id':
      return `#${anchor.value}`;
    case 'landmark':
      return String(anchor.value);
    case 'document':
      return 'document';
    default:
      throw new Error(`canonicalFromDescriptor: unknown anchor kind ${anchor?.kind}`);
  }
}

// descriptor = { ruleId, anchor: { kind: featured|project|id|landmark|document, value? },
//                text: { textContent, ariaLabel, alt, title, src } }
export function canonicalFromDescriptor(descriptor) {
  const { ruleId, anchor, text } = descriptor;
  if (!ruleId || typeof ruleId !== 'string') throw new Error('canonicalFromDescriptor: ruleId required');
  return `${ruleId}::${anchorSig(anchor)}::${textSig(text || {})}`;
}

// axe target(selector 또는 frame/shadow 경로 배열의 마지막 selector)를 canonical target으로 바꾼다.
export async function canonicalTargetInPage(page, ruleId, selector) {
  const sel = Array.isArray(selector) ? selector[selector.length - 1] : selector;
  const descriptor = await page.evaluate(
    ({ sel, landmarkSelector }) => {
      const el = document.querySelector(sel);
      if (!el) return null;
      let anchor;
      const featured = el.closest('[data-featured-card][data-project]');
      const project = el.closest('[data-project]');
      const withId = el.closest('[id]');
      const landmark = el.closest(landmarkSelector);
      if (featured) anchor = { kind: 'featured', value: featured.getAttribute('data-project') };
      else if (project) anchor = { kind: 'project', value: project.getAttribute('data-project') };
      else if (withId) anchor = { kind: 'id', value: withId.id };
      else if (landmark) anchor = { kind: 'landmark', value: landmark.tagName.toLowerCase() };
      else anchor = { kind: 'document' };
      return {
        anchor,
        text: {
          textContent: el.textContent,
          ariaLabel: el.getAttribute('aria-label'),
          alt: el.getAttribute('alt'),
          title: el.getAttribute('title'),
          src: el.getAttribute('src'),
        },
      };
    },
    { sel, landmarkSelector: LANDMARK_SELECTOR },
  );
  if (!descriptor) throw new Error(`canonicalTargetInPage: target not found: ${sel}`);
  return canonicalFromDescriptor({ ruleId, ...descriptor });
}

const sortedUnique = (xs) => [...new Set(xs)].sort();

// wcag2a·wcag2aa 중 serious/critical 위반만 → [{ ruleId, impact, targets, selectors }] (ruleId 순).
export async function runAxe(page, { include } = {}) {
  let builder = new AxeBuilder({ page }).withTags(AXE_TAGS);
  if (include) builder = builder.include(include);
  const result = await builder.analyze();
  const out = [];
  for (const v of result.violations) {
    if (!KEPT_IMPACTS.has(v.impact)) continue;
    const targets = [];
    const selectors = [];
    for (const node of v.nodes) {
      const sel = node.target.map((t) => (Array.isArray(t) ? t.join(' >> ') : t)).join(' >> ');
      selectors.push(sel);
      targets.push(await canonicalTargetInPage(page, v.id, node.target[node.target.length - 1]));
    }
    out.push({ ruleId: v.id, impact: v.impact, targets: sortedUnique(targets), selectors: sortedUnique(selectors) });
  }
  return out.sort((a, b) => (a.ruleId < b.ruleId ? -1 : a.ruleId > b.ruleId ? 1 : 0));
}
