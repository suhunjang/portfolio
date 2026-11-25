# Step 14: canonical-final-verification

## Always-on invariants
Do not modify historical phase records/evidence. Preserve all copy, numbers, font assets/weights, information architecture, 3 featured project identities, all 13 PROJECTS and order. No new copy, section, image, icon, project or placeholder content. css/themes.css is read-only; if it or index.html is required outside the listed lane, stop and replan. Implementation workers must not commit, push, merge, edit the canonical phase index, or write outside their exact lane files. Run only focused tests in lanes; canonical FULL/UI/a11y run at steps 12 and 14.

## Exact work order
Final gate only (not an invariant for earlier steps): first collect axe and require zero violations before replacing baseline with `[]` and remediation plan with `{"groups":[]}`. Then run FULL, screenshots/UI, state colors, mobile-dark menu open/close, modal open/close/focus return for six explicit project indices 1,5,7,0,2,12, and final diff contract. `verify-final-contract.mjs` checks BASE→HEAD/index/worktree are limited to allowedPaths plus this phase, HEAD→index and index→worktree are clean, js/data.js contains only three `featured: true` additions, css/themes.css is byte-identical, and historical phases/evidence are unchanged.

## Exact write boundary
final-gate-artifacts: tests/fixtures/axe-baseline.json, tests/fixtures/axe-remediation-plan.json, tests/specs/screenshots.spec.js, tests/scripts/verify-final-contract.mjs, tests/specs/final-contract.spec.js

## Acceptance
Run every argv in this step’s immutable `index.json.acceptanceCommands` in order. Any nonzero exit blocks the next step.
