// resume step 0 — verify-scope §R3 resume 면제 (node 전용, desktop-dark에서만 실행)
// 가짜 git 입력으로 collectInput → evaluatePaths를 호출한다.
import { test, expect } from '@playwright/test';
import { BASE } from '../scripts/scope-snapshot.mjs';
import {
  collectInput, evaluatePaths, GIT_DIFF_PATH_ARGS, GIT_DIFF_PATCH_ARGS,
} from '../scripts/verify-scope.mjs';

const RESUME_DESIGN = 'docs/superpowers/specs/2026-11-24-portfolio-redesign-resume-design.md';
const ORIGINAL_DESIGN = 'docs/superpowers/specs/2026-11-23-portfolio-layout-redesign-design.md';
const RESUME_PHASE = 'phases/HOO-81-portfolio-redesign-resume';

const EMPTY = { committed: [], staged: [], worktree: [], untracked: [], tracked: [] };

function fakeGit(scenario) {
  const s = { ...EMPTY, ...scenario };
  const z = (list) => list.map((p) => `${p}\0`).join('');
  return (args) => {
    if (args[0] === 'ls-files') return z(args.includes('--others') ? s.untracked : s.tracked);
    expect(args[0]).toBe('diff');
    if (args.includes('--unified=0')) return '';
    if (args.includes(BASE) && args.includes('HEAD')) return z(s.committed);
    if (args.includes('--cached')) return z(s.staged);
    return z(s.worktree);
  };
}
const evalScenario = (scenario) => evaluatePaths(collectInput({ git: fakeGit(scenario) }));

test.describe('verify-scope resume 면제 (§R3)', () => {
  test.beforeEach(({}, testInfo) => {
    test.skip(testInfo.project.name !== 'desktop-dark', 'node 전용 검사는 desktop-dark에서만 실행');
  });

  test('diff 인자 상수 불변', () => {
    expect([...GIT_DIFF_PATH_ARGS]).toEqual(['--no-renames', '--name-only']);
    expect([...GIT_DIFF_PATCH_ARGS]).toEqual(['--no-renames', '--unified=0']);
  });

  test('허용: committed resume 설계', () => {
    expect(evalScenario({ committed: [RESUME_DESIGN] })).toEqual([]);
  });

  for (const file of ['index.json', 'step0.md']) {
    for (const layer of ['committed', 'worktree', 'untracked']) {
      test(`허용: ${layer} ${RESUME_PHASE}/${file}`, () => {
        expect(evalScenario({ [layer]: [`${RESUME_PHASE}/${file}`] })).toEqual([]);
      });
    }
  }

  const violations = [
    [{ worktree: [RESUME_DESIGN] }, [`harness-uncommitted:worktree:${RESUME_DESIGN}`]],
    [{ staged: [RESUME_DESIGN] }, [`harness-uncommitted:staged:${RESUME_DESIGN}`]],
    [{ committed: ['docs/superpowers/specs/other.md'] },
      ['outside-scope:committed:docs/superpowers/specs/other.md']],
    [{ committed: [`${RESUME_DESIGN}.bak`] }, [`outside-scope:committed:${RESUME_DESIGN}.bak`]],
    [{ committed: ['phases/OTHER/x.json'] }, ['outside-scope:committed:phases/OTHER/x.json']],
    [{ worktree: ['phases/OTHER/x.json'] }, ['outside-scope:worktree:phases/OTHER/x.json']],
    [{ committed: [`${RESUME_PHASE}-x/a.json`] }, [`outside-scope:committed:${RESUME_PHASE}-x/a.json`]],
    [{ staged: ['.harness/policy.json'] }, ['harness-uncommitted:staged:.harness/policy.json']],
    [{ worktree: ['.harness/policy.json'] }, ['harness-uncommitted:worktree:.harness/policy.json']],
    [{ untracked: ['.harness/policy.json'] }, ['harness-uncommitted:untracked:.harness/policy.json']],
    [{ worktree: [ORIGINAL_DESIGN] }, [`harness-uncommitted:worktree:${ORIGINAL_DESIGN}`]],
    [{ staged: ['CLAUDE.md'] }, ['harness-uncommitted:staged:CLAUDE.md']],
    [{ worktree: ['CLAUDE.md'] }, ['harness-uncommitted:worktree:CLAUDE.md']],
    [{ untracked: ['CLAUDE.md'] }, ['harness-uncommitted:untracked:CLAUDE.md']],
  ];
  for (const [scenario, expected] of violations) {
    test(`위반: ${JSON.stringify(scenario)}`, () => {
      expect(evalScenario(scenario)).toEqual(expected);
    });
  }
});
