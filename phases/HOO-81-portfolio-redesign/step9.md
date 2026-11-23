# Step 9 — final-verification

- 예상 시간: 12분
- 실행 횟수: 테스트 1회(웹서버 1회), verify-scope --final 1회, self-test 1회
- 선행 step: 0~8 completed

## 공통: 시작 전 필수 확인 (read-first)

1. `README.md`를 읽는다. `CLAUDE.md`나 `AGENTS.md`가 있으면 함께 읽는다.
2. 설계 문서 두 개를 읽는다.
   - `docs/superpowers/specs/2026-07-29-quiet-executive-redesign-design.md`
   - `docs/superpowers/specs/2026-11-23-portfolio-layout-redesign-design.md` — 전체, 특히 §2, §11, §12
3. index.json에서 step 0~8이 completed인지 확인한다. 아니면 중단한다.
4. `tests/specs/` 목록을 확인한다.
   - smoke, content, interaction, first-visit, axe, hero, layout, focus, print가 모두 있어야 한다.
   - `axe-known.json`이 `[]`인지 확인한다.
5. `CLAUDE.md`, `docs/**`, `phases/**`, `.harness/**`는 읽기 전용이다. 문서 변경은 하네스만 한다.
6. main 직접 변경, merge, deploy, push는 금지다. PR 준비 상태까지만 진행한다.

## 허용 파일 (exact)

- `tests/specs/screenshots.spec.js`
- `tests/.gitignore` (`screenshots/` 항목 확인만)

## 수정 금지

- 사이트 파일 전부: `index.html`, `css/*`, `js/*`
- 기존 spec, fixtures, scripts
- 검증이 실패해도 사이트를 고치지 않는다. 원인 step 번호와 실패 출력을 보고하고 중단한다. 하네스가 해당 step을 다시 연다.

## 작업

1. `tests/specs/screenshots.spec.js`를 작성한다. 6개 project에서 실행한다.
   - reducedMotion reduce 상태로 전체 페이지를 `tests/screenshots/{project}-page.png`로 저장한다.
   - desktop project에서는 다음도 저장한다.
     - 대표 카드 3개 각각의 모달: `{project}-modal-{idx}.png`
     - lightbox: `{project}-lightbox.png`
     - print 미디어: `{project}-print.png`
   - 각 모달에 `.modal-visual svg text`가 있으면, computed font-family에 Space Grotesk가 포함되는지 assert한다.
   - 스크린샷은 gitignored다. 커밋하지 않고 경로만 로그에 남긴다.
2. 다음 명령을 순서대로 실행한다.
   - `npm --prefix tests run verify-scope:selftest`
   - `npm --prefix tests test`
   - `npm --prefix tests run verify-scope -- --final`
3. 결과 요약을 로그로만 출력한다. 파일로 쓰지 않는다.
   - spec별 통과 수와 project 6개 결과
   - axe 위반 0건, 콘솔 에러 0건
   - verify-scope OK, data.js featured 3줄

## 완료 기준 (AC)

`npm --prefix tests run verify-scope:selftest && npm --prefix tests test && npm --prefix tests run verify-scope -- --final` → 모두 exit 0
