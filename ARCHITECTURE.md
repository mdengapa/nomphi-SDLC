# Nomphi Agentic SDLC — Architecture

## 1. Architecture boundary

Nomphi Core is domain-agnostic and project-agnostic.

It owns:
- workflow;
- roles;
- separation of duties;
- handoff protocol;
- risk classes;
- minimum security gates;
- minimum release gates;
- artifact schemas;
- shared skills;
- provider/model bindings.

A Project Adapter owns:
- product/domain context;
- existing system architecture;
- repository conventions;
- project invariants;
- security boundaries unique to the product;
- local quality commands;
- project-specific skills;
- optional stricter gates.

No project name, product rule, API route, visual identity or domain invariant belongs in Core.

## 2. Separation of duties

### Orchestrator
Controls state, routes work, packages context and enforces gates. It should be mostly deterministic. An LLM may classify or summarize, but cannot override workflow constraints or implement product changes.

### Planner
Turns a requirement into an implementation contract. It reads but does not modify production code.

### Security
Runs twice. Before implementation it produces a threat model. After verification it performs an independent AppSec audit.

### Implementer
Writes production code and implementation-level tests. It is not allowed to redefine the specification.

### Verifier
Tries to falsify the implementation. It may add verification tests but does not silently repair production code.

### Documenter
Updates durable documentation to match accepted behavior. It must not continue if its required upstream handoff/evidence is absent or invalid.

### Release Gate
Checks evidence. It does not make product judgments, infer missing artifacts or waive failed checks.

Role boundaries are executable policy where practical. Prompt text alone is not considered sufficient enforcement for critical permissions.

## 3. State machine

```text
NEW
 ↓
PLANNING
 ↓
SPEC_READY
 ↓
SECURITY_DESIGN  ─────────────┐
 ↓                            │ optional only when policy permits
SECURITY_DESIGN_READY         │
 ↓                            │
IMPLEMENTING ◄────────────────┘
 ↓
IMPLEMENTED
 ↓
VERIFYING
 ├─ REJECTED ─────────► IMPLEMENTING
 │                      or PLANNING for spec defects
 └─ ACCEPTED
       ↓
SECURITY_AUDIT
 ├─ BLOCKED ──────────► IMPLEMENTING / PLANNING
 └─ PASSED
       ↓
DOCUMENTING
       ↓
DOCUMENTED
       ↓
RELEASE_GATE
 ├─ BLOCKED ──────────► owning stage
 └─ RELEASED
```

Every transition must be declared explicitly. Direct state editing or skipped stages must not create a release-eligible task.

## 4. Risk classes

### LOW
Documentation-only, copy, isolated styling or changes with no sensitive data/behavior impact.

### MEDIUM
Normal product behavior, UI interaction, ordinary APIs and non-sensitive persistence changes.

### HIGH
Authentication, authorization, personal data, chat/messaging, uploads, payments, security-sensitive integrations, scheduling/business invariants, non-trivial data migrations or external side effects.

### CRITICAL
Privilege model redesign, secrets/credentials, cryptography, destructive migrations, production infrastructure controls, financial settlement or foundational security mechanisms.

A project can add signals that raise risk. It cannot automatically downgrade a risk explicitly set by a human.

## 5. Context packaging

An agent gets the minimum sufficient context:

```text
role manifest
+ immutable core policies
+ project profile/invariants
+ relevant skills
+ task artifacts
+ relevant repository paths/diff
```

Raw historical conversation is excluded by default.

## 6. Handoff protocol

Agents communicate through persistent artifacts, not shared conversational memory:

```text
requirement.md
spec.md
threat-model.md
implementation-report.md
verification-report.md
security-report.md
documentation-report.md
release-report.md
state.json
handoff-*.md
```

Required handoffs are execution contracts. The receiving stage must fail closed if a mandatory handoff is missing, empty, malformed, stale, produced by the wrong stage, or associated with a different `project_id`/`task_id`.

Agents must not reconstruct missing authoritative handoffs from repository context and continue silently.

Every rejection identifies the owning stage.

## 7. Readiness semantics

Readiness is a structured property of artifacts and state.

Explanatory prose is not executable state. Tokens such as `PENDING`, `REPLACE_ME`, `TODO` or `TBD` only affect readiness when they occur in contract fields explicitly defined as unresolved.

Malformed or missing required readiness metadata fails closed.

## 8. Retry routing

- Functional code defect → Implementer.
- Missing/incorrect verification evidence → Implementer/Verifier as appropriate.
- Specification contradiction → Planner.
- Security implementation defect → Implementer.
- Security design defect → Planner + Security Design.
- Documentation inconsistency → Verifier or Planner; Documenter never invents behavior.
- Deterministic gate failure → stage that owns the failed check.
- Missing/invalid handoff → upstream stage responsible for producing that handoff.

## 9. Release integrity

A release decision must be based on current evidence for one canonical project/task identity.

Release must reject:
- missing mandatory artifacts;
- stale evidence from a previous iteration;
- artifacts belonging to another project or task;
- contradictory mandatory verdicts;
- illegal/skipped state transitions;
- failed mandatory tests/checks;
- unresolved required findings.

An LLM cannot override these checks.

## 10. Human authority

Explicit human approval is required to:
- change project invariants;
- lower an assigned risk;
- accept a known HIGH/CRITICAL security finding;
- perform destructive data changes;
- change authentication/authorization architecture;
- release with failing mandatory tests;
- expand scope beyond the approved requirement;
- deploy or modify production credentials unless separately authorized.

Human approval is explicit evidence; it is not permission for an agent to infer a waiver.

## 11. Extension model

Projects extend the core with:

```text
.nomphi/project/skills/<skill-name>/SKILL.md
```

and may define stricter policies in the project profile. Project skills can be loaded by Planner, Implementer, Verifier or Security based on the task.

The core remains unchanged.

## 12. Current hardening phase

`NOM-TEST-007` established the current end-to-end baseline. Defects exposed by that smoke are being addressed in `NOM-FWK-008 — Framework Hardening`.

See `docs/FRAMEWORK_HARDENING.md` for the workstreams and exit criteria.
