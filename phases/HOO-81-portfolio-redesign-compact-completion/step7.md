# Compact Step 7 — print (r30)

- 목적: 원 §7의 인쇄 동작을 구현한다. 범위는 두 상태(기본, lightbox 열림), clamp 해제, PDF 조건이다.
- 예상 15분, hard timeout 30분. 선행: step 6. 공통 선행조건: §C0.
- 허용 파일(exact):
  - `css/style.css`: `@media print`만 수정한다. 색 선언은 넣지 않는다.
  - `tests/specs/final-contract.spec.js`: 보강
- runtime: §C4
- 금지: `index.html`, `js/*`, 색 규칙 순서 변경, PDF 파서 의존성 추가

## 작업
1. `final-contract.spec.js`에 아래 assertion을 보강하고 RED를 확인한다. 대상은 desktop-dark와 desktop-light다.
   - `pdfPageCount(buf) = (buf.toString('latin1').match(/\/Type\s*\/Page\b/g) || []).length`
     - `/Type` 다음에 오는 `/Page`만 센다. `/Pages`는 제외한다.
     - 함수 자체 검증 fixture는 정확히 4개다.

| 입력 | 기대 |
|---|---|
| `'/Type /Page'` | 1 |
| `'/Type/Page'` | 1 |
| `'/Type /Pages'` | 0 |
| `'/Page'` 단독 | 0 |

   - A(기본 상태)
     - 본문과 featured가 visible이고 opacity가 1이다.
     - reveal 요소가 비어 있지 않다.
     - interaction 요소와 modal은 숨겨지고, lightbox는 없거나 `none`이다.
     - clamp가 `none`이거나 `unset`이다.
     - PDF가 10240 bytes보다 크고, page count가 1 이상이다.
   - B(lightbox가 열린 상태)
     - print에서 lightbox와 modal이 `none`이다.
     - PDF 조건은 A와 같다.
2. 구현한다.

## AC
- `OWN_SPEC tests/specs/final-contract.spec.js`
- `T specs/final-contract.spec.js`
- `T <GS>`
