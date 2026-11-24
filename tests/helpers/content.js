// step 24 — 콘텐츠 보존 helper (설계 §5): norm · readLiveData · normalizeFeatured
const FEATURED_INDEXES = new Set([1, 5, 7]);

export function norm(s) {
  return String(s).replace(/\s+/g, ' ').trim();
}

// 페이지의 data.js 전역(top-level const)을 BaselineData 형태의 JSON 값으로 읽는다.
export async function readLiveData(page) {
  return page.evaluate(() =>
    JSON.parse(
      JSON.stringify({
        PROFILE, // eslint-disable-line no-undef
        STATS, // eslint-disable-line no-undef
        CAREER, // eslint-disable-line no-undef
        VIS_ACCENT, // eslint-disable-line no-undef
        PROJECTS, // eslint-disable-line no-undef
        STRENGTHS, // eslint-disable-line no-undef
        SKILLS, // eslint-disable-line no-undef
      }),
    ),
  );
}

// 허용 예외 (1): PROJECTS index 1·5·7의 `featured: true`만 제거한 복제본. 그 밖은 throw.
export function normalizeFeatured(data) {
  const out = structuredClone(data);
  out.PROJECTS.forEach((p, i) => {
    if (!Object.prototype.hasOwnProperty.call(p, 'featured')) return;
    if (!FEATURED_INDEXES.has(i)) throw new Error(`normalizeFeatured: featured not allowed at index ${i}`);
    if (p.featured !== true) throw new Error(`normalizeFeatured: featured at index ${i} must be true`);
    delete p.featured;
  });
  return out;
}
