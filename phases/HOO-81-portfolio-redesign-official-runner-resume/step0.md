# Step 0: inherit-preflight

## Always-on invariants
Do not modify historical phase records/evidence. Preserve all copy, numbers, font assets/weights, information architecture, 3 featured project identities, all 13 PROJECTS and order. No new copy, section, image, icon, project or placeholder content. css/themes.css is read-only; if it or index.html is required outside the listed lane, stop and replan. Implementation workers must not commit, push, merge, edit the canonical phase index, or write outside their exact lane files. Run only focused tests in lanes; canonical FULL/UI/a11y run at steps 12 and 14.

## Exact work order
Read in order and hash-check: `CLAUDE.md` (b63e8c71bea72313c7ae312c6c5582e6fd1ccc98b122d2f4ade46f09e65cb8aa), original design (eb229f57acb23bd9a24d990d3c510ec3fb824fc24051909bb02665408cd54e49), resume design (351a18f1b6ca30f46606ab25ff310329eeecd8cd4db138d7848a86d414b3ffe1), execution.json, historical indexes and inherited artifacts. `continuation-preflight.mjs` must call official `harness check`, find current `approval-current.json`, call `harness approval verify` without consuming a second first-run, assert BASE_HEAD ancestry, official lock source/manifest, all listed hashes/sizes (pairs 47392 bytes, collected 28809 bytes), approved snapshot/plan binding, and exact execution.json hash from the approved manifest. Any mismatch exits nonzero before step1. It may create only itself and its spec; product behavior must not change.

## Exact write boundary
preflight-contract: tests/scripts/continuation-preflight.mjs, tests/specs/continuation-preflight.spec.js

## Acceptance
Run every argv in this step’s immutable `index.json.acceptanceCommands` in order. Any nonzero exit blocks the next step.
