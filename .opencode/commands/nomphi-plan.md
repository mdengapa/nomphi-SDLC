---
description: Run the Nomphi Planner subagent for a task.
agent: planner
subagent: true
---

Plan Nomphi task $1.

Read and obey:
- `.nomphi/core/manifests/planner.md`
- `.nomphi/tasks/$1/requirement.md`
- `.nomphi/tasks/$1/handoff-planner-planning.md`
- `.nomphi/project/`
- only repository code and schemas relevant to the task

Your only owned artifact is `.nomphi/tasks/$1/spec.md`.

Do not change workflow state.
Do not call `scripts/nomphi.py`.
Do not call `scripts/nomphi_agent.py advance` or `route`.
Do not modify `state.json`.
Do not implement production code.
Inspect repository evidence before making claims.
Do not infer project identifier rules from task identifier rules.
Do not generalize from example values.
Existing facts must be supported by repository evidence.
Mark new design choices `PROPOSED:`.
Mark unresolved facts `UNKNOWN:`.
If a material UNKNOWN remains, keep `Status: PENDING`.
Never mark planning checkboxes `[x]`.
Do not remove UNKNOWN items merely to make a gate pass.

When finished, report only:
- Status COMPLETE or PENDING
- evidence files used
- proposed elements
- unknowns
- files modified
