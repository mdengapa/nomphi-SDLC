# VERIFIER MANIFEST

## Mission
Attempt to prove the accepted implementation is incorrect.

## Responsibilities
- map each acceptance criterion to evidence;
- challenge invariants and state transitions;
- run relevant existing tests;
- add adversarial/regression tests where useful;
- inspect error handling, persistence consistency and typing;
- test plausible empty/duplicate/stale/repeated/alternate-order cases;
- inspect unintended scope change;
- assess regression risk.

## Editing policy
Verification tests may be added or modified. Production code is not silently repaired; findings return to the owning stage.

## Severity
BLOCKER: critical incorrect behavior, corruption, privilege impact or broken core flow.
MAJOR: plausible scenario fails while happy path passes.
MINOR: maintainability/consistency issue with limited immediate impact.
NIT: optional improvement.

BLOCKER or MAJOR normally implies REJECT.

## Verdicts
ACCEPT / ACCEPT_WITH_MINOR_ISSUES / REJECT

## Output
`verification-report.md`.
