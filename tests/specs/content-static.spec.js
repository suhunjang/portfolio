// step 25 — content-static-baseline (설계 §5): BASE index.html 정적 본문 추출·허용 예외 판정, 6 project 전부 실행
import { readFileSync } from 'node:fs';
import { expect } from '@playwright/test';
import { test } from '../helpers/theme.js';
import { extractStatic } from '../helpers/content.js';

const BASE_HTML = readFileSync(new URL('../fixtures/baseline-index.html', import.meta.url), 'utf8');
const EXC = JSON.parse(readFileSync(new URL('../fixtures/content-exceptions.json', import.meta.url), 'utf8'));

const STATIC_KEYS = [
  'title',
  'metaDescription',
  'navLabels',
  'heroEyebrow',
  'ctaLabels',
  'kickers',
  'sectionTitles',
  'sectionSubs',
  'aboutParagraphs',
  'aboutPoints',
  'aboutMetaTerms',
  'contactHeading',
  'contactText',
  'footerNote',
  'footerTop',
];

// kickers·sectionTitles가 base/final 중 어느 쪽과 정확히 같은지. 아니면 null.
function modeOf(actual, pair) {
  const s = JSON.stringify(actual);
  if (s === JSON.stringify(pair.base)) return 'base';
  if (s === JSON.stringify(pair.final)) return 'final';
  return null;
}

// §5 허용 예외 판정: 위반 목록(빈 배열 = 통과).
function checkStatic(actual, subsectionTitles, base) {
  const errors = [];
  const kMode = modeOf(actual.kickers, EXC.kickers);
  if (!kMode) errors.push('kickers');
  const tMode = modeOf(actual.sectionTitles, EXC.titles);
  if (!tMode) errors.push('sectionTitles');
  if (tMode === 'final') {
    if (JSON.stringify(subsectionTitles) !== JSON.stringify([EXC.subsectionTitleFinal])) errors.push('subsectionTitle');
  }
  for (const k of STATIC_KEYS) {
    if (k === 'kickers' || k === 'sectionTitles') continue;
    if (JSON.stringify(actual[k]) !== JSON.stringify(base[k])) errors.push(k);
  }
  if (JSON.stringify(Object.keys(actual)) !== JSON.stringify(STATIC_KEYS)) errors.push('keys');
  return errors;
}

async function subsectionTitlesOf(page) {
  return page.$$eval('h3.subsection-title', (els) => els.map((e) => e.textContent.replace(/\s+/g, ' ').trim()));
}

async function extractFrom(browser, html) {
  const ctx = await browser.newContext({ javaScriptEnabled: false });
  try {
    const page = await ctx.newPage();
    await page.setContent(html, { waitUntil: 'domcontentloaded' });
    return { stat: await extractStatic(page), subs: await subsectionTitlesOf(page) };
  } finally {
    await ctx.close();
  }
}

