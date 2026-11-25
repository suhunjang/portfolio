# Compact Step 7 — publish-gated (coordinator)

- 목적: feature branch push와 OPEN PR. **대표가 push/PR을 별도로 승인한 경우에만** 실행한다. 구현 승인은 이 승인을 대신하지 않는다.
- 예상 10분, hard timeout 30분. 선행: step 6.
- 허용 파일: 없음

## 작업
1. 별도 승인이 없으면 이 step은 보류 상태로 둔다.
2. 승인이 있으면 push 전에 tested = reviewed = HEAD = local branch tip이고 worktree가 clean인지 확인한다.
3. `feat/HOO-81/portfolio-redesign`에 no-force로 push한다.
4. PR을 확인하거나 만든다. 조건은 OPEN, base `main`, head가 정확히 이 branch다. CLOSED·MERGED PR은 재사용하지 않는다. auth·network 오류면 block한다.
5. local·remote·PR head SHA가 모두 같은지 확인한다.

## AC
- local = remote = PR head = tested = reviewed SHA
- merge·deploy를 하지 않았다.
