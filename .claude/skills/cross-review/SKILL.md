---
name: cross-review
description: codex가 Claude의 작업을 교차 리뷰한다(읽기 전용). 코드 diff·설계 문서·계획을 다른 모델의 눈으로 검증해 맹점을 잡는다. "교차 리뷰", "교차검증", "codex 리뷰", "codex한테 리뷰시켜", "codex로 검증", "다른 모델로 검토", "cross review", "cross-check with codex", "have codex review this", "/cross-review" 요청에 트리거.
---

# Cross Review

Claude가 만든 것을 **codex**가 리뷰한다. 두 모델이 맹점을 공유하지 않으므로, 같은 모델이 자기 작업을 재검토할 때보다 잡히는 게 많다.

`execute.py`의 phase-end 리뷰가 하네스 안에서만 도는 것과 달리, 이건 일반 세션에서 애드혹으로 부른다.

## 사용법

```
./.venv/bin/python scripts/cross_review.py                                    # 현재 diff (기본)
./.venv/bin/python scripts/cross_review.py diff                               # 위와 동일 (ref 기본값 HEAD)
./.venv/bin/python scripts/cross_review.py diff HEAD~3                        # 범위 지정
./.venv/bin/python scripts/cross_review.py spec docs/superpowers/specs/foo.md
./.venv/bin/python scripts/cross_review.py plan 0-mvp --issue <ISSUE> --repo-root <TARGET> --evidence-dir <E>
```

> 항상 repo-local `./.venv/bin/python`(Python 3.14.9)으로 부른다. `/usr/bin/python3`(3.9)는 쓰지 않는다.

인자 없이 부르면 `git diff HEAD`를 리뷰한다. 대부분의 경우 이걸 쓴다.

`spec` 경로는 리포 루트 기준이며, 리포 밖을 가리키면 거부한다.

## 대상별 차이

| 대상 | 리뷰 기준 | 성격 |
|---|---|---|
| `diff` | 버그·회귀·경계조건·에러 처리 누락·기존 코드와의 일관성 (스타일 지적 금지) | 읽기 전용, stdout |
| `spec` | 내부 모순·누락 케이스·검증 불가능한 성공 기준·과도한 범위 (문장 다듬기 금지) | 읽기 전용, stdout |
| `plan` | scope·자기완결성·AC 실행가능성 | 읽기 전용, evidence record (아래 주의) |

> ⚠️ `plan`은 `scripts/review_plan.py`(codex gpt-6-astra strict 계획 리뷰)에 위임된다. 계획을 **수정하지 않는다** — findings면 종료코드 4, 같은 planning session으로 계획을 재생성한 뒤 새 hash로 다시 리뷰해야 한다. `--issue`, `--repo-root`(target 독립 clone), `--evidence-dir`(target·하네스 repo 밖)가 필수이고, 종료 코드는 `review_plan.py`의 것을 그대로 전달한다(0 clean / 4 findings / 2 실패 / 1 preflight).

## 결과 읽는 법

codex는 지적마다 severity를 붙인다:

- **critical** — 고치지 않으면 안 되는 것. 동작이 틀렸거나 데이터가 깨진다.
- **major** — 고쳐야 하는 것. 엣지 케이스에서 실패한다.
- **minor** — 고려해볼 것.

지적할 것이 없으면 정확히 `CLEAN` 한 단어만 나온다. 그 외의 출력은 findings로 읽는다.

**자동으로 고치지 않는다.** 리뷰는 지적만 하고, 반영할지는 사람이 정한다. codex의 지적이 항상 옳은 것도 아니다 — 납득이 안 되면 근거를 따져보고, 틀렸다고 판단하면 무시해도 된다.

## 종료 코드

| 코드 | 의미 |
|---|---|
| `0` | 리뷰 성공, 또는 리뷰할 변경이 없음 |
| `2` | codex 리뷰 실패 (CLI 없음 / 타임아웃 900초 / codex가 0이 아닌 코드로 종료 / 출력 없음) |
| `1` | 인자가 잘못됨, 또는 `spec` 경로가 없거나 리포 밖 |

diff가 비어 있으면 codex를 아예 부르지 않고 "리뷰할 변경이 없습니다"를 출력한 뒤 `0`으로 끝난다.

## 언제 부르나

- 커밋 전, 변경이 어느 정도 쌓였을 때
- 설계 문서를 쓰고 난 직후 (구현 전에 모순을 잡는 게 훨씬 싸다)
- Stop hook이 미리뷰 변경을 알릴 때

## 전제

- `codex` CLI가 설치돼 있어야 한다 (0.144.4 기준). 없으면 exit 2와 함께 설치 안내가 나온다.
- 리뷰어는 **항상** `codex exec --sandbox read-only --model gpt-6-astra`로 뜬다(하네스 리뷰 게이트와 같은 argv). 리뷰는 읽기 작업이므로 쓰기 권한을 주지 않는다.
- 대상 텍스트를 stdin으로 통째로 넘기므로 codex가 파일을 열 필요가 없다. 그래서 read-only로 충분하다.
- 결과는 stdout으로만 나온다. 리뷰 결과를 파일로 남기지 않는다 — 이력은 대화에만 남는다.
- 리뷰가 **성공하면** `.claude/.cross-review-state`의 시각이 갱신되고 Stop hook 알림이 조용해진다. **실패하면 갱신하지 않는다** — 미리뷰 변경이 리뷰된 것으로 잘못 표시되면 안 되기 때문이다.
