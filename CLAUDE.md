# DT Helper

Platform that administers Dynatrace via API calls. You don't call DT APIs from
this assistant — you produce artifacts (request files, scripts, configs) and
n8n + the Python runner execute them.

## Hard rules
- Never hardcode tenant URL, tokens, app names, or env names. Read from
  `config/global.yaml` and `config/apps/<app>/<env>.yaml`.
- Every script generated MUST have: `execute.py`, `verify.py`, `README.md`, `manifest.yaml`.
- Every DT object created MUST follow `config/naming-convention.yaml`.
- Ask users for human-friendly inputs (service name, app, env). Never IDs.
  If you need an ID, resolve from a name inside the script using `lib/dt_client.py`.
- Every task has a Task ID `DT-YYYYMMDD-<6char>`. All artifacts go under `tasks/<id>/`.

## Where things live
- Catalog (simple requests, no LLM at runtime): `catalog/`
- Reusable scripts: `templates/` — check `templates/index.yaml` BEFORE generating new code.
- App/env config: `config/apps/<app>/<env>.yaml`
- Naming rules: `config/naming-convention.yaml`
- DT API endpoints index: `docs/dt-api-index.md`
- Architecture: `docs/architecture.md`

## Future roles (Phase 2+)
- Interface bot — `agents/interface/CLAUDE.md`
- CodeGen bot — `agents/codegen/CLAUDE.md`
- Problem responder — `agents/problem-responder/CLAUDE.md`

When acting as one of these, load ONLY that role's CLAUDE.md.

## Current scope: Phase 1
No LLM bots yet. Only the catalog → PR → runner → verify loop, exercised by
the `create-management-zone` template. See `docs/architecture.md`.
