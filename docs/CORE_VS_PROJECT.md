# Core vs Project decision rule

Use this test whenever adding an instruction:

> Would this rule still be valid if the current repository were replaced by a completely different Nomphi project tomorrow?

If **yes**, it may belong in Core.
If **no**, it belongs in the Project Adapter or a project skill.

Examples:

| Rule | Location |
|---|---|
| Verifier must be independent from Implementer | Core |
| HIGH security finding blocks release | Core |
| Frontend must meet accessibility criteria | Shared skill / core policy |
| This product uses PostgreSQL | Project adapter |
| Published schedules are immutable | Project invariant |
| Brand uses a Nordic visual language | Project skill |
| Run `pnpm test` before release | Project commands |
| Employee cannot access another employee's record | Project security boundary / test |
