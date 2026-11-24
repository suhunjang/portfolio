# Step 12 — claude-design-intake

- 목적: bundle exact hash 읽기 전용 검증과 고정 fixture. 첫 GATE.
- 15분 / 선행 0~11 / 공통 §9 / gate GATE
- 허용(exact): `tests/scripts/design-intake-check.py`, `tests/fixtures/claude-design-intake.json`, `tests/specs/design-intake.spec.js`(모두 신규)
- runtime: R0(`tests/.tmp/design-intake-<pid>/`)
- 추가 금지: 외부 evidence 쓰기·이동·삭제·복사, 사이트 파일

## 작업
1. `SNAP 12`
2. fixture = 설계 `### 11.1` 첫 fenced block과 deep-equal(끝 개행 1개). check script = 설계 §11.1 계약.
3. spec(node, desktop-dark, 외부 경로 읽지 않음): fixture = 설계 블록; files 9개 소문자 64hex; adopted·excluded·tokens; 합성 bundle 9개·summary·fixture 사본 → `--fixture <사본>`: 정상 `design-intake: OK`, 바이트 변경 `design-intake: hash mismatch:{name}`, 파일 추가 `design-intake: files mismatch`, symlink `design-intake: unsafe:{path}`, summary 줄 변경 `design-intake: summary mismatch:{name}`; 사본 불변; 삭제.

## AC
- `T design-intake.spec.js && DI && FULL && GATE 12 tests/scripts/design-intake-check.py,tests/fixtures/claude-design-intake.json,tests/specs/design-intake.spec.js tests/scripts/design-intake-check.py,tests/fixtures/claude-design-intake.json,tests/specs/design-intake.spec.js`
