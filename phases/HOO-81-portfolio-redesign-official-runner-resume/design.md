# HOO-81 Official Runner Continuation v63

## Goal and completion line
Resume only the unfinished HOO-81 redesign work with official Harness 2.0.1, preserve historical evidence, remediate 61 verified color-contrast and 78 verified nested-interactive occurrences, then finish at `blocker 0 + all acceptance criteria + exact-commit Astra CLEAN + OPEN PR with SHA identity`.

## Immutable scope
- BASE_HEAD `5a34759acf16e7beb96c415101c152d6e786c4b3`; historical original step 0~39 completed/40 blocked and resume step 0~16 completed/17 blocked are read-only.
- Preserve copy, numbers, font assets/weights, IA hero→Career→Projects→Strengths→About→Contact, three featured project identities (existing records 1,5,7), all 13 PROJECTS and order.
- No new copy, section, image, icon, project, placeholder content, generic framework, custom coordinator, unrelated refactor or palette redesign.
- `css/themes.css` is read-only. Only minimal values/roles proved necessary for the 61 contrast occurrences may change in `css/style.css`.

## Execution and ownership
Steps 0~14 run through official runner. Every implementation step is an exact-file wave, including single-lane waves, so phase-wide allowedPaths never grants a worker unrelated writes. Only step3 and step13 contain truly concurrent lanes. Official fresh worktrees, deterministic fan-in, maxAttempts=2 and recovery are required; partial fan-in is forbidden. Steps 15~17 are coordinator-only gates after the implementation runner stops. Workers never commit, push, merge, edit canonical phase metadata, or perform publication.

## Testing layers
Lane workers run focused tests only. Canonical FULL and accessibility collection run at step12, and final FULL/UI/accessibility/diff checks run at step14. The final-gate conditions apply only at step14; earlier steps enforce the always-on invariants and their own focused AC.

## Recovery and stop conditions
A lane failure retries only that lane from a fresh base. Exact-anchor overlap, new axe rule, missing occurrence, need for index.html/css/themes.css during remediation, approval/snapshot mismatch, dirty protected path, or any SHA mismatch blocks and requires replanning/review. Scope or assumption changes require a new Astra plan review and exact approval.

## Review and publication
After step14, Ryan records the tested HEAD. Step15 obtains GPT-6 Astra CLEAN for that exact commit. Step16 pushes that same HEAD and creates/reuses an OPEN PR without merge. Step17 requires tested=reviewed=local=pushed=PR-head SHA and clean repository. Any HEAD change sends the work back through final tests and exact-commit review.
