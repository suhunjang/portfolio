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

// step 33 — axe baseline·regression (설계 §6.2 step 33·§6.4)
// BASELINE_PATH · COLLECTED_PATH · PLAN_PATH · FIX_FILES_BY_KIND · baselineExists · loadBaseline · resolveBaselineMode ·
// validateBaseline · checkRegression · assertEmptyFile · CLI `--assert-empty [--baseline f]`
export const BASELINE_PATH = 'tests/fixtures/axe-baseline.json';
export const COLLECTED_PATH = DEFAULT_MERGE_OUT;
export const PLAN_PATH = 'tests/fixtures/axe-remediation-plan.json';
export const FIX_FILES_BY_KIND = Object.freeze({
  'css-token': Object.freeze(['css/themes.css']),
  'css-rule': Object.freeze(['css/style.css']),
  'js-render': Object.freeze(['js/main.js']),
  'static-markup': Object.freeze(['index.html']),
  'text-change': Object.freeze([]),
});
// kind별 허용 requiresColorChange 값(§6.4).
const RCC_ALLOWED = Object.freeze({
  'css-token': [true],
  'css-rule': [true, false],
  'js-render': [false],
  'static-markup': [false],
  'text-change': [false],
});
const ENTRY_FIELDS = ['key', 'scenario', 'project', 'ruleId', 'impact', 'targets', 'selectors', 'fixes', 'fixFiles'];
const FIX_FIELDS = ['target', 'fixKind', 'fixFiles', 'requiresColorChange'];

const repoAbs = (p) => path.resolve(REPO_ROOT, p);
const isPlainObject = (x) => x !== null && typeof x === 'object' && !Array.isArray(x);
const sameArray = (a, b) => Array.isArray(a) && a.length === b.length && a.every((x, i) => x === b[i]);

export function baselineExists(baselinePath = BASELINE_PATH) {
  return fs.existsSync(repoAbs(baselinePath));
}

// JSON 배열이 아니면(없음·깨짐·비배열) throw. 스키마 검증은 validateBaseline 담당.
export function loadBaseline(baselinePath = BASELINE_PATH) {
  let text;
  try {
    text = fs.readFileSync(repoAbs(baselinePath), 'utf8');
  } catch (e) {
    throw new Error(`loadBaseline: missing: ${baselinePath}`, { cause: e });
  }
  let data;
  try {
    data = JSON.parse(text);
  } catch (e) {
    throw new Error(`loadBaseline: invalid json: ${baselinePath}`, { cause: e });
  }
  if (!Array.isArray(data)) throw new Error(`loadBaseline: not-array: ${baselinePath}`);
  return data;
}

// baseline 있음 → 'check'; 없음 + collected 있음 + plan 없음 → 'pending'; 그 밖 throw. 환경변수 우회 없음.
export function resolveBaselineMode({
  baselinePath = BASELINE_PATH,
  collectedPath = COLLECTED_PATH,
  planPath = PLAN_PATH,
} = {}) {
  if (baselineExists(baselinePath)) return 'check';
  if (!fs.existsSync(repoAbs(collectedPath))) {
    throw new Error(`resolveBaselineMode: baseline and collected missing: ${baselinePath}, ${collectedPath}`);
  }
  if (fs.existsSync(repoAbs(planPath))) {
    throw new Error(`resolveBaselineMode: plan without baseline: ${planPath}`);
  }
  return 'pending';
}

function fieldsProblem(obj, fields) {
  const keys = Object.keys(obj);
  const missing = fields.filter((f) => !Object.prototype.hasOwnProperty.call(obj, f));
  const extra = keys.filter((k) => !fields.includes(k)).sort(byCodeUnit);
  if (missing.length === 0 && extra.length === 0) return null;
  return `fields missing=[${missing.join(',')}] extra=[${extra.join(',')}]`;
}

// 문자열 배열 검사: not-string → duplicate → unsorted 중 첫 문제(없으면 null).
function stringListProblem(xs) {
  if (!Array.isArray(xs) || xs.some((x) => typeof x !== 'string')) return 'not-string';
  if (new Set(xs).size !== xs.length) return 'duplicate';
  for (let i = 1; i < xs.length; i++) if (byCodeUnit(xs[i - 1], xs[i]) > 0) return 'unsorted';
  return null;
}

const validToken = (v) => typeof v === 'string' && v !== '' && !v.includes(':');

