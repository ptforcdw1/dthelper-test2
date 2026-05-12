---
name: triage-failure
description: Problem Responder — diagnose why a task failed and write tasks/<id>/diagnosis.md. Does not modify code or retry.
---

# triage-failure

Read-only diagnosis. Classifies the failure into one of a fixed set so
fixes are mechanical, not improvised.

## Inputs to gather
- Task ID

## Steps

1. Run `/task-inspect <task_id>` to get the lifecycle summary.
2. Read in detail:
   - `tasks/<id>/execution.jsonl` — find events with name `error` or non-success
   - `tasks/<id>/verify.json` — `passed`, `expected_name`, `found_id`
   - `tasks/<id>/result.json` — runner stdout/stderr if present
3. Read the template that ran:
   - `templates/<template>/execute.py`
   - `templates/<template>/verify.py`
   - `templates/<template>/manifest.yaml`
4. **Classify** the failure into exactly ONE class:
   - **input-invalid** — input violated manifest's type / regex / enum.
     Cite the offending field + the rule.
   - **naming-violation** — generated name failed validation. Run
     `/check-naming` to confirm.
   - **dt-api-error** — HTTP non-2xx. Cite status code + DT error body if
     captured.
   - **scope-missing** — likely a missing DT scope. Cross-check the
     template's `dt_scopes` against the token's actual scopes (point user
     to `docs/secrets-setup.md`).
   - **idempotency-bug** — `execute` reported success but `verify` failed.
     Likely the `find_*_by_name` lookup is wrong.
   - **infra** — runner unreachable, GitHub commit failed, etc.
   - **unknown** — evidence doesn't fit. Surface raw evidence. Do not guess.
5. Write `tasks/<id>/diagnosis.md` with:
   - **Class**: one of the above
   - **Evidence**: file:line citations from the logs
   - **Suggested fix**: minimum change (Rule 2). Reference the exact file
     and line to edit.
   - **Suggested next action**: e.g. "run `/task-replay <id>` after fix",
     or "open a PR with the fix and re-run"
6. Return a one-paragraph summary + path to the diagnosis file.

## When evidence points multiple ways
List candidate classes ranked by likelihood, each with its own evidence.
Do NOT silently pick one (Rule 1).

## Do not
- Make assumptions. If evidence is missing, class = `unknown` and say so.
- Modify code or config. Diagnosis is the only artifact this skill writes.
- Attempt to retry. Use `/task-replay` AFTER a fix is committed.
- Recommend disabling verify scripts or bypassing approval as a "fix".
  Those are guardrails, not bugs.
