# OpenCode integration

Nomphi manifests are vendor-independent and canonical. `.opencode/agents/` only adapts those roles to OpenCode.

Local roles are preconfigured with baseline Ollama IDs. External frontier model IDs remain placeholders because model availability/versioning changes independently of the SDLC.

When binding external agents, copy the template to its active filename and set the model ID available in your environment:

```text
planner.template.md  -> planner.md
verifier.template.md -> verifier.md
security.template.md -> security.md
```

Changing an OpenCode model must not change the corresponding Nomphi manifest.
