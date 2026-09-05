# Operating model

## Intake
A requirement enters the system with a human-readable goal and initial risk classification.

## Planning
Planner creates a bounded technical contract with explicit acceptance criteria, non-goals, invariants, test plan and Definition of Done.

## Security design
Security creates a threat model for all tasks required by core/project policy.

## Implementation
Implementer writes code and local tests using the approved spec and project adapter.

## Verification
Verifier independently tests the implementation against the spec and plausible failure modes.

## Security audit
Security reviews the final attack surface and checks the threat model against the implementation.

## Documentation
Documenter updates durable docs only after the implementation has been accepted functionally and by security.

## Release
Deterministic commands and artifact verdicts determine release eligibility.

## Cost model
Frontier models are used where reasoning quality materially changes risk: planning, independent verification and cybersecurity. Local models handle high-volume bounded work such as implementation, documentation and orchestration assistance.

## Context discipline
Agents should not ingest the entire repository by default. Context is selected from project profile, invariants, relevant skills, task specification, touched modules and direct dependencies.

## Core-change rule
If a lesson is true only for one product, it is not a core change.
