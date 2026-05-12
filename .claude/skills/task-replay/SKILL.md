---
name: task-replay
description: Re-run a past task (same template + inputs) against the runner. For testing fixes. Mints a NEW task ID; never overwrites the original.
---

# task-replay

Use after fixing a template / config that caused a prior failure. Bypasses
the PR approval flow — debugging-only (see caveats).

## Inputs to gather
- Original Task ID to replay
- Explicit confirmation: "Yes, replay against the configured DT tenant."

## Steps
1. Read `tasks/<original_id>/request.json` — extract `template` and `inputs`.
   If missing, STOP.
2. Read `templates/<template>/manifest.yaml` — check `idempotent: true`. If
   false, surface a warning and require an extra confirmation before continuing.
3. Mint a new Task ID: `DT-<UTC YYYYMMDD>-<6 hex>`.
4. Health-check the runner: `GET http://localhost:8080/health`. If down,
   instruct user to `docker compose up -d` and STOP.
5. POST to `http://localhost:8080/run` with
   `{task_id: <new>, template: <orig>, inputs: <orig>}`.
6. Wait for the response (synchronous).
7. Surface: pass/fail, the new Task ID, and a relative path to
   `tasks/<new_id>/`.
8. Suggest `/task-inspect <new_id>` to see details.

## Output
- Pass/fail summary
- New Task ID
- Side-by-side diff vs. original `verify.json` if both exist

## Caveats — surface explicitly
- Bypasses the PR approval (Rule 16). Debugging only — NOT for production
  work.
- Non-idempotent templates may double-act. Always check
  `manifest.yaml.idempotent`.
- Default target is whichever DT tenant is in the runner's env. If the
  original task targeted a different tenant, this WILL hit the current one.

## Do not
- Replay against PROD without explicit `--prod-ack` confirmation.
- Delete or modify the original `tasks/<original_id>/` folder.
