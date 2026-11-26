import { defineConfig } from '@playwright/test';

const VIEWPORTS = {
  mobile: { width: 375, height: 812 },
  tablet: { width: 768, height: 1024 },
  desktop: { width: 1280, height: 800 },
};
const THEMES = ['dark', 'light'];

const projects = [];
for (const [device, viewport] of Object.entries(VIEWPORTS)) {
  for (const theme of THEMES) {
    projects.push({
      name: `${device}-${theme}`,
      metadata: { theme },
      use: { viewport, colorScheme: theme },
    });
  }
}

export default defineConfig({
  testDir: './specs',
  outputDir: './test-results',
  reporter: 'list',
  retries: 0,
  // 직렬화(고정): 실제 저장소를 읽는 parity·snapshot 테스트와 runtime probe 테스트가 겹치지 않게 한다.
  workers: 1,
  fullyParallel: false,
  use: {
    baseURL: 'http://127.0.0.1:4173',
  },
  webServer: {
    command: 'python3 -m http.server 4173 --bind 127.0.0.1',
    cwd: '..',
    url: 'http://127.0.0.1:4173',
    reuseExistingServer: true,
  },
  projects,
});
