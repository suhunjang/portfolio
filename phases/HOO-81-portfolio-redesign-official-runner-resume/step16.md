# Step 16: publish-open-pr

## Always-on invariants
Do not modify historical phase records/evidence. Preserve all copy, numbers, font assets/weights, information architecture, 3 featured project identities, all 13 PROJECTS and order. No new copy, section, image, icon, project or placeholder content. css/themes.css is read-only; if it or index.html is required outside the listed lane, stop and replan. Implementation workers must not commit, push, merge, edit the canonical phase index, or write outside their exact lane files. Run only focused tests in lanes; canonical FULL/UI/a11y run at steps 12 and 14.

## Exact work order
Coordinator-only after step15 CLEAN and the approved plan. Push the exact reviewed feature HEAD with no force, then create or read an OPEN PR against main. Do not merge or deploy. The command is idempotent: it reuses an existing PR for the branch.

## Exact write boundary
No repository file writes. Coordinator external actions/evidence only.

## Acceptance
Run every argv in this step’s immutable `index.json.acceptanceCommands` in order. Any nonzero exit blocks the next step.
