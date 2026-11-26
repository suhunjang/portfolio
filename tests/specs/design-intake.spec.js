// step 12 — Claude Design intake fixture·check script (node 전용, desktop-dark에서만 실행, 외부 evidence 경로 읽지 않음)
import { test, expect } from '@playwright/test';
import { createHash } from 'node:crypto';
import fs from 'node:fs';
import path from 'node:path';
import { REPO_ROOT, designBlock, runPython } from '../helpers/synthetic-repo.js';

const FIXTURE = path.join(REPO_ROOT, 'tests/fixtures/claude-design-intake.json');
const SCRIPT = 'tests/scripts/design-intake-check.py';
const sha256 = (buf) => createHash('sha256').update(buf).digest('hex');
const NAMES = [
  'canvas.json', 'Main.dc.html', 'Foundations.dc.html', 'Components.dc.html', 'DesktopTop.dc.html',
  'DesktopExplore.dc.html', 'DesktopFirstLight.dc.html', 'Mobile.dc.html', 'MobileMenu.dc.html',
];

test.beforeEach(({}, testInfo) => {
  test.skip(testInfo.project.name !== 'desktop-dark', 'node 전용 검사는 desktop-dark에서만 실행');
});

test('fixture는 설계 §11.1 첫 fenced block과 같다', () => {
  const block = designBlock('### 11.1');
  const text = fs.readFileSync(FIXTURE, 'utf8');
  expect(text).toBe(block);
  expect(text.endsWith('}\n')).toBe(true);
  expect(JSON.parse(text)).toEqual(JSON.parse(block));
});

test('fixture files 9개·소문자 64hex, adopted·excluded·tokens', () => {
  const fx = JSON.parse(fs.readFileSync(FIXTURE, 'utf8'));
  expect(fx.schemaVersion).toBe(1);
  expect(Object.keys(fx.files)).toEqual(NAMES);
  for (const v of Object.values(fx.files)) expect(v).toMatch(/^[0-9a-f]{64}$/);
  expect(fx.adopted).toEqual([
    'explore-surface', 'hero-two-column-left', 'mobile-single-column', 'final-section-order', 'featured-three',
    'projects-thirteen-order', 'component-states', 'hit-target-44', 'section-padding', 'card-gap',
    'type-hierarchy', 'line-clamp', 'strength-stripe-removal',
  ]);
  expect(fx.excluded).toEqual([
    'new-color', 'color-role-change', 'dark-text-0d0f12', 'muted-grey-reassign', 'font-asset-change',
    'new-copy-or-number', 'new-section-image-icon', 'project-order-or-ia-change', 'placeholder-as-content',
  ]);
  expect(fx.tokens).toEqual({
    heroTwoColumnMinViewportPx: 1024,
    heroColumns: 'minmax(0, 5fr) minmax(0, 7fr)',
    heroColumnGapPx: 48,
    heroAreas: ['eyebrow summary', 'name summary', 'tagline summary', 'role cta', 'stats stats', 'featured featured'],
    sectionPaddingPx: { 375: 64, 768: 80, 1280: 96 },
    cardGapPx: 24,
    hitTargetMinPx: 44,
    blurbLineClamp: 3,
  });
});

test('합성 bundle로 check script 판정', () => {
  const work = path.join(REPO_ROOT, 'tests/.tmp', `design-intake-${process.pid}`);
  fs.rmSync(work, { recursive: true, force: true });
  const bundle = path.join(work, 'bundle');
  const summary = path.join(work, 'summary.md');
  const fixtureCopy = path.join(work, 'fixture.json');
  fs.mkdirSync(bundle, { recursive: true });
  try {
    const files = {};
    for (const n of NAMES) {
      const body = Buffer.from(`synthetic ${n}\n`);
      fs.writeFileSync(path.join(bundle, n), body);
      files[n] = sha256(body);
    }
    const summaryLines = () => ['# summary', '', ...NAMES.map((n) => `- \`${n}\` — \`${files[n]}\``), ''].join('\n');
    fs.writeFileSync(summary, summaryLines());
    const fx = JSON.parse(fs.readFileSync(FIXTURE, 'utf8'));
    fx.summaryPath = summary;
    fx.bundleDir = bundle;
    fx.files = files;
    const copyText = `${JSON.stringify(fx, null, 2)}\n`;
    fs.writeFileSync(fixtureCopy, copyText);

    const run = () => {
      const r = runPython(['-I', SCRIPT, '--fixture', fixtureCopy]);
      return { code: r.code, out: r.stdout.trim() };
    };

    expect(run()).toEqual({ code: 0, out: 'design-intake: OK' });

    // 바이트 변경
    const target = path.join(bundle, 'Mobile.dc.html');
    const orig = fs.readFileSync(target);
    fs.writeFileSync(target, Buffer.concat([orig, Buffer.from('x')]));
    expect(run()).toEqual({ code: 1, out: 'design-intake: hash mismatch:Mobile.dc.html' });
    fs.writeFileSync(target, orig);
    expect(run()).toEqual({ code: 0, out: 'design-intake: OK' });

    // 파일 추가
    const extra = path.join(bundle, 'extra.txt');
    fs.writeFileSync(extra, 'x');
    expect(run()).toEqual({ code: 1, out: 'design-intake: files mismatch' });
    fs.unlinkSync(extra);
    // 파일 누락
    const canvas = path.join(bundle, 'canvas.json');
    const canvasBody = fs.readFileSync(canvas);
    fs.unlinkSync(canvas);
    expect(run()).toEqual({ code: 1, out: 'design-intake: files mismatch' });
    fs.writeFileSync(canvas, canvasBody);

    // symlink
    const real = path.join(work, 'real-main.html');
    const main = path.join(bundle, 'Main.dc.html');
    const mainBody = fs.readFileSync(main);
    fs.writeFileSync(real, mainBody);
    fs.unlinkSync(main);
    fs.symlinkSync(real, main);
    expect(run()).toEqual({ code: 1, out: `design-intake: unsafe:${main}` });
    fs.unlinkSync(main);
    fs.writeFileSync(main, mainBody);
    // summary symlink
    const summaryReal = path.join(work, 'summary-real.md');
    fs.renameSync(summary, summaryReal);
    fs.symlinkSync(summaryReal, summary);
    expect(run()).toEqual({ code: 1, out: `design-intake: unsafe:${summary}` });
    fs.unlinkSync(summary);
    fs.renameSync(summaryReal, summary);
    expect(run()).toEqual({ code: 0, out: 'design-intake: OK' });

    // summary 줄 변경
    fs.writeFileSync(summary, summaryLines().replace(`\`${files['Components.dc.html']}\``, `\`${'0'.repeat(64)}\``));
    expect(run()).toEqual({ code: 1, out: 'design-intake: summary mismatch:Components.dc.html' });
    fs.writeFileSync(summary, summaryLines());
    expect(run()).toEqual({ code: 0, out: 'design-intake: OK' });

    // 사본 불변
    expect(fs.readFileSync(fixtureCopy, 'utf8')).toBe(copyText);
  } finally {
    fs.rmSync(work, { recursive: true, force: true });
  }
  expect(fs.existsSync(work)).toBe(false);
});
