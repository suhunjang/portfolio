// step 20 — markup patch 검사·guard 입력 수집·실저장소 guard (설계 §11.4).
// checkMarkupPatch·runGuard는 순수 함수. collectGuardInput은 읽기만 한다(git show·git diff·CSS 두 파일).
import { spawnSync } from 'node:child_process';
import { readFile } from 'node:fs/promises';
import { dirname, join, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';
import { checkCss } from './design-guard-css.js';

export const GUARD_BASE = 'd0a8a6e462bc1366757b1401c3ba7aeb0fbf391d';
const REPO_ROOT = resolve(dirname(fileURLToPath(import.meta.url)), '..', '..');
const STYLE = 'css/style.css';
const THEMES = 'css/themes.css';
const PATCH_ARGS = ['diff', '--no-renames', '--unified=0', GUARD_BASE, '--'];

// 추가 줄에서 찾는 markup asset 토큰. HTML 태그·속성은 대소문자 무시, JS style 속성 접근은 원문.
const HTML_TOKENS = ['<img', '<svg', '<picture', '<video', '<i ', '<i>', '<link', '<script', '<font', 'style='];
const JS_TOKENS = ['.style.color', '.style.background', '.style.font'];
const HUNK_RE = /^@@ -\d+(?:,\d+)? \+(\d+)(?:,\d+)? @@/;

const hasAsset = (line) => {
  const lower = line.toLowerCase();
  return HTML_TOKENS.some((t) => lower.includes(t)) || JS_TOKENS.some((t) => line.includes(t));
};

// unified diff의 추가 줄만 본다. n = 새 파일 기준 줄 번호(hunk 헤더 +start부터, 문맥 줄도 센다).
// 파일 헤더(diff --git·index·---·+++)와 hunk 밖 줄, 삭제 줄, "\ No newline" 줄은 무시.
export function checkMarkupPatch(patch, kind) {
  const out = [];
  let inHunk = false;
  let line = 0;
  for (const raw of String(patch).split('\n')) {
    if (raw.startsWith('diff --git ')) { inHunk = false; continue; }
    const m = HUNK_RE.exec(raw);
    if (m) { inHunk = true; line = Number(m[1]); continue; }
    if (!inHunk) continue;
    if (raw.startsWith('+')) {
      if (hasAsset(raw.slice(1))) out.push(`markup-asset:${kind}:${line}`);
      line += 1;
    } else if (raw.startsWith(' ')) {
      line += 1;
    }
  }
  return out;
}

function runGit(args, root) {
  const r = spawnSync('git', args, { cwd: root, maxBuffer: 256 * 1024 * 1024 });
  if (r.error) throw r.error;
  if (r.status !== 0) throw new Error(`git ${args.join(' ')} failed: ${String(r.stderr).trim()}`);
  return r.stdout;
}

// 호출 순서 고정: git show style → git show themes → worktree style·themes 읽기 → diff index.html → diff js/main.js.
export async function collectGuardInput({ git, fs = { readFile }, root = REPO_ROOT } = {}) {
  const readGit = git ?? ((args) => runGit(args, root));
  const text = (v) => String(v);
  const baseCss = text(await readGit(['show', `${GUARD_BASE}:${STYLE}`]));
  const baseThemes = text(await readGit(['show', `${GUARD_BASE}:${THEMES}`]));
  const currentCss = text(await fs.readFile(join(root, STYLE), 'utf8'));
  const currentThemes = text(await fs.readFile(join(root, THEMES), 'utf8'));
  const htmlPatch = text(await readGit([...PATCH_ARGS, 'index.html']));
  const jsPatch = text(await readGit([...PATCH_ARGS, 'js/main.js']));
  return { baseCss, currentCss, baseThemes, currentThemes, htmlPatch, jsPatch };
}

export function runGuard({ baseCss, currentCss, baseThemes, currentThemes, htmlPatch, jsPatch }) {
  return [
    ...checkCss({ baseCss, currentCss, baseThemes, currentThemes }),
    ...checkMarkupPatch(htmlPatch, 'index.html'),
    ...checkMarkupPatch(jsPatch, 'js/main.js'),
  ];
}
