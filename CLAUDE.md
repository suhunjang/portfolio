# 프로젝트: {프로젝트명}

개인 포트폴리오 정적 사이트(index.html·css·js, GitHub Pages). 테스트는 tests/ 아래 Playwright. 아래 개발 방식 블록을 따른다.

<!-- dev-lite:begin -->
## 개발 방식 (DEV-LITE-001, 2026-11-26 대표 승인)

정본: `~/.hermes/company/operations/dev-workflow-lite-policy.md`. 외부 Harness runner는 쓰지 않는다.

- feature branch에서만 작업한다. main 직접 변경·push·merge 금지(대표 승인 후 PM이 수행).
- **TDD 필수:** 구현 전에 `superpowers:test-driven-development` 스킬을 불러온다.
  1. `tests/specs/`에 실패하는 테스트를 쓰고 RED를 확인한 뒤 **테스트만 담은 commit**을 만든다.
  2. 최소 구현으로 GREEN을 만들고 구현 commit을 따로 만든다.
  - 편집 hook(`scripts/hooks/tdd-guard.py`)은 테스트 변경 없이 `index.html`·`css/**`·`js/**`를 고치면 막는다.
  - 동작 불변 리팩터링은 계획 승인 때 `tdd-exception.json`에 등록된 파일만 예외다.
- 테스트: `sh tests/scripts/with-env.sh npm --prefix tests test` (기존 4173 서버를 재사용하지 않도록 먼저 비어 있는지 확인).
- 완료 확인은 PM이 테스트 commit에서 RED, 최종 commit에서 같은 테스트 GREEN을 직접 재현하고(Harness 2.1 설치 후에는 스텝 판정 명령), 변경분은 GPT-6 Astra가 리뷰한다.
- 위험 명령(`rm -rf`, `git push --force`, `git reset --hard`, `DROP TABLE`)은 `scripts/hooks/block-dangerous.sh`가 막는다.
<!-- dev-lite:end -->
