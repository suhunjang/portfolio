# Step 12 — claude-design-intake

- 목적: Claude Design bundle을 읽기 전용으로 exact hash 검증하고, 허용·제외 패턴과 수치 tokens를 고정 fixture로 남긴다. 시각 구현 전 단계. 이 step부터 종료 gate는 CLI다(첫 CLI gate).
- 예상 15분 / 선행 0~11 / 공통 절차 설계 §15 / 종료 gate: CLI
- read-first: 설계 §2, §9, §16(전체), §11.6; 외부 summary 파일(읽기 전용)
- tracked 허용(exact): `tests/scripts/design-intake-check.py`(신규), `tests/fixtures/claude-design-intake.json`(신규), `tests/specs/design-intake.spec.js`(신규)
- runtime: R0
- 금지: §15.7, 외부 evidence 디렉터리·파일 쓰기·이동·삭제, bundle 내용의 복사·반입, 사이트 파일

## 작업

1. 시작 snapshot: `python3 -I tests/scripts/start-snapshot.py step12`
2. `tests/fixtures/claude-design-intake.json`: 설계 §16.1 블록과 같은 JSON(파싱 결과 deep-equal, 끝 개행 1개).
3. `tests/scripts/design-intake-check.py`: 설계 §16.1 계약 그대로(표준 라이브러리, 읽기만, 오류 메시지 형식 고정).
4. `design-intake.spec.js`(node 전용, desktop-dark만, 외부 경로는 읽지 않음): fixture가 설계 §16.1 블록(설계 문서에서 그 fenced block을 읽어 파싱, 문서는 읽기만)과 deep-equal; `files` 9개·64hex 소문자; `adopted`·`excluded` 정확한 목록; tokens 값; 합성 검사 — `tests/.tmp/design-intake-<pid>/`에 가짜 bundle 9개·summary와 그 fixture 사본을 만들고 `python3 -I tests/scripts/design-intake-check.py`를 그 사본 경로로 실행할 수 있도록 스크립트는 선택 인자 `--fixture <path>`를 받는다(기본 `tests/fixtures/claude-design-intake.json`): 정상 OK, 파일 1개 바이트 변경 → `hash mismatch:`, 파일 추가 → `files mismatch`, 파일을 symlink로 → `unsafe:`, summary 줄 변경 → `summary mismatch:`, 모든 경우 사본 bytes 불변; 끝나면 디렉터리 삭제.

## AC (한 셸에서 순서대로, 모두 exit 0)

- `sh tests/scripts/with-env.sh npm --prefix tests test -- design-intake.spec.js && python3 -I tests/scripts/design-intake-check.py && sh tests/scripts/with-env.sh npm --prefix tests test && sh tests/scripts/with-env.sh node tests/scripts/scope-snapshot.mjs --check tests/.tmp/start-snapshot-step12.json --allow tests/scripts/design-intake-check.py,tests/fixtures/claude-design-intake.json,tests/specs/design-intake.spec.js --require-absent tests/scripts/design-intake-check.py,tests/fixtures/claude-design-intake.json,tests/specs/design-intake.spec.js` (두 번째 명령 stdout `design-intake: OK`)
