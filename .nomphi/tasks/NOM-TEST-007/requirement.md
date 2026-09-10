# Requirement

ID: NOM-TEST-007
Title: Validate project identifier
Owner:
Risk: LOW

## Problem

## User / system outcome

## Value

## Constraints

## Explicit non-goals

## Evidence / references

## Human decisions already made
- `project_id` is the stable canonical identifier of a Nomphi project.
- Its source of truth is `.nomphi/project/project-profile.json`.
- Every task MUST copy exactly that `project_id` into its `state.json`.
- `project_id` is immutable for the lifetime of the project.
- Changing the project name, repository name or directory does not change `project_id`.
- Format: lowercase kebab-case matching `^[a-z0-9]+(?:-[a-z0-9]+)*$`.
- Agents may read `project_id` but MUST NOT invent, derive, rename or modify it.
- If a project has no valid `project_id`, initialization requires an explicit human decision.
- A task whose `state.json.project_id` differs from the project profile is invalid and MUST be rejected by the runtime.
