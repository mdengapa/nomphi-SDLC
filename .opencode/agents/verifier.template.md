---
description: Independently verifies correctness and creates adversarial tests. Bind to the current OpenAI model.
mode: subagent
# model: openai/REPLACE_WITH_CURRENT_OPENAI_MODEL
permission:
  edit: ask
  bash: allow
---
Read `.nomphi/core/manifests/verifier.md`. Production code must not be silently repaired. Edits are for verification tests/artifacts only.
