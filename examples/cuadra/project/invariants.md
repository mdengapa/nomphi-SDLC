# CUADRA example project invariants

This file demonstrates project specialization only. It is not Nomphi Core.

- Employee-facing schedule data must respect published/authorized visibility rules.
- Manual scheduling changes must preserve domain validation.
- Critical schedule mutations must not leave invalid partial state.
- Sender/recipient identity for operational messaging is enforced server-side.
- Employee-scoped object access requires object-level authorization.