// §6.4 baseline 검증 → 오류 문자열 배열(발견 순). 입력 불변.
export function validateBaseline(baseline) {
  if (!Array.isArray(baseline)) return ['baseline: not-array'];
  const errors = [];
  const keys = [];
  baseline.forEach((entry, i) => {
    const at = `baseline[${i}]`;
    if (!isPlainObject(entry)) {
      errors.push(`${at}: not-object`);
      return;
    }
    if (typeof entry.key === 'string') keys.push(entry.key);
    const fp = fieldsProblem(entry, ENTRY_FIELDS);
    if (fp) {
      errors.push(`${at}: ${fp}`);
      return;
    }
    const okScenario = SCENARIOS.includes(entry.scenario);
    const okProject = PROJECTS.includes(entry.project);
    const okRule = validToken(entry.ruleId);
    if (!okScenario) errors.push(`${at}: bad-scenario`);
    if (!okProject) errors.push(`${at}: bad-project`);
    if (!okRule) errors.push(`${at}: bad-ruleId`);
    if (okScenario && okProject && okRule) {
      const want = makeEntryKey({ scenario: entry.scenario, project: entry.project, ruleId: entry.ruleId });
      if (entry.key !== want) errors.push(`${at}: key-mismatch`);
    }
    if (!Object.prototype.hasOwnProperty.call(IMPACT_RANK, entry.impact)) {
      errors.push(`${at}: bad-impact`);
    }
    const targets = entry.targets;
    if (Array.isArray(targets) && targets.length === 0) errors.push(`${at}: targets empty`);
    else {
      const tp = stringListProblem(targets);
      if (tp) errors.push(`${at}: targets ${tp}`);
    }
    const sp = stringListProblem(entry.selectors);
    if (sp) errors.push(`${at}: selectors ${sp}`);

    const fixes = entry.fixes;
    if (!Array.isArray(fixes) || !Array.isArray(targets) || fixes.length !== targets.length) {
      errors.push(`${at}: fixes count`);
      return;
    }
    let fixError = false;
    const union = new Set();
    fixes.forEach((fix, j) => {
      const fat = `${at}.fixes[${j}]`;
      const before = errors.length;
      if (!isPlainObject(fix)) {
        errors.push(`${fat}: not-object`);
      } else {
        const ffp = fieldsProblem(fix, FIX_FIELDS);
        if (ffp) errors.push(`${fat}: ${ffp}`);
        else {
          if (fix.target !== targets[j]) errors.push(`${fat}: target-mismatch`);
          const kindOk = typeof fix.fixKind === 'string' && Object.prototype.hasOwnProperty.call(FIX_FILES_BY_KIND, fix.fixKind);
          if (!kindOk) errors.push(`${fat}: bad-fixKind`);
          else if (!sameArray(fix.fixFiles, FIX_FILES_BY_KIND[fix.fixKind])) errors.push(`${fat}: fixFiles-mismatch`);
          const rcc = fix.requiresColorChange;
          if (typeof rcc !== 'boolean' || (kindOk && !RCC_ALLOWED[fix.fixKind].includes(rcc))) {
            errors.push(`${fat}: bad-requiresColorChange`);
          }
          if (Array.isArray(fix.fixFiles)) for (const f of fix.fixFiles) union.add(f);
        }
      }
      if (errors.length !== before) fixError = true;
    });
    if (!fixError && !sameArray(entry.fixFiles, [...union].sort(byCodeUnit))) {
      errors.push(`${at}: fixFiles union-mismatch`);
    }
  });
  const seen = new Set();
  const reported = new Set();
  for (const k of keys) {
    if (seen.has(k) && !reported.has(k)) {
      errors.push(`baseline: duplicate-key ${k}`);
      reported.add(k);
    }
    seen.add(k);
  }
  for (let i = 1; i < keys.length; i++) {
    if (byCodeUnit(keys[i - 1], keys[i]) > 0) {
      errors.push('baseline: unsorted');
      break;
    }
  }
  return errors;
}

// runAxe 결과를 baseline과 비교: baseline에 없는 key → `new-key:{key}`, key의 새 target → `new-target:{key}:{target}`.
// 사라진 key·target은 허용. 결과는 고유·코드 유닛 정렬. 입력 불변.
export function checkRegression(violations, baseline, scenario, project) {
  if (!Array.isArray(violations)) throw new Error('checkRegression: violations not-array');
  if (!Array.isArray(baseline)) throw new Error('checkRegression: baseline not-array');
  const byKey = new Map();
  for (const e of baseline) if (isPlainObject(e) && typeof e.key === 'string') byKey.set(e.key, e);
  const out = new Set();
  for (const v of violations) {
    const key = makeEntryKey({ scenario, project, ruleId: v?.ruleId });
    const entry = byKey.get(key);
    if (!entry) {
      out.add(`new-key:${key}`);
      continue;
    }
    const known = new Set(Array.isArray(entry.targets) ? entry.targets : []);
    for (const t of v.targets || []) if (!known.has(t)) out.add(`new-target:${key}:${t}`);
  }
  return [...out].sort(byCodeUnit);
}

// 파일이 정확히 JSON 빈 배열이 아니면(없음·깨짐·비배열·비어 있지 않음) throw.
export function assertEmptyFile(file = BASELINE_PATH) {
  const data = loadBaseline(file);
  if (data.length !== 0) throw new Error(`assertEmptyFile: expected [], got ${data.length} entries: ${file}`);
}

