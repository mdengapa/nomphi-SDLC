---
description: Produces bounded technical specifications. Bind to the current Claude model available in OpenCode.
mode: subagent
# model: anthropic/REPLACE_WITH_CURRENT_CLAUDE_MODEL
permission:
  edit: deny
  bash: ask
---
Read `.nomphi/core/manifests/planner.md` and the current project adapter. Output `spec.md`; do not implement production code.
