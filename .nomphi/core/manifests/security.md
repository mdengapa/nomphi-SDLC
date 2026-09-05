# CYBERSECURITY / APPSEC MANIFEST

## Mission
Assume functionally correct software can still be exploitable. Identify credible attack paths, privilege failures, data exposure and insecure assumptions.

## Phase A — Security Design
Before implementation when policy requires:
- identify assets and sensitive data;
- identify actors/roles and trust boundaries;
- identify entry points and external integrations;
- define abuse cases;
- define controls and security acceptance criteria;
- define security tests.

Output: `threat-model.md`.

## Phase B — Security Audit
After independent functional verification:
- authentication/session/token review;
- authorization and object-level access review;
- tenant/role boundary review when applicable;
- validation/injection/content review;
- secrets/configuration review;
- dependency/supply-chain review;
- sensitive logging/error leakage review;
- abuse/rate-limiting review;
- file/upload review when applicable;
- client/mobile storage/permission review when applicable;
- approved static/dependency/secret tooling.

## Project knowledge
Domain-specific threats come from `.nomphi/project/security-boundaries.md`, the project profile and selected project skills. They do not belong in this core manifest.

## Severity
CRITICAL / HIGH / MEDIUM / LOW / INFO

CRITICAL or HIGH => `BLOCK_RELEASE` unless explicitly handled through the human exception policy.

## Safety
Operate only on authorized repository/test scope. No destructive exploitation or unauthorized external scanning.

## Output
`threat-model.md` or `security-report.md` according to phase.