// step 34 — baseline projection (§6.2 step 34). fixes·fixFiles·fix의 requiresColorChange는
// projection과 collected 비교에서 명시적으로 제외한다.
export const PROJECTION_FIELDS = Object.freeze(['key', 'scenario', 'project', 'ruleId', 'impact', 'targets', 'selectors']);
const COMPARED_FIELDS = ['scenario', 'project', 'ruleId', 'impact', 'selectors'];

// entry(collected MergedEntry 또는 baseline entry) → PROJECTION_FIELDS 7필드만. targets·selectors 정렬·중복 제거.
// 필드 누락·key 불일치 throw. 입력 불변.
export function projectEntry(entry) {
  if (!isPlainObject(entry)) throw new Error('projectEntry: not-object');
  const missing = PROJECTION_FIELDS.filter((f) => !Object.prototype.hasOwnProperty.call(entry, f));
  if (missing.length) throw new Error(`projectEntry: missing=[${missing.join(',')}]`);
  for (const f of ['targets', 'selectors']) {
    if (!Array.isArray(entry[f]) || entry[f].some((x) => typeof x !== 'string')) {
      throw new Error(`projectEntry: ${f} not-string-array: ${entry.key}`);
    }
  }
  const want = makeEntryKey({ scenario: entry.scenario, project: entry.project, ruleId: entry.ruleId });
  if (entry.key !== want) throw new Error(`projectEntry: key-mismatch: ${entry.key} != ${want}`);
  return {
    key: entry.key,
    scenario: entry.scenario,
    project: entry.project,
    ruleId: entry.ruleId,
    impact: entry.impact,
    targets: sortedUniqueStrings(entry.targets),
    selectors: sortedUniqueStrings(entry.selectors),
  };
}

function projectByKey(list, label) {
  if (!Array.isArray(list)) throw new Error(`compareCollectedBaseline: ${label} not-array`);
  const map = new Map();
  for (const e of list) {
    const p = projectEntry(e);
    if (map.has(p.key)) throw new Error(`compareCollectedBaseline: ${label} duplicate-key ${p.key}`);
    map.set(p.key, p);
  }
  return map;
}

const byKeyThen = (second) => (a, b) => byCodeUnit(a.key, b.key) || byCodeUnit(a[second], b[second]);

// collected vs baseline projection 비교. 입력 불변, 모든 배열 정렬. ok = 다섯 배열 빔.
export function compareCollectedBaseline(collected, baseline) {
  const c = projectByKey(collected, 'collected');
  const b = projectByKey(baseline, 'baseline');
  const missingEntries = [];
  const extraEntries = [];
  const missingTargets = [];
  const extraTargets = [];
  const fieldMismatches = [];
  for (const [key, ce] of c) {
    const be = b.get(key);
    if (!be) {
      missingEntries.push(key);
      continue;
    }
    const bt = new Set(be.targets);
    const ct = new Set(ce.targets);
    for (const t of ce.targets) if (!bt.has(t)) missingTargets.push({ key, target: t });
    for (const t of be.targets) if (!ct.has(t)) extraTargets.push({ key, target: t });
    for (const field of COMPARED_FIELDS) {
      if (JSON.stringify(ce[field]) !== JSON.stringify(be[field])) fieldMismatches.push({ key, field });
    }
  }
  for (const key of b.keys()) if (!c.has(key)) extraEntries.push(key);
  missingEntries.sort(byCodeUnit);
  extraEntries.sort(byCodeUnit);
  missingTargets.sort(byKeyThen('target'));
  extraTargets.sort(byKeyThen('target'));
  fieldMismatches.sort(byKeyThen('field'));
  const ok = [missingEntries, extraEntries, missingTargets, extraTargets, fieldMismatches].every((x) => x.length === 0);
  return { ok, missingEntries, extraEntries, missingTargets, extraTargets, fieldMismatches };
}

// 비교 결과 → stderr 줄(missing-entry → extra-entry → missing-target → extra-target → field-mismatch).
function baselineMatchLines(r) {
  return [
    ...r.missingEntries.map((k) => `missing-entry:${k}`),
    ...r.extraEntries.map((k) => `extra-entry:${k}`),
    ...r.missingTargets.map((x) => `missing-target:${x.key}|${x.target}`),
    ...r.extraTargets.map((x) => `extra-target:${x.key}|${x.target}`),
    ...r.fieldMismatches.map((x) => `field-mismatch:${x.key}|${x.field}`),
  ];
}

