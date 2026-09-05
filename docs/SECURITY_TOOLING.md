# Security tooling

The Security Agent reasons about attack paths, but deterministic tools should provide evidence whenever available.

Typical categories:
- dependency audit;
- secret scanning;
- static application security testing;
- secure lint rules;
- API authorization negative tests;
- container/image scan when applicable;
- IaC scan when applicable;
- mobile permission/storage review when applicable;
- SBOM generation for release-critical software where appropriate.

Security testing must remain inside the authorized repository/test environment. External or destructive exploitation is not part of the default workflow.

Projects add domain-specific abuse cases in `.nomphi/project/security-boundaries.md` and project skills.
