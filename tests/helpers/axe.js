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

// step 32 — axe collect tooling (설계 §6.1 entry key·§6.2 step 32)
// makeEntryKey · COLLECT_DIR · EXPECTED_FILES · resolveCollectDir · resetCollected · writeCollected · mergeCollected ·
// CLI `--reset [--dir d]`, `--merge [--dir d] [--out f]`
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';

const REPO_ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '../..');
const TMP_ROOT = path.join(REPO_ROOT, 'tests/.tmp');

export const SCENARIOS = Object.freeze(['page', 'modal', 'lightbox']);
export const PROJECTS = Object.freeze([
  'mobile-dark',
  'mobile-light',
  'tablet-dark',
  'tablet-light',
  'desktop-dark',
  'desktop-light',
]);
// 시나리오 10개(§6.1): page × 6 project, modal·lightbox × desktop dark/light.
const EXPECTED_PAIRS = Object.freeze([
  ...PROJECTS.map((p) => ['page', p]),
  ['modal', 'desktop-dark'],
  ['modal', 'desktop-light'],
  ['lightbox', 'desktop-dark'],
  ['lightbox', 'desktop-light'],
]);

export const COLLECT_DIR = 'tests/.tmp/axe-collected';
export const DEFAULT_MERGE_OUT = 'tests/fixtures/axe-collected.json';
const collectFileName = (scenario, project) => `${scenario}--${project}.json`;
export const EXPECTED_FILES = Object.freeze(EXPECTED_PAIRS.map(([s, p]) => collectFileName(s, p)).sort());

const IMPACT_RANK = { serious: 1, critical: 2 };
const byCodeUnit = (a, b) => (a < b ? -1 : a > b ? 1 : 0);

// `${scenario}:${project}:${ruleId}` — 각 값은 비어 있지 않은 문자열, `:` 금지.
export function makeEntryKey({ scenario, project, ruleId } = {}) {
  for (const [name, v] of [
    ['scenario', scenario],
    ['project', project],
    ['ruleId', ruleId],
  ]) {
    if (typeof v !== 'string' || v === '') throw new Error(`makeEntryKey: empty ${name}`);
    if (v.includes(':')) throw new Error(`makeEntryKey: ':' in ${name}: ${v}`);
  }
  return `${scenario}:${project}:${ruleId}`;
}

// 인자 > AXE_COLLECT_DIR > COLLECT_DIR. 상대 경로는 저장소 루트 기준. tests/.tmp 하위(자신 제외)만 허용.
export function resolveCollectDir(dir) {
  let chosen;
  if (dir !== undefined && dir !== null) chosen = dir;
  else if (process.env.AXE_COLLECT_DIR !== undefined && process.env.AXE_COLLECT_DIR !== '') chosen = process.env.AXE_COLLECT_DIR;
  else chosen = COLLECT_DIR;
  if (typeof chosen !== 'string' || chosen === '') throw new Error('resolveCollectDir: empty dir');
  const abs = path.resolve(REPO_ROOT, chosen);
  const rel = path.relative(TMP_ROOT, abs);
  if (rel === '' || rel.startsWith('..') || path.isAbsolute(rel)) {
    throw new Error(`resolveCollectDir: outside tests/.tmp: ${chosen}`);
  }
  // 이미 있는 구성요소가 symlink면 tests/.tmp 밖으로 나갈 수 있으므로 거부.
  let cur = TMP_ROOT;
  for (const part of rel.split(path.sep)) {
    cur = path.join(cur, part);
    let st;
    try {
      st = fs.lstatSync(cur);
    } catch {
      break;
    }
    if (st.isSymbolicLink()) throw new Error(`resolveCollectDir: symlink: ${chosen}`);
  }
  return abs;
}

// 수집 디렉터리를 비우고(없으면 만들고) 절대 경로를 돌려준다.
export function resetCollected(dir) {
  const abs = resolveCollectDir(dir);
  fs.rmSync(abs, { recursive: true, force: true });
  fs.mkdirSync(abs, { recursive: true });
  return abs;
}

function assertPair(scenario, project) {
  if (!SCENARIOS.includes(scenario)) throw new Error(`axe collect: bad scenario: ${scenario}`);
  if (!PROJECTS.includes(project)) throw new Error(`axe collect: bad project: ${project}`);
  if (!EXPECTED_PAIRS.some(([s, p]) => s === scenario && p === project)) {
    throw new Error(`axe collect: unexpected scenario/project: ${scenario}/${project}`);
  }
}

const sortedUniqueStrings = (xs) => [...new Set(xs)].sort(byCodeUnit);

// runAxe 결과 → MergedEntry[](같은 ruleId 병합, targets·selectors 고유·정렬, impact는 더 높은 쪽, key 정렬). 입력 불변.
export function violationsToEntries(scenario, project, violations) {
  assertPair(scenario, project);
  if (!Array.isArray(violations)) throw new Error('axe collect: violations not-array');
  const byKey = new Map();
  for (const v of violations) {
    if (!IMPACT_RANK[v?.impact]) throw new Error(`axe collect: bad impact: ${v?.impact}`);
    const key = makeEntryKey({ scenario, project, ruleId: v.ruleId });
    const prev = byKey.get(key);
    const targets = [...(prev?.targets || []), ...(v.targets || [])];
    const selectors = [...(prev?.selectors || []), ...(v.selectors || [])];
    const impact = prev && IMPACT_RANK[prev.impact] > IMPACT_RANK[v.impact] ? prev.impact : v.impact;
    byKey.set(key, { key, scenario, project, ruleId: v.ruleId, impact, targets, selectors });
  }
  return [...byKey.values()]
    .map((e) => ({ ...e, targets: sortedUniqueStrings(e.targets), selectors: sortedUniqueStrings(e.selectors) }))
    .sort((a, b) => byCodeUnit(a.key, b.key));
}

