---
name: cross-review
description: codex가 Claude의 작업을 교차 리뷰한다(읽기 전용). 코드 diff·설계 문서·계획을 다른 모델의 눈으로 검증해 맹점을 잡는다. "교차 리뷰", "교차검증", "codex 리뷰", "codex한테 리뷰시켜", "codex로 검증", "다른 모델로 검토", "cross review", "cross-check with codex", "have codex review this", "/cross-review" 요청에 트리거.
---

# Cross Review (중앙 하네스 wrapper)

본문·사용법·종료 코드는 이 프로젝트가 고정한 중앙 release에 있다. 먼저 아래를 실행해 읽고 따른다.

```bash
harness --project-root . docs cross-review
```

실행은 stable launcher로만 한다(이 프로젝트에는 하네스 코드가 없다).

```bash
harness --project-root . cross-review                     # 현재 diff
harness --project-root . cross-review spec <경로>
harness --project-root . cross-review plan <task> --issue <ISSUE> --repo-root <TARGET> --evidence-dir <E>
```

<!-- harness:wrapper skill cross-review -->