// step 35 — remediation plan schema (§6.2 step 35·§6.5)
// GROUP_ID_RE · loadPlan · requiredBlockReason · validateRemediationPlan · CLI `--check-plan`
export const GROUP_ID_RE = /^[a-z0-9]+(?:-[a-z0-9]+)*$/;
const PLAN_FIELDS = ['groups'];
const GROUP_FIELDS = ['id', 'targets', 'fixFiles', 'difficulty', 'estMinutes', 'blocked', 'reason'];
const PLAN_TARGET_FIELDS = ['key', 'target'];
const DIFFICULTIES = ['low', 'medium', 'high'];
const REASON_TEXT = 'text change excluded';
const REASON_COLOR = 'color change excluded (HOO-81 §16.3)';

const ptId = (key, target) => `${key}|${target}`;

// baseline → Map(`${key}|${target}` → fix). 형식이 맞지 않는 entry·fix는 건너뛴다(검증은 validateBaseline 담당).
function baselineFixIndex(baseline) {
  const map = new Map();
  if (!Array.isArray(baseline)) return map;
  for (const e of baseline) {
    if (!isPlainObject(e) || typeof e.key !== 'string' || !Array.isArray(e.fixes)) continue;
    for (const fix of e.fixes) {
      if (!isPlainObject(fix) || typeof fix.target !== 'string') continue;
      const id = ptId(e.key, fix.target);
      if (!map.has(id)) map.set(id, fix);
    }
  }
  return map;
}

// JSON으로 읽기만(없음·깨짐 throw). 스키마 검증은 validateRemediationPlan 담당.
export function loadPlan(planPath = PLAN_PATH) {
  let text;
  try {
    text = fs.readFileSync(repoAbs(planPath), 'utf8');
  } catch (e) {
    throw new Error(`loadPlan: missing: ${planPath}`, { cause: e });
  }
  try {
    return JSON.parse(text);
  } catch (e) {
    throw new Error(`loadPlan: invalid json: ${planPath}`, { cause: e });
  }
}

// 그룹 targets의 baseline fix에서 필수 block reason 계산(§6.5). 순수·입력 불변. baseline에 없는 target 무시.
export function requiredBlockReason(groupTargets, baseline) {
  const index = baselineFixIndex(baseline);
  let text = false;
  let color = false;
  for (const t of Array.isArray(groupTargets) ? groupTargets : []) {
    if (!isPlainObject(t) || typeof t.key !== 'string' || typeof t.target !== 'string') continue;
    const fix = index.get(ptId(t.key, t.target));
    if (!fix) continue;
    if (fix.fixKind === 'text-change') text = true;
    if (fix.requiresColorChange === true) color = true;
  }
  const parts = [];
  if (text) parts.push(REASON_TEXT);
  if (color) parts.push(REASON_COLOR);
  return parts.join('; ');
}

const cmpPlanTarget = (a, b) => byCodeUnit(a.key, b.key) || byCodeUnit(a.target, b.target);

