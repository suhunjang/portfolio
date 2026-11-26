// step 24 — content-data-baseline (설계 §5): BASE data fixture·데이터 보존, 6 project 전부 실행
import { readFileSync } from 'node:fs';
import { expect } from '@playwright/test';
import { test } from '../helpers/theme.js';
import { norm, readLiveData, normalizeFeatured } from '../helpers/content.js';

const baseline = JSON.parse(readFileSync(new URL('../fixtures/baseline-data.json', import.meta.url), 'utf8'));
const FEATURED = [1, 5, 7];

function withFeatured(data, idxs, value = true) {
  const d = structuredClone(data);
  for (const i of idxs) d.PROJECTS[i] = { ...d.PROJECTS[i], featured: value };
  return d;
}

test.describe('step 24 content-data', () => {
  test('baseline fixture: 키·개수', () => {
    expect(Object.keys(baseline)).toEqual(['PROFILE', 'STATS', 'CAREER', 'VIS_ACCENT', 'PROJECTS', 'STRENGTHS', 'SKILLS']);
    expect(baseline.STATS).toHaveLength(4);
    expect(baseline.PROJECTS).toHaveLength(13);
    expect(baseline.STRENGTHS).toHaveLength(6);
    expect(baseline.PROJECTS.some((p) => 'featured' in p)).toBe(false);
    const html = readFileSync(new URL('../fixtures/baseline-index.html', import.meta.url), 'utf8');
    expect(html).toContain('id="heroName"');
  });

  test('norm: 공백 정규화', () => {
    expect(norm('  a \n\t b  ')).toBe('a b');
    expect(norm(5)).toBe('5');
  });

  test('normalizeFeatured: 1·5·7 제거, 입력 불변', () => {
    const input = withFeatured(baseline, FEATURED);
    const before = JSON.stringify(input);
    const out = normalizeFeatured(input);
    expect(out).toEqual(baseline);
    expect(out).not.toBe(input);
    expect(JSON.stringify(input)).toBe(before);
    expect(normalizeFeatured(baseline)).toEqual(baseline);
    expect(normalizeFeatured(withFeatured(baseline, [5]))).toEqual(baseline);
  });

  test('normalizeFeatured: 그 밖 index·true 아님 throw', () => {
    expect(() => normalizeFeatured(withFeatured(baseline, [0]))).toThrow();
    expect(() => normalizeFeatured(withFeatured(baseline, [1, 12]))).toThrow();
    expect(() => normalizeFeatured(withFeatured(baseline, [1], false))).toThrow();
    expect(() => normalizeFeatured(withFeatured(baseline, [5], 'true'))).toThrow();
    expect(() => normalizeFeatured(withFeatured(baseline, [7], null))).toThrow();
  });

  test('live data = baseline (featured 정규화), featured 없음 또는 1·5·7만, 빈 연락처', async ({ page }) => {
    await page.goto('/');
    const live = await readLiveData(page);
    expect(normalizeFeatured(live)).toEqual(baseline);
    const featured = live.PROJECTS.flatMap((p, i) => ('featured' in p ? [i] : []));
    expect([[], FEATURED]).toContainEqual(featured);
    expect(live.PROFILE.email).toBe('');
    expect(live.PROFILE.phone).toBe('');
    for (const v of Object.values(live.PROFILE.social)) expect(v).toBe('');
    expect(Object.keys(live.PROFILE.social)).toEqual(Object.keys(baseline.PROFILE.social));
  });

  test('렌더 개수: stats 4·timeline = CAREER·project-card 13·strengths 6', async ({ page }) => {
    await page.goto('/');
    await expect(page.locator('#heroStats > li')).toHaveCount(4);
    await expect(page.locator('#timeline .timeline-item')).toHaveCount(baseline.CAREER.length);
    await expect(page.locator('#projectGrid .project-card')).toHaveCount(13);
    await expect(page.locator('#strengthsGrid .strength-card')).toHaveCount(6);
  });

  test('#projectGrid data-project 0~12 순서·제목 = baseline', async ({ page }) => {
    await page.goto('/');
    const cards = page.locator('#projectGrid .project-card');
    await expect(cards).toHaveCount(13);
    const got = await cards.evaluateAll((els) =>
      els.map((el) => ({ idx: el.getAttribute('data-project'), title: el.querySelector('.project-title')?.textContent ?? null })),
    );
    expect(got.map((g) => g.idx)).toEqual(baseline.PROJECTS.map((_, i) => String(i)));
    expect(got.map((g) => norm(g.title))).toEqual(baseline.PROJECTS.map((p) => norm(p.title)));
  });
});
