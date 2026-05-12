---
name: add-template
description: Create a new reusable Dynatrace template (execute.py + verify.py + manifest.yaml + README.md) and register it in templates/index.yaml. Use when a DT operation will run more than once.
---

# add-template

Encodes the contract from `CLAUDE.md`: every script generated MUST have all
4 files (Rule 15), must follow naming conventions (Rule 11), must read config
from `config/` (Rule 10).

## Inputs to gather
- Template id (kebab-case, e.g. `create-tag`)
- One-line description
- Inputs needed (human-friendly names only — Rule 14; no `*_id` fields)
- DT API endpoints touched (must already exist in `docs/dt-api-index.md` —
  if not, invoke `/dt-api-add-endpoint` first)
- Resource type code from `config/naming-convention.yaml` (`mz`, `tag`, `ap`, ...)

## Steps
1. Check `templates/index.yaml` — if id exists, STOP and report.
2. Confirm every DT endpoint already exists in `docs/dt-api-index.md`. If
   not, invoke `/dt-api-add-endpoint` for the missing ones.
3. Create `templates/<id>/` with the 4 required files. Use
   `templates/create-management-zone/` as the structural reference:
   - `manifest.yaml` — id, title, description, inputs[], outputs[], dt_scopes,
     naming.{resource_type, pattern_key}, idempotent: true
   - `execute.py` — read env (`TASK_ID`, `INPUT_*`, `DT_TENANT_URL`, `DT_API_TOKEN`),
     audit start, compute name from naming convention, idempotency check
     (look up by name first), perform action, audit done
   - `verify.py` — read-back; write `tasks/<TASK_ID>/verify.json`; non-zero exit on failure
   - `README.md` — inputs table, expected name pattern, manual run command, scopes
4. Append a row to `templates/index.yaml`.
5. If exposing in the catalog, invoke `/add-catalog-item`.
6. Run `/simplify` on the new directory.
7. Run `/check-naming` to confirm pattern resolution.

## Done when
- All 4 files exist and parse (`python -m py_compile` for .py, valid YAML).
- `templates/index.yaml` has the new entry.
- Manual run command in README matches the template's env-var contract.

## Do not
- Hardcode tenant URL, tokens, app names, or env names anywhere.
- Add `app`/`env` inputs unless the operation actually needs them.
- Generate code that mutates existing DT objects unless explicitly asked.
  Default = "create if not exists".
- Commit directly to `main`. New templates go through a PR (design decision 3).