// §6.5 plan 검증 → 오류 문자열 배열(발견 순). 필수 reason은 requiredBlockReason으로만 계산. 입력 불변.
export function validateRemediationPlan(plan, baseline, { coverage = false, requireEmpty = false } = {}) {
  if (!isPlainObject(plan)) return ['plan: not-object'];
  const pfp = fieldsProblem(plan, PLAN_FIELDS);
  if (pfp) return [`plan: ${pfp}`];
  if (!Array.isArray(plan.groups)) return ['plan: groups not-array'];
  const index = baselineFixIndex(baseline);
  const errors = [];
  const ids = [];
  const owner = new Map(); // PlanTarget id → 처음 나온 그룹 index
  const multi = [];
  plan.groups.forEach((g, i) => {
    const at = `groups[${i}]`;
    if (!isPlainObject(g)) {
      errors.push(`${at}: not-object`);
      return;
    }
    const gfp = fieldsProblem(g, GROUP_FIELDS);
    if (gfp) {
      errors.push(`${at}: ${gfp}`);
      return;
    }
    if (typeof g.id === 'string') ids.push(g.id);
    if (typeof g.id !== 'string' || !GROUP_ID_RE.test(g.id)) errors.push(`${at}: bad-id`);

    let targetError = false;
    const valid = [];
    if (!Array.isArray(g.targets) || g.targets.length === 0) {
      errors.push(`${at}: targets empty`);
      targetError = true;
    } else {
      g.targets.forEach((t, j) => {
        const tat = `${at}.targets[${j}]`;
        if (!isPlainObject(t)) {
          errors.push(`${tat}: not-object`);
          targetError = true;
          return;
        }
        const tfp = fieldsProblem(t, PLAN_TARGET_FIELDS);
        if (tfp) {
          errors.push(`${tat}: ${tfp}`);
          targetError = true;
          return;
        }
        if (typeof t.key !== 'string' || typeof t.target !== 'string' || !index.has(ptId(t.key, t.target))) {
          errors.push(`${tat}: unknown-target`);
          targetError = true;
          return;
        }
        valid.push(t);
      });
      const seenInGroup = new Set();
      let dup = false;
      for (const t of valid) {
        const id = ptId(t.key, t.target);
        if (seenInGroup.has(id)) dup = true;
        seenInGroup.add(id);
      }
      if (dup) errors.push(`${at}: targets duplicate`);
      for (let k = 1; k < valid.length; k++) {
        if (cmpPlanTarget(valid[k - 1], valid[k]) > 0) {
          errors.push(`${at}: targets unsorted`);
          break;
        }
      }
      for (const id of seenInGroup) {
        if (!owner.has(id)) owner.set(id, i);
        else if (owner.get(id) !== i && !multi.includes(id)) multi.push(id);
      }
    }
    if (!targetError) {
      const union = new Set();
      for (const t of valid) {
        const files = index.get(ptId(t.key, t.target)).fixFiles;
        if (Array.isArray(files)) for (const f of files) union.add(f);
      }
      if (!sameArray(g.fixFiles, [...union].sort(byCodeUnit))) errors.push(`${at}: fixFiles-mismatch`);
    }
    if (!DIFFICULTIES.includes(g.difficulty)) errors.push(`${at}: bad-difficulty`);
    if (!Number.isInteger(g.estMinutes) || g.estMinutes < 1 || g.estMinutes > 20) errors.push(`${at}: bad-estMinutes`);
    if (typeof g.blocked !== 'boolean') {
      errors.push(`${at}: bad-blocked`);
      return;
    }
    const required = requiredBlockReason(g.targets, baseline);
    const reason = g.reason;
    if (required !== '') {
      if (g.blocked !== true) errors.push(`${at}: blocked-required`);
      else if (typeof reason !== 'string' || reason === '') errors.push(`${at}: reason-required`);
      else if (reason !== required) errors.push(`${at}: reason-mismatch`);
    } else if (g.blocked) {
      if (typeof reason !== 'string' || reason === '') errors.push(`${at}: reason-required`);
    } else if (reason !== '') {
      errors.push(`${at}: reason-must-be-empty`);
    }
  });

  const seenIds = new Set();
  const reportedIds = new Set();
  for (const id of ids) {
    if (seenIds.has(id) && !reportedIds.has(id)) {
      errors.push(`plan: duplicate-id ${id}`);
      reportedIds.add(id);
    }
    seenIds.add(id);
  }
  for (let k = 1; k < ids.length; k++) {
    if (byCodeUnit(ids[k - 1], ids[k]) > 0) {
      errors.push('plan: groups unsorted');
      break;
    }
  }
  for (const id of multi) errors.push(`plan: target-in-multiple-groups ${id}`);
  if (coverage && Array.isArray(baseline)) {
    for (const e of baseline) {
      if (!isPlainObject(e) || typeof e.key !== 'string' || !Array.isArray(e.targets)) continue;
      for (const t of e.targets) {
        const id = ptId(e.key, t);
        if (!owner.has(id)) errors.push(`plan: uncovered ${id}`);
      }
    }
  }
  if (requireEmpty && plan.groups.length !== 0) errors.push(`groups: expected empty, got ${plan.groups.length}`);
  return errors;
}

// §6.2 step 36: 실행 가능성 검사(전제: 같은 입력이 validateRemediationPlan → []). blocked 그룹만 거부.
// 그룹 순서대로 blocked-group:{id} → 그 그룹 text-change target마다 text-change:{id}:{key}:{target}
// → fixFiles 비면 empty-fixfiles:{id}. requiresColorChange 재판정 없음(step 35 몫). 순수·입력 불변.
export const EXECUTABLE_HEADER = 'Harness 재계획 필요: 실행 불가 remediation 그룹';

export function validateRemediationExecutable(plan, baseline) {
  const errors = [];
  const index = baselineFixIndex(baseline);
  const groups = isPlainObject(plan) && Array.isArray(plan.groups) ? plan.groups : [];
  for (const g of groups) {
    if (!isPlainObject(g) || g.blocked !== true) continue;
    errors.push(`blocked-group:${g.id}`);
    for (const t of Array.isArray(g.targets) ? g.targets : []) {
      if (!isPlainObject(t)) continue;
      const fix = index.get(ptId(t.key, t.target));
      if (fix && fix.fixKind === 'text-change') errors.push(`text-change:${g.id}:${t.key}:${t.target}`);
    }
    if (!Array.isArray(g.fixFiles) || g.fixFiles.length === 0) errors.push(`empty-fixfiles:${g.id}`);
  }
  return errors;
}

// §6.2 step 37: 현재 collected 검사. collected = MergedEntry 배열(key·targets만 읽음). PlanTarget 단위, 순수·입력 불변.
export const CURRENT_COLLECTED_PATH = 'tests/.tmp/axe-current.json';

