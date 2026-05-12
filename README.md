# DT Helper

POC platform for Dynatrace administration via:
- a self-service **catalog** (n8n form),
- approval via **GitHub PR**,
- execution by a **Python runner**,
- with auditable logs + verify-after-execute.

## Status: Phase 1
Template-driven loop only. No LLM bots wired yet. See `docs/architecture.md`.

## Quickstart
1. Configure secrets — see `docs/secrets-setup.md`.
2. `cp .env.example .env` and fill values.
3. `docker compose up -d` to start n8n + runner.
4. In n8n UI (http://localhost:5678), build workflows following
   `automation/n8n/README.md`.
5. Submit the catalog form. A PR will appear in this repo. Merge it to trigger
   execution.

## Test scenario
Create a management zone `myapp_uat_mz_default` in Dynatrace via the catalog.
See `templates/create-management-zone/README.md`.

## Repo layout
```
catalog/    — self-serve request forms
templates/  — reusable execute.py + verify.py scripts (Rule 6)
config/     — centralized YAML configs (Rule 10, 11, 12)
lib/        — shared Python helpers
runner/     — FastAPI service that executes templates
automation/ — n8n workflow setup notes
docs/       — architecture, naming convention, DT API index
tasks/      — per-task audit folder (one folder per Task ID)
```
