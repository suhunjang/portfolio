# Step 21 — tests-browser-smoke

- 목적: 브라우저 설치, §THEME `installProjectTheme`·`test` fixture·`collectConsoleErrors`, 6 project smoke(§12 제거 파일은 참고하지 않고 새로 작성).
- 17분 / 선행 0~20 / 공통 §9 / gate GATE
- 허용(exact): `tests/helpers/theme.js`, `tests/specs/smoke.spec.js`
- runtime: R0 + `tests/.pw-browsers/**`
- 추가 금지: §12 backup 참조·복원, `page.addInitScript`로 테마 주입, 비-null 저장값 덮어쓰기

## 작업
1. `SNAP 21` → `W npm --prefix tests run browsers:install`.
2. `theme.js` = 설계 §8.3 §THEME: `installProjectTheme(context, testInfo)`(project name `/-(dark|light)$/` strict 추출·아니면 throw, `context.addInitScript` 정확히 1회, init script는 origin localStorage `THEME_KEY`가 `null`일 때만 setItem, `THEME_KEY`는 `js/main.js`에서 정규식 추출); `test` = `test.extend`로 `context` fixture가 navigation 전 `installProjectTheme` 호출; `collectConsoleErrors(page)`(§8.3).
3. RED `smoke.spec.js`(6 project, theme.js의 `test` 사용):
   - (a) 기본 `page` goto `/` → `html[data-theme]` = project suffix, heroName 보임
   - (b) `const p2 = await context.newPage()` → goto `/` → `html[data-theme]` = suffix
   - (c) seed page(`context.newPage()`) goto `/` → `localStorage.setItem(THEME_KEY, 반대 테마)` → close → 새 `context.newPage()` goto `/` → `localStorage.getItem(THEME_KEY)` = 반대 테마, `html[data-theme]` = 반대 테마(덮어쓰지 않음)
   - `installProjectTheme` 단위: project name `desktop` 등 suffix 없음 → throw; 같은 context에 `addInitScript` 호출 1회(spy)
   - console: collect → goto → finish 두 배열 `[]`, 비동기 throw 주입 시 pageErrors 1건
4. 구현 → GREEN.

## AC
- `T smoke.spec.js && FULL && GATE 21 tests/helpers/theme.js,tests/specs/smoke.spec.js tests/helpers/theme.js,tests/specs/smoke.spec.js`
