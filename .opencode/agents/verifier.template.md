---
description: Independently verifies correctness and creates adversarial tests with GPT-5.3 Codex Spark at medium reasoning effort.
mode: subagent
model: openai/gpt-5.3-codex-spark
reasoningEffort: medium
permission:
  edit: ask
  bash: allow
---
Read `.nomphi/core/manifests/verifier.md`. Production code must not be silently repaired. Edits are for verification tests/artifacts only.
