# OpenCode integration

Nomphi manifests are vendor-independent and canonical. `.opencode/agents/` only adapts those roles to OpenCode.

Model bindings are configuration, not architecture. Changing a provider or model must not redefine the corresponding Nomphi role, authority or workflow contract.

## Current validated bindings

Baseline after `NOM-TEST-007`:

| Role | Binding | Effort |
|---|---|---|
| Orchestrator | GPT-5.6 Terra | medium |
| Planner | GPT-5.6 Sol | high |
| Implementer | GPT-5.6 Terra | medium |
| Verifier | GPT-5.6 Terra | medium |
| Documenter | GPT-5.6 Terra | medium |

These bindings remain fixed during `NOM-FWK-008` unless a binding itself blocks execution. The purpose is to isolate framework hardening from model experimentation.

Qwen3 Coder 30B is not used on the critical editing path for this phase because the smoke showed materially lower reliability in roles with write authority.

## Adapter rule

`.opencode/agents/` files are runtime adapters only. The corresponding Nomphi manifests remain canonical.

Changing an OpenCode model must not:
- expand the role's authority;
- weaken a handoff requirement;
- bypass the state machine;
- alter release/security gates;
- convert a forbidden action into an allowed one.

During framework hardening, role separation must increasingly be enforced by executable permissions and deterministic guards rather than prompt compliance alone.
