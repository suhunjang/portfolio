# Step 12 — claude-design-intake

- 목적: Claude Design bundle을 읽기 전용으로 exact hash 검증하고 허용·제외 패턴과 tokens를 고정 fixture로 남긴다. 첫 CLI gate.
- 예상 15분 / 선행 0~11 / 공통 절차 설계 §15 / 종료 gate: CLI
- read-first: 설계 §2, §9, §16, §11.6; 외부 summary(읽기 전용)
- tracked 허용(exact): `tests/scripts/design-intake-check.py`(신규), `tests/fixtures/claude-design-intake.json`(신규), `tests/specs/design-intake.spec.js`(신규)
- runtime: R0(`tests/.tmp/design-intake-<pid>/`)
- 금지: §15.7, 외부 evidence 쓰기·이동·삭제, bundle 내용 복사·반입, 사이트 파일

## 작업

1. 시작 snapshot: `python3 -I tests/scripts/start-snapshot.py step12`
2. fixture: 설계 §16.1 fenced block과 파싱 결과 deep-equal(끝 개행 1개).
3. `design-intake-check.py`: 설계 §16.1 계약(`--fixture` 선택 인자, 읽기만, 메시지 형식 고정).
4. `design-intake.spec.js`(node 전용, desktop-dark만, 외부 경로는 읽지 않음): fixture = 설계 블록(설계 문서는 읽기만); `files` 9개 소문자 64hex; `adopted`·`excluded`·tokens 값; 합성 — `tests/.tmp/design-intake-<pid>/`에 가짜 bundle 9개·summary·그에 맞춘 fixture 사본 → `python3 -I tests/scripts/design-intake-check.py --fixture <사본>`: 정상 `design-intake: OK`, 한 파일 바이트 변경 `design-intake: hash mismatch:{name}`, 파일 추가 `design-intake: files mismatch`, 파일을 symlink로 `design-intake: unsafe:{path}`, summary 줄 변경 `design-intake: summary mismatch:{name}`, 사본 bytes 불변; 삭제.

## AC (한 셸에서 순서대로, 모두 exit 0)

- `sh tests/scripts/with-env.sh npm --prefix tests test -- design-intake.spec.js && python3 -I tests/scripts/design-intake-check.py && sh tests/scripts/with-env.sh npm --prefix tests test && sh tests/scripts/with-env.sh node tests/scripts/scope-snapshot.mjs --check tests/.tmp/start-snapshot-step12.json --allow tests/scripts/design-intake-check.py,tests/fixtures/claude-design-intake.json,tests/specs/design-intake.spec.js --require-absent tests/scripts/design-intake-check.py,tests/fixtures/claude-design-intake.json,tests/specs/design-intake.spec.js` (두 번째 명령 stdout `design-intake: OK`)
