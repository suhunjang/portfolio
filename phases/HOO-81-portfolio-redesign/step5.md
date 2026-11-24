# Step 5 — scope-snapshot-symlink

- 목적: 비runtime symlink와 snapshot 파일 자체 symlink 거부를 시작 snapshot 생성·재사용(S), 현재 상태 수집(`takeCurrent`), 종료 gate(C), loader에서 실행 검증한다. 코드 추가 없이 테스트만.
- 예상 18분 / 선행 0~4 / 공통 절차 설계 §15 / 종료 gate: S reused + inline C
- read-first: 설계 §11.7(경로 유형 계약, 실행 전제, 실행 순서, S, C, 설계 블록 추출 규칙, 테스트 격리), §12(합성 저장소 예외); `tests/helpers/synthetic-repo.js`
- tracked 허용(exact): `tests/specs/scope-snapshot-symlink.spec.js`(신규)
- runtime: R0(합성 저장소와 `<pid>-outside/`, 실제 저장소 `tests/.tmp/start-snapshot-parity-{숫자}.json` 위치의 symlink와 사본)
- 금지: §15.7, `scope-snapshot.mjs`·`start-snapshot.py`·helper 수정, 실제 저장소 비runtime 경로에 symlink 생성, 권한 변경

## 작업

1. 시작 snapshot: `python3 -I tests/scripts/start-snapshot.py step5`
2. `scope-snapshot-symlink.spec.js` (node 전용, desktop-dark만, 각 사례는 새 `makeSyntheticRepo()`, finally `cleanup()`, subprocess timeout 10초). 외부 대상 `outside/secret.txt` 내용은 고유 sentinel 문자열. 링크는 모두 실행 전에 만들어 두고 실행 중에는 바꾸지 않는다. 세 실행 경로:
   - JS: `takeCurrent(start, { root: dir, fs: 기록용 fs 래퍼 })` → `unsafe`에 기대 항목, `files` `{}`, 기록에 링크 경로·대상 경로의 read·stat(follow)·readlink·realpath·open 없음
   - S: cwd `dir`에서 `python3 -I <프로젝트>/tests/scripts/start-snapshot.py parity-1` → exit ≠ 0, stderr `unsafe path:` + 기대 항목, `dir/tests/.tmp/start-snapshot-parity-1.json` 생성 없음. 재사용 분기: 미리 둔 정상 형식 snapshot 파일이 있을 때도 exit ≠ 0, 그 bytes 불변
   - C: `dir/tests/.tmp/start-snapshot-parity-1.json`에 키 집합만 맞춘 start(stepId `parity-1`, files `{}`, xy `{}`)를 쓰고, cwd `dir`에서 `python3 -I - parity-1 '<allow>' ''` + `designBlock('inline 범위 검사 C')` 본문 → exit 1, stderr에 기대 `symlink:` 항목, 변경 판정 줄(`tests-changed:`·`outside-tests:`·`status-changed:`) 없음, `…-after.z` 미생성. allow에 링크 경로를 넣어도 같음
   - 모든 경로에서 stdout·stderr·생성 파일에 sentinel 없음
3. 사례
   - (a) allow 밖 ignored symlink: `.gitignore`에 `link-ignored`, `fs.symlinkSync(<outside>/secret.txt, dir/link-ignored)` → `symlink:link-ignored`
   - (b) 이미 수정된 tracked symlink의 target 변경: 초기 commit에 `tracked-link → a.txt` 포함(`add -A`) → 링크를 `b.txt`로 교체(status ` M`) 상태에서 세 경로 모두 `symlink:tracked-link`로 실패 → 다시 `c.txt`로 교체해도 세 경로 모두 실패(각 교체는 실행과 실행 사이에 수행)
   - (c) symlink 디렉터리 `docs-link → <outside>`: `symlink:docs-link`, 내부 미진입(`docs-link/secret.txt` 항목 없음)
   - (d) 대조: 링크 없는 같은 구조에서 JS `unsafe` `[]`, C는 symlink 항목 없음
   - (e) snapshot 파일 자체 symlink(실제 저장소 runtime 경로, 번호 `<A>`·`<k>`·`<m>`은 서로 다른 숫자): S로 정상 `tests/.tmp/start-snapshot-parity-<A>.json`을 만들고 그 bytes를 별도 번호의 사본 `tests/.tmp/start-snapshot-parity-<k>.json`으로 복사한 뒤, `tests/.tmp/start-snapshot-parity-<m>.json`을 사본 경로 `tests/.tmp/start-snapshot-parity-<k>.json`을 target으로 하는 symlink로 만든다 → `python3 -I tests/scripts/start-snapshot.py parity-<m>` exit ≠ 0·stderr `unsafe path: symlink:tests/.tmp/start-snapshot-parity-<m>.json`, loader `loadStartSnapshot('tests/.tmp/start-snapshot-parity-<m>.json')` `unsafe path: symlink:` throw, 사본 sha256 불변. finally에서 링크 `parity-<m>`, 사본 `parity-<k>`, 원본 `parity-<A>`를 모두 삭제(실제 저장소에는 테스트 격리 규칙의 `tests/.tmp/start-snapshot-parity-{숫자}.json` 경로만 쓴다)
   - runtime 디렉터리 `tests/.tmp` 자체 symlink는 step 6이 검증한다

## AC (모두 exit 0)

1. `sh tests/scripts/with-env.sh npm --prefix tests test -- scope-snapshot-symlink.spec.js && sh tests/scripts/with-env.sh npm --prefix tests test && python3 -I tests/scripts/start-snapshot.py step5` (마지막은 `reused`)
2. 범위 gate: `python3 -I - step5 'tests/specs/scope-snapshot-symlink.spec.js' 'tests/specs/scope-snapshot-symlink.spec.js' <<'PY'` + 설계 §11.7 C 코드 블록 본문(그대로) + `PY`
