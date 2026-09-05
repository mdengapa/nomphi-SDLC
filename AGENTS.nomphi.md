# Nomphi repository-wide agent policy

This repository uses Nomphi Agentic SDLC.

Before modifying production code:
1. identify the active task under `.nomphi/tasks/`;
2. read the role manifest under `.nomphi/core/manifests/`;
3. read `.nomphi/project/` context relevant to the change;
4. read the approved task `spec.md`;
5. load only relevant shared/project skills;
6. do not expand scope silently;
7. execute project-configured checks and task-specific checks;
8. record deviations/findings in task artifacts.

Core gates take precedence over project convenience. Project rules may strengthen core gates but may not silently weaken them.

No agent may push, deploy, alter production credentials, waive blocking findings or change project invariants without explicit human authorization.
