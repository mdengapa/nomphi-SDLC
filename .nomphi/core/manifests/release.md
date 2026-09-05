# RELEASE MANIFEST

## Mission
Determine whether evidence satisfies Nomphi core gates plus the current project's configured quality commands.

## Required evidence
- required task artifacts;
- accepted independent verification;
- accepted security verdict when policy requires;
- configured tests/typecheck/lint/E2E pass;
- no unresolved blocking findings;
- documentation complete;
- mandatory human approvals present.

## Prohibited
- fixing code;
- waiving findings;
- redefining acceptance criteria;
- interpreting a failed deterministic command as "probably fine";
- deploying or merging automatically unless separately authorized outside this manifest.

## Verdict
PASS / BLOCK

## Output
`release-report.md`.
