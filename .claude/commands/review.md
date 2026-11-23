이 프로젝트의 변경 사항을 리뷰하라.

기준: correctness 버그·회귀·경계조건·보안·에러 처리 누락·테스트가 실제로 동작을
검증하는가·CLAUDE.md CRITICAL 규칙 위반. 스타일 취향은 nit로만.

하네스 게이트의 정식 리뷰는 codex `gpt-6-astra`(read-only)가 한다
(`execute.py:_run_review`, `review_plan.py`). 이 커맨드는 그 보조다.

## 이 프로젝트에서 추가로 볼 것

- 테스트: `./.venv/bin/python -m pytest scripts -q`
- 게이트가 약해지지 않았는가: descriptor 직접 진입 거부, 승인 결속(plan commit·
  content hash·clean Astra review·별도 승인 메시지), sandbox 경계, tested = reviewed = HEAD.
- 외부 바이너리(claude·codex·sandbox-exec) 코드에 실제 spawn 테스트가 있는가.
- Python과 shell 양쪽에 같은 계약을 구현한 곳이 없는가.

## 교차 리뷰

`./.venv/bin/python scripts/cross_review.py` — codex gpt-6-astra read-only, 결과는 stdout.
