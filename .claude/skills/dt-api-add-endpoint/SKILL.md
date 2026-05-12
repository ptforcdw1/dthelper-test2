---
name: dt-api-add-endpoint
description: Add a Dynatrace API endpoint to docs/dt-api-index.md, with required scopes.
---

# dt-api-add-endpoint

Use when a new template needs a DT API operation not yet in the index.
Keeping this index minimal (no full DT docs) is how we honor Rule 13.

## Inputs to gather
- Human-readable operation name (e.g. "List alerting profiles")
- HTTP method (GET / POST / PUT / DELETE)
- Path (starts with `/api/`)
- Required scopes (DT permission codes, e.g. `ReadConfig`, `WriteConfig`,
  `settings.read`, `settings.write`)
- Optional: link to DT docs and any known JSON-body caveat

## Steps
1. Read `docs/dt-api-index.md`.
2. If a row already exists for the same method + path, STOP and report.
3. Append a row to the table, columns matching the existing format:
   `| Operation | Method | Path | Required scopes |`
4. If your scopes include any not listed in `docs/secrets-setup.md` under
   the DT token-scope list, append them there too. Otherwise leave alone.
5. If there's a known version-dependent JSON-body shape, add a bullet to
   "Caveats / known unknowns" with the specific concern.

## Done when
- Row exists in the table with correct columns.
- Scopes are listed accurately (DT will fail-fast on missing scopes).

## Do not
- Add endpoints speculatively. Only add what an actual template needs now.
- Document full DT API bodies here — that belongs in each template's
  `execute.py`. This index stays intentionally minimal.
