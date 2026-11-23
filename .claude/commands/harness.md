이 프로젝트의 하네스(Discord↔Claude 하네스 모드) 운영 문서는 프로젝트가 고정한 중앙 release에 있다.

1. 먼저 아래를 실행해 지금 이 프로젝트가 쓰는 release의 `/harness` 본문을 읽고 그대로 따른다.

   ```bash
   harness --project-root . docs harness
   ```

2. 모든 운영 명령은 `harness --project-root . <command>`(check·plan-session·review-plan·approval·runner)로만
   부른다. 이 프로젝트에는 하네스 코드(`scripts/`)가 없다 — 로컬 경로로 부르지 마라.

<!-- harness:wrapper command harness -->