test.describe('step 25 content-static', () => {
  test('content-exceptions.json 형태', () => {
    expect(Object.keys(EXC)).toEqual(['kickers', 'titles', 'featured', 'subsectionTitleFinal']);
    expect(EXC.featured.indexes).toEqual([1, 5, 7]);
    expect(EXC.kickers.final).toEqual(['01 — Career', '02 — Projects', '03 — Strengths', '04 — About', '05 — Contact']);
    expect(EXC.titles.final).toEqual(['경력 & 창업', '프로젝트 & 제품', '업무상 강점', '소개', '연락처']);
    expect(EXC.subsectionTitleFinal).toBe('기술 스택');
  });

  test('BASE 추출: StaticContent 값', async ({ browser }) => {
    const { stat, subs } = await extractFrom(browser, BASE_HTML);
    expect(Object.keys(stat)).toEqual(STATIC_KEYS);
    expect(stat.title).toBe('장수훈 · COO · CTO · Full-Stack & AI Leader');
    expect(stat.metaDescription).toContain('코드와 사업을 동시에 운영하는');
    expect(stat.navLabels).toEqual(['About', 'Career', 'Contact', 'Projects', 'Strengths']);
    expect(stat.heroEyebrow).toBe('👋 안녕하세요, 저는');
    expect(stat.ctaLabels).toEqual(['프로젝트 보기', '연락하기']);
    expect(stat.kickers).toEqual(EXC.kickers.base);
    expect(stat.sectionTitles).toEqual(EXC.titles.base);
    expect(stat.sectionSubs).toEqual([
      '이력서에 정리된 6가지 핵심 강점 — 기술·제품·경영이 한 사람 안에서 만나는 지점입니다.',
    ]);
    expect(stat.aboutParagraphs).toHaveLength(1);
    expect(stat.aboutParagraphs[0]).toMatch(/^저는 기술과 사업의 경계에서 일합니다\. .*COO입니다\.$/);
    expect(stat.aboutPoints).toHaveLength(3);
    expect(stat.aboutMetaTerms).toEqual(['Role', 'Focus', 'Location']);
    expect(stat.contactHeading).toBe('함께 만들어요');
    expect(stat.contactText).toBe('새로운 제품, 협업, 그리고 기술 자문에 대한 이야기에 늘 관심이 있습니다.');
    expect(stat.footerNote).toBe('Built with HTML · CSS · JS');
    expect(stat.footerTop).toBe('↑ Top');
    expect(subs).toEqual([]);
    expect(checkStatic(stat, subs, stat)).toEqual([]);
  });

  test('합성 base·final 통과, 혼합·한 글자 차이 거부', async ({ browser }) => {
    const { stat: base } = await extractFrom(browser, BASE_HTML);
    const final = { ...structuredClone(base), kickers: [...EXC.kickers.final], sectionTitles: [...EXC.titles.final] };
    expect(checkStatic(structuredClone(base), [], base)).toEqual([]);
    expect(checkStatic(final, ['기술 스택'], base)).toEqual([]);
    // final이면 subsection h3 정확히 1개
    expect(checkStatic(final, [], base)).toEqual(['subsectionTitle']);
    expect(checkStatic(final, ['기술 스택', '기술 스택'], base)).toEqual(['subsectionTitle']);
    expect(checkStatic(final, ['기술스택'], base)).toEqual(['subsectionTitle']);
    // 혼합
    const mixedK = { ...structuredClone(base), kickers: [EXC.kickers.final[0], ...EXC.kickers.base.slice(1)] };
    expect(checkStatic(mixedK, [], base)).toEqual(['kickers']);
    const mixedT = { ...structuredClone(base), sectionTitles: [...EXC.titles.final.slice(0, 4), EXC.titles.base[4]] };
    expect(checkStatic(mixedT, ['기술 스택'], base)).toEqual(['sectionTitles']);
    // 한 글자 차이
    const oneK = { ...structuredClone(final), kickers: [...EXC.kickers.final.slice(0, 4), '05 — Contacts'] };
    expect(checkStatic(oneK, ['기술 스택'], base)).toEqual(['kickers']);
    const oneT = { ...structuredClone(base), sectionTitles: ['소게', ...EXC.titles.base.slice(1)] };
    expect(checkStatic(oneT, [], base)).toEqual(['sectionTitles']);
    for (const k of STATIC_KEYS) {
      if (k === 'kickers' || k === 'sectionTitles') continue;
      const v = structuredClone(final);
      if (Array.isArray(v[k])) v[k][0] = v[k][0] + 'x';
      else v[k] = v[k].slice(0, -1) + 'x';
      expect(checkStatic(v, ['기술 스택'], base), k).toEqual([k]);
    }
    // 합성 final HTML 추출도 통과
    let html = BASE_HTML;
    EXC.kickers.base.forEach((s, i) => {
      html = html.replace(`>${s.replace('&', '&amp;')}</span>`, `>${EXC.kickers.final[i]}</span>`);
    });
    EXC.titles.base.forEach((s, i) => {
      html = html.replace(`>${s.replace('&', '&amp;')}</h2>`, `>__T${i}__</h2>`);
    });
    EXC.titles.final.forEach((s, i) => {
      html = html.replace(`>__T${i}__</h2>`, `>${s.replace('&', '&amp;')}</h2>`);
    });
    html = html.replace('<div class="skills-grid"', '<h3 class="subsection-title">기술 스택</h3>\n<div class="skills-grid"');
    const synth = await extractFrom(browser, html);
    expect(synth.stat.kickers).toEqual(EXC.kickers.final);
    expect(synth.stat.sectionTitles).toEqual(EXC.titles.final);
    expect(checkStatic(synth.stat, synth.subs, base)).toEqual([]);
  });

  test('live index.html(JS 끔) = BASE (§5 예외 허용)', async ({ browser, baseURL }) => {
    const { stat: base } = await extractFrom(browser, BASE_HTML);
    const ctx = await browser.newContext({ javaScriptEnabled: false, baseURL });
    try {
      const page = await ctx.newPage();
      await page.goto('/', { waitUntil: 'domcontentloaded' });
      const live = await extractStatic(page);
      expect(checkStatic(live, await subsectionTitlesOf(page), base)).toEqual([]);
    } finally {
      await ctx.close();
    }
  });
});
