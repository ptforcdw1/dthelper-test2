---
name: new-request
description: Interface Bot — clarify a complex Dynatrace ask, find or generate the right template, write tasks/<id>/request.json, open a PR for approval.
---

# new-request

Phase 4 entry point. Interactive flow from Claude Code CLI (per design
decision: chat interface = CLI). For simple needs, point the user at the
catalog instead.

## Steps

1. **Listen.** Ask what the user wants. Do not assume. Do not propose
   solutions until you understand the intent.
2. **Disambiguate.** Convert any IDs in the ask to names (Rule 14). Ask
   for app/env if missing (Rule 12). Surface confusion explicitly (Rule 1).
3. **Match a template.** Read `templates/index.yaml`. If the ask maps to an
   existing template's id and inputs, USE IT — do not regenerate (Rule 6, 13).
4. **If no template matches:**
   - Confirm with the user that no existing template fits.
   - Invoke `/add-template` to scaffold a new one (Phase 2 automation would
     route this to a CodeGen Bot via n8n instead).
   - Always open as a PR; do NOT commit to main (design decision 3).
5. **Validate inputs.** For each input: confirm against the template's
   manifest (types, required, enum options). For names that will appear in
   DT, run `/check-naming`.
6. **Mint Task ID:** `DT-<UTC YYYYMMDD>-<6 hex>`.
7. **Write `tasks/<task_id>/request.json`** with
   `{task_id, template, inputs, requester}`.
8. **Open a branch + PR:**
   - Branch: `task/<task_id>`
   - Title: `[<task_id>] Approve: <template> for <app>/<env>`
   - Body: the request JSON + a one-paragraph human-readable summary of
     what will change in DT
9. **Return** Task ID, PR URL, and the summary.

## Do not
- Execute against the DT API. You produce a request; the runner executes
  after the PR is merged (Rule 16).
- Generate scripts inline in the chat. New code goes through `/add-template`
  so all 4 required files are produced (Rule 15).
- Skip the PR even for "simple" asks (Rule 16).
- Ask for IDs (Rule 14). If an ID is needed at runtime, the template's
  `execute.py` resolves it from a name via `lib/dt_client.py`.

## Hand-off cases
- User asks a **question** (not a change request) → answer from `docs/`,
  `templates/`, `catalog/`. No PR.
- User reports a **failed task** → invoke `/triage-failure <task_id>`
  instead of opening a new request.
