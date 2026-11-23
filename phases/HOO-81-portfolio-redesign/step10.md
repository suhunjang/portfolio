# Step 10 — final-verification

- 예상 시간: 12분
- 실행 횟수: self-test 1회, 테스트 1회(웹서버 1회), verify-scope --final 1회
- 선행 step: 0~9 completed

## 공통: 시작 전 필수 확인 (read-first)

1. 저장소 지침을 읽는다: `CLAUDE.md`(하네스 계약 포함), `README.md`. 하위 디렉터리에 `CLAUDE.md`나 `AGENTS.md`가 있으면 함께 읽는다.
2. 설계 문서를 읽는다.
   - `docs/superpowers/specs/2026-07-29-quiet-executive-redesign-design.md`
   - `docs/superpowers/specs/2026-11-23-portfolio-layout-redesign-design.md` 전체(특히 §2, §11, §12)
3. index.json에서 step 0~9가 completed인지 확인한다. 아니면 중단한다.
4. `tests/specs`에 다음 spec이 모두 있는지 확인한다: smoke, content, interaction, first-visit, axe, hero, layout, focus, print. 또 `axe-baseline.json`이 `[]`인지 확인한다.
5. 다음은 읽기 전용이다.
   - `CLAUDE.md`, `docs/**`, `phases/**`, `.harness/**`
   - 하네스 managed 파일: `scripts/**`, `.claude/**`, `.codex/**`, `templates/**`, `harness-manifest.json`, `pytest.ini`, `.python-version`, `.gitattributes`, 루트 `.gitignore`
6. git add·commit·push는 하네스만 한다. main 직접 변경, merge, deploy는 금지다. PR 준비 상태까지만 진행한다.

## tracked source 허용 파일 (exact)

- `tests/specs/screenshots.spec.js`

## runtime 쓰기 허용 경로 (추적 금지)

- `tests/.tmp/**`
- `tests/test-results/**`
- `tests/playwright-report/**`
- `tests/screenshots/**` (step 0의 `tests/.gitignore`에 이미 포함)

## 수정 금지

- 사이트 파일 전부: `index.html`, `css/*`, `js/*`
- 기존 spec, fixtures, scripts, `tests/.gitignore`
- 실패해도 사이트를 고치지 않는다. 원인 step 번호와 실패 출력을 보고하고 중단한다. 하네스가 해당 step을 다시 연다.

## 작업

1. `tests/specs/screenshots.spec.js`를 작성한다. 6개 project에서 실행한다.
   - reducedMotion reduce 상태로 전체 페이지를 `tests/screenshots/{project}-page.png`에 저장한다.
   - desktop project에서는 다음도 저장한다.
     - 대표 프로젝트 3개의 모달: `{project}-modal-{idx}.png`
     - lightbox: `{project}-lightbox.png`
     - print 미디어: `{project}-print.png`
   - 각 모달에 `.modal-visual svg text`가 있으면 font-family에 Space Grotesk가 포함되는지 assert한다.
2. 다음 명령을 순서대로 실행한다.
   - `npm --prefix tests run verify-scope:selftest`
   - `npm --prefix tests test`
   - `npm --prefix tests run verify-scope -- --final`
3. 결과를 로그로만 요약한다.
   - spec별 통과 수(project 6개)
   - axe 위반 0건, 콘솔 에러 0건
   - verify-scope OK, featured 3줄
   - 스크린샷 경로

## 완료 기준 (AC)

- `npm --prefix tests run verify-scope:selftest && npm --prefix tests test && npm --prefix tests run verify-scope -- --final`이 모두 exit 0이다.