// collected → 정렬된 고유 PlanTarget 목록. 비배열·형식 오류 entry는 Error('invalid collected').
function collectedTargets(collected) {
  if (!Array.isArray(collected)) throw new Error('invalid collected');
  const map = new Map();
  for (const e of collected) {
    if (!isPlainObject(e) || typeof e.key !== 'string' || !Array.isArray(e.targets)) throw new Error('invalid collected');
    for (const target of e.targets) {
      if (typeof target !== 'string') throw new Error('invalid collected');
      map.set(ptId(e.key, target), { key: e.key, target });
    }
  }
  return [...map.values()].sort(cmpPlanTarget);
}

const planGroups = (plan) => (isPlainObject(plan) && Array.isArray(plan.groups) ? plan.groups : []);

export function checkGroupDone(collected, plan, id) {
  const present = new Set(collectedTargets(collected).map((t) => ptId(t.key, t.target)));
  const g = planGroups(plan).find((x) => isPlainObject(x) && typeof id === 'string' && x.id === id);
  if (!g) throw new Error(`unknown group id: ${id}`);
  const seen = new Set();
  const remaining = [];
  for (const t of Array.isArray(g.targets) ? g.targets : []) {
    if (!isPlainObject(t) || typeof t.key !== 'string' || typeof t.target !== 'string') continue;
    const k = ptId(t.key, t.target);
    if (present.has(k) && !seen.has(k)) {
      seen.add(k);
      remaining.push({ key: t.key, target: t.target });
    }
  }
  remaining.sort(cmpPlanTarget);
  return { done: remaining.length === 0, remaining };
}

export function checkCollectedCoverage(collected, plan) {
  const all = collectedTargets(collected);
  const inPlan = new Set();
  for (const g of planGroups(plan)) {
    if (!isPlainObject(g) || !Array.isArray(g.targets)) continue;
    for (const t of g.targets) if (isPlainObject(t)) inPlan.add(ptId(t.key, t.target));
  }
  const uncovered = all.filter((t) => !inPlan.has(ptId(t.key, t.target)));
  return { ok: uncovered.length === 0, uncovered };
}

// (key, target) 위반 건수. 같은 target 문자열도 key가 다르면 따로 센다.
export function countCollectedTargets(collected) {
  return collectedTargets(collected).length;
}

// §6.2 step 38: collected(MergedEntry 배열) 회귀 검사. key가 makeEntryKey(scenario, project, ruleId)와 다르거나
// 만들 수 없으면 `bad-key:{key}`, baseline에 없는 key → `new-key:{key}`, key의 새 target → `new-target:{key}:{target}`.
// 사라진 key·target 허용. 고유·코드 유닛 정렬. 순수·입력 불변.
export function checkCollectedRegression(collected, baseline) {
  collectedTargets(collected); // 형식 검사(Error('invalid collected'))
  const byKey = new Map();
  for (const e of Array.isArray(baseline) ? baseline : []) {
    if (isPlainObject(e) && typeof e.key === 'string') byKey.set(e.key, e);
  }
  const out = new Set();
  for (const e of collected) {
    let expected = null;
    try {
      expected = makeEntryKey({ scenario: e.scenario, project: e.project, ruleId: e.ruleId });
    } catch {
      expected = null;
    }
    if (expected !== e.key) {
      out.add(`bad-key:${e.key}`);
      continue;
    }
    const entry = byKey.get(e.key);
    if (!entry) {
      out.add(`new-key:${e.key}`);
      continue;
    }
    const known = new Set(Array.isArray(entry.targets) ? entry.targets : []);
    for (const t of e.targets) if (!known.has(t)) out.add(`new-target:${e.key}:${t}`);
  }
  return [...out].sort(byCodeUnit);
}

// §6.5 prune: (1) collected에 없는 PlanTarget 제거(순서 유지) (2) 빈 그룹 삭제(순서 유지) (3) fixFiles 재계산·
// R' = requiredBlockReason(남은 targets) (4) R' ≠ "" → blocked true·reason R' (5) R' = "" → manual block
// (prune 전 blocked true·reason 비어 있지 않음·prune 전 requiredBlockReason과 다름)만 유지, 아니면 false·""
// (6) id·difficulty·estMinutes 유지, 필드 추가 없음. 순수·입력 불변·결정적.
export function prunePlan(plan, collected, baseline) {
  const present = new Set(collectedTargets(collected).map((t) => ptId(t.key, t.target)));
  if (!isPlainObject(plan) || !Array.isArray(plan.groups)) throw new Error('invalid plan');
  const index = baselineFixIndex(baseline);
  const groups = [];
  for (const g of plan.groups) {
    if (!isPlainObject(g) || !Array.isArray(g.targets)) throw new Error('invalid plan');
    const targets = g.targets
      .filter((t) => isPlainObject(t) && present.has(ptId(t.key, t.target)))
      .map((t) => ({ key: t.key, target: t.target }));
    if (targets.length === 0) continue;
    const files = [];
    for (const t of targets) {
      const fix = index.get(ptId(t.key, t.target));
      if (fix && Array.isArray(fix.fixFiles)) files.push(...fix.fixFiles);
    }
    const required = requiredBlockReason(targets, baseline);
    let blocked = false;
    let reason = '';
    if (required !== '') {
      blocked = true;
      reason = required;
    } else if (
      g.blocked === true &&
      typeof g.reason === 'string' &&
      g.reason !== '' &&
      g.reason !== requiredBlockReason(g.targets, baseline)
    ) {
      blocked = true;
      reason = g.reason;
    }
    groups.push({
      id: g.id,
      targets,
      fixFiles: sortedUniqueStrings(files),
      difficulty: g.difficulty,
      estMinutes: g.estMinutes,
      blocked,
      reason,
    });
  }
  return { groups };
}

