# Step 10 — final-verification

- 예상 시간: 12분
- 실행 횟수: self-test 1회, 테스트 1회(웹서버 1회), verify-scope --final 1회
- 선행 step: 0~9 completed

## 공통: 시작 전 필수 확인 (read-first)

1. 저장소 지침을 읽는다: `CLAUDE.md`(중앙 Harness 계약), `README.md`. 하위 디렉터리에 `CLAUDE.md`나 `AGENTS.md`가 있으면 함께 읽는다.
2. 설계 문서를 읽는다.
   - `docs/superpowers/specs/2026-07-29-quiet-executive-redesign-design.md`
   - `docs/superpowers/specs/2026-11-23-portfolio-layout-redesign-design.md` 전체
3. index.json에서 step 0~9가 completed인지 확인한다. 아니면 중단한다.
4. spec 9개가 있는지, `axe-baseline.json`이 `[]`인지 확인한다.
5. 다음 경로는 read-only다.
   - `CLAUDE.md`, `docs/**`, `phases/**`
   - `.harness/**`, `.claude/**`, `.codex/**`
   - `pytest.ini`, `.python-version`, `.gitattributes`, 루트 `.gitignore`
6. git과 Harness 운영 명령은 하네스만 실행한다. main 직접 변경, merge, deploy는 금지다. PR 준비까지만 한다.
7. 공통 실행 계약: npm·node 명령은 모두 `sh tests/scripts/with-env.sh <명령>`으로 실행한다.

## tracked source 허용 파일 (exact)

- `tests/specs/screenshots.spec.js`

## runtime 쓰기 허용 경로 (추적 금지)

- `tests/.tmp/**`
- `tests/.npm-cache/**`
- `tests/test-results/**`
- `tests/playwright-report/**`
- `tests/screenshots/**`

## 수정 금지

- 사이트 파일 전부
- 기존 spec, fixtures, scripts, `tests/.gitignore`
- 검증이 실패해도 사이트를 수정하지 않는다. 원인이 된 step을 보고하고 중단한다.

## 작업

1. `tests/specs/screenshots.spec.js`
   - 6개 project 모두 page 스크린샷을 찍는다.
   - desktop에서는 대표 모달 3개, lightbox, print 화면도 찍는다.
   - 모달 SVG text의 font-family에 Space Grotesk가 들어 있는지 assert한다.
2. 다음 명령을 실행한다.
   - `sh tests/scripts/with-env.sh npm --prefix tests run verify-scope:selftest`
   - `sh tests/scripts/with-env.sh npm --prefix tests test`
   - `sh tests/scripts/with-env.sh npm --prefix tests run verify-scope -- --final`
3. 로그에 결과를 요약한다.
   - spec별 통과 수
   - axe 위반 0건, 콘솔 에러 0건
   - verify-scope OK
   - 스크린샷 경로

## 완료 기준 (AC)

- `sh tests/scripts/with-env.sh npm --prefix tests run verify-scope:selftest && sh tests/scripts/with-env.sh npm --prefix tests test && sh tests/scripts/with-env.sh npm --prefix tests run verify-scope -- --final` → 모두 exit 0
