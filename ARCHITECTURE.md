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
Controls state, routes work, packages context and enforces gates. It should be mostly deterministic. An LLM may classify or summarize, but cannot override workflow constraints.

### Planner
Turns a requirement into an implementation contract. It reads but does not modify production code.

### Security
Runs twice. Before implementation it produces a threat model. After verification it performs an independent AppSec audit.

### Implementer
Writes production code and implementation-level tests. It is not allowed to redefine the specification.

### Verifier
Tries to falsify the implementation. It may add verification tests but does not silently repair production code.

### Documenter
Updates durable documentation to match accepted behavior.

### Release Gate
Checks evidence. It does not make product judgments or waive failed checks.

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

Every rejection identifies the owning stage.

## 7. Retry routing

- Functional code defect → Implementer.
- Missing/incorrect verification evidence → Implementer/Verifier as appropriate.
- Specification contradiction → Planner.
- Security implementation defect → Implementer.
- Security design defect → Planner + Security Design.
- Documentation inconsistency → Verifier or Planner; Documenter never invents behavior.
- Deterministic gate failure → stage that owns the failed check.

## 8. Human authority

Explicit human approval is required to:
- change project invariants;
- lower an assigned risk;
- accept a known HIGH/CRITICAL security finding;
- perform destructive data changes;
- change authentication/authorization architecture;
- release with failing mandatory tests;
- expand scope beyond the approved requirement;
- deploy or modify production credentials unless separately authorized.

## 9. Extension model

Projects extend the core with:

```text
.nomphi/project/skills/<skill-name>/SKILL.md
```

and may define stricter policies in the project profile. Project skills can be loaded by Planner, Implementer, Verifier or Security based on the task.

The core remains unchanged.
