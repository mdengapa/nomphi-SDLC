# Adoption guide

## Install the core

Run `bootstrap.sh` against an existing repository. The bootstrap installs the Nomphi core and creates a blank project adapter.

## Complete the project adapter

Before the first real task, document:
- project purpose and type;
- stack;
- architecture;
- domain terminology;
- hard invariants;
- coding/repository conventions;
- security boundaries;
- test/lint/typecheck/E2E commands;
- mandatory project-specific skills.

The adapter is not marketing documentation. It should contain only durable facts an engineering agent needs to make correct decisions.

## Pilot

Use one bounded, reversible feature. Do not validate the SDLC first with a foundational authentication rewrite or destructive migration.

Observe:
- context size sent to each agent;
- specification ambiguity;
- unnecessary returns to Planning;
- false positives/negatives from Verification;
- security findings that should have been caught during design;
- local-model implementation quality;
- token spend by role;
- cycle time and number of iterations.

Change the core only when the lesson is generic across projects. Put project-specific lessons in that project's adapter or skills.