// 시나리오 1개 결과를 `{scenario}--{project}.json`으로 쓴다(덮어쓰기). 쓴 절대 경로를 돌려준다.
export function writeCollected(scenario, project, violations, { dir } = {}) {
  const entries = violationsToEntries(scenario, project, violations);
  const abs = resolveCollectDir(dir);
  fs.mkdirSync(abs, { recursive: true });
  const file = path.join(abs, collectFileName(scenario, project));
  fs.writeFileSync(file, JSON.stringify({ scenario, project, entries }, null, 2) + '\n');
  return file;
}

function resolveMergeOut(out) {
  const abs = path.resolve(REPO_ROOT, out);
  const rel = path.relative(TMP_ROOT, abs);
  const inTmp = rel !== '' && !rel.startsWith('..') && !path.isAbsolute(rel);
  if (!inTmp && abs !== path.join(REPO_ROOT, DEFAULT_MERGE_OUT)) {
    throw new Error(`mergeCollected: out must be ${DEFAULT_MERGE_OUT} or under tests/.tmp: ${out}`);
  }
  return abs;
}

// EXPECTED_FILES 10개를 정확히 읽어 MergedEntry[](key 정렬)로 합친다. 문제가 있으면 Error(problems)로 throw하고 쓰지 않는다.
export function mergeCollected({ collectDir, out } = {}) {
  const abs = resolveCollectDir(collectDir);
  const outAbs = out === undefined || out === null ? null : resolveMergeOut(out);
  const present = fs.existsSync(abs) ? fs.readdirSync(abs) : [];
  const problems = [];
  for (const f of EXPECTED_FILES) if (!present.includes(f)) problems.push(`missing:${f}`);
  const outName = outAbs && path.dirname(outAbs) === abs ? path.basename(outAbs) : null;
  for (const f of [...present].sort(byCodeUnit)) {
    if (!EXPECTED_FILES.includes(f) && f !== outName) problems.push(`extra:${f}`);
  }
  const entries = [];
  if (problems.length === 0) {
    for (const f of EXPECTED_FILES) {
      const [scenario, project] = f.replace(/\.json$/, '').split('--');
      let data;
      try {
        data = JSON.parse(fs.readFileSync(path.join(abs, f), 'utf8'));
      } catch {
        problems.push(`invalid:${f}`);
        continue;
      }
      if (!data || data.scenario !== scenario || data.project !== project || !Array.isArray(data.entries)) {
        problems.push(`invalid:${f}`);
        continue;
      }
      try {
        entries.push(...violationsToEntries(scenario, project, data.entries));
      } catch {
        problems.push(`invalid:${f}`);
      }
    }
  }
  if (problems.length) {
    const err = new Error(`mergeCollected: ${problems.join(', ')}`);
    err.problems = problems;
    throw err;
  }
  const merged = entries
    .map((e) => ({
      key: e.key,
      scenario: e.scenario,
      project: e.project,
      ruleId: e.ruleId,
      impact: e.impact,
      targets: e.targets,
      selectors: e.selectors,
    }))
    .sort((a, b) => byCodeUnit(a.key, b.key));
  if (outAbs) {
    fs.mkdirSync(path.dirname(outAbs), { recursive: true });
    fs.writeFileSync(outAbs, JSON.stringify(merged, null, 2) + '\n');
  }
  return merged;
}

function parseCliArgs(argv) {
  const opts = { cmd: null, dir: undefined, out: undefined };
  for (let i = 0; i < argv.length; i++) {
    const a = argv[i];
    if (a === '--reset' || a === '--merge') {
      if (opts.cmd) throw new Error(`axe.js: duplicate command ${a}`);
      opts.cmd = a.slice(2);
    } else if (a === '--dir' || a === '--out') {
      const v = argv[++i];
      if (v === undefined || v.startsWith('--')) throw new Error(`axe.js: ${a} requires a value`);
      opts[a.slice(2)] = v;
    } else {
      throw new Error(`axe.js: unknown argument ${a}`);
    }
  }
  if (!opts.cmd) throw new Error('axe.js: command required (--reset | --merge)');
  if (opts.cmd === 'reset' && opts.out !== undefined) throw new Error('axe.js: --out only with --merge');
  return opts;
}

export function runCli(argv) {
  let opts;
  try {
    opts = parseCliArgs(argv);
    if (opts.cmd === 'reset') {
      const abs = resetCollected(opts.dir);
      process.stdout.write(`axe reset: ${path.relative(REPO_ROOT, abs)}\n`);
      return 0;
    }
    const out = opts.out ?? DEFAULT_MERGE_OUT;
    const merged = mergeCollected({ collectDir: opts.dir, out });
    const targets = merged.reduce((n, e) => n + e.targets.length, 0);
    process.stdout.write(`axe merge: ${merged.length} entries, ${targets} targets -> ${out}\n`);
    return 0;
  } catch (e) {
    for (const line of e.problems || [e.message]) process.stderr.write(`${line}\n`);
    return 1;
  }
}

if (process.argv[1] && import.meta.url === pathToFileURL(path.resolve(process.argv[1])).href) {
  process.exitCode = runCli(process.argv.slice(2));
}
