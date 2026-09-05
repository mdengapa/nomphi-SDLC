# Project Adapter

This directory is intentionally project-specific. It is the boundary between reusable Nomphi engineering rules and the current product/repository.

Fill these files with durable engineering context. Do not copy historical chats.

- `project-profile.json`: project identity, stack, default risk and mandatory skills.
- `architecture.md`: current architecture and important boundaries.
- `domain.md`: domain terminology and business concepts.
- `invariants.md`: rules the system must never violate.
- `conventions.md`: repository, code and design conventions.
- `security-boundaries.md`: assets, roles, trust boundaries and project-specific abuse cases.
- `commands.json`: deterministic quality commands.
- `skills/`: project-only skills.
