# Compact Step 6 — exact-range-review

- 목적: exact implementation range `<step 0 기록 HEAD>..<tested HEAD>`를 GPT-6 Astra로 리뷰한다.
- 예상 15분, hard timeout 30분. 선행: step 5.
- 허용 파일(exact): step 4와 같다. blocker를 수정할 때만 쓴다.

## 작업
1. 리뷰 기록에 base·head·range와 binary diff SHA-256을 남긴다.
2. 리뷰에 blocker나 major가 있으면:
   - 실제 blocker만 허용 범위 안에서 수정한다.
   - step 4 AC와 step 5 AC를 다시 실행한다.
   - 새 HEAD로 다시 리뷰한다.
3. 비차단 항목은 원래 등급을 보존한 채 별도 이슈로 기록한다.

## AC
- Astra 결과가 CLEAN이다.
- tested SHA = reviewed SHA = HEAD.
- `git status --porcelain`이 비어 있다.
