// step 20 — tests/helpers/design-guard.js checkMarkupPatch·collectGuardInput·runGuard (설계 §11.4, node 전용, desktop-dark에서만 실행)
import { test, expect } from '@playwright/test';
import { checkMarkupPatch, collectGuardInput, runGuard, GUARD_BASE } from '../helpers/design-guard.js';

const BASE = 'd0a8a6e462bc1366757b1401c3ba7aeb0fbf391d';
const CSS = 'body{color:#111;font-family:"Pretendard",sans-serif}';
const THEMES = ':root{--brand:#3355ff}';

const patch = (file, hunks) => [
  `diff --git a/${file} b/${file}`,
  'index 1111111..2222222 100644',
  `--- a/${file}`,
  `+++ b/${file}`,
  ...hunks,
].join('\n') + '\n';

test.describe('step 20 design-guard', () => {
  test.beforeEach(({}, testInfo) => {
    test.skip(testInfo.project.name !== 'desktop-dark', 'node 전용 검사는 desktop-dark에서만 실행');
  });

  test('checkMarkupPatch: 추가 줄 asset → markup-asset:{kind}:{새 파일 줄 번호}', () => {
    const p = patch('index.html', [
      '@@ -3,0 +4,5 @@',
      '+<img src="a.png">',
      '+<svg viewBox="0 0 1 1"></svg>',
      '+<i class="x"></i>',
      '+<p style="color:red">t</p>',
      '+<p>ok</p>',
      '@@ -20 +25 @@',
      '-<img src="old.png">',
      '+<picture></picture>',
    ]);
    expect(checkMarkupPatch(p, 'index.html')).toEqual([
      'markup-asset:index.html:4',
      'markup-asset:index.html:5',
      'markup-asset:index.html:6',
      'markup-asset:index.html:7',
      'markup-asset:index.html:25',
    ]);
    const js = patch('js/main.js', ['@@ -9,0 +10,2 @@', '+el.style.color = x;', '+el.textContent = x;']);
    expect(checkMarkupPatch(js, 'js/main.js')).toEqual(['markup-asset:js/main.js:10']);
    const more = patch('js/main.js', [
      '@@ -1,0 +1,8 @@',
      '+el.style.background = x;', '+el.style.fontSize = x;', '+<video></video>', '+<i>x</i>',
      '+<link rel="x">', '+<script src="y"></script>', '+<font color="red">', '+const a = 1;',
    ]);
    expect(checkMarkupPatch(more, 'k')).toEqual([1, 2, 3, 4, 5, 6, 7].map((n) => `markup-asset:k:${n}`));
  });

  test('checkMarkupPatch: 삭제·문맥·헤더 줄 무시, 정상 []', () => {
    const p = patch('index.html', [
      '@@ -1,3 +1,2 @@',
      ' <img src="ctx.png">',
      '-<svg></svg>',
      '-el.style.color = x;',
      '+<p class="lead">text</p>',
      '\\ No newline at end of file',
    ]);
    expect(checkMarkupPatch(p, 'index.html')).toEqual([]);
    const header = ['diff --git a/<img>.html b/<img>.html', '--- a/<svg>', '+++ b/<svg>', '@@ -1 +1 @@', '-a', '+b'].join('\n');
    expect(checkMarkupPatch(header, 'index.html')).toEqual([]);
    expect(checkMarkupPatch('', 'index.html')).toEqual([]);
  });

  test('collectGuardInput: git·fs 호출 기록과 runGuard', async () => {
    expect(GUARD_BASE).toBe(BASE);
    const gitCalls = [];
    const fsCalls = [];
    const html = patch('index.html', ['@@ -1,0 +2 @@', '+<img src="a.png">']);
    const git = (args) => {
      gitCalls.push([...args]);
      const key = args.join(' ');
      if (key === `show ${BASE}:css/style.css`) return Buffer.from(CSS);
      if (key === `show ${BASE}:css/themes.css`) return Buffer.from(THEMES);
      if (key === `diff --no-renames --unified=0 ${BASE} -- index.html`) return Buffer.from(html);
      if (key === `diff --no-renames --unified=0 ${BASE} -- js/main.js`) return Buffer.from('');
      throw new Error(`unexpected git ${key}`);
    };
    const fs = {
      readFile: async (p, enc) => {
        fsCalls.push([p, enc]);
        if (p.endsWith('css/style.css')) return CSS;
        if (p.endsWith('css/themes.css')) return THEMES;
        throw new Error(`unexpected read ${p}`);
      },
    };
    const input = await collectGuardInput({ git, fs, root: '/repo' });
    expect(gitCalls).toEqual([
      ['show', `${BASE}:css/style.css`],
      ['show', `${BASE}:css/themes.css`],
      ['diff', '--no-renames', '--unified=0', BASE, '--', 'index.html'],
      ['diff', '--no-renames', '--unified=0', BASE, '--', 'js/main.js'],
    ]);
    expect(fsCalls).toEqual([['/repo/css/style.css', 'utf8'], ['/repo/css/themes.css', 'utf8']]);
    expect(input).toEqual({ baseCss: CSS, currentCss: CSS, baseThemes: THEMES, currentThemes: THEMES, htmlPatch: html, jsPatch: '' });
    expect(runGuard(input)).toEqual(['markup-asset:index.html:2']);
    expect(runGuard({ ...input, htmlPatch: '' })).toEqual([]);
    const bad = runGuard({ ...input, currentThemes: `${THEMES} `, jsPatch: patch('js/main.js', ['@@ -0,0 +1 @@', '+el.style.color = x;']) });
    expect(bad).toEqual(['themes-changed', 'markup-asset:index.html:2', 'markup-asset:js/main.js:1']);
  });

  test('실저장소 runGuard(await collectGuardInput()) → []', async () => {
    expect(runGuard(await collectGuardInput())).toEqual([]);
  });
});