function parseCliArgs(argv) {
  const opts = {
    cmd: null,
    dir: undefined,
    out: undefined,
    baseline: undefined,
    collected: undefined,
    plan: undefined,
    coverage: false,
    requireEmpty: false,
    groupId: undefined,
  };
  for (let i = 0; i < argv.length; i++) {
    const a = argv[i];
    if (a === '--check-group-done' || a === '--check-coverage' || a === '--assert-no-violations') {
      if (opts.cmd) throw new Error(`axe.js: duplicate command ${a}`);
      opts.cmd = a.slice(2);
      if (a === '--check-group-done') {
        const v = argv[++i];
        if (v === undefined || v.startsWith('--')) throw new Error(`axe.js: ${a} requires a group id`);
        opts.groupId = v;
      }
    } else if (
      a === '--reset' ||
      a === '--merge' ||
      a === '--assert-empty' ||
      a === '--check-baseline-match' ||
      a === '--check-plan' ||
      a === '--check-executable' ||
      a === '--check-regression' ||
      a === '--prune-plan'
    ) {
      if (opts.cmd) throw new Error(`axe.js: duplicate command ${a}`);
      opts.cmd = a.slice(2);
    } else if (a === '--dir' || a === '--out' || a === '--baseline' || a === '--collected' || a === '--plan') {
      const v = argv[++i];
      if (v === undefined || v.startsWith('--')) throw new Error(`axe.js: ${a} requires a value`);
      opts[a.slice(2)] = v;
    } else if (a === '--coverage') {
      opts.coverage = true;
    } else if (a === '--require-empty') {
      opts.requireEmpty = true;
    } else {
      throw new Error(`axe.js: unknown argument ${a}`);
    }
  }
  if (!opts.cmd) {
    throw new Error('axe.js: command required (--reset | --merge | --assert-empty | --check-baseline-match | --check-plan | --check-executable)');
  }
  if (opts.cmd === 'check-group-done' || opts.cmd === 'check-coverage' || opts.cmd === 'assert-no-violations') {
    const planAllowed = opts.cmd !== 'assert-no-violations';
    if (
      opts.dir !== undefined ||
      opts.out !== undefined ||
      opts.baseline !== undefined ||
      opts.coverage ||
      opts.requireEmpty ||
      (!planAllowed && opts.plan !== undefined)
    ) {
      throw new Error(`axe.js: --${opts.cmd} takes only --collected${planAllowed ? ' and --plan' : ''}`);
    }
    return opts;
  }
  if (opts.cmd === 'check-regression' || opts.cmd === 'prune-plan') {
    const planAllowed = opts.cmd === 'prune-plan';
    if (
      opts.dir !== undefined ||
      opts.out !== undefined ||
      opts.coverage ||
      opts.requireEmpty ||
      (!planAllowed && opts.plan !== undefined)
    ) {
      throw new Error(`axe.js: --${opts.cmd} takes only --collected${planAllowed ? ', --plan' : ''} and --baseline`);
    }
    return opts;
  }
  if (opts.cmd === 'check-executable') {
    if (opts.dir !== undefined || opts.out !== undefined || opts.collected !== undefined || opts.coverage || opts.requireEmpty) {
      throw new Error('axe.js: --check-executable takes only --plan and --baseline');
    }
    return opts;
  }
  if (opts.cmd === 'check-plan') {
    if (opts.dir !== undefined || opts.out !== undefined || opts.collected !== undefined) {
      throw new Error('axe.js: --check-plan takes only --coverage, --require-empty, --plan and --baseline');
    }
    return opts;
  }
  if (opts.plan !== undefined || opts.coverage || opts.requireEmpty) {
    throw new Error('axe.js: --plan, --coverage and --require-empty only with --check-plan');
  }
  if (opts.cmd === 'check-baseline-match') {
    if (opts.dir !== undefined || opts.out !== undefined) {
      throw new Error('axe.js: --check-baseline-match takes only --collected and --baseline');
    }
    return opts;
  }
  if (opts.collected !== undefined) throw new Error('axe.js: --collected only with --check-baseline-match');
  if (opts.cmd === 'reset' && opts.out !== undefined) throw new Error('axe.js: --out only with --merge');
  if (opts.cmd !== 'assert-empty' && opts.baseline !== undefined) throw new Error('axe.js: --baseline only with --assert-empty');
  if (opts.cmd === 'assert-empty' && (opts.dir !== undefined || opts.out !== undefined)) {
    throw new Error('axe.js: --assert-empty takes only --baseline');
  }
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
    if (opts.cmd === 'assert-empty') {
      const file = opts.baseline ?? BASELINE_PATH;
      assertEmptyFile(file);
      process.stdout.write(`axe assert-empty: OK (${file})\n`);
      return 0;
    }
    if (opts.cmd === 'check-plan') {
      const plan = loadPlan(opts.plan ?? PLAN_PATH);
      const baseline = loadBaseline(opts.baseline ?? BASELINE_PATH);
      const errors = validateRemediationPlan(plan, baseline, { coverage: opts.coverage, requireEmpty: opts.requireEmpty });
      if (errors.length) {
        for (const line of errors) process.stderr.write(`${line}\n`);
        return 1;
      }
      process.stdout.write('check-plan: OK\n');
      return 0;
    }
    if (opts.cmd === 'check-executable') {
      const plan = loadPlan(opts.plan ?? PLAN_PATH);
      const baseline = loadBaseline(opts.baseline ?? BASELINE_PATH);
      const errors = validateRemediationExecutable(plan, baseline);
      if (errors.length) {
        for (const line of [EXECUTABLE_HEADER, ...errors]) process.stderr.write(`${line}\n`);
        return 1;
      }
      process.stdout.write('check-executable: OK\n');
      return 0;
    }
    if (opts.cmd === 'check-regression' || opts.cmd === 'prune-plan') {
      const collected = loadBaseline(opts.collected ?? CURRENT_COLLECTED_PATH);
      const baseline = loadBaseline(opts.baseline ?? BASELINE_PATH);
      const planPath = opts.plan ?? PLAN_PATH;
      const plan = opts.cmd === 'prune-plan' ? loadPlan(planPath) : null;
      const regressions = checkCollectedRegression(collected, baseline);
      if (regressions.length) {
        for (const line of regressions) process.stderr.write(`${line}\n`);
        return 1;
      }
      if (opts.cmd === 'check-regression') {
        process.stdout.write('check-regression: OK\n');
        return 0;
      }
      const inputErrors = validateRemediationPlan(plan, baseline);
      if (inputErrors.length) {
        for (const line of inputErrors) process.stderr.write(`${line}\n`);
        return 1;
      }
      const pruned = prunePlan(plan, collected, baseline);
      const prunedErrors = validateRemediationPlan(pruned, baseline);
      if (prunedErrors.length) {
        for (const line of prunedErrors) process.stderr.write(`${line}\n`);
        return 1;
      }
      fs.writeFileSync(repoAbs(planPath), JSON.stringify(pruned, null, 2) + '\n');
      process.stdout.write(`prune-plan: OK (${planPath})\n`);
      return 0;
    }
    if (opts.cmd === 'check-group-done' || opts.cmd === 'check-coverage' || opts.cmd === 'assert-no-violations') {
      const collected = loadBaseline(opts.collected ?? CURRENT_COLLECTED_PATH);
      if (opts.cmd === 'assert-no-violations') {
        const n = countCollectedTargets(collected);
        if (n > 0) {
          process.stderr.write(`violations: ${n}\n`);
          return 1;
        }
        process.stdout.write('assert-no-violations: OK\n');
        return 0;
      }
      const plan = loadPlan(opts.plan ?? PLAN_PATH);
      if (opts.cmd === 'check-group-done') {
        const r = checkGroupDone(collected, plan, opts.groupId);
        if (!r.done) {
          for (const t of r.remaining) process.stderr.write(`remaining:${t.key}|${t.target}\n`);
          return 1;
        }
        process.stdout.write(`check-group-done: OK (${opts.groupId})\n`);
        return 0;
      }
      const r = checkCollectedCoverage(collected, plan);
      if (!r.ok) {
        for (const t of r.uncovered) process.stderr.write(`uncovered:${t.key}|${t.target}\n`);
        return 1;
      }
      process.stdout.write('check-coverage: OK\n');
      return 0;
    }
    if (opts.cmd === 'check-baseline-match') {
      const collected = loadBaseline(opts.collected ?? COLLECTED_PATH);
      const baseline = loadBaseline(opts.baseline ?? BASELINE_PATH);
      const r = compareCollectedBaseline(collected, baseline);
      if (!r.ok) {
        for (const line of baselineMatchLines(r)) process.stderr.write(`${line}\n`);
        return 1;
      }
      process.stdout.write('baseline-match: OK\n');
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
