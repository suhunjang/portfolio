// step 39 — axe 10개 시나리오 (설계 §6.1·§6.2 실행 모드)
// 수집(AXE_COLLECT=1): prepareForAxe → runAxe → writeCollected만.
// 일반: resolveBaselineMode() — check면 회귀·baseline·plan 검사, pending이면 준비까지 후 skip.
import { expect } from '@playwright/test';
import { test } from '../helpers/theme.js';
import { prepareForAxe } from '../helpers/axe-prepare.js';
import {
  runAxe,
  writeCollected,
  resolveBaselineMode,
  loadBaseline,
  checkRegression,
  validateBaseline,
  loadPlan,
  validateRemediationPlan,
  PLAN_PATH,
} from '../helpers/axe.js';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const REPO_ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '../..');
const COLLECT = process.env.AXE_COLLECT === '1';
const OVERLAY_PROJECTS = ['desktop-dark', 'desktop-light'];

for (const scenario of ['page', 'modal', 'lightbox']) {
  test(`axe ${scenario}`, async ({ page }, testInfo) => {
    const project = testInfo.project.name;
    test.skip(scenario !== 'page' && !OVERLAY_PROJECTS.includes(project), `${scenario}: desktop only`);
    test.setTimeout(120000);

    // 일반 모드는 준비 전에 모드를 확정한다(throw면 실패).
    const mode = COLLECT ? 'collect' : resolveBaselineMode();

    await page.goto('/');
    const { include } = await prepareForAxe(page, { scenario });
    if (mode === 'pending') {
      test.skip(true, 'axe classification pending (step 40)');
      return;
    }
    const violations = await runAxe(page, { include });

    if (mode === 'collect') {
      writeCollected(scenario, project, violations);
      return;
    }

    // mode === 'check'
    const baseline = loadBaseline();
    expect(checkRegression(violations, baseline, scenario, project)).toEqual([]);
    if (scenario === 'page' && project === 'desktop-dark') {
      expect(validateBaseline(baseline)).toEqual([]);
      if (fs.existsSync(path.join(REPO_ROOT, PLAN_PATH))) {
        expect(validateRemediationPlan(loadPlan(), baseline, { coverage: false })).toEqual([]);
      }
    }
  });
}
