# Step 10 — final-verification

- 예상 시간: 12분
- 실행 횟수: self-test 1회, 테스트 1회(웹서버 1회), verify-scope --final 1회
- 선행 step: 0~9 completed

## 공통: 시작 전 필수 확인 (read-first)

1. 저장소 지침을 읽는다.
   - `CLAUDE.md`(하네스 계약 포함)
   - `README.md`
   - 하위 디렉터리에 `CLAUDE.md`나 `AGENTS.md`가 있으면 함께 읽는다.
2. 설계 문서를 읽는다.
   - `docs/superpowers/specs/2026-07-29-quiet-executive-redesign-design.md`
   - `docs/superpowers/specs/2026-11-23-portfolio-layout-redesign-design.md` 전체
3. index.json에서 step 0~9가 모두 completed인지 확인한다. 아니면 중단한다.
4. tests/specs에 smoke, content, interaction, first-visit, axe, hero, layout, focus, print 9개 spec이 모두 있는지 확인한다. `axe-baseline.json`이 `[]`인지도 확인한다.
5. 다음 경로는 수정하지 않는다(read-only).
   - `CLAUDE.md`, `docs/**`, `phases/**`, `.harness/**`
   - 하네스 managed 파일: `scripts/**`, `.claude/**`, `.codex/**`, `templates/**`, `harness-manifest.json`, `pytest.ini`, `.python-version`, `.gitattributes`, 루트 `.gitignore`
6. git add·commit·push는 하네스만 한다. main 직접 변경, merge, deploy는 금지다. PR 준비까지만 진행한다.

## tracked source 허용 파일 (exact)

- `tests/specs/screenshots.spec.js`

## runtime 쓰기 허용 경로 (추적 금지)

- `tests/.tmp/**`
- `tests/test-results/**`
- `tests/playwright-report/**`
- `tests/screenshots/**`

## 수정 금지

- 사이트 파일 전부
- 기존 spec, fixtures, scripts, `tests/.gitignore`
- 검증이 실패해도 사이트를 고치지 않는다. 원인이 된 step 번호와 실패 출력을 보고하고 중단한다.

## 작업

1. `tests/specs/screenshots.spec.js`를 작성한다.
   - 6개 project 모두: reducedMotion reduce 상태로 `tests/screenshots/{project}-page.png`를 저장한다.
   - desktop project에서만 추가로 저장한다.
     - 대표 모달 3개: `-modal-{idx}.png`
     - lightbox: `-lightbox.png`
     - print: `-print.png`
   - 모달 SVG에 text 요소가 있으면 font-family에 Space Grotesk가 포함되는지 assert한다.
2. 다음 명령을 차례로 실행한다.
   - `npm --prefix tests run verify-scope:selftest`
   - `npm --prefix tests test`
   - `npm --prefix tests run verify-scope -- --final`
3. 결과를 로그로 요약한다.
   - spec별 통과 수
   - axe 위반 0건, 콘솔 에러 0건
   - verify-scope OK, featured 3줄
   - 스크린샷 경로

## 완료 기준 (AC)

- `npm --prefix tests run verify-scope:selftest && npm --prefix tests test && npm --prefix tests run verify-scope -- --final`가 모두 exit 0
