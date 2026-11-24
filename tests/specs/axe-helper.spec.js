// step 28 — axe canonical target (설계 §6.1·§6.2): ALIASES · canonicalTargetInPage · canonicalFromDescriptor · runAxe
import { test, expect } from '@playwright/test';
import { ALIASES, canonicalTargetInPage, canonicalFromDescriptor, runAxe } from '../helpers/axe.js';

const RULE = 'color-contrast';

const wrap = (body) => `<!doctype html><html lang="ko"><head><title>t</title></head><body>${body}</body></html>`;

async function keyOf(page, html, selector, ruleId = RULE) {
  await page.setContent(wrap(html));
  return canonicalTargetInPage(page, ruleId, selector);
}

test.describe('step 28 axe-canonical', () => {
  test.beforeEach(async ({}, testInfo) => {
    test.skip(testInfo.project.name !== 'desktop-dark', 'desktop-dark 전용');
  });

  test('ALIASES는 §6.1 두 alias 그대로다', () => {
    expect(ALIASES).toEqual({ '## — Stack & Contact': '## — Contact', '기술 스택 & 연락처': '연락처' });
  });

  test('canonicalFromDescriptor: anchor 우선순위·textSig fallback·숫자 #·80자', () => {
    const empty = { textContent: '', ariaLabel: null, alt: null, title: null, src: null };
    const t = (anchor, text = {}) => canonicalFromDescriptor({ ruleId: 'r', anchor, text: { ...empty, ...text } });
    expect(t({ kind: 'featured', value: '5' }, { textContent: ' A\n  b ' })).toBe('r::featured:5::A b');
    expect(t({ kind: 'project', value: '5' }, { textContent: 'x' })).toBe('r::project:5::x');
    expect(t({ kind: 'id', value: 'career' }, { textContent: 'x' })).toBe('r::#career::x');
    expect(t({ kind: 'landmark', value: 'main' }, { textContent: 'x' })).toBe('r::main::x');
    expect(t({ kind: 'document' }, { textContent: 'x' })).toBe('r::document::x');
    expect(t({ kind: 'document' }, { ariaLabel: 'Menu 2', alt: 'a', title: 't' })).toBe('r::document::Menu #');
    expect(t({ kind: 'document' }, { alt: 'Alt', title: 't' })).toBe('r::document::Alt');
    expect(t({ kind: 'document' }, { title: 'Ti' })).toBe('r::document::Ti');
    expect(t({ kind: 'document' }, { src: 'https://x.test/img/shot-12.png?v=3' })).toBe('r::document::shot-##.png');
    expect(t({ kind: 'document' }, {})).toBe('r::document::');
    expect(t({ kind: 'document' }, { textContent: 'y'.repeat(100) })).toBe(`r::document::${'y'.repeat(80)}`);
    expect(t({ kind: 'document' }, { textContent: '04 — Stack & Contact' })).toBe('r::document::## — Contact');
    expect(() => t({ kind: 'bogus' }, {})).toThrow();
  });

  test('section#career subtree 이동·h3→span·01→04는 key 같음', async ({ page }) => {
    const a = await keyOf(
      page,
      '<header><nav>n</nav></header><main><section id="career"><h3 class="t">01 — Career</h3></section><section id="x">x</section></main>',
      '.t',
    );
    const b = await keyOf(
      page,
      '<header><nav>n</nav></header><main><section id="x">x</section><div><section id="career"><span class="t">04 — Career</span></section></div></main>',
      '.t',
    );
    expect(a).toBe('color-contrast::#career::## — Career');
    expect(b).toBe(a);
  });

  test('h3만 section#career 밖으로 이동하면 key 다름', async ({ page }) => {
    const a = await keyOf(page, '<main><section id="career"><h3 class="t">01 — Career</h3></section></main>', '.t');
    const b = await keyOf(page, '<main><h3 class="t">01 — Career</h3><section id="career"></section></main>', '.t');
    expect(b).toBe('color-contrast::main::## — Career');
    expect(b).not.toBe(a);
  });

  test('[data-project=5] 안 div→p는 key 같음, 텍스트 다르면 다름', async ({ page }) => {
    const a = await keyOf(page, '<main id="m"><article data-project="5"><div class="d">Hello world</div></article></main>', '.d');
    const b = await keyOf(page, '<main id="m"><article data-project="5"><p class="d">Hello   world</p></article></main>', '.d');
    const c = await keyOf(page, '<main id="m"><article data-project="5"><p class="d">Hello there</p></article></main>', '.d');
    expect(a).toBe('color-contrast::project:5::Hello world');
    expect(b).toBe(a);
    expect(c).not.toBe(a);
  });

  test('project:5 ≠ featured:5', async ({ page }) => {
    const p = await keyOf(page, '<main><article data-project="5"><p class="d">T</p></article></main>', '.d');
    const f = await keyOf(page, '<main><article data-featured-card data-project="5"><p class="d">T</p></article></main>', '.d');
    expect(p).toBe('color-contrast::project:5::T');
    expect(f).toBe('color-contrast::featured:5::T');
    expect(p).not.toBe(f);
  });

  test('alias 적용 후 key 같음', async ({ page }) => {
    const a = await keyOf(page, '<main><section id="contact"><h2 class="t">04 — Stack &amp; Contact</h2></section></main>', '.t');
    const b = await keyOf(page, '<main><section id="contact"><h2 class="t">05 — Contact</h2></section></main>', '.t');
    expect(a).toBe('color-contrast::#contact::## — Contact');
    expect(b).toBe(a);
    const c = await keyOf(page, '<main><section id="contact"><h3 class="t">기술 스택 &amp; 연락처</h3></section></main>', '.t');
    const d = await keyOf(page, '<main><section id="contact"><h3 class="t">연락처</h3></section></main>', '.t');
    expect(c).toBe('color-contrast::#contact::연락처');
    expect(d).toBe(c);
  });

  test('canonicalTargetInPage: 없는 selector는 throw', async ({ page }) => {
    await page.setContent(wrap('<main></main>'));
    await expect(canonicalTargetInPage(page, RULE, '.nope')).rejects.toThrow(/not found/);
  });

  test('runAxe: serious/critical만, include 범위, targets·selectors 정렬', async ({ page }) => {
    await page.setContent(
      wrap('<main><section id="a"><img src="/img/p1.png"></section><section id="b"><img src="/img/p2.png"></section></main>'),
    );
    const all = await runAxe(page);
    const alt = all.find((v) => v.ruleId === 'image-alt');
    expect(alt).toBeTruthy();
    expect(['serious', 'critical']).toContain(alt.impact);
    expect(alt.targets).toEqual(['image-alt::#a::p#.png', 'image-alt::#b::p#.png']);
    expect(alt.selectors).toEqual([...alt.selectors].sort());
    expect(alt.selectors).toHaveLength(2);
    for (const v of all) expect(['serious', 'critical']).toContain(v.impact);
    const onlyB = await runAxe(page, { include: '#b' });
    expect(onlyB.find((v) => v.ruleId === 'image-alt').targets).toEqual(['image-alt::#b::p#.png']);
  });
});
