---
name: task-inspect
description: Read-only summary of a task's lifecycle from its tasks/<id>/ folder. Use to debug or audit a past task.
---

# task-inspect

Read-only. Hits no APIs. Just summarizes what's already in the repo.

## Inputs to gather
- Task ID (format `DT-YYYYMMDD-<6 hex>`)

## Steps
1. Locate `tasks/<task_id>/`. If missing, STOP and report.
2. Read whichever of these exist:
   - `request.json` — what was requested
   - `execution.jsonl` — line-by-line audit events
   - `verify.json` — verification outcome
   - `result.json` — runner's HTTP response (committed by n8n)
   - `diagnosis.md` — present only if `/triage-failure` ran
3. Build a summary in this order:
   - **Request**: template, inputs, requester
   - **Status**: derived from `verify.json.passed`, else `result.json.status`,
     else "incomplete"
   - **Timeline**: first and last `ts` from `execution.jsonl`, total duration
   - **Key events**: events from `execution.jsonl` (skip the routine
     `start` / `done`; show the interesting ones)
   - **Outputs**: e.g. `management_zone_id` from the `done` event
   - **Failure** (if any): error events + verify fields
4. Surface git log entries touching `tasks/<task_id>/` (one-line summaries).

## Output
A single-screen Markdown summary. Aim for under 30 lines.

## Do not
- Write or modify anything under `tasks/<id>/`. Read-only.
- Call Dynatrace. Inspect the local audit trail only.
