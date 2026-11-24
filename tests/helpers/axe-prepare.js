// step 29 — axe 실행 전 페이지 준비 (설계 §6.3): PREPARE_PREFIX · prepareError · withPrepareCode · preparePage

export const PREPARE_PREFIX = 'prepareForAxe: ';

export function prepareError(code, cause) {
  const err = cause === undefined
    ? new Error(PREPARE_PREFIX + code)
    : new Error(PREPARE_PREFIX + code, { cause });
  err.code = code;
  return err;
}

function isPrepareError(e) {
  return e instanceof Error && typeof e.code === 'string' && e.message === PREPARE_PREFIX + e.code;
}

// fn 실패를 code로 감싼다. 이미 prepareError면 안쪽 code를 그대로 유지한다.
export async function withPrepareCode(code, fn) {
  try {
    return await fn();
  } catch (e) {
    if (isPrepareError(e)) throw e;
    throw prepareError(code, e);
  }
}

// 테마·reduced-motion은 건드리지 않는다. fonts 대기 → 뷰포트 단위 스크롤로 reveal 유발 → 맨 위 복귀 → 모든 .reveal이 .in인지 확인.
export async function preparePage(page, { timeoutMs = 10000 } = {}) {
  await withPrepareCode('fonts-not-ready', () =>
    page.evaluate(
      (ms) =>
        Promise.race([
          document.fonts.ready.then(() => true),
          new Promise((_, reject) => setTimeout(() => reject(new Error(`fonts not ready in ${ms}ms`)), ms)),
        ]),
      timeoutMs,
    ),
  );

  const scrollSteps = await page.evaluate(async () => {
    const frame = () => new Promise((r) => requestAnimationFrame(() => requestAnimationFrame(r)));
    const step = Math.max(1, Math.floor(window.innerHeight * 0.8));
    let steps = 0;
    for (let y = 0; ; y += step) {
      window.scrollTo({ top: y, left: 0, behavior: 'instant' });
      steps += 1;
      await frame();
      const max = document.documentElement.scrollHeight - window.innerHeight;
      if (y >= max) break;
    }
    window.scrollTo({ top: 0, left: 0, behavior: 'instant' });
    await frame();
    return steps;
  });

  try {
    await page.waitForFunction(() => document.querySelectorAll('.reveal:not(.in)').length === 0, null, {
      timeout: timeoutMs,
    });
  } catch (e) {
    const hidden = await page.evaluate(() => document.querySelectorAll('.reveal:not(.in)').length);
    if (hidden > 0) throw prepareError(`reveal-hidden:${hidden}`, e);
  }

  const revealChecked = await page.evaluate(() => document.querySelectorAll('.reveal').length);
  return { revealChecked, scrollSteps };
}
